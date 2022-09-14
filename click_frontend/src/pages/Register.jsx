import React, { useState, useEffect } from "react";
import axios from "axios";
import styled from "styled-components";
import { useNavigate, Link } from "react-router-dom";
import Logo from "../media/logo.svg";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { registerRoute } from "../utils/APIRoutes";

export default function Register() {
  const navigate = useNavigate();

  const toastOptions = {
    position: "bottom-right",
    autoClose: 8000,
    pauseOnHover: true,
    draggable: true,
    theme: "dark",
  };

  const if401Logout = (response) => {
    if (response.status === 401) {
      localStorage.clear();
    }
  };

  useEffect(() => {
    if (localStorage.getItem(process.env.REACT_APP_STORAGE_TOKEN_KEY)) {
      navigate("/chat");
    }
  }, []);

  const handleValidation = (data) => {
    if (data?.password !== data?.confirmPassword) {
      toast.error(
        "Password and confirm password should be same.",
        toastOptions
      );
      return false;
    } else if (data?.username.length < 3) {
      toast.error(
        "Username should be greater than 3 characters.",
        toastOptions
      );
      return false;
    } else if (data?.password.length < 8) {
      toast.error(
        "Password should be equal or greater than 8 characters.",
        toastOptions
      );
      return false;
    } else if (data?.email === "") {
      toast.error("Email is required.", toastOptions);
      return false;
    }

    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    let requestData = {};
    Array.from(event?.target?.children).forEach((elem) => {
      if (elem?.className === "input_data") {
        requestData[elem?.name] = elem?.value;
      }
    });

    if (handleValidation(requestData)) {
      const responseData = await axios.post(
        registerRoute,
        requestData
      )
        .catch((error) => {
          if (!if401Logout(error.response)) {
            toast.error(error.response?.data?.Error, toastOptions);
          }
        });

      if (responseData?.status === 200) {
        localStorage.setItem(
          process.env.REACT_APP_STORAGE_USER_KEY,
          JSON.stringify(responseData?.data?.user)
        );
        localStorage.setItem(
          process.env.REACT_APP_STORAGE_TOKEN_KEY,
          JSON.stringify(responseData?.data?.token)
        );
        navigate("/chat");
      } else {
        toast.error(responseData?.data?.Error, toastOptions);
      }
    }
  };

  return (
    <>
      <FormContainer>
        <form action="" onSubmit={(event) => handleSubmit(event)}>
          <div className="brand">
            <img src={Logo} alt="logo" />
            <h1>click</h1>
          </div>
          <input
            className="input_data"
            type="text"
            placeholder="Username"
            name="username"
          />
          <input
            className="input_data"
            type="text"
            placeholder="First Name"
            name="first_name"
          />
          <input
            className="input_data"
            type="text"
            placeholder="Last Name"
            name="last_name"
          />
          <input
            className="input_data"
            type="email"
            placeholder="Email"
            name="email"
          />
          <input
            className="input_data"
            type="password"
            placeholder="Password"
            name="password"
          />
          <input
            className="input_data"
            type="password"
            placeholder="Confirm Password"
            name="confirmPassword"
          />
          <button type="submit">Create User</button>
          <span>
            Already have an account ? <Link to="/login">Login.</Link>
          </span>
        </form>
      </FormContainer>
      <ToastContainer />
    </>
  );
}

const FormContainer = styled.div`
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
  align-items: center;
  background-color: #131324;
  .brand {
    display: flex;
    align-items: center;
    gap: 1rem;
    justify-content: center;
    img {
      height: 5rem;
    }
    h1 {
      color: white;
      text-transform: uppercase;
    }
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    background-color: #00000076;
    border-radius: 2rem;
    padding: 3rem 5rem;
  }
  input {
    height: 1rem;
    background-color: transparent;
    padding: 1rem;
    border: 0.1rem solid #4e0eff;
    border-radius: 0.4rem;
    color: white;
    width: 100%;
    font-size: 1rem;
    &:focus {
      border: 0.1rem solid #997af0;
      outline: none;
    }
  }
  button {
    background-color: #4e0eff;
    color: white;
    padding: 1rem 2rem;
    border: none;
    font-weight: bold;
    cursor: pointer;
    border-radius: 0.4rem;
    font-size: 1rem;
    text-transform: uppercase;
    &:hover {
      background-color: #4e0eff;
    }
  }
  span {
    color: white;
    text-transform: uppercase;
    a {
      color: #4e0eff;
      text-decoration: none;
      font-weight: bold;
    }
  }
`;
