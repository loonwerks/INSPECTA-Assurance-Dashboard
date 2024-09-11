import "./Home.scss";
import TopBox from "../../components/topBox/TopBox";
import ChartBox from "../../components/chartBox/ChartBox";
import AreaChartBox from "../../components/areaChartBox/AreaChartBox";
import BarChartBox from "../../components/barChartBox/BarChartBox";
import ComposedChartBox from "../../components/composedChartBox/ComposedChartBox";
import RadarChartBox from "../../components/radarChartBox/RadarChartBox";

const Home = () => {
  return (
    <div className= "home">
      <div className="box box1">
        <TopBox/>
      </div>
      <div className="box box2"><ChartBox /></div>
      <div className="box box3"><ChartBox /></div>
      <div className="box box4"><RadarChartBox /></div>
      <div className="box box5"><ChartBox /></div>
      <div className="box box6"><ChartBox /></div>
      <div className="box box7"><AreaChartBox /></div>
      <div className="box box8"><BarChartBox /></div>
      <div className="box box9"><ComposedChartBox /></div>
    </div>
  )
}

export default Home