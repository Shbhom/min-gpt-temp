import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Outlet } from "react-router-dom";
import Spinner from "../Spinner";
import toast from "react-hot-toast";

export default function PrivateRoute() {
  const [auth] = useAuth();
  const [ok, setOk] = useState(false);

  useEffect(() => {
    
    const authCheck = async () => {
      try {
        if (localStorage.getItem('auth')) {
          setOk(true);
        } else {
          setOk(false);
        }
      } catch (error) {
        toast.error("Un Authorized access")
      }
    };

    if (auth?.token) authCheck();

  }, [auth?.token]);

  return ok ? <Outlet /> : <Spinner />;
}
