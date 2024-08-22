import React from "react";
import Layout from "../../components/Layout/Layout";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

import { GoogleLogin } from "react-google-login";

const Login1 = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [auth, setAuth] = useAuth();
  const [loadingSpinner, setLoadingSpinner] = useState(false);
  const navigate = useNavigate();

  const handleFailure = async (response) => {
    toast.error("Something Went Wrong");
  };
  // ....................................................................................................
  const handleGoogleLogin = async (response) => {
    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API}/api/v1/auth/google`,
        { token: response.tokenId }
      );

      if (res.data.success === "true") {
        const decoded_token = jwtDecode(res.data.token);

        setAuth({ ...auth, user: decoded_token, token: res.data.token });

        localStorage.setItem("auth", res.data.token);

        navigate("/");
      } else {
        toast.error(res.data.messege, {
          duration: 2000,
        });
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };
  // ....................................................................................................
  const handelSubmit = async (e) => {
    e.preventDefault();
    setLoadingSpinner(true);
    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API}/api/v1/auth/login`,
        { email, password }
      );

      if (res.data.success === true) {
        setAuth({ ...auth, user: res.data.user, token: res.data.token });
        localStorage.setItem(
          "auth",
          JSON.stringify({ user: res.data.user, token: res.data.token })
        );
        toast.success("login Successfull");
        navigate("/");
      } else if (res.data.success === false) {
        toast.error(res.data.message);
      }
    } catch (error) {
      toast.error("Something Went Wrong");
    } finally {
      setLoadingSpinner(false);
    }
  };

  return (
    <Layout title="registration form">
      <div className="registerationform">
        <h1>Login page</h1>
        <GoogleLogin
          clientId="606228478540-0i4lkljtfp2qhrhmc3p3fcckg4l9crag.apps.googleusercontent.com"
          buttonText="Continue with Google"
          onSuccess={handleGoogleLogin}
          onFailure={handleFailure}
          cookiePolicy={"single_host_origin"}
          isSignedIn={true}
          className="google-login-button"
          autoLoad={false}
        />
        <p style={{ textAlign: "center", paddingBottom: 0, marginBottom: 10 }}>
          or
        </p>
        <form onSubmit={handelSubmit}>
          <div className="mb-3">
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              className="form-control"
              id="exampleInputEmail1"
              aria-describedby="emailHelp"
              placeholder="enter your email"
              required
            />
          </div>
          <div className="mb-3">
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              className="form-control"
              id="exampleInputPassword1"
              placeholder="enter your password"
              required
            />
          </div>

          <Link className="navlink" to="/forgetpassword">
            Forgot Password?
          </Link>

          <button disabled={loadingSpinner}  type="submit" className="d-flex align-items-center justify-content-center form-btn">
          {loadingSpinner ? (
                <div
                  className="Spinner"
                ></div>
              ) : null}
            Login
          </button>
        </form>
      </div>
    </Layout>
  );
};

export default Login1;
