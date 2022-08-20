import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Checkmark } from 'react-checkmark'
import "react-toastify/dist/ReactToastify.css";
import { ToastContainer, toast } from "react-toastify";
import { IoMdSend } from "react-icons/io";
import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import { v4 as uuidv4 } from "uuid";
import { useNavigate } from "react-router-dom";
import XMARK from "../media/x-lg.svg";
import CHECK from "../media/check-lg.svg";
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
    const toastOptions = {
        position: "bottom-right",
        autoClose: 8000,
        pauseOnHover: true,
        draggable: true,
        theme: "dark",
    };
    const scrollRef = useRef();
    const navigate = useNavigate();
    const [requests, setRequests] = useState([]);
    const [user, setUser] = useState(undefined);
    const [friendUsername, setFriendUsername] = useState("");

    const if401Logout = (response) => {
        if (response.status === 401) {
            localStorage.clear();
            navigate("/login");
        }
    };
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
                if (!if401Logout(error.response)) {
                    toast.error(error.response?.data?.Error, toastOptions);
                }
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
        setRequests(response?.data);
    }, []);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [requests]);

    const acceptRequest = async (r) => {
        if (user) {
            const newRequests = [];
            for (const request of requests) {
                if (request?.id == r?.id) {
                    continue;
                }
                newRequests.push(request);
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
                "participants": [user.id, r?.sent_from_id],
                "room_name": uuidv4(),
                "last_message": dateString,
            }
            await axios.post(`${createChat}`, data, { headers: headers })
                .catch((error) => {
                    if (!if401Logout(error.response)) {
                        toast.error(error.response?.data?.Error, toastOptions);
                    }
                });

            axios.delete(`${requestsDeleteRoute}`, { headers: headers, data: { id: r?.id } },)
                .catch((error) => {
                    if (!if401Logout(error.response)) {
                        toast.error(error.response?.data?.Error, toastOptions);
                    }
                });

            const response = await axios.get(`${listChatsRoute}${user?.username}/`, { headers: headers })
                .catch((error) => {
                    if (!if401Logout(error.response)) {
                        toast.error(error.response?.data?.Error, toastOptions);
                    }
                });
            const chats = response.data.map((chat) => {
                for (const username of chat?.participants) {
                    if (!(username === user.username)) {
                        return {
                            username: username, id: chat?.id
                        };
                    }
                };
            });

            setRequests(newRequests);
            changeContacts(chats);
        }
    };

    const declineRequest = async (r) => {
        axios.delete(`${requestsDeleteRoute}`, { headers: headers, data: { id: r?.id } },)
            .catch((error) => {
                if (!if401Logout(error.response)) {
                    toast.error(error.response?.data?.Error, toastOptions);
                }
            });

        const newRequests = [];
        for (const request of requests) {
            if (request?.id == r?.id) {
                continue;
            }
            newRequests.push(request);
        }
        setRequests(newRequests);
    };

    return (
        <Container>
            <div>
                <h3>Friend Requests</h3>
                <div className="friend-requests">
                    <div ref={scrollRef} key={uuidv4()}>
                        <div className="requests">
                            <div className='content' key={uuidv4()}>
                                {(requests.length === 0) ?
                                    <p className="no-pending">No pending requests</p> :
                                    requests.map((request) => {
                                        return (
                                            <div className='request' key={uuidv4()}>
                                                <div className="friend-username"
                                                    key={request?.id}
                                                >
                                                    <p>{request?.sent_from_username}</p>
                                                </div>
                                                <div className='mark' value={request} onClick={() => acceptRequest(request)}>
                                                    <img src={CHECK} alt="check" />
                                                </div>
                                                <div className='mark'>
                                                    <img src={XMARK} alt="xmark" onClick={() => declineRequest(request)} />
                                                </div>
                                            </div>
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
            <ToastContainer />
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
        top: 7rem;
        left: -0.35rem;
    }
    .content {
        position: relative;
        left: 0.4rem;
        top: 1.5rem;
        display: flex;
        padding: 0.5rem;
        gap: 0.5rem;
        flex-direction: column;
    }
    .friend-username {
        display: flex;
        width: 10rem;
        background-color: #fc8403;
        align-items: center;
        justify-content: center;
        color: white;
        border-radius: 0.2rem;
    }
    .mark {
        position: relative;
        top: 0.1rem;
        background-color: white;
        display: flex;
        width: 2rem;
        height: 1.5rem;
        border-radius: 0.5rem;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }
    .request {
        height: 1.8rem;
        width: 9rem;
        display: flex;
        flex-direction: row;
        border-radius: 0.2rem;
        border: none;
        gap: 0.5rem;
    }
`;

const Button = styled.div`

`;