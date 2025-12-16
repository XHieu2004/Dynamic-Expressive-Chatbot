import React from 'react';

const Avatar = ({ url }) => {
  return (
    <div className="avatar-container" style={{ textAlign: 'center', marginBottom: '20px' }}>
      <img 
        src={url} 
        alt="Avatar" 
        style={{ width: '200px', height: '200px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #ccc' }} 
        onError={(e) => { e.target.src = 'https://via.placeholder.com/200?text=Avatar'; }}
      />
    </div>
  );
};

export default Avatar;
