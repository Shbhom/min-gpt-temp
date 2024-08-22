import React from "react";
import { useState } from "react";
import { useNavigate} from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import Layout from "../../components/Layout/Layout";

const Forgetpassword = () => {
  const [email, setEmail] = useState("");
  const [newpassword, setNewpassword] = useState("");
  const [answer, setAnswer] = useState("");
  const navigate = useNavigate();
  const [loadingSpinner,setIsLoadingSpinner] = useState(false)
  
  const handelSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        `${process.env.REACT_APP_API}/api/v1/auth/forget-password`,
        { email, newpassword, answer }
      );

      if (res.data.success === true) {
        toast.success("password has changed")
        navigate("/login")
      } else if (res.data.success === false) {
        toast.error(res.data.messege);
      }
    } catch (error) {
      toast.error("Something Went Wrong")
    } finally{
      setIsLoadingSpinner(false)
    }
  };

  return (
    <Layout title="forget password">
      <div className="registerationform">
        <h1>Reset Password</h1>
        <form onSubmit={handelSubmit}>
          <div className="mb-3">
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              className="form-control"
              id="exampleInputEmail3"
              aria-describedby="emailHelp"
              placeholder="enter your email"
              required
            />
          </div>
          <div className="mb-3">
            <input
              value={newpassword}
              onChange={(e) => setNewpassword(e.target.value)}
              type="password"
              className="form-control"
              id="exampleInputPasswordnew"
              placeholder="enter new password"
              required
            />
          </div>
          <div className="mb-3">
            <p>Who is your favourite person?</p>
            <input
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              type="text"
              className="form-control"
              id="exampleInputanswer"
              placeholder="Security Question"
              required
            />
          </div>

          <button disabled={loadingSpinner}  type="submit" className="d-flex align-items-center justify-content-center form-btn">
          {loadingSpinner ? (
                <div
                  className="Spinner"
                ></div>
              ) : null}
            Update
          </button>
        </form>
      </div>
    </Layout>
  );
};

export default Forgetpassword;
