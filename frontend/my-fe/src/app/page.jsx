"use client"

import { useEffect, useState } from "react";

export default function Home(){

    const [isChatting, setIsChatting] = useState(false);
    const [inputValue, setInputValue] = useState("");

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (inputValue.trim() !== "") {
            setIsChatting(true);
            
            console.log("What's your problem from ICT283?:", inputValue);
            setInputValue(""); 
        }
    };

    return (
        <div className="main-container">
            {!isChatting && (
                <div className="welcome-screen">
                    <h1>Hi! I am a DSA bot</h1>

                </div>
            )}

            {isChatting && (
                <div className="chat-history">
                    {/* render chat here */}
                    <div className="message ai">
                        Willing to help you
                    </div>
                </div>
            )}
            <div className={`input-area ${isChatting ? "at-bottom" : "at-center"}`}>
                <form onSubmit={handleSendMessage}>
                    <input 
                        type="text" 
                        placeholder="Enter your problem here..." 
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                    />
                    <button type="submit">Send</button>
                </form>
            </div>
        </div>
    )
}
