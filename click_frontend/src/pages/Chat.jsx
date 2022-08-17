import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import { webSocketRoute } from "../utils/APIRoutes";
import ChatContainer from "../components/ChatContainer";
import Contacts from "../components/Contacts";
import Welcome from "../components/Welcome";
import { listChatsRoute } from "../utils/APIRoutes";
import axios from "axios";

export default function Chat() {
  const [contacts, setContacts] = useState([]);
  const [currentChat, setCurrentChat] = useState(undefined);
  const [currentUser, setCurrentUser] = useState(undefined);
  const socket = useRef(undefined);

  const navigate = useNavigate();

  const if401Logout = (response) => {
    if (response.status === 401) {
      localStorage.clear();
      navigate("/login");
    }
  };


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

      const response = await axios.get(`${listChatsRoute}${currentUser.username}/`, { headers: headers })
        .catch((error) => {
          if401Logout(error.response)
        });
      const chats = response.data.map((chat) => {
        for (const username of chat.participants) {
          if (!(username === currentUser.username)) {
            return {
              username: username, id: chat.id
            };
          }
        };
      });

      setContacts(chats);
    }
  }, [currentUser]);

  useEffect(async () => {
    if (currentChat) {
      const validID = currentChat.id.replaceAll('-', '');
      socket.current = new WebSocket(
        `${webSocketRoute}${validID}/`
      );
    }
  }, [currentChat]);

  const handleChatChange = (chat) => {
    setCurrentChat(chat);
  };

  return (
    <>
      <Container>
        <div className="container">
          <Contacts contacts={contacts} changeChat={handleChatChange} />
          {currentChat === undefined ? (
            <Welcome />
          ) : (
            <ChatContainer currentChat={currentChat} socket={socket} />
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
