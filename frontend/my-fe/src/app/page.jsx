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

const API_GATEWAY = process.env.NEXT_PUBLIC_API_GATEWAY || "http://localhost:8060";
const RAGBOT_API = process.env.NEXT_PUBLIC_RAGBOT_API || "http://localhost:5000";
const CLASSIFIER_API = process.env.NEXT_PUBLIC_CLASSIFIER_API || "http://localhost:8011";

function formatTopicLabel(label) {
    return label
        .split("_")
        .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
        .join(" ");
}

async function classifyQuestion(text) {
    try {
        const res = await fetch(`${CLASSIFIER_API}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

function safeJsonParse(s) {
    try { return JSON.parse(s); } catch { return null; }
}

function decodeJwtPayload(token) {
    if (!token) return null;
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
    const json = atob(padded);
    return safeJsonParse(json);
}

export default function Home(){

    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [isResponseLoading, setIsResponseLoading] = useState(false);
    const [copiedCode, setCopiedCode] = useState(null);
    const [topicPopup, setTopicPopup] = useState(null);

    const messageEndRef = useRef(null);

    const [accessToken, setAccessToken] = useState(null);
    const [userClaims, setUserClaims] = useState(null);
    const isLoggedIn = !!accessToken;

    const [conversations, setConversations] = useState([]); // logged-in only
    const [activeChatId, setActiveChatId] = useState(null); // logged-in: numeric chatId, guest: null
    const [guestThreadId, setGuestThreadId] = useState(() => {
        // guest mode: ephemeral per refresh
        if (typeof crypto !== "undefined" && crypto.randomUUID) return `guest-${crypto.randomUUID()}`;
        return `guest-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    });

    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const authHeaders = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};

    const refreshAuth = () => {
        const token = localStorage.getItem("accessToken");
        setAccessToken(token || null);
        setUserClaims(decodeJwtPayload(token));
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isResponseLoading]);

    useEffect(() => {
        refreshAuth();
        const handler = () => refreshAuth();
        window.addEventListener("accessTokenChanged", handler);
        window.addEventListener("storage", handler);
        return () => {
            window.removeEventListener("accessTokenChanged", handler);
            window.removeEventListener("storage", handler);
        };
    }, []);

    const loadConversations = async (userId) => {
        try {
            const res = await fetch(`${API_GATEWAY}/api/chat/user/${userId}/all`, {
                headers: { ...authHeaders },
            });
            if (!res.ok) return;
            const data = await res.json();
            setConversations(Array.isArray(data) ? data : []);
        } catch {
            // ignore
        }
    };

    useEffect(() => {
        // When logged in, load chat list (requires userId claim)
        if (!isLoggedIn) {
            setConversations([]);
            setActiveChatId(null);
            return;
        }
        const userId = userClaims?.userId;
        if (typeof userId === "number") {
            loadConversations(userId);
        }
    }, [isLoggedIn, userClaims?.userId]);

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
        setTopicPopup(null);
        if (!isLoggedIn) {
            if (typeof crypto !== "undefined" && crypto.randomUUID) setGuestThreadId(`guest-${crypto.randomUUID()}`);
            else setGuestThreadId(`guest-${Date.now()}-${Math.random().toString(16).slice(2)}`);
        } else {
            setActiveChatId(null);
        }
    };

    const handleOpenConversation = async (chatId) => {
        if (!isLoggedIn) return;
        const userId = userClaims?.userId;
        if (typeof userId !== "number") return;
        try {
            const res = await fetch(`${API_GATEWAY}/api/chat/user/${chatId}`, {
                headers: { ...authHeaders },
            });
            if (!res.ok) return;
            const chat = await res.json();
            const msgs = Array.isArray(chat?.messages) ? chat.messages : [];
            setActiveChatId(chatId);
            setMessages(
                msgs.map((m) => ({
                    role: m?.senderRole === "ai" ? "ai" : "user",
                    content: m?.content ?? "",
                }))
            );
        } catch {
            // ignore
        }
    };

    const handleDeleteConversation = async (chatId) => {
        if (!isLoggedIn) return;
        const userId = userClaims?.userId;
        if (typeof userId !== "number") return;
        try {
            await fetch(`${API_GATEWAY}/api/chat/${chatId}/user/${userId}`, {
                method: "DELETE",
                headers: { ...authHeaders },
            });
        } finally {
            setConversations((prev) => prev.filter((c) => c?.chatId !== chatId));
            if (activeChatId === chatId) {
                setActiveChatId(null);
                setMessages([]);
            }
        }
    };

    const ensureChatId = async () => {
        const userId = userClaims?.userId;
        if (!isLoggedIn || typeof userId !== "number") return null;
        if (typeof activeChatId === "number") return activeChatId;

        // create a new chat in chat-service
        const chatRes = await fetch(`${API_GATEWAY}/api/chat/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders,
            },
            body: JSON.stringify({ userId, messages: [] }),
        });
        if (!chatRes.ok) return null;
        const chat = await chatRes.json();
        const newChatId = chat?.chatId;
        if (typeof newChatId === "number") {
            setActiveChatId(newChatId);
            setConversations((prev) => [chat, ...prev]);
            return newChatId;
        }
        return null;
    };

    const persistMessage = async (chatId, userId, role, content) => {
        await fetch(`${API_GATEWAY}/api/chat/${chatId}/user/${userId}/messages`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders,
            },
            body: JSON.stringify({ senderRole: role, content }),
        });
    };

    const chatWithRag = async (messageText) => {
        if (!messageText) return;

        try {
            setLoading(true)
            setIsResponseLoading(true)

            // Persist user message (logged-in only)
            const userId = userClaims?.userId;
            let chatIdForThread = null;
            if (isLoggedIn && typeof userId === "number") {
                chatIdForThread = await ensureChatId();
                if (chatIdForThread) {
                    await persistMessage(chatIdForThread, userId, "user", messageText);
                }
            }

            const [classifyResult, respond] = await Promise.all([
                classifyQuestion(messageText),
                fetch(`${RAGBOT_API}/api/response`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        query: messageText,
                        thread_id: isLoggedIn && chatIdForThread ? String(chatIdForThread) : guestThreadId,
                    }),
                }),
            ]);

            if (classifyResult?.label && classifyResult.label !== "OTHER") {
                const resources = Array.isArray(classifyResult.resource)
                    ? classifyResult.resource.filter(Boolean)
                    : [];
                if (resources.length > 0) {
                    setTopicPopup({
                        topic: classifyResult.label,
                        resources,
                    });
                } else {
                    setTopicPopup(null);
                }
            } else {
                setTopicPopup(null);
            }

            if (!respond.ok) {
                throw new Error(`API Error: ${respond.status}`);
            }
            const res = await respond.json();
            setMessages((prev) => [
                ...prev,
                { role: "ai", content: res.ai }
            ]);

            // Persist ai response (logged-in only)
            if (isLoggedIn && typeof userId === "number" && chatIdForThread) {
                await persistMessage(chatIdForThread, userId, "ai", res.ai);
            }
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
                    {!isLoggedIn ? (
                        <div className="historyItem">Guest mode (not saved)</div>
                    ) : (
                        conversations.map((c) => (
                            <div
                                key={c.chatId}
                                className={`historyItem ${activeChatId === c.chatId ? "active" : ""}`}
                            >
                                <button
                                    className="historyOpenBtn"
                                    onClick={() => handleOpenConversation(c.chatId)}
                                >
                                    Chat #{c.chatId}
                                </button>
                                <button
                                    className="historyDeleteBtn"
                                    onClick={() => handleDeleteConversation(c.chatId)}
                                    title="Delete"
                                >
                                    ×
                                </button>
                            </div>
                        ))
                    )}
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

            {topicPopup && (
                <div
                    className="topicToast"
                    role="dialog"
                    aria-labelledby="topic-popup-title"
                    aria-live="polite"
                >
                    <button
                        type="button"
                        className="topicToastClose"
                        onClick={() => setTopicPopup(null)}
                        aria-label="Close"
                    >
                        ×
                    </button>

                    <div className="topicToastHeader">
                        <span className="topicToastBadge" aria-hidden="true">
                            {topicPopup.topic.slice(0, 2)}
                        </span>
                        <div className="topicToastTitleBlock">
                            <h2 id="topic-popup-title">Related study materials</h2>
                            <span className="topicLabel">{formatTopicLabel(topicPopup.topic)}</span>
                        </div>
                    </div>

                    <div className="topicToastBody">
                        <p>We found resources that may help with your question:</p>
                        <ul>
                            {topicPopup.resources.map((url, i) => (
                                <li key={i}>
                                    <a href={url} target="_blank" rel="noopener noreferrer">
                                        {url}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="topicToastActions">
                        <button
                            type="button"
                            className="topicToastBtn topicToastBtn--secondary"
                            onClick={() => setTopicPopup(null)}
                        >
                            Dismiss
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
