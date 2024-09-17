import MiniBox from "../miniBox/MiniBox";
import "./simpleBox.scss";

type Props = {
    title: String;
    value: number;
    colVal?: String
}

const SimpleBox = (props : Props) => {
  return (
    <div className="simpleBox">
        <MiniBox {...props} />
    </div>
  )
}

export default SimpleBox