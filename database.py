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
    role TEXT
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

conn.commit()

# Add a default admin user (for testing)
cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?)',
               ('admin', 'secret1', 'admin'))

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

def create_user(user_id, api_key, role):
    cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?)',(user_id, api_key, role))
    conn.commit()

def get_user_id_by_api_key(api_key):
    cursor.execute('SELECT id FROM users WHERE api_key = ?', (api_key,))
    row = cursor.fetchone()
    return row[0] if row else None

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