import sqlite3
from datetime import datetime

# Connect to SQLite
conn = sqlite3.connect('documents.db', check_same_thread=False)
cursor = conn.cursor()

# Create documents table
cursor.execute('''
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content TEXT,
    created_at TEXT
)
''')

# Create document history table
cursor.execute('''
CREATE TABLE IF NOT EXISTS document_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT,
    content TEXT,
    updated_at TEXT
)
''')

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    api_key TEXT,
    role TEXT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE
)
''')

# Create document_permissions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS document_permissions (
    document_id TEXT,
    user_id TEXT,
    permission TEXT
)
''')

# Create operations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT,
    type TEXT,  # 'insert' or 'delete'
    position INTEGER,
    text TEXT,
    timestamp TEXT
)
''')

# Create document_versions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT,
    content TEXT,
    created_at TEXT
)
''')

# Create document_shares table
cursor.execute('''
CREATE TABLE IF NOT EXISTS document_shares (
    document_id TEXT,
    user_id TEXT,
    permission TEXT
)
''')

# Create comments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    document_id TEXT,
    user_id TEXT,
    text TEXT,
    selection TEXT,  # JSON: {start: 5, end: 10}
    created_at TEXT,
    resolved BOOLEAN DEFAULT FALSE
)
''')

# Create user_preferences table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id TEXT PRIMARY KEY,
    email_notifications BOOLEAN DEFAULT TRUE,
    notification_sound BOOLEAN DEFAULT TRUE
)
''')

conn.commit()

# Add a default admin user (for testing)
cursor.execute('INSERT OR IGNORE INTO users (id, api_key, role, username, password, email) VALUES (?, ?, ?, ?, ?, ?)',
                ('admin', 'secret1', 'admin', 'admin', 'password', 'admin@example.com'))

# Add default permissions (for testing)
cursor.execute('INSERT OR IGNORE INTO document_permissions VALUES (?, ?, ?)',
                ('doc1', 'admin', 'edit'))

conn.commit()

def create_document(document_id, content):
    cursor.execute('INSERT INTO documents VALUES (?, ?, ?)',
                    (document_id, content, datetime.now().isoformat()))
    conn.commit()

def update_document(document_id, content):
    cursor.execute('UPDATE documents SET content = ? WHERE id = ?',
                    (content, document_id))
    cursor.execute('INSERT INTO document_history (document_id, content, updated_at) VALUES (?, ?, ?)',
                    (document_id, content, datetime.now().isoformat()))
    conn.commit()

def get_document(document_id):
    cursor.execute('SELECT content FROM documents WHERE id = ?', (document_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_document_history(document_id):
    cursor.execute('SELECT content, updated_at FROM document_history WHERE document_id = ? ORDER BY updated_at DESC', (document_id,))
    return cursor.fetchall()

def get_user_role(api_key):
    cursor.execute('SELECT role FROM users WHERE api_key = ?', (api_key,))
    row = cursor.fetchone()
    return row[0] if row else None

def create_user(user_id, api_key, role, username, password, email):
    cursor.execute('INSERT OR IGNORE INTO users (id, api_key, role, username, password, email) VALUES (?, ?, ?, ?, ?, ?)',(user_id, api_key, role, username, password, email))
    conn.commit()

def get_user_id_by_api_key(api_key):
    cursor.execute('SELECT id FROM users WHERE api_key = ?', (api_key,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_user_by_id(user_id):
    cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    return {'id': row[0], 'username': row[1], 'email': row[2]} if row else None

def get_document_permission(document_id, user_id):
    cursor.execute('SELECT permission FROM document_permissions WHERE document_id = ? AND user_id = ?', (document_id, user_id))
    row = cursor.fetchone()
    return row[0] if row else None

def set_document_permission(document_id, user_id, permission):
    cursor.execute('INSERT OR REPLACE INTO document_permissions VALUES (?, ?, ?)',(document_id, user_id, permission))
    conn.commit()

def insert_operation(document_id, operation_type, position, text):
    cursor.execute('INSERT INTO operations (document_id, type, position, text, timestamp) VALUES (?, ?, ?, ?, ?)',
                    (document_id, operation_type, position, text, datetime.now().isoformat()))
    conn.commit()

def get_operations(document_id):
    cursor.execute('SELECT type, position, text FROM operations WHERE document_id = ? ORDER BY timestamp', (document_id,))
    return cursor.fetchall()

def create_document_version(document_id, content):
    cursor.execute('INSERT INTO document_versions (document_id, content, created_at) VALUES (?, ?, ?)',
                    (document_id, content, datetime.now().isoformat()))
    conn.commit()

def get_document_versions(document_id):
    cursor.execute('SELECT id, content, created_at FROM document_versions WHERE document_id = ? ORDER BY created_at DESC', (document_id,))
    return cursor.fetchall()

def restore_document_version(version_id):
    cursor.execute('SELECT document_id, content FROM document_versions WHERE id = ?', (version_id,))
    row = cursor.fetchone()
    if row:
        document_id, content = row
        cursor.execute('UPDATE documents SET content = ? WHERE id = ?', (content, document_id))
        conn.commit()
        return document_id
    return None

def share_document(document_id, user_id, permission):
    cursor.execute('INSERT INTO document_shares (document_id, user_id, permission) VALUES (?, ?, ?)',
                    (document_id, user_id, permission))
    conn.commit()

def get_shared_documents(user_id):
    cursor.execute('SELECT document_id, permission FROM document_shares WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def get_user_preferences(user_id):
    cursor.execute('SELECT email_notifications, notification_sound FROM user_preferences WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        return {'email_notifications': bool(row[0]), 'notification_sound': bool(row[1])}
    else:
        # Create default preferences if they don't exist
        cursor.execute('INSERT OR IGNORE INTO user_preferences (user_id) VALUES (?)', (user_id,))
        conn.commit()
        return {'email_notifications': True, 'notification_sound': True}

def set_user_preferences(user_id, email_notifications, notification_sound):
    cursor.execute('INSERT OR REPLACE INTO user_preferences (user_id, email_notifications, notification_sound) VALUES (?, ?, ?)',
                    (user_id, int(email_notifications), int(notification_sound)))
    conn.commit()
    