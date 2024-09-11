import "./topBox.scss";
import { topUsers } from "../../data";
import { Link } from "react-router-dom";

const TopBox = () => {
  return (
    <div className="topBox">
        <h1>Top Users</h1>
        <div className="list">
            {topUsers.map(user => (
                <div className="listItem" key={user.id}>
                    <div className="user">
                        <img src={user.img} alt="" />
                        <div className="userTexts">
                            <span className="username">{user.username}</span>
                            <span className="email">{user.email}</span>
                        </div> 
                    </div>
                    <span className="logins">{user.logins}</span>
                </div>
            ))}
        </div>
        <div className="boxInfo">
            <Link to="/">View all</Link>
        </div>
    </div>
  )
}

export default TopBox