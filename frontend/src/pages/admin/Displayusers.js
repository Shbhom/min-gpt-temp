import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import Adminmenu from '../../components/Layout/Adminmenu';
import Layout from '../../components/Layout/Layout';
import { useAuth } from '../../context/AuthContext';

const Displayusers = () => {
  const [auth] = useAuth()
  const [users, setUsers] = useState([]);

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API}/api/v1/auth/delete-user?id=${userId}`,{headers:{Authorization:`Bearer ${auth?.token}`}});
    
        if (response.data.success === true) {
          toast.success('User deleted successfully');
          window.location.reload()
        } else {
          toast.error(response.data.message)
        }
      } catch {
        toast.error("Something Went Wrong");
      }
    }
  };

  const handleUpdate = async (userId) => {
    if (window.confirm('Are you sure you want to switch this user\'s role?')) {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API}/api/v1/auth/update-user?id=${userId}`,{headers:{Authorization:`Bearer ${auth?.token}`}});
  
        if (response.data.success === true) {
          toast.success('User deleted successfully');
          window.location.reload()
        } else {
          toast.error(response.data.message)
        }
      } catch {
        toast.error("Something Went Wrong");
      }
    }
  };

  const fetchData = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API}/api/v1/auth/get-all-users`,{headers:{Authorization:`Bearer ${auth?.token}`}});
      setUsers(response.data.users);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, []);

  return (
    <Layout className="layout">
      <div className="row m-0 p-0">
        <div className="col-md-4 mb-2 p-0">
          <Adminmenu />
        </div>
        <div className="col-md-8 p-0 ps-md-2">
          <div className="card">
            <div className="container p-0">
              <table className="table container-fluid table-bordered m-3" style={{ width:"94%" }}>
                <thead>
                  <tr>
                    <th colSpan="2">
                      <h3 className="category-head">Manage Users</h3>
                    </th>
                  </tr>
                  <tr>
                    <th scope="col" className="col-md-5">Users</th>
                    <th scope="col" className="col-md-7">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users?.map((item) => (
                    <tr key={item._id}>
                      <td style={{
                    fontFamily: "'Poppins', sans-serif",
                    fontWeight: "1",
                  }} className="category-title">{item.name}</td>
                      <td>
                        <button
                          className="btn btn-primary "
                          onClick={() => handleUpdate(item._id)}
                        >
                          Switch user to {item.role === 0 ? "Premium" : "Basic"}
                        </button>
                        <button
                          className="btn btn-danger ms-3 "
                          onClick={() => handleDelete(item._id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Displayusers;
