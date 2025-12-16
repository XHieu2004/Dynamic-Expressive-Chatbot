import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
        // If no session selected and sessions exist, select the first one
        if (!currentSessionId && data.length > 0) {
          setCurrentSessionId(data[0].id);
        } else if (data.length === 0) {
          // If no sessions, create one
          createNewSession();
        }
      }
    } catch (error) {
      console.error("Error fetching sessions:", error);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: "New Chat" })
      });
      if (response.ok) {
        const newSession = await response.json();
        setSessions(prev => [newSession, ...prev]);
        setCurrentSessionId(newSession.id);
      }
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm("Are you sure you want to delete this chat?")) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setSessions(prev => prev.filter(s => s.id !== sessionId));
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          // Optionally select another session
          fetchSessions();
        }
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  return (
    <div className="App" style={{ display: 'flex', flexDirection: 'row', height: '100vh', width: '100vw' }}>
      <Sidebar 
        sessions={sessions} 
        currentSessionId={currentSessionId}
        onSelectSession={setCurrentSessionId}
        onNewSession={createNewSession}
        onDeleteSession={deleteSession}
      />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <h1 style={{ textAlign: 'center', padding: '10px', margin: 0, borderBottom: '1px solid #eee' }}>Raiden Ei</h1>
        {currentSessionId ? (
          <ChatInterface sessionId={currentSessionId} />
        ) : (
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            Select a chat or create a new one.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
