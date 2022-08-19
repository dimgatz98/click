import { IoMdSend } from "react-icons/io";
import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import { v4 as uuidv4 } from "uuid";
import { useNavigate } from "react-router-dom";
import {
    requestsListRoute,
    createChat,
    listChatsRoute,
    requestsDeleteRoute,
    sendRequestRoute,
} from "../utils/APIRoutes"
import axios from 'axios';

export default function FriendRequests({ changeContacts }) {
    const token = JSON.parse(localStorage.getItem(process.env.REACT_APP_STORAGE_TOKEN_KEY));
    const headers = {
        "Authorization": `Token ${token}`,
    };
    const if401Logout = (response) => {
        if (response.status === 401) {
            localStorage.clear();
            navigate("/login");
        }
    };

    const scrollRef = useRef();
    const navigate = useNavigate();
    const [requests, setRequests] = useState([]);
    const [user, setUser] = useState(undefined);
    const [friendUsername, setFriendUsername] = useState("");

    const addFriend = (event) => {
        event.preventDefault();
        if (friendUsername.length > 0) {
            handleFriendRequest(friendUsername);
            setFriendUsername("");
        }
    };

    const handleFriendRequest = async (username) => {
        axios.post(`${sendRequestRoute}`, { received_from: username }, { headers: headers })
            .catch((error) => {
                if401Logout(error.response);
            });
    };

    useEffect(() => {
        if (!localStorage.getItem(process.env.REACT_APP_STORAGE_TOKEN_KEY) ||
            !localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY)) {
            localStorage.clear();
            navigate('/login');
        } else {
            setUser(
                JSON.parse(localStorage.getItem(process.env.REACT_APP_STORAGE_USER_KEY))
            );
        }
    }, []);

    useEffect(async () => {
        const response = await axios.get(`${requestsListRoute}`, { headers: headers })
            .catch((error) => {
                if401Logout(error.response);
            });
        setRequests(response.data);
    }, []);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [requests]);

    const handleClick = async (r) => {
        if (user) {
            const newRequests = [];
            for (const request of requests) {
                if (request.id == r.id) {
                    continue;
                }
                newRequests.append(request);
            }

            const m = new Date();
            const dateString =
                m.getUTCFullYear() + "-" +
                ("0" + (m.getUTCMonth() + 1)).slice(-2) + "-" +
                ("0" + m.getUTCDate()).slice(-2) + "T" +
                ("0" + m.getUTCHours()).slice(-2) + ":" +
                ("0" + m.getUTCMinutes()).slice(-2) + ":" +
                ("0" + m.getUTCSeconds()).slice(-2);

            const data = {
                "participants": [user.id, r.sent_from_id],
                "room_name": uuidv4(),
                "last_message": dateString,
            }
            await axios.post(`${createChat}`, data, { headers: headers })
                .catch((error) => {
                    if401Logout(error.response);
                });

            axios.delete(`${requestsDeleteRoute}`, { headers: headers, data: { id: r.id } },)
                .catch((error) => {
                    if401Logout(error.response)
                });

            const response = await axios.get(`${listChatsRoute}${user.username}/`, { headers: headers })
                .catch((error) => {
                    if401Logout(error.response)
                });
            const chats = response.data.map((chat) => {
                for (const username of chat.participants) {
                    if (!(username === user.username)) {
                        return {
                            username: username, id: chat.id
                        };
                    }
                };
            });

            setRequests(newRequests);
            changeContacts(chats);
        }
    };

    return (
        <Container>
            <div>
                <h3>Friend Requests</h3>
                <div className="friend-requests">
                    <div ref={scrollRef} key={uuidv4()}>
                        <div className="requests">
                            <div className="content">
                                {(requests.length === 0) ?
                                    <p className="no-pending">No pending requests</p> :
                                    requests.map((request) => {
                                        return (
                                            <Button
                                                className={`${request.id}`}
                                                key={request.id}
                                                onClick={() => handleClick(request)}
                                            >
                                                {request.sent_from_username}
                                            </Button>
                                        )
                                    }
                                    )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="button-container">
            </div>
            <form className="input-container" onSubmit={(event) => addFriend(event)}>
                <input
                    type="text"
                    placeholder="Send a friend request"
                    onChange={(e) => setFriendUsername(e.target.value)}
                    value={friendUsername}
                />
                <button type="submit">
                    <IoMdSend />
                </button>
            </form>
        </Container >
    );
};

const Container = styled.div`
    display: grid;
    grid-template-rows: 10% 80% 10%;
    gap: 0.1rem;
    overflow: hidden;
    h3 {
        color: white;
        position: relative;
        top: 1rem;
        left: 0.77rem;
    }
    .no-pending {
        color: white;
        position: relative;
        top: 9rem;
        left: 0.57rem;
    }
`;

const Button = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.5rem;
  background-color: #9a86f3;
  border: none;
  cursor: pointer;
  position: relative;
  top: 1.5rem;
  svg {
    font-size: 1.3rem;
    color: #ebe7ff;
  }
`;