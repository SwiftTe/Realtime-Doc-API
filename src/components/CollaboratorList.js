// src/components/CollaboratorList.js
import React, { useEffect, useState } from 'react';

const CollaboratorList = ({ documentId }) => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8765/${documentId}`);
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'presence') {
        setUsers(msg.users);
      }
    };
    return () => ws.close();
  }, [documentId]);

  return (
    <div className="collaborators">
      {users.map(user => (
        <div key={user} className="user-avatar" style={{ backgroundColor: stringToColor(user) }}>
          {user.charAt(0).toUpperCase()}
        </div>
      ))}
    </div>
  );
};

// Helper: Generate color from user ID
const stringToColor = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return `hsl(${hash % 360}, 70%, 60%)`;
};