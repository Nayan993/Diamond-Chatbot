

import React, { useState, useRef, useEffect } from "react";
import "./ChatScreen.css";

// IMPORT BACKGROUND , PROFILE IMAGES
import chatBg from "../assets/chatbg.png";
import botPfp from "../assets/botPfp.png";
import userPfp from "../assets/userPfp.avif";

function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Add greeting messages on initial render
  useEffect(() => {
    const currentHour = new Date().getHours();
    let greeting = "Hello";

    if (currentHour >= 5 && currentHour < 12) greeting = "Good Morning";
    else if (currentHour >= 12 && currentHour < 17) greeting = "Good Afternoon";
    else greeting = "Good Evening";

    // First message: greeting
    setMessages([{ sender: "bot", text: greeting }]);

    // Diamond Bot intro after 1.5 seconds
    const timer = setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Hello! I am Diamond Bot. How can I help you today?" },
      ]);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    const question = input;
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.answer || "Gemini returned no answer." },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error: Could not fetch answer." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="chat-container" style={{ backgroundImage: `url(${chatBg})` }}>
      <h1 className="chat-title">Diamond Bot</h1>
      <h2 className="chat-subtitle">Your personal chatbot</h2>
      <div className="messages-area">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message-row ${msg.sender === "bot" ? "left" : "right"}`}
          >
            {msg.sender === "bot" && <img src={botPfp} className="pfp" alt="bot" />}

            <div className={`message-bubble ${msg.sender === "bot" ? "bot" : "user"}`}>
              {msg.text}
            </div>

            {msg.sender === "user" && <img src={userPfp} className="pfp" alt="user" />}
          </div>
        ))}

        {loading && (
          <div className="message-row left">
            <img src={botPfp} className="pfp" alt="bot" />
            <div className="message-bubble bot">Typing...</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <textarea
          className="chat-input"
          placeholder="Type your message..."
          value={input}
          rows={1}
          onChange={(e) => {
            setInput(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = e.target.scrollHeight + "px";
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        />

        <button className="send-btn" onClick={sendMessage}>
          <svg
            width="26"
            height="26"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default ChatScreen;
