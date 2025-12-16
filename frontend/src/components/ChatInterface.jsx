import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Avatar from './Avatar';

const ChatInterface = ({ sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('http://localhost:8000/static/avatars/default.png');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [socket, setSocket] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load history when sessionId changes
  useEffect(() => {
    setAvatarUrl('http://localhost:8000/static/avatars/default.png');
    const fetchHistory = async () => {
      if (!sessionId) return;
      setMessages([]); // Clear previous messages
      try {
        const response = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}/messages`);
        if (response.ok) {
          const data = await response.json();
          setMessages(data.map(m => ({ sender: m.sender, text: m.content })));
        }
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };
    fetchHistory();
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    
    ws.onopen = () => {
      console.log("Connected to WebSocket");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'avatar_update') {
        setAvatarUrl(data.avatar_url);
      }
    };

    ws.onclose = () => {
      console.log("Disconnected from WebSocket");
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: userMessage.text,
          session_id: sessionId
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setMessages(prev => [...prev, { sender: 'bot', text: data.reply_text }]);
        if (data.avatar_url) {
          setAvatarUrl(data.avatar_url);
        }
      } else if (data.status === 'generating_avatar') {
         setMessages(prev => [...prev, { sender: 'bot', text: data.reply_text }]);
         // WebSocket will handle the avatar update later
      }

    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, { sender: 'bot', text: "Error connecting to server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ flex: 1, padding: '20px', display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Avatar url={avatarUrl} />
      
      <div className="chat-window" style={{ flex: 1, overflowY: 'auto', border: '1px solid #ddd', padding: '10px', marginBottom: '10px', borderRadius: '5px' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '5px 0' }}>
            <div style={{ 
              background: msg.sender === 'user' ? '#007bff' : '#f1f1f1', 
              color: msg.sender === 'user' ? 'white' : 'black',
              padding: '8px 12px', 
              borderRadius: '15px',
              display: 'inline-block',
              maxWidth: '80%',
              textAlign: 'left'
            }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.text}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && <div style={{ textAlign: 'left' }}>Bot is typing...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex' }}>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          style={{ flex: 1, padding: '10px', borderRadius: '5px', border: '1px solid #ddd' }}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage} style={{ marginLeft: '10px', padding: '10px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
