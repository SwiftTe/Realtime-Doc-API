// src/components/CommentSidebar.js
import React, { useState } from 'react';

const CommentSidebar = ({ documentId, selection }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  const fetchComments = async () => {
    const res = await axios.get(`/documents/${documentId}/comments`);
    setComments(res.data);
  };

  const addComment = async () => {
    await axios.post(`/documents/${documentId}/comments`, {
      text: newComment,
      selection: { start: selection.start, end: selection.end }
    });
    fetchComments();
  };

  return (
    <div className="comment-sidebar">
      {comments.map(comment => (
        <div key={comment.id} className="comment">
          <p>{comment.text}</p>
          <small>By User {comment.user_id}</small>
        </div>
      ))}
      <textarea onChange={(e) => setNewComment(e.target.value)} />
      <button onClick={addComment}>Add Comment</button>
    </div>
  );
};