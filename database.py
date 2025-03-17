import sqlite3

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