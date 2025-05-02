import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { w3cwebsocket as W3CWebSocket } from 'websocket';

const CommentSidebar = ({ documentId, selection }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [users, setUsers] = useState([]);
  const [showMentionAutocomplete, setShowMentionAutocomplete] = useState(false);
  const [newCommentId, setNewCommentId] = useState(null); // To store the ID of the newly added comment

  useEffect(() => {
    axios.get('/api/users').then((res) => setUsers(res.data));
  }, []);

  const getDocumentUrl = (commentId) => {
    return `${window.location.origin}/documents/${documentId}#comment-${commentId}`;
  };

  const fetchComments = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/documents/${documentId}/comments`);
      setComments(res.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const addComment = async () => {
    try {
      const res = await axios.post(`http://localhost:8000/documents/${documentId}/comments`, {
        text: newComment,
        selection: { start: selection.start, end: selection.end },
      });
      setNewComment('');
      setShowMentionAutocomplete(false);
      setNewCommentId(res.data.comment_id); // Store the ID of the newly created comment
      fetchComments();
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  const resolveComment = async (commentId) => {
    const ws = new W3CWebSocket(`ws://localhost:8765/${documentId}`);
    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          type: 'resolve_comment',
          comment_id: commentId,
          document_id: documentId,
        })
      );
    };
  };

  useEffect(() => {
    fetchComments();
    const ws = new W3CWebSocket(`ws://localhost:8765/${documentId}`);

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);

      if (msg.type === 'new_comment') {
        setComments((prev) => [...prev, msg.comment]);
      }

      if (msg.type === 'comment_resolved') {
        setComments((prev) => prev.filter((c) => c.id !== msg.comment_id));
      }
    };

    return () => {
      if (ws && ws.readyState === W3CWebSocket.OPEN) {
        ws.close();
      }
    };
  }, [documentId]);

  const handleCommentChange = (text) => {
    if (text.endsWith('@')) {
      setShowMentionAutocomplete(true);
    } else {
      setShowMentionAutocomplete(false);
    }
    setNewComment(text);
  };

  return (
    <div className="comment-sidebar">
      {comments.map((comment) => (
        <div key={comment.id} id={`comment-${comment.id}`} className={`comment ${comment.resolved ? 'resolved' : ''}`}>
          <p>{comment.text}</p>
          <small>By User {comment.user_id}</small>
          {!comment.resolved && (
            <button className="resolve-btn" onClick={() => resolveComment(comment.id)}>
              Resolve
            </button>
          )}
        </div>
      ))}
      <textarea value={newComment} onChange={(e) => handleCommentChange(e.target.value)} />
      {showMentionAutocomplete && (
        <MentionAutocomplete
          users={users}
          onSelect={(mention) => {
            setNewComment(newComment.slice(0, -1) + mention + ' ');
            setShowMentionAutocomplete(false);
          }}
        />
      )}
      <button onClick={addComment}>Add Comment</button>
    </div>
  );
};

// Dummy MentionAutocomplete component - replace with your actual implementation
const MentionAutocomplete = ({ users, onSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const filteredUsers = users.filter((user) =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="mention-autocomplete">
      <input
        type="text"
        placeholder="Search users..."
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <ul>
        {filteredUsers.map((user) => (
          <li key={user.id} onClick={() => onSelect(`@${user.username}`)}>
            {user.username} ({user.email})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CommentSidebar;

// Request Notification Permissions (place this outside the component)
if (typeof Notification !== 'undefined') {
  Notification.requestPermission().then((perm) => {
    if (perm === 'granted') {
      localStorage.setItem('notifications_enabled', 'true');
    }
  });
}
