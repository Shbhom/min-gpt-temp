
import React from 'react'
import Header from './Header'
import Footer from './Footer'
import { Helmet } from 'react-helmet'
import { Toaster } from 'react-hot-toast'

export const Layout = ({ children }) => {
  return (
    <div className='app' style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header />
      <main className="main-content" style={{backgroundColor:'#e9ecef', flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <Toaster />
        {children}
      </main>
      <Footer />
    </div>
  );
}



export default Layout