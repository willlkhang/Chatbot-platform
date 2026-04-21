"use client"

import { useEffect, useState } from "react";

import ReactMarkdown from 'react-markdown';

export default function Home(){

    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [isResponseLoading, setIsResponseLoading] = useState(false);

    const isChatting = messages.length > 0;

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (query.trim() === "") return;

        const textToSend = query;

        const newMessages = [
            ...messages,
            { role: "user", content: textToSend }
        ];

        setMessages(newMessages);
        console.log("What's your problem from ICT283?:", query);
        setQuery("");

        chatWithRag(textToSend);

        // setTimeout(() => {
        //     setMessages((prev) => [
        //         ...prev,
        //         { role: "ai", content: "I am ready to help you with your DSA problem. What are you stuck on?" }
        //     ]);
        // }, 600);
    };

    const handleNewChat = () => {
        setMessages([]);
    };

    const chatWithRag = async (messageText) => {
        if (!messageText) return;

        try {
            setLoading(true)
            setIsResponseLoading(true)
            const respond = await fetch(
                "http://localhost:5000/api/response",
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: messageText })
            });

            if (!respond.ok) {
                throw new Error(`API Error: ${respond.status}`);
            }
            const res = await respond.json();
            setMessages((prev) => [
                ...prev,
                { role: "ai", content: res.ai }
            ]);
        } catch (error) {
            console.log("Fetch Failed ", error);
        } finally {
            setLoading(false);
            setIsResponseLoading(false);
        }
    };

    return (

        <div className="container">
            {/* History bar */}
            <aside className="sidebar">
                <button className="newChatBtn" onClick={handleNewChat}>
                    + New Chat
                </button>
                <div className="historyList">
                    <div className="historyItem">Test 1</div>
                    <div className="historyItem">Test 2</div>
                </div>
            </aside>

            {/* Main Chat Interface */}
            <div className="mainChat">
                {!isChatting ? (
                    <div className="welcomeScreen">
                        <h1>Hi! I am a DSA bot</h1>
                        <p>Tell me your DSA problem</p>
                    </div>
                ) : (
                    <div className="messageArea">
                        {messages.map((msg, index) => (
                            <div
                                key={index} 
                                className={`messageWrapper ${msg.role}`}
                            >
                                <div className={`message ${msg.role}`}>
                                    {msg.role === 'ai' ? (
                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                    ) : (
                                        msg.content
                                    )}
                                </div>
                            </div>
                        ))}

                        {isResponseLoading && (
                            <div className="messageWrapper ai">
                                <div className="message ai typingIndicator">
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* The pinned input area at the bottom */}
                <div className={`inputContainer ${isChatting ? "at-bottom" : "at-center"}`}>
                    <form className="form" onSubmit={handleSendMessage}>
                        <input type="text"
                                placeholder="Enter your questions here"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)} 
                        />
                        <button type="submit" disabled={!query.trim()}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}
