import React from 'react'
import { NavLink } from 'react-router-dom'

const Adminmenu = () => {
  return (
    <div className='card m-auto p-3 container-fluid '><div className='list-group text-center'>
       <h4 className='category-head'style={{ fontFamily: "'Poppins', sans-serif", fontWeight:"1" }}>Admin Panel</h4>
       <NavLink to="/admin" className="list-group-item list-group-item-action rounded">Manage Users</NavLink>
    </div>
    </div>
  )
}

export default Adminmenu