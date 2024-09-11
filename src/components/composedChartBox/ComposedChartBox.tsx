import "./composedChartBox.scss";
import React, { PureComponent } from 'react';
import {
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const data = [
  {
    name: 'Page A',
    uv: 590,
    pv: 800,
    amt: 1400,
  },
  {
    name: 'Page B',
    uv: 868,
    pv: 967,
    amt: 1506,
  },
  {
    name: 'Page C',
    uv: 1397,
    pv: 1098,
    amt: 989,
  },
  {
    name: 'Page D',
    uv: 1480,
    pv: 1200,
    amt: 1228,
  },
  {
    name: 'Page E',
    uv: 1520,
    pv: 1108,
    amt: 1100,
  },
  {
    name: 'Page F',
    uv: 1400,
    pv: 680,
    amt: 1700,
  },
];


const ComposedChartBox = () => {
  return (
    <div className="composedChartBox">
      <h1>Composed Chart</h1>
        <ResponsiveContainer width="100%" height={150}>
        <ComposedChart
          data={data}
        >
          <XAxis dataKey="name" label={{ value: 'Pages', position: 'insideBottomRight', offset: 0 }} scale="band" />
          <YAxis label={{ value: 'Index', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            contentStyle={{background:"transparent", border:"none"}}
            labelStyle={{display:"none"}}
            position={{x: -25, y: 60}}
          />
          <Legend />
          <Area type="monotone" dataKey="amt" fill= "aqua" stroke="aqua" />
          <Bar dataKey="pv" barSize={20} fill="gold" />
          <Line type="monotone" dataKey="uv" stroke="#ff7300" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ComposedChartBox