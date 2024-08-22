import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Outlet } from "react-router-dom";
import Spinner from "../Spinner";
import axios from "axios"

const AdminRoute = () => {
    const [auth] = useAuth();
    const [ok, setOk] = useState(false);

    const authCheck = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_API}/api/v1/auth/admin-auth`,
          {
            headers: {
              Authorization: `Bearer ${auth.token}`
            }
          }
        );
        if (response.data.success === true) {
          setOk(true);
        } else {
          setOk(false);
        }
      } catch (error) {
        setOk(false)
      }
    };

    useEffect(()=>{
      if (auth?.token) authCheck();
    },[auth.token])

    return ok ? <Outlet /> : <Spinner timer={5} path="/" admin="admin"/>;
  }

export default AdminRoute