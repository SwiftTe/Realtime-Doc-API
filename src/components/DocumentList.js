import React, { useEffect, useState } from 'react';
import axios from 'axios';

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/documents')
      .then(response => setDocuments(response.data))
      .catch(error => console.error(error));
  }, []);

  return (
    <div>
      <h2>Documents</h2>
      <ul>
        {documents.map(doc => (
          <li key={doc.id}>
            <a href={`/documents/${doc.id}`}>{doc.id}</a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentList;