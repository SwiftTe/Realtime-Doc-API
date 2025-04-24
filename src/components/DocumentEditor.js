import React, { useEffect, useState, useRef } from 'react';
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
  const [comments, setComments] = useState([]);
  const editorRef = useRef(null);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/documents/${documentId}`);
        setContent(response.data.content);
        fetchComments();
      } catch (error) {
        console.error('Error fetching document:', error);
      }
    };

    const fetchComments = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/documents/${documentId}/comments`);
        setComments(response.data);
      } catch (error) {
        console.error('Error fetching comments:', error);
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
      } else if (data.type === 'notification' && data.payload.type === 'mention') {
        if (Notification.permission === 'granted' && !document.hasFocus()) {
          new Notification(`You were mentioned in ${data.payload.document_title}`, {
            body: `Click to view comment`,
            icon: '/logo.png', // Ensure you have a logo.png in your public directory
          });
        }
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
          operation: { type: 'insert', position: e.target.selectionStart, text: newContent.slice(e.target.selectionStart, e.target.selectionStart + (newContent.length - content.length)) },
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

  const renderHighlightedText = (content) => {
    let result = [];
    let lastPos = 0;

    comments.forEach((comment) => {
      try {
        const { start, end } = JSON.parse(comment.selection);
        result.push(content.slice(lastPos, start));
        result.push(
          <span className="highlighted-text" key={`highlight-${comment.id}`}>
            {content.slice(start, end)}
          </span>
        );
        lastPos = end;
      } catch (error) {
        console.error('Error parsing comment selection:', error, comment);
        result.push(content.slice(lastPos));
        lastPos = content.length;
      }
    });

    result.push(content.slice(lastPos));
    return result;
  };

  return (
    <div className="editor-container">
      <h2>Edit Document</h2>
      <textarea
        ref={editorRef}
        value={content}
        onChange={handleChange}
        onSelect={handleSelectionChange}
        on Select={handleTextSelect}
      />
      <div className="document-content">{renderHighlightedText(content)}</div>
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

// Request Notification Permissions (when the component mounts)
useEffect(() => {
  if (typeof Notification !== 'undefined') {
    Notification.requestPermission().then((perm) => {
      if (perm === 'granted') {
        localStorage.setItem('notifications_enabled', 'true');
      }
    });
  }
}, []);

export default DocumentEditor;
