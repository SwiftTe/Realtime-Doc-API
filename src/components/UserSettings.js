import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserSettings = () => {
  const [prefs, setPrefs] = useState({ email_notifications: true });

  useEffect(() => {
    // Fetch preferences from backend on load
    axios.get('/user/preferences').then(res => {
      setPrefs(res.data);
    });
  }, []);

  const updatePrefs = async (key, value) => {
    try {
      await axios.put('/user/preferences', { [key]: value });
      setPrefs(prev => ({ ...prev, [key]: value }));
    } catch (err) {
      console.error('Failed to update preferences:', err);
    }
  };

  return (
    <div>
      <h2>User Notification Settings</h2>
      <label>
        <input 
          type="checkbox" 
          checked={prefs.email_notifications}
          onChange={(e) => updatePrefs('email_notifications', e.target.checked)}
        />
        Email Notifications
      </label>
    </div>
  );
};

export default UserSettings;
