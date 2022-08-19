import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import ChatInput from "./ChatInput";
import Logout from "./Logout";
import { v4 as uuidv4 } from "uuid";
import { useNavigate } from "react-router-dom";
import {
  updateLastMessage,
  saveMessageRoute,
  retrieveChatMessagesRoute,
} from "../utils/APIRoutes"
import axios from 'axios';

export default function ChatContainer({ changeContacts, currentChat, socket }) {
  const token = JSON.parse(localStorage.getItem(process.env.REACT_APP_STORAGE_TOKEN_KEY));
  const headers = {
    'Authorization': `Token ${token}`,
  };
  const [messages, setMessages] = useState([]);
  const [arrivalMessage, setArrivalMessage] = useState(null);
  const [user, setUser] = useState(undefined);
  const navigate = useNavigate();
  const scrollRef = useRef();

  const if401Logout = (response) => {
    if (response.status === 401) {
      localStorage.clear();
      navigate("/login");
    }
  };

  useEffect(() => {
    arrivalMessage && setMessages((prev) => [...prev, arrivalMessage]);
  }, [arrivalMessage]);

  useEffect(async () => {
    setUser(
      JSON.parse(
        localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)
      )
    );
  }, []);

  useEffect(async () => {
    if (user && currentChat) {
      const response = await axios.get(`${retrieveChatMessagesRoute}${currentChat.id}/`, { headers: headers })
        .catch((error) => {
          if401Logout(error.response)
        });

      const existing_messages = response.data.map((dict) => {
        return dict.sent_from === user.username ? { fromSelf: true, message: dict.text } : { fromSelf: false, message: dict.text };
      });
      setMessages(existing_messages);
    }
  }, [currentChat, user]);

  useEffect(() => {
    if (!localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)) {
      localStorage.clear();
      navigate("/login");
    }
  }, [user]);

  const handleSendMsg = async (msg) => {
    const messageData = {
      "text": msg,
      "chat": currentChat.id,
      "sent_from": user.username,
    };

    // save new message in db
    await axios.post(`${saveMessageRoute}`, messageData, { headers: headers })
      .catch((error) => {
        if401Logout(error.response)
      });
    const m = new Date();
    const dateString =
      m.getUTCFullYear() + "-" +
      ("0" + (m.getUTCMonth() + 1)).slice(-2) + "-" +
      ("0" + m.getUTCDate()).slice(-2) + "T" +
      ("0" + m.getUTCHours()).slice(-2) + ":" +
      ("0" + m.getUTCMinutes()).slice(-2) + ":" +
      ("0" + m.getUTCSeconds()).slice(-2);

    // update last_message field in Chat model when new message is sent
    await axios.patch(`${updateLastMessage}${currentChat.id}/`, { "last_message": dateString }, { headers: headers })
      .catch((error) => {
        if401Logout(error.response)
      });

    socket.current.send(JSON.stringify({
      'message': msg,
      'username': user.username,
    }));
    console.log(socket.current);

    const msgs = [...messages];
    msgs.push({ fromSelf: true, message: msg });
    setMessages(msgs);
  };

  useEffect(() => {
    if (socket.current) {
      socket.current.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (!(data.username === user.username)) {
          setArrivalMessage({ fromSelf: false, message: data.message });
        }
      }
    }
  }, [socket.current]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Container>
      <div className="chat-header">
        <div className="user-details">
          <div className="chat-name">
            <h3>{(!currentChat === undefined) ? currentChat.username : ""}</h3>
          </div>
        </div>
        <Logout />
      </div>
      <div className="chat-messages">
        {messages.map((message) => {
          return (
            <div ref={scrollRef} key={uuidv4()}>
              <div
                className={`message ${message.fromSelf ? "sended" : "recieved"
                  }`}
              >
                <div className="content ">
                  <p>{message.message}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <ChatInput handleSendMsg={handleSendMsg} />
    </Container>
  );
}

const Container = styled.div`
  height: 85vh;
  width: 52.5vw;
  display: grid;
  grid-template-rows: 10% 80% 10%;
  gap: 0.1rem;
  overflow: hidden;
  @media screen and (min-width: 720px) and (max-width: 1080px) {
    grid-template-rows: 15% 70% 15%;
  }
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    .user-details {
      display: flex;
      align-items: center;
      gap: 1rem;
      .chat-name {
        h3 {
          color: white;
        }
      }
    }
  }
  .chat-messages {
    padding: 1rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow: auto;
    &::-webkit-scrollbar {
      width: 0.2rem;
      &-thumb {
        background-color: #ffffff39;
        width: 0.1rem;
        border-radius: 1rem;
      }
    }
    .message {
      display: flex;
      align-items: center;
      .content {
        max-width: 40%;
        overflow-wrap: break-word;
        padding: 1rem;
        font-size: 1.1rem;
        border-radius: 1rem;
        color: #d1d1d1;
        @media screen and (min-width: 720px) and (max-width: 1080px) {
          max-width: 70%;
        }
      }
    }
    .sended {
      justify-content: flex-end;
      .content {
        background-color: #4f04ff21;
      }
    }
    .recieved {
      justify-content: flex-start;
      .content {
        background-color: #9900ff20;
      }
    }
  }
`;
