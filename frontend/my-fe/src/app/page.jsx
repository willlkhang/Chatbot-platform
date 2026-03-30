"use client"

import { useEffect, useState } from "react";

export default function Home(){

    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState("");

    const isChatting = messages.length > 0;

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (inputValue.trim() === "") return;

        const newMessages = [
            ...messages,
            { role: "user", content: inputValue }
        ];

        setMessages(newMessages);
        console.log("What's your problem from ICT283?:", inputValue);
        setInputValue("");

        setTimeout(() => {
            setMessages((prev) => [
                ...prev,
                { role: "ai", content: "I am ready to help you with your DSA problem. What are you stuck on?" }
            ]);
        }, 600);
    };

    const handleNewChat = () => {
        setMessages([]);
    };

    return (

        <div className="container">
            {/* History bar */}
            <aside className="sidebar">
                <button className="newChatBtn" onClick={handleNewChat}>
                    + New Chat
                </button>
                <div className="historyList">
                    <div className="historyItem">Previous Array Problem</div>
                    <div className="historyItem">Linked List Reverval</div>
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
                                    {msg.content}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* The pinned input area at the bottom */}
                <div className={`inputContainer ${isChatting ? "at-bottom" : "at-center"}`}>
                    <form className="form" onSubmit={handleSendMessage}>
                        <input type="text"
                                placeholder="Enter your questions here"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)} 
                        />
                        <button type="submit" disabled={!inputValue.trim()}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>


        // <div className="main-container">
        //     {!isChatting && (
        //         <div className="welcome-screen">
        //             <h1>Hi! I am a DSA bot</h1>

        //         </div>
        //     )}

        //     {isChatting && (
        //         <div className="chat-history">
        //             {/* render chat here */}
        //             <div className="message ai">
        //                 Willing to help you
        //             </div>
        //         </div>
        //     )}
        //     <div className={`input-area ${isChatting ? "at-bottom" : "at-center"}`}>
        //         <form onSubmit={handleSendMessage}>
        //             <input 
        //                 type="text" 
        //                 placeholder="Enter your problem here..." 
        //                 value={inputValue}
        //                 onChange={(e) => setInputValue(e.target.value)}
        //             />
        //             <button type="submit">Send</button>
        //         </form>
        //     </div>
        // </div>
    )
}
