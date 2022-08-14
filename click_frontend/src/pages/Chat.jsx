import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import { publicWebSocket } from "../utils/APIRoutes";
import ChatContainer from "../components/ChatContainer";

export default function Chat() {
  const chatSocket = new WebSocket(
    publicWebSocket
  );

  const navigate = useNavigate();

  useEffect(async () => {
    if (!localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)) {
      navigate("/login");
    }
  }, []);

  return (
    <>
      <Container>
        <div className="container">
          <ChatContainer socket={chatSocket} />
        </div>
      </Container>
    </>
  );
}

const Container = styled.div`
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
  align-items: center;
  background-color: #131324;
  .container {
    height: 85vh;
    width: 85vw;
    background-color: #00000076;
    display: grid;
    grid-template-columns: 25% 75%;
    @media screen and (min-width: 720px) and (max-width: 1080px) {
      grid-template-columns: 35% 65%;
    }
  }
`;
