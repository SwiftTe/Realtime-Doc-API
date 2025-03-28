import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { w3cwebsocket as W3CWebSocket } from 'websocket';

const DocumentEditor = ({ documentId }) => {
  const [content, setContent] = useState('');
  const [socket, setSocket] = useState(null);
  const [shareEmail, setShareEmail] = useState('');
  const [sharePermission, setSharePermission] = useState('view');

  useEffect(() => {
    // Fetch the document content
    axios.get(`http://localhost:8000/documents/${documentId}`)
      .then(response => setContent(response.data.content))
      .catch(error => console.error(error));

    // Connect to the WebSocket server
    const ws = new W3CWebSocket(`ws://localhost:8765/${documentId}`);
    ws.onopen = () => console.log('WebSocket connected');
    ws.onmessage = (message) => {
      const data = JSON.parse(message.data);
      if (data.type === 'operation') {
        setContent(prevContent => applyOperation(prevContent, data.operation));
      }
    };
    setSocket(ws);

    return () => ws.close();
  }, [documentId]);

  const handleChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    if (socket) {
      socket.send(JSON.stringify({
        type: 'operation',
        operation: { type: 'insert', position: newContent.length, text: newContent.slice(-1) }
      }));
    }
  };

  const handleShare = async () => {
    try {
      await axios.post(`http://localhost:8000/documents/${documentId}/share`, {
        user_id: shareEmail,
        permission: sharePermission
      });
      alert('Document shared successfully!');
      setShareEmail('');
      setSharePermission('view');
    } catch (error) {
      console.error('Error sharing document:', error);
      alert('Failed to share document.');
    }
  };

  return (
    <div>
      <h2>Edit Document</h2>
      <textarea value={content} onChange={handleChange} />

      <div>
        <h3>Share Document</h3>
        <input
          type="email"
          placeholder="Enter email to share with"
          value={shareEmail}
          onChange={(e) => setShareEmail(e.target.value)}
        />
        <select value={sharePermission} onChange={(e) => setSharePermission(e.target.value)}>
          <option value="view">View</option>
          <option value="edit">Edit</option>
        </select>
        <button onClick={handleShare}>Share</button>
      </div>
    </div>
  );
};

export default DocumentEditor;
