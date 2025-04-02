import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { w3cwebsocket as W3CWebSocket } from 'websocket';

const CursorOverlay = ({ otherCursors }) => {
  return (
    <div className="cursor-overlay">
      {Object.entries(otherCursors).map(([userId, position]) => (
        <div
          key={userId}
          className="other-cursor"
          style={{ position: 'absolute', left: `${position * 8}px`, top: '0px' }}
        >
          {userId}
        </div>
      ))}
    </div>
  );
};

const DocumentEditor = ({ documentId }) => {
  const [content, setContent] = useState('');
  const [socket, setSocket] = useState(null);
  const [shareEmail, setShareEmail] = useState('');
  const [sharePermission, setSharePermission] = useState('view');
  const [otherCursors, setOtherCursors] = useState({});
  const [selection, setSelection] = useState(null);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/documents/${documentId}`);
        setContent(response.data.content);
      } catch (error) {
        console.error('Error fetching document:', error);
      }
    };

    fetchDocument();

    const ws = new W3CWebSocket(`ws://localhost:8765/${documentId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (message) => {
      const data = JSON.parse(message.data);
      if (data.type === 'operation') {
        setContent((prevContent) => applyOperation(prevContent, data.operation));
      } else if (data.type === 'cursor_update') {
        setOtherCursors((prev) => ({
          ...prev,
          [data.user_id]: data.position,
        }));
      }
    };

    setSocket(ws);

    return () => {
      if (ws && ws.readyState === W3CWebSocket.OPEN) {
        ws.close();
      }
    };
  }, [documentId]);

  const handleChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    if (socket && socket.readyState === W3CWebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: 'operation',
          operation: { type: 'insert', position: newContent.length, text: newContent.slice(-1) },
        })
      );
    }
  };

  const handleShare = async () => {
    try {
      await axios.post(`http://localhost:8000/documents/${documentId}/share`, {
        user_id: shareEmail,
        permission: sharePermission,
      });
      alert('Document shared successfully!');
      setShareEmail('');
      setSharePermission('view');
    } catch (error) {
      console.error('Error sharing document:', error);
      alert('Failed to share document.');
    }
  };

  const handleSelectionChange = (e) => {
    if (socket && socket.readyState === W3CWebSocket.OPEN) {
      const cursorPos = e.target.selectionStart;
      socket.send(
        JSON.stringify({
          type: 'cursor_update',
          position: cursorPos,
        })
      );
    }
  };

  const handleTextSelect = (e) => {
    setSelection({
      start: e.target.selectionStart,
      end: e.target.selectionEnd,
    });
  };

  const applyOperation = (prevContent, operation) => {
      if (operation.type === 'insert') {
          return prevContent.slice(0, operation.position) + operation.text + prevContent.slice(operation.position);
      } else if (operation.type === 'delete') {
          return prevContent.slice(0, operation.position) + prevContent.slice(operation.position + operation.text.length);
      }
      return prevContent;
  };

  return (
    <div className="editor-container">
      <h2>Edit Document</h2>
      <textarea
        value={content}
        onChange={handleChange}
        onSelect={handleSelectionChange}
        onSelect={handleTextSelect}
      />
      <CursorOverlay otherCursors={otherCursors} />
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
