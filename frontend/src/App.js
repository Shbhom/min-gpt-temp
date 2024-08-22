import { Route, Routes } from "react-router-dom";
import Pagenotfound from "./pages/Pagenotfound";
import Register from "./pages/auth/Register";
import Login1 from "./pages/auth/Login1";
import PrivateRoute from "./components/Routes/Private";
import Forgetpassword from "./pages/auth/Forgetpassword";
import Homepage from "./pages/Homepage";
import AdminRoute from "./components/Routes/AdminRoute";
import Displayusers from "./pages/admin/Displayusers";
import {gapi} from "gapi-script"
import React,{useEffect} from "react";


function App() {

  useEffect(() =>{
    function start() {
      gapi.client.init({
        clientId:"606228478540-0i4lkljtfp2qhrhmc3p3fcckg4l9crag.apps.googleusercontent.com",
        scope:""
        
      })
    }
    gapi.load("client:auth2",start);
   })
  
  return (
    <div className="w-[100vw] h-[100vw] overflow-x-hidden">

    <Routes>

      <Route path="*" element={<Pagenotfound />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login1 />} />
      <Route path="/forgetpassword" element={<Forgetpassword />} />


      <Route path="/" element={<PrivateRoute/>}>
            <Route path="" element={<Homepage/>}/>
      </Route>
        
      <Route path="/admin" element={<AdminRoute/>}>
           <Route path="" element={<Displayusers/>} />
      </Route>

    </Routes>
    </div>
  );
}

export default App;
