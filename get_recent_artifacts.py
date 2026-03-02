#!/usr/bin/env python3

import argparse
import certifi
import getpass
import json
import logging
import os
import shutil
import tempfile
import urllib3

from posixpath import join as posixjoin
from urllib.parse import urljoin
from urllib.request import urlopen

GITHUB_API_URL = 'https://api.github.com'
GITHUB_REPOS = 'repos'
GITHUB_ACTIONS = 'actions'
GITHUB_WORKFLOWS = 'workflows'
GITHUB_WORKFLOW_RUNS = 'workflow_runs'
GITHUB_RUNS = 'runs'
GITHUB_NAME = 'name'
GITHUB_ID = 'id'

HTTP_GET = 'GET'
UTF8 = 'utf-8'

HELP_DESCRIPTION = """Query the GitHub REST API to search for and retieve INSPECTA CI/CD Pipeline \
reporting and built artifacts."""

HELP_EPILOG = """
  Suggested usage scenarios:
  Retrieve all artifacts of Workflow #1 (Analysis and HAMR code generation):
    get_recent_artifacts.py --workflow="Model Analysis and Code Generation"
  Retrieve the Logika and Verus analysis artifacts from the most-recent workflow run on the feb-2026 branch:
    get_recent_artifacts.py --branch feb-2026 --artifact_names=logika-analysis-report,verus-analysis-report
"""

logger = logging.getLogger(__name__)

def get_auth_str():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    return f"{username}:{password}"

def get_workflows(args, http):
    url = urljoin(GITHUB_API_URL,
        posixjoin(GITHUB_REPOS, args.organization, args.repository, GITHUB_ACTIONS, GITHUB_WORKFLOWS))
    logger.debug('Querying workflows from {}'.format(url))
    response = urllib3.request(HTTP_GET, url)
    logger.debug('Workflow query response status {}'.format(response.status))
    workflows_result = json.loads(response.data.decode(UTF8))
    logger.debug('Found {} workflows {}'.format(workflows_result['total_count'],
        [w[GITHUB_NAME] for w in workflows_result[GITHUB_WORKFLOWS]]))
    result = []
    for workflow in workflows_result[GITHUB_WORKFLOWS]:
        if args.workflow is None or args.workflow == str(workflow[GITHUB_ID]) \
                or args.workflow == workflow[GITHUB_NAME] or args.workflow == workflow['path']:
            logger.debug('Workflow {} matches'.format(workflow[GITHUB_NAME]))
            result.append(workflow)
    return result

def get_workflow_runs(args, http, workflow):
    url = urljoin(GITHUB_API_URL, posixjoin(GITHUB_REPOS, args.organization, args.repository, GITHUB_ACTIONS,
                       GITHUB_WORKFLOWS, str(workflow[GITHUB_ID]), GITHUB_RUNS))
    logger.debug('Querying workflow runs from {}'.format(url))
    response = urllib3.request(HTTP_GET, url)
    logger.debug('Workflow query response status {}'.format(response.status))
    workflow_runs = json.loads(response.data.decode(UTF8))
    logger.debug('Found {} workflow {} run numbers {}'.format(workflow_runs['total_count'],
        workflow[GITHUB_NAME],
        [w[GITHUB_ID] for w in workflow_runs[GITHUB_WORKFLOW_RUNS]]))
    result = []
    for workflow_run in workflow_runs[GITHUB_WORKFLOW_RUNS]:
        if (args.branch is None or args.branch == workflow_run['head_branch']) \
                and (args.commit is None or args.commit == workflow_run['head_sha']):
            logger.debug('Workflow run {} matches'.format(workflow_run[GITHUB_ID]))
            result.append(workflow_run)
    return result

def get_most_recent_workflow_runs(workflow_runs):
    # The GitHub API guarantees the order of retrieval is most recent to least recent
    # The input here is list of runs across possibly multiple workflows.  Get the most
    # recent run for each workflow.
    result = []
    found_workflow_names = []
    for workflow_run in workflow_runs:
        if workflow_run[GITHUB_NAME] not in found_workflow_names:
            found_workflow_names.append(workflow_run[GITHUB_NAME])
            logger.debug('Selecting recent workflow {} run {}'.format(workflow_run[GITHUB_NAME], workflow_run[GITHUB_ID]))
            result.append(workflow_run)
    return result

def get_most_recent_artifacts(args, https, workflow_run):
    artifacts_url = workflow_run['artifacts_url']
    logger.debug('Querying artifacts from {}'.format(artifacts_url))
    response = urllib3.request(HTTP_GET, artifacts_url)
    logger.debug('Artifacts query response status {}'.format(response.status))
    return json.loads(response.data.decode(UTF8))

def fetch_artifacts(args, http, artifacts):
    for artifact in artifacts['artifacts']:
        if args.artifact_names is None or str(artifact[GITHUB_ID]) in args.artifact_names.split(',') \
                or artifact[GITHUB_NAME] in args.artifact_names.split(','):
            logger.debug('Artifact {} from workflow {} matches'.format(artifact[GITHUB_NAME], artifact['workflow_run'][GITHUB_ID]))
            artifact_url = artifact['archive_download_url']
            logger.debug('Artifact download URL is {}'.format(artifact_url))
            if args.dry_run:
                logger.info('Would download {} from {}'.format(artifact[GITHUB_NAME], artifact_url))
            else:
                logger.info('Downloading artifact {}'.format(artifact[GITHUB_NAME]))
                fetch_artifact(args, http, artifact[GITHUB_NAME], artifact_url)

def fetch_artifact(args, http, artifact_name, artifact_url):
    if args.destination is not None and not os.path.exists(args.destination):
        os.makedirs(args.destination)
    destination_dir = os.path.join(args.destination, artifact_name) \
        if args.destination is not None else os.path.join(os.getcwd(), artifact_name)
    with http.request(HTTP_GET, artifact_url, redirect=True, preload_content=False) as response:
        logger.debug('Artifact download response status {}'.format(response.status))
        if response.status == 200:
            with tempfile.NamedTemporaryFile() as tfile:
                while True:
                    data = response.read(1000000)
                    if not data:
                        break;
                    tfile.write(data)
                logger.debug('Downloaded {} bytes'.format(tfile.tell()))
                tfile.seek(0)
                if not os.path.exists(destination_dir):
                    os.mkdir(destination_dir)
                shutil.unpack_archive(tfile.name, destination_dir, format='zip')
                filelist = os.listdir(destination_dir)
                if len(filelist) == 1 and os.path.splitext(filelist[0])[1] == '.tar':
                    tarfile = os.path.join(destination_dir, filelist[0])
                    shutil.unpack_archive(tarfile, destination_dir, format='tar')
                    os.remove(tarfile)
        else:
            logger.error('Unable to download artifact: {}'.format(response.status))

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION,
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--organization",
                        help="The owner organization of the repository. Default 'loonwerks'",
                        default='loonwerks')
    parser.add_argument("--repository",
                        help="The repository on which the actions run. Default 'INSPECTA-demo'",
                        default='INSPECTA-demo')
    parser.add_argument("--branch",
                        help="Limit the artifact search to the given branch.  Default searches all branches")
    parser.add_argument("--commit",
                        help="Limit the artifact search to the given commit hash.  Default searches all commits")
    parser.add_argument("--workflow",
                        help="The id, name, or path of the workflow to search.  Default searches all workflows")
    parser.add_argument("--artifact_names", type=str,
                        help="Limit the search to the given comma-separated list of artifact names")
    parser.add_argument("--token",
                        help="Use the given token for authorization.  If not specified, uses value of GITHUB_TOKEN as token.")
    parser.add_argument("--destination",
                        help="Extract the artifacts to the given directory.  If not specified, uses the current working directory.",
                        default=None)
    parser.add_argument("--dry-run",
                        help="Perform API actions except do not download artifacts",
                        action="store_true")
    parser.add_argument('--log', default='INFO', help='Set log level')
    args = parser.parse_args()

    logger.setLevel(args.log.upper())

    logger.debug('Arguments: {}'.format(vars(args)))

    token = args.token if args.token is not None else os.environ.get('GITHUB_TOKEN')

    headers = {'Authorization' : 'Bearer {}'.format(token)} if token is not None else urllib3.make_headers(basic_auth=get_auth_str())

    http = urllib3.PoolManager(10, headers=headers, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    workflows = get_workflows(args, http)

    for workflow in workflows:
        workflow_runs = get_most_recent_workflow_runs(get_workflow_runs(args, http, workflow))
        for workflow_run in workflow_runs:
            artifacts = get_most_recent_artifacts(args, http, workflow_run)
            fetch_artifacts(args, http, artifacts)

if __name__ == "__main__":
    main()