
import React, { useState, useEffect, useRef } from 'react';
import Markdown from 'markdown-to-jsx'; // Assuming you use a library for Markdown rendering
import { GoogleGenerativeAI } from "@google/generative-ai";

const apiKey = 'AIzaSyDYZzLdmRGK0Ev7az3u4csgs1jnb5tTZF8'; //api key
const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const ChatApp = () => {
  const [chatSession, setChatSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messageScrollRef = useRef(null);

  useEffect(() => {
    const initChat = async () => {
      // Initialize chat session (if needed)
      // This can be adapted based on your specific use case with the Google Generative AI
      setChatSession({ history: [] }); // Placeholder for chat session initialization
    };
    initChat();
  }, []);

  const scrollToBottom = () => {
    messageScrollRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    setIsLoading(true);
    try {
      // Send user message to the AI model
      const result = await model.generateContent(userMessage);
      const response = await result.response;
      const aiMessage = response.text();

      // Update messages with user and AI messages
      setMessages([...messages, { role: 'user', text: userMessage }]);
      setMessages([...messages, { role: 'gemini', text: aiMessage }]);
    } catch (error) {
      displayError(error.toString());
    } finally {
      setIsLoading(false);
      setUserMessage('');
      scrollToBottom();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      sendMessage();
    }
  };

  const displayError = (message) => {
    alert(message); // Replace with more sophisticated error handling
  };

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <span className="message-role">{message.role === 'user' ? 'User:' : 'Gemini:'}</span>
            <Markdown>{message.text}</Markdown>
          </div>
        ))}
        <div ref={messageScrollRef} />
      </div>
      <div className="input-container">
        <input
          type="text"
          placeholder="Enter your prompt"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatApp;
