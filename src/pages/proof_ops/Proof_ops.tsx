import { useEffect, useState } from "react"
import "./Proof_ops.scss"
import { Octokit } from "@octokit/rest"
import axios from "axios"
import { getValueByDataKey } from "recharts/types/util/ChartUtils"

const Proof_ops = () => {
  const [items, setItems] = useState<any[]>([])
  const [owner] = useState("loonwerks")
  const [repo] = useState("AGREE-Toy-Example")
  const [d, setD] = useState([])

  // useEffect(() => {
  const fetchRepos = async () => {
    // const res = await fetch('https://api.github.com/users')
    const res = await fetch('https://api.github.com/repos/loonwerks/AGREE-Toy-Example/actions/runs', {method:'GET', 
    });
    const data = await res.json()
    const result = Object.keys(data).map((key) => data[key]);
    setItems(result)
    console.log("Hello:" + typeof(items))

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

    // fetchRepos()
     // console.log(items.length)
  // }, [])

  useEffect(() => {
    fetchRepos();
  }, []);


  return (
    <div className= "proof_ops">
      {items[1].map((item: any) => (
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
  // return (
  //   <div className= "proof_ops">Proof_ops</div>
  // )
}

export default Proof_ops