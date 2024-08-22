import React, { useEffect, useContext, useState, createContext } from "react";
import {jwtDecode} from "jwt-decode"

const authContext = createContext();

const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    user: null,
    token:''
  });
  useEffect(() => {
    async function fetchData() {
      const data = JSON.parse(localStorage.getItem("auth"))
      if (data) {
        setAuth({...auth, user: data.user, token: data.token});
      }
    }
  
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <authContext.Provider value={[auth, setAuth]}>
      {children}
    </authContext.Provider>
  );
};

const useAuth = () => useContext(authContext);

export { useAuth, AuthProvider };
