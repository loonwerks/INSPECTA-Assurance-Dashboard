import "./miniBox.scss";

type Props = {
    title: String;
    value: number;
    colVal?: String
}

const MiniBox = (props : Props) => {
  return (
    <div className="miniBox">
        <h1 style={{color: props.colVal as string}}>{props.title}</h1>
        <div className="text">
            {props.value}
        </div>
    </div>
  )
}

export default MiniBox