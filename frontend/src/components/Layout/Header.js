import React,{useRef} from "react";
import { NavLink, Link, useNavigate } from "react-router-dom";
import { TfiShoppingCartFull } from "react-icons/tfi";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";
import { GoogleLogout } from "react-google-login";
export const Header = () => {
  const [auth, setAuth] = useAuth();
  const logoutButtonRef = useRef(null);

  const navigate = useNavigate();

  const handleLogout = () => {
    setAuth({
      ...auth,
      user: null,
      token: "",
    });
    localStorage.removeItem("auth");
    navigate("/login");
    toast.success("logout successfully");
  };

  const triggerLogout = () => {
    if (logoutButtonRef.current) {
      logoutButtonRef.current.querySelector('button').click();
    }
  };

  return (
    <>
      <nav className="navbar navbar-expand bg-body-tertiary">
        <div className="container-fluid">
          <div
            style={{ display: "flex", justifyContent: "center", width: "100%" }}
          >
            <img
              style={{ maxWidth: "50%", height: "auto" }}
              src="https://texmin.in/wp-content/uploads/2019/12/Merge-NM-ICPS-Logo-2048x293.png"
              alt="Logo 3"
            />
          </div>
          <div
            style={{ display: "flex", justifyContent: "center", width: "100%" }}
          >
            <img
              style={{ maxWidth: "170px", height: "auto" }}
              src="https://texmin.in/wp-content/uploads/2021/05/Texmin-Foundation.png"
              alt="Logo 3"
            />
          </div>
          <div
            style={{ display: "flex", justifyContent: "center", width: "100%" }}
          >
            <img
              style={{ maxWidth: "50%", height: "auto" }}
              src="https://d2lk14jtvqry1q.cloudfront.net/media/small_Department_of_Management_Studies_IIT_Dhanbad_ae040bdd59_00524faa81_587e594e98_3dd33e6e60_8561d0e94d.png"
              alt="Logo 3"
            />
          </div>
          <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
            {!auth.user ? (
              <>
                <li className="nav-item">
                  <NavLink
                    to="/register"
                    className="nav-link "
                    aria-current="page"
                  >
                    Register
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink
                    to="/login"
                    className="nav-link me-md-5 "
                    aria-current="page"
                  >
                    Login
                  </NavLink>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <NavLink to="/" className="nav-link " aria-current="page">
                    Home
                  </NavLink>
                </li>
                <li className="dropdown nav-item">
                  <NavLink
                    className="nav-link dropdown-toggle me-md-5"
                    id="navbarDropdownMenuLink"
                    role="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    {auth?.user?.name.split(" ")[0]}
                  </NavLink>

                  <ul className="dropdown-menu ul-dashboard" style={{maxWidth:"10px"}}>
                    <li>
                      <div style={{ cursor: 'pointer'}} className="nav-optional" onClick={triggerLogout}>Log Out</div>
                      <div ref={logoutButtonRef} >
                        <GoogleLogout
                          id="googleLogoutButton"
                          clientId="606228478540-0i4lkljtfp2qhrhmc3p3fcckg4l9crag.apps.googleusercontent.com"
                          buttonText={"Logout"}
                          onLogoutSuccess={handleLogout}
                          className="googlelogout d-none"
                        />
                      </div>
                    </li>
                  </ul>
                </li>
              </>
            )}

            <li className="nav-item"> </li>
          </ul>
        </div>
      </nav>
    </>
  );
};

export default Header;
