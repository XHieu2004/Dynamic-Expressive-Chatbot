import React from 'react';

const Sidebar = ({ sessions, currentSessionId, onSelectSession, onNewSession, onDeleteSession }) => {
  return (
    <div style={{ 
      width: '250px', 
      background: '#f8f9fa', 
      borderRight: '1px solid #ddd', 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      padding: '10px'
    }}>
      <button 
        onClick={onNewSession}
        style={{
          padding: '10px',
          marginBottom: '20px',
          background: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        + New Chat
      </button>
      
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {sessions.map(session => (
          <div 
            key={session.id}
            style={{
              padding: '10px',
              marginBottom: '5px',
              background: session.id === currentSessionId ? '#e9ecef' : 'transparent',
              borderRadius: '5px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
            onClick={() => onSelectSession(session.id)}
          >
            <span style={{ 
              whiteSpace: 'nowrap', 
              overflow: 'hidden', 
              textOverflow: 'ellipsis',
              maxWidth: '180px',
              fontSize: '14px'
            }}>
              {session.title}
            </span>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
              }}
              style={{
                background: 'none',
                border: 'none',
                color: '#dc3545',
                cursor: 'pointer',
                fontSize: '16px',
                padding: '0 5px'
              }}
            >
              &times;
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
