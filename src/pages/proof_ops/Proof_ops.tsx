import { SetStateAction, useEffect, useState } from "react"
import "./Proof_ops.scss"
import SimpleBox from "../../components/simpleBox/SimpleBox"
import DataTable from "../../components/dataTable/DataTable"
import { GridColDef } from "@mui/x-data-grid";

const columns: GridColDef[] = [
  { field: 'id', headerName: 'ID', width: 90 },
  { field: 'runNum', headerName: 'Run Number', width: 150 },
  {
    field: 'itemName',
    headerName: 'Name',
    width: 150,
  //   editable: true,
  },
  {
    field: 'itemTitle',
    headerName: 'Title',
    width: 150,
  //   editable: true,
  },
  {
    field: 'itemConclusion',
    headerName: 'Status',
  //   type: 'number',
    width: 110,
  //   editable: true,
  },
  {
    field: 'itemCreatedAt',
    headerName: 'Created At',
    description: 'This column has a value getter and is not sortable.',
    sortable: false,
    width: 160,
  //   valueGetter: (value, row) => `${row.firstName || ''} ${row.lastName || ''}`,
  },
  {
      field: 'itemActor',
      headerName: 'Actor',
      width: 150,
    //   editable: true,
    },
    {
      field: 'itemRepo',
      headerName: 'Repository Name',
      width: 150,
    //   editable: true,
    },
];

const Proof_ops = () => {
  const [items, setItems] = useState<any[]>([])
  const [owner] = useState("loonwerks")
  const [repo] = useState("AGREE-Toy-Example")
  const [dataRows, setDataRows] = useState([])
  const [totalWorkflowRuns, setWorkflowRuns] = useState(0)
  const [totalCompetedRuns, setCompetedRuns] = useState(0)
  const [totalFailedRuns, setFailedRuns] = useState(0)
  const [totalCancelledRuns, setCancelledRuns] = useState(0)
  let competedRuns = 0
  let failedRuns = 0
  let cancelledRuns = 0
  let rows: []
  // useEffect(() => {
  const fetchRepos = async () => {
    // const res = await fetch('https://api.github.com/users')
    const res = await fetch('https://api.github.com/repos/loonwerks/AGREE-Toy-Example/actions/runs', {method:'GET', 
    });
    const data = await res.json()
    const result = Object.keys(data).map((k) => data[k]);
    setItems(result)
    setWorkflowRuns(result[0])
    console.log(totalWorkflowRuns)
    for (let i = 0; i < result[1].length; i++){
      let tempRow = {};
      if (result[1][i].conclusion === 'failure'){
        failedRuns ++;
      } else if (result[1][i].conclusion === 'success'){
        competedRuns ++;
      } else if (result[1][i].conclusion === 'cancelled'){
        cancelledRuns ++;
      }
      // tempRow[] = result[1].id;
      // runNum: result[1].run_number,
      // itemName: result[1].name,
      // itemTitle: result[1].title,
      // itemConclusion: result[1].conclusion, 
      // itemCreatedAt: result[1].created_at,
      // itemActor: result[1].actor.login,
      // itemRepo: result[1].head_repository.name
    }
    // setDataRows(rows)
    setCompetedRuns(competedRuns)
    setFailedRuns(failedRuns)
    setCancelledRuns(cancelledRuns)
    // console.log("Hello:" + typeof(items))

    // axios
    //     .get("https://api.github.com/repos/loonwerks/AGREE-Toy-Example/actions/workflows", {
    //     })
    //     .then((response) => {
    //       setItems(response.data);
    //     })
    //     .catch((error) => {
    //       alert("error fetching data:" + error);
    //     });
  };

  useEffect(() => {
    fetchRepos();
  }, []);


  return (
    <div className= "proof_ops">
      <div className="box1">
        <SimpleBox title={'Total Workflow Runs'} value={totalWorkflowRuns} colVal={'aquamarine'}/>
        <SimpleBox title={'Completed Runs'} value={totalCompetedRuns} colVal={'greenyellow'}/>
        <SimpleBox title={'Cancelled Runs'} value={totalCancelledRuns} colVal={'gold'}/>
        <SimpleBox title={'Failed Runs'} value={totalFailedRuns} colVal={'red'}/>
      </div>
      <div className="box2">
        <DataTable columns={columns} rows={dataRows}/>
      </div>
      {items[1]?.map((item: any) => (
        <div className="item" key={item.id}>
          <span className="item_run_num">{item.run_number}</span>
          <span className="item_id">{item.id}</span> 
          <span className="item_name">{item.name}</span> 
          <span className="item_display_title">{item.display_title}</span>
          <span className="item_conclusion">{item.conclusion}</span>
          <span className="item_createdAt">{item.created_at}</span>
          <span className="item_actor">{item.actor.login}</span>
          <span className="item_repo">{item.head_repository.name}</span>
        </div>
      ))}
    </div>
  )
  
}

export default Proof_ops