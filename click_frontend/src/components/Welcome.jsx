import React, { useState, useEffect } from "react";
import styled from "styled-components";
import Robot from "../media/robot.gif";
import Logout from "../components/Logout";

export default function Welcome({ }) {
  const [user, setUser] = useState("");
  const [username, setUsername] = useState("");
  useEffect(async () => {
    setUser(
      await JSON.parse(
        localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)
      )
    );
  }, []);

  useEffect(async () => {
    if (user) {
      setUsername(
        user.username
      );
    }
  }, [user]);

  return (
    <Container>
      <div className="welcome-logout">
        <Logout />
      </div>

      <div className="chat-messages">
        <img src={Robot} alt="" />
        <h1>
          Welcome, <span>{username}!</span>
        </h1>
        <h3>Please select a chat to Start messaging.</h3>
      </div>
    </Container>
  );
}

const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  flex-direction: column;
  img {
    height: 20rem;
  }
  span {
    color: #4e0eff;
  }
  .welcome-logout {
    position: relative;
    top: -3.5rem;
    right: -18.15rem;
  }
`;
