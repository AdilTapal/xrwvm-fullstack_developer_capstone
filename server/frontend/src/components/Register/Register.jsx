import React, { useState } from 'react';

import "./Register.css";
import Header from '../Header/Header';

const Register = ({ onClose }) => {

  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [password, setPassword] = useState("");
  const [open, setOpen] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  let register_url = window.location.origin+"/djangoapp/register";

  const register = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Validate inputs
      if (!userName.trim() || !userEmail.trim() || !password.trim()) {
        setError("All fields are required");
        setLoading(false);
        return;
      }

      const res = await fetch(register_url, {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({
              "userName": userName,
              "email": userEmail,
              "password": password
          }),
      });
      
      const json = await res.json();
      
      if (res.ok && json.status === "User Registered") {
          sessionStorage.setItem('username', json.userName);
          setOpen(false);
      } else if (json.message) {
          setError(json.message);
      } else if (json.status) {
          setError(json.status);
      } else {
          setError("Registration failed. Please try again.");
      }
    } catch (err) {
      setError("Network error. Please check your connection and try again.");
      console.error("Registration error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    window.location.href = "/";
  };
  

  return (
    <div>
      <Header/>
    <div onClick={onClose}>
      <div
        onClick={(e) => {
          e.stopPropagation();
        }}
        className='modalContainer'
      >
          <form className="reg_panel" style={{}} onSubmit={register}>
              {error && <div className="error_message" style={{color: 'red', marginBottom: '10px'}}>{error}</div>}
              <div>
              <span className="input_field">Username </span>
              <input type="text" name="username" placeholder="Username" className="input_field" onChange={(e) => setUserName(e.target.value)} disabled={loading}/>
              </div>
              <div>
              <span className="input_field">Email </span>
              <input type="email" name="email" placeholder="Email" className="input_field" onChange={(e) => setUserEmail(e.target.value)} disabled={loading}/>
              </div>
              <div>
              <span className="input_field">Password </span>
              <input name="psw" type="password" placeholder="Password" className="input_field" onChange={(e) => setPassword(e.target.value)} disabled={loading}/>            
              </div>
              <div>
              <input className="action_button" type="submit" value={loading ? "Registering..." : "Register"} disabled={loading}/>
              <input className="action_button" type="button" value="Cancel" onClick={()=>setOpen(false)} disabled={loading}/>
              </div>
              <a className="loginlink" href="/login">Already have an account? Login</a>
          </form>
      </div>
    </div>
    </div>
  );
};

export default Register;
