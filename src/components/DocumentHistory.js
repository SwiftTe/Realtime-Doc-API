import React, { useEffect, useState } from 'react';
import axios from 'axios';

const DocumentHistory = ({ documentId }) => {
  const [versions, setVersions] = useState([]);

  useEffect(() => {
    axios.get(`http://localhost:8000/documents/${documentId}/versions`)
      .then(response => setVersions(response.data))
      .catch(error => console.error(error));
  }, [documentId]);

  return (
    <div>
      <h2>Document History</h2>
      <ul>
        {versions.map(version => (
          <li key={version.id}>
            <button onClick={() => restoreVersion(version.id)}>Restore</button>
            <span>{version.created_at}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentHistory;
