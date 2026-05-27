"use client" // this is client side

import { useEffect, useRef, useState } from "react";

//markdown for neat response text
import ReactMarkdown from 'react-markdown';

//for code block (mordern ai tool standard, user-friendly)
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

//logo
import { FaRegCopy } from "react-icons/fa6";
import { LuSendHorizontal } from "react-icons/lu";

//defines backend_sprintboot ports, rabbot port, and FAAA port
const API_GATEWAY = process.env.NEXT_PUBLIC_API_GATEWAY || "http://localhost:8060";
const RAGBOT_API = process.env.NEXT_PUBLIC_RAGBOT_API || "http://localhost:5000";
const CLASSIFIER_API = process.env.NEXT_PUBLIC_CLASSIFIER_API || "http://localhost:8011";

// this helper function helps format ugly string labels
function formatTopicLabel(label) {
    return label
        .split("_")
        .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
        .join(" ");
}
// function call to FAAA classifier to classify which topic does the user's
//prompt belong to.
async function classifyQuestion(text) {
    try {
        // call to topic classifier
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
        //guest mode, ephemeral per refresh
        //modern crypto to make a highly unique guest ID
        if (typeof crypto !== "undefined" && crypto.randomUUID) return `guest-${crypto.randomUUID()}`;
        return `guest-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    });

    //when a new message is send either from user or AI.
    // the coversation will scroll down to the bottom.
    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const authHeaders = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};

    //method refresh, and get access token, and set to the variable
    const refreshAuth = () => {
        const token = localStorage.getItem("accessToken");
        setAccessToken(token || null); // if there is not login which is guest mode, then null here
        setUserClaims(decodeJwtPayload(token)); //decode and set to user profile data
    };

    useEffect(() => {
        scrollToBottom(); //this one if for when either user or AI send message, it always scroll down to bottomx
    }, [messages, isResponseLoading]); //this is only triggered if messages array is changed
    //which is when user or AI is sending messagexs

    useEffect(() => {
        refreshAuth(); //check if user is login
        const handler = () => refreshAuth();
        window.addEventListener("accessTokenChanged", handler); //listen for login/logout
        window.addEventListener("storage", handler);//listens for token changes across tabs
        return () => {
            window.removeEventListener("accessTokenChanged", handler); //remove listner
            window.removeEventListener("storage", handler);// free memory
        };
    }, []); //empty array means runs only once on mount

    // async function to get user's hisotry for side bar
    const loadConversations = async (userId) => {
        try { //get get API to get conversations blocks history
            const res = await fetch(`${API_GATEWAY}/api/chat/user/${userId}/all`, {
                headers: { ...authHeaders }, //attaches the secure auth token
            });
            if (!res.ok) return; //return nothing is there is nothing, or database dies
            const data = await res.json(); //parse the list of chatx
            setConversations(Array.isArray(data) ? data : []); //if data is ok, set to converations array variable
        } catch {
            // ignore
            //if call failed, then failed
        }
    };

    useEffect(() => {
        // When logged in, load chat list (requires userId claim)
        if (!isLoggedIn) {// guest mode
            // clear old conversation list bar
            setConversations([]);
            setActiveChatId(null); //clear all activity ID
            return;  //return 0, obviously
        }
        const userId = userClaims?.userId; //when user logs in, get user ID
        if (typeof userId === "number") { // if a valid ID exists
            loadConversations(userId); // load user's old conversation history.
        }
    }, [isLoggedIn, userClaims?.userId]); //re-run if user changes

    const isChatting = messages.length > 0; // when user start prompting

    const handleSendMessage = (e) => {
        e.preventDefault(); //present browser doing all page refresh
        if (query.trim() === "") return; //check if input is just spaces, Yes? abort

        const textToSend = query; //saves the input string to a local variable

        const newMessages = [ // if new massages comming
            ...messages, //copy items from existing array to new now
            { role: "user", content: textToSend } // append this new "tuple" (sounds like python) to new array
        ];

        setMessages(newMessages); //update varivable array messages
        console.log("What's your problem from ICT283?:", query);
        setQuery(""); //clear query/prompt after sendding it to language model

        //call the main async function to get the AI's response
        chatWithRag(textToSend);

        // setTimeout(() => {
        //     setMessages((prev) => [
        //         ...prev,
        //         { role: "ai", content: "I am ready to help you with your DSA problem. What are you stuck on?" }
        //     ]);
        // }, 600);
    };

    const handleNewChat = () => { //when user create a new chat
        setMessages([]); //make new array variable
        setTopicPopup(null); //this is FAAA pop up function
        if (!isLoggedIn) { // in guest mode
            if (typeof crypto !== "undefined" && crypto.randomUUID) setGuestThreadId(`guest-${crypto.randomUUID()}`);
            else setGuestThreadId(`guest-${Date.now()}-${Math.random().toString(16).slice(2)}`);
        } else { //if login
            //sets active ID to null so the next message sent will create an entirely new db record
            setActiveChatId(null);
        }
    };

    //async function, trigger when user click on those past conversation on history bar
    const handleOpenConversation = async (chatId) => {
        if (!isLoggedIn) return; //guest mode does not have past comv
        const userId = userClaims?.userId; //get user id
        if (typeof userId !== "number") return; // safety check
        try { // call get API loads past conv from db
            const res = await fetch(`${API_GATEWAY}/api/chat/user/${chatId}`, {
                headers: { ...authHeaders },
            });
            if (!res.ok) return; //if failed, then nothing
            const chat = await res.json(); //assign returned data to chat variable
            //create new array variables to assign message item
            const msgs = Array.isArray(chat?.messages) ? chat.messages : [];
            setActiveChatId(chatId); // set which chatId is online
            setMessages( //set message variable, also distinguish if this message is from AI or user
                //the package is packed including user role, and message content
                msgs.map((m) => ({
                    role: m?.senderRole === "ai" ? "ai" : "user",
                    content: m?.content ?? "",
                }))
            );
        } catch {
            // ignore
        }
    };

    //function trigger by deleting
    const handleDeleteConversation = async (chatId) => {
        if (!isLoggedIn) return; // no login, then nothing
        const userId = userClaims?.userId; //get user id
        if (typeof userId !== "number") return; //safety check
        try { //call delete API
            await fetch(`${API_GATEWAY}/api/chat/${chatId}/user/${userId}`, {
                method: "DELETE",
                headers: { ...authHeaders },
            });
        } finally { // this block runs to update UI 
            // remove the deleted chat from history bar instantly
            setConversations((prev) => prev.filter((c) => c?.chatId !== chatId));
            if (activeChatId === chatId) { //if user is looking at the deleting chat
                setActiveChatId(null); //chat the active chatid to null which throw user back to the welcome screen
                setMessages([]); // empties the array messages
            }
        }
    };

    // make sure a logged-in user has a database ID before saving a message
    const ensureChatId = async () => {
        const userId = userClaims?.userId; // retrive get userId.
        if (!isLoggedIn || typeof userId !== "number") return null; //if guest, then nothing
        // if we already have a chat open, just return its ID
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

    //this function saves every single message text to the database
    const persistMessage = async (chatId, userId, role, content) => {
        //call POST APIs to load current chat
        await fetch(`${API_GATEWAY}/api/chat/${chatId}/user/${userId}/messages`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders,
            },
            body: JSON.stringify({ senderRole: role, content }),
        });
    };

    //the soul of this system
    const chatWithRag = async (messageText) => {
        if (!messageText) return; //safety check to stop if text is empty

        try {
            setLoading(true) //turns on the general loading state.
            setIsResponseLoading(true) // turns on the AI is typing, which are three bouncing dots

            // Persist user message (logged-in only)
            const userId = userClaims?.userId; // get user id
            let chatIdForThread = null; //this thread it is for ragbot, which is ID for rag short-term memory
            if (isLoggedIn && typeof userId === "number") {  //check user is authenticated
                // call to function to get an exisitng ID or create a new one
                chatIdForThread = await ensureChatId();
                if (chatIdForThread) { //when threadid is secured
                    //save the user's text to the database immediately
                    await persistMessage(chatIdForThread, userId, "user", messageText);
                }
            }

            //runs two network requests at the exact same time to save waiting time.
            const [classifyResult, respond] = await Promise.all([
                // this is for asking classider what DSA is this
                classifyQuestion(messageText),
                // this is the second request sending prompt to RAGBOT server
                fetch(`${RAGBOT_API}/api/response`, { 
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        query: messageText,
                        thread_id: isLoggedIn && chatIdForThread ? String(chatIdForThread) : guestThreadId,
                    }),
                }),
            ]);
            // check if the prompt is classified into a specific topic
            // or it's a "other" label
            if (classifyResult?.label && classifyResult.label !== "OTHER") {
                //safety extracts the array of URL resources
                const resources = Array.isArray(classifyResult.resource)
                    ? classifyResult.resource.filter(Boolean) //filter out any null array
                    : []; // nothing is nothing
                if (resources.length > 0) {// if we have at least one valid link to show
                    setTopicPopup({ //open UI toast notification
                        topic: classifyResult.label, //pass the topic name
                        resources, //pass the array of URLs
                    });
                } else {
                    setTopicPopup(null); // if no resources, ensure the toast is closed, which is not toast at all
                }
            } else {
                setTopicPopup(null); // if the label as "OTHER", close the toast
            }

            if (!respond.ok) { //no response, raise exception?
                throw new Error(`API Error: ${respond.status}`);
            }
            const res = await respond.json();
            setMessages((prev) => [ //update message array
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

    //make response from AI more beautiful
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
