import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { w3cwebsocket as W3CWebSocket } from 'websocket';

const CommentSidebar = ({ documentId, selection }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

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
      await axios.post(`http://localhost:8000/documents/${documentId}/comments`, {
        text: newComment,
        selection: { start: selection.start, end: selection.end },
      });
      setNewComment('');
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

  return (
    <div className="comment-sidebar">
      {comments.map((comment) => (
        <div key={comment.id} className="comment">
          <p>{comment.text}</p>
          <small>By User {comment.user_id}</small>
          <button onClick={() => resolveComment(comment.id)}>Resolve</button>
        </div>
      ))}
      <textarea value={newComment} onChange={(e) => setNewComment(e.target.value)} />
      <button onClick={addComment}>Add Comment</button>
    </div>
  );
};

export default CommentSidebar;
