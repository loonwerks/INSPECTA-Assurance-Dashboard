import Home from "./pages/home/Home"
import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
} from "react-router-dom";
import Proof_ops from "./pages/proof_ops/Proof_ops";
import Users from "./pages/users/Users";
import Navbar from "./components/navbar/Navbar";
import Menu from "./components/menu/Menu";
import Login from "./pages/login/Login";
import "./styles/global.scss"
import Footer from "./components/footer/Footer";
import Build_ops from "./pages/build_ops/Build_ops";
import Test_ops from "./pages/test_ops/Test_ops";
import Cert_ops from "./pages/cert_ops/Cert_ops";
import Review_ops from "./pages/review_ops/Review_ops";
import Doc_ops from "./pages/doc_ops/Doc_ops";
import Tool_ops from "./pages/tool_ops/Tool_ops";


function App() {

  const Layout = ()=> {
    return (
      <div className="main">
      <Navbar/>
      <div className="container">
        <div className="menuContainer">
          <Menu/>
        </div>
        <div className="contentContainer">
          <Outlet/>
        </div>
      </div>
      <Footer/>
      </div>
    )
  }

  const router = createBrowserRouter([
    {
      path: "/",
      element: <Layout/>,
      children: [
        {
          path: "/",
          element: <Home/>
        },
        {
          path: "/users",
          element: <Users/>
        },
        {
          path: "/proof_ops",
          element: <Proof_ops/>
        },
        {
          path: "/build_ops",
          element: <Build_ops/>
        },
        {
          path: "/test_ops",
          element: <Test_ops/>
        },
        {
          path: "/cert_ops",
          element: <Cert_ops/>
        },
        {
          path: "/review_ops",
          element: <Review_ops/>
        },
        {
          path: "/doc_ops",
          element: <Doc_ops/>
        },
        {
          path: "/tool_ops",
          element: <Tool_ops/>
        }
      ]
    },
    {
      path: "/login",
      element: <Login/>
    }
  ]);

  return (
    <RouterProvider router={router} />
  )
}

export default App
