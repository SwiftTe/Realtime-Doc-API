import React, { useState } from 'react';

const MentionAutocomplete = ({ users, onSelect }) => {
  const [query, setQuery] = useState('');
  
  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="mention-autocomplete">
      <input 
        type="text" 
        value={query} 
        onChange={(e) => setQuery(e.target.value.replace('@', ''))}
        placeholder="@username"
      />
      {query && (
        <div className="suggestions">
          {filteredUsers.map(user => (
            <div key={user.id} onClick={() => {
              onSelect(`@${user.name}`);
              setQuery('');
            }}>
              <img src={user.avatar} width="20" /> {user.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
