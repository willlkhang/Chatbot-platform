"use client"

import { useEffect, useRef, useState } from "react";

//markdown for neat response text
import ReactMarkdown from 'react-markdown';

//for code block (mordern ai tool standard, user-friendly)
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

//logo
import { FaRegCopy } from "react-icons/fa6";
import { LuSendHorizontal } from "react-icons/lu";

export default function Home(){

    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [isResponseLoading, setIsResponseLoading] = useState(false);
    const [copiedCode, setCopiedCode] = useState(null);

    const messageEndRef = useRef(null);

    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isResponseLoading]);

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

    const handleCopy = (text) => {
        navigator.clipboard.writeText(text);
        setCopiedCode(text);
        setTimeout(() => setCopiedCode(null, 2000));
    }

    const MarkdownComponents = {

        pre({ children }){
            return <div className="preWrapper">{children}</div>
        },
        code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const codeText = String(children).replace(/\n$/, '');
            
            if (!inline && match) {
                return (
                    <div className="customCodeBlock">
                        <div className="codeHeader">
                            <span className="codeLanguage">{match[1]}</span>
                            <button 
                                className="copyBtn" 
                                onClick={() => handleCopy(codeText)}
                            >
                                <FaRegCopy />
                                {copiedCode === codeText ? "Copied!" : "Copy"}
                            </button>
                        </div>
                        <SyntaxHighlighter
                            {...props}
                            style={oneLight}
                            language={match[1]}
                            PreTag="div"
                            customStyle={{ margin: 0, padding: '16px', backgroundColor: '#f9f9f9' }}
                        >
                            {codeText}
                        </SyntaxHighlighter>
                    </div>
                );
            }
            
            return (
                <code className="inlineCode" {...props}>
                    {children}
                </code>
            );
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
                                        <ReactMarkdown components={MarkdownComponents}>
                                            {msg.content}
                                        </ReactMarkdown>
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

                        <div ref={messageEndRef}></div>
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
                            <LuSendHorizontal />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}
