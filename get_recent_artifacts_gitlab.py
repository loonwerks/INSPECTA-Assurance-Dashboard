#!/usr/bin/env python3

import argparse
import certifi
import getpass
import json
import logging
import os
import re
import shutil
import ssl
import tempfile
import urllib3

from posixpath import join as posixjoin
from urllib.parse import urljoin
from urllib.request import urlopen

GITLAB_API = 'api'
GITLAB_API_VERSION = 'v4'
GITLAB_PROJECTS = 'projects'
GITLAB_ACTIONS = 'actions'
GITLAB_PIPELINES = 'pipelines'
GITLAB_ARTIFACTS = 'artifacts'
GITLAB_JOBS = 'jobs'
GITLAB_RUNS = 'runs'
GITLAB_NAME = 'name'
GITLAB_ID = 'id'

HTTP_GET = 'GET'
UTF8 = 'utf-8'

HELP_DESCRIPTION = """Query the GitLab REST API to search for and retieve INSPECTA CI/CD Pipeline \
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

def get_projects(args, http):
    url = urljoin(args.gitlab, posixjoin(GITLAB_API, GITLAB_API_VERSION, GITLAB_PROJECTS))
    logger.debug('Querying projects from {}'.format(url))
    response = http.request(HTTP_GET, url)
    logger.debug('Project query response status {}'.format(response.status))
    projects_result = json.loads(response.data.decode(UTF8))
    logger.debug('Found {} projects {}'.format(len(projects_result),
        [w[GITLAB_NAME] for w in projects_result]))
    result = []
    for project in projects_result:
        if args.project is None or args.project == str(project[GITLAB_ID]) \
                or args.project == project[GITLAB_NAME] or args.project == project['path_with_namespace']:
            logger.debug('Project {} ({}) matches'.format(project[GITLAB_NAME], project[GITLAB_ID]))
            result.append(project)
    return result

def get_pipelines(args, http, project):
    url = urljoin(args.gitlab,
        posixjoin(GITLAB_API, GITLAB_API_VERSION, GITLAB_PROJECTS, str(project['id']), GITLAB_PIPELINES))
    logger.debug('Querying pipelines from {}'.format(url))
    response = http.request(HTTP_GET, url)
    logger.debug('Pipeline query response status {}'.format(response.status))
    pipelines_result = json.loads(response.data.decode(UTF8))
    logger.debug(json.dumps(pipelines_result, indent=4))
    logger.debug('Found {} pipelines {}'.format(len(pipelines_result),
        [w[GITLAB_ID] for w in pipelines_result]))
    return pipelines_result

def find_latest_pipeline(pipelines):
    def find_latest_pipeline_rec(result, pipelines):
        if pipelines:
            head, *tail = pipelines
            if head.get('updated_at', '0') > result.get('updated_at', '0'):
                result = head
            return find_latest_pipeline_rec(result, tail)
        else:
            return result
    if pipelines:
        return find_latest_pipeline_rec(pipelines[0], pipelines)
    return None

def get_latest_pipeline(args, http, project):
        url = urljoin(args.gitlab,
            posixjoin(GITLAB_API, GITLAB_API_VERSION, GITLAB_PROJECTS, str(project['id']), GITLAB_PIPELINES, 'latest'))
        logger.debug('Querying pipeline from {}'.format(url))
        response = http.request(HTTP_GET, url)
        logger.debug('Pipeline query response status {}'.format(response.status))
        if response.status == 200:
            pipeline = json.loads(response.data.decode(UTF8))
            logger.debug(json.dumps(pipeline, indent=4))
            if (args.branch is None or args.branch == pipeline['head_branch']) \
                    and (args.commit is None or args.commit == pipeline['head_sha']):
                logger.debug('Pipeline run {} matches'.format(pipeline[GITLAB_ID]))
                return pipeline
        return None

def get_jobs(args, http, project):
    result = []
    url = urljoin(args.gitlab, posixjoin(GITLAB_API, GITLAB_API_VERSION, GITLAB_PROJECTS, str(project[GITLAB_ID]), GITLAB_JOBS))
    logger.debug('Querying jobs from {}'.format(url))
    response = http.request(HTTP_GET, url)
    logger.debug('Job query response status {}'.format(response.status))
    if response.status == 200:
        jobs_result = json.loads(response.data.decode(UTF8))
        #logger.debug(json.dumps(jobs_result, indent=4))
        logger.debug('Found {} jobs {}'.format(len(jobs_result),
            [w[GITLAB_NAME] for w in jobs_result]))
        for job in jobs_result:  # commit, 
            if args.workflow is None or args.workflow == str(job['stage']) \
                    or args.workflow == job[GITLAB_NAME]:
                logger.debug('Job {} ({}) matches'.format(job[GITLAB_NAME], job[GITLAB_ID]))
                result.append(job)
    return result

def list_artifacts(args, http, project_id, job_id):
    def list_tree_rec(args, http, project_id, job_id, path):
        url = urljoin(args.gitlab, posixjoin(GITLAB_API, GITLAB_API_VERSION, GITLAB_PROJECTS, str(project_id), GITLAB_JOBS,
                                              str(job_id), GITLAB_ARTIFACTS, 'tree?path={}'.format(path) if path is not None else 'tree'))
        logger.debug('Querying artifacts from {}'.format(url))
        response = http.request(HTTP_GET, url)
        logger.debug('Artifact query response status {}'.format(response.status))
        #logger.debug('Response data: {}'.format(str(response.data)))
        result = []
        if response.status == 200:
            artifacts_result = json.loads(response.data.decode(UTF8))
            #logger.debug(json.dumps(artifacts_result, indent=4))
            for artifact in artifacts_result:
                if artifact['type'] == 'directory':
                    result.extend(list_tree_rec(args, http, project_id, job_id, artifact['path']))
                elif artifact['type'] == 'file':
                    if args.artifact_names is None:
                        result.append(artifact['path'])
                    else:
                        artifact_names = [s.strip() for s in args.artifact_names.split(',')]
                        if artifact['name'] in artifact_names or artifact['path'] in artifact_names or \
                                any([p.search(artifact['name']) or p.search(artifact['path']) for p in [re.compile(aname) for aname in artifact_names]]):
                            result.append(artifact['path'])
        return result
    return list_tree_rec(args, http, project_id, job_id, None)

def fetch_artifacts(args, http, project_id, job_id, artifacts):
    for artifact in artifacts:
        logger.debug('Artifact {} matches'.format(artifact))
        artifact_url = urljoin(args.gitlab, posixjoin(GITLAB_API, GITLAB_API_VERSION, GITLAB_PROJECTS, str(project_id), GITLAB_JOBS,
                                              str(job_id), GITLAB_ARTIFACTS, artifact))
        logger.debug('Artifact download URL is {}'.format(artifact_url))
        if args.dry_run:
            logger.info('Would download {} from {}'.format(artifact, artifact_url))
        else:
            logger.info('Downloading artifact {}'.format(artifact))
            fetch_artifact(args, http, artifact, artifact_url)

def fetch_artifact(args, http, artifact_name, artifact_url):
    if args.destination is not None and not os.path.exists(args.destination):
        os.makedirs(args.destination)
    destination_file = os.path.join(args.destination, artifact_name) \
        if args.destination is not None else os.path.join(os.getcwd(), artifact_name)
    with http.request(HTTP_GET, artifact_url, redirect=True, preload_content=False) as response:
        logger.debug('Artifact download response status {}'.format(response.status))
        if response.status == 200:
            destination_dir = os.path.dirname(destination_file)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            with open(destination_file, 'wb') as tfile:
                while True:
                    data = response.read(1000000)
                    if not data:
                        break;
                    tfile.write(data)
                logger.debug('Downloaded {} bytes'.format(tfile.tell()))
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
    parser.add_argument("--gitlab",
                        help="The URL of the GitLab instance",
                        default='https://gitlab.inspecta.local:8929')
    parser.add_argument("--cacert",
                        help="Path to a certificate file to use rather than the default")
    parser.add_argument("--organization",
                        help="The owner organization of the repository. Default 'loonwerks'",
                        default='loonwerks')
    parser.add_argument("--project",
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
                        help="Use the given token for authorization.  If not specified, uses value of GITLAB_TOKEN as token.")
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

    token = args.token if args.token is not None else os.environ.get('GITLAB_TOKEN')

    headers = {'Authorization' : 'Bearer {}'.format(token)} if token is not None else urllib3.make_headers(basic_auth=get_auth_str())

    http = urllib3.PoolManager(10, headers=headers, cert_reqs='CERT_NONE' if args.cacert is not None else 'CERT_REQUIRED',
                                ca_certs=args.cacert if args.cacert is not None else certifi.where())

    projects = get_projects(args, http)

    for project in projects:
        pipelines = get_pipelines(args, http, project)
        latest_pipeline = find_latest_pipeline(pipelines)
        if latest_pipeline is not None:
            jobs = get_jobs(args, http, project)
            for job in jobs:
                if job['pipeline'][GITLAB_ID] == latest_pipeline[GITLAB_ID]:
                    logger.debug('Querying artifacts for pipeline {} ({}) job {} ({})'
                                 .format(latest_pipeline[GITLAB_NAME], latest_pipeline[GITLAB_ID], job[GITLAB_NAME], job[GITLAB_ID]))
                    artifacts = list_artifacts(args, http, project[GITLAB_ID], job[GITLAB_ID])
                    logger.debug('Job artifacts: {}'.format(json.dumps(artifacts, indent=4)))
                    fetch_artifacts(args, http, project[GITLAB_ID], job[GITLAB_ID], artifacts)

if __name__ == "__main__":
    main()