// src/components/CursorOverlay.js
import React, { useEffect, useState } from 'react';

const CursorOverlay = ({ documentId, otherCursors }) => {
  return (
    <div className="cursor-overlay">
      {Object.entries(otherCursors).map(([userId, pos]) => (
        <div 
          key={userId}
          className="cursor"
          style={{ left: `${pos}px` }}
        >
          <span className="cursor-label">{userId}</span>
        </div>
      ))}
    </div>
  );
};