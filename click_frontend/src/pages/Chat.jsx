import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import { publicWebSocket } from "../utils/APIRoutes";
import ChatContainer from "../components/ChatContainer";
import Contacts from "../components/Contacts";
import Welcome from "../components/Welcome";
import { listChatsRoute } from "../utils/APIRoutes";
import axios from "axios";

export default function ChlistChatsRouteat() {
  const [contacts, setContacts] = useState([]);
  const [currentChat, setCurrentChat] = useState(undefined);
  const [currentUser, setCurrentUser] = useState(undefined);

  const chatSocket = new WebSocket(
    publicWebSocket
  );

  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem(process.env.REACT_APP_STORAGE_TOKEN_KEY) ||
      !localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)) {
      navigate("/login");
    } else {
      setCurrentUser(
        JSON.parse(
          localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)
        )
      );
    }
  }, []);
  useEffect(async () => {
    if (currentUser) {
      const token = JSON.parse(localStorage.getItem(process.env.REACT_APP_STORAGE_TOKEN_KEY));
      const headers = {
        'Authorization': `Token ${token}`,
      };

      const data = await axios.get(`${listChatsRoute}${currentUser.username}/`, { headers: headers });
      const chats = data.data.map((chat) => {
        for (const id of chat.participants) {
          if (!(id === currentUser.id)) {
            return id;
          }
        };
      })

      setContacts(chats);
    }
  }, [currentUser]);

  const handleChatChange = (chat) => {
    setCurrentChat(chat);
  };

  return (
    <>
      <Container>
        <div className="container">
          <Contacts contacts={contacts} changeChat={handleChatChange} currentUserName={currentUser} />
          {currentChat === undefined ? (
            <Welcome />
          ) : (
            <ChatContainer currentChat={currentChat} socket={chatSocket} />
          )}
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
    width: 70vw;
    background-color: #00000076;
    display: grid;
    grid-template-columns: 25% 75%;
    @media screen and (min-width: 720px) and (max-width: 1080px) {
      grid-template-columns: 35% 65%;
    }
  }
`;
