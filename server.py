from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import websockets
import asyncio
from database import create_document, update_document, get_document, get_document_history, get_user_role, get_user_id_by_api_key, get_document_permission, insert_operation, get_operations, get_document_versions, restore_document_version, create_document_version, share_document, get_shared_documents, conn, cursor
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # Replace with a strong key in production

# RESTful API
class DocumentAPIHandler(BaseHTTPRequestHandler):
    def authenticate(self):
        api_key = self.headers.get('X-API-Key')
        user_id = get_user_id_by_api_key(api_key)
        if not user_id:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized')
            return None
        role = get_user_role(api_key)
        return (user_id, role)

    def check_permission(self, user_id, document_id, permission):
        permission_level = get_document_permission(document_id, user_id)
        return permission_level and permission in permission_level

    def do_POST(self):
        if self.path == '/register':
            # Extract username/password from request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_data = json.loads(post_data)
            # Hash password (use bcrypt in production) and store user in DB
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                           (user_data['username'], user_data['password']))
            conn.commit()
            self.send_response(201)
            self.end_headers()

        elif self.path == '/login':
            # Verify credentials
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_data = json.loads(post_data)
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?',
                           (user_data['username'], user_data['password']))
            user = cursor.fetchone()
            if user:
                # Generate JWT token
                token = jwt.encode({
                    'user_id': user[0],
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }, SECRET_KEY)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'token': token}).encode())
            else:
                self.send_response(401)
                self.end_headers()
        else:
            user = self.authenticate()
            if not user:
                return
            user_id, role = user
            if self.path.startswith('/documents/'):
                document_id = self.path.split('/')[-1]
                if self.path.endswith('/share'):
                    if not self.check_permission(user_id, document_id, 'share'):
                        self.send_response(403)
                        self.end_headers()
                        self.wfile.write(b'Forbidden')
                        return
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    share_data = json.loads(post_data)
                    shared_user_id = share_data.get('user_id')
                    permission = share_data.get('permission')
                    share_document(document_id, shared_user_id, permission)
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'message': 'Document shared'}).encode())
                elif self.path.endswith('/restore'):
                    if not self.check_permission(user_id, document_id, 'edit'):
                        self.send_response(403)
                        self.end_headers()
                        self.wfile.write(b'Forbidden')
                        return
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    version_id = json.loads(post_data).get('version_id')
                    if restore_document_version(version_id):
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'message': 'Document restored'}).encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Version not found')
                else:
                    if not self.check_permission(user_id, document_id, 'edit'):
                        self.send_response(403)
                        self.end_headers()
                        self.wfile.write(b'Forbidden')
                        return
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    document_data = json.loads(post_data)
                    document_id = document_data.get('id')
                    content = document_data.get('content', '')
                    create_document(document_id, content)
                    create_document_version(document_id, content)
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'id': document_id}).encode())
            elif self.path == '/documents':
                if not self.check_permission(user_id, 'doc1', 'edit'):
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(b'Forbidden')
                    return
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                document_data = json.loads(post_data)
                document_id = document_data.get('id')
                content = document_data.get('content', '')
                create_document(document_id, content)
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'id': document_id}).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')

    def do_GET(self):
        user = self.authenticate()
        if not user:
            return
        user_id, role = user
        if self.path.startswith('/documents/'):
            document_id = self.path.split('/')[-1]
            if self.path.endswith('/versions'):
                if not self.check_permission(user_id, document_id, 'view'):
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(b'Forbidden')
                    return
                versions = get_document_versions(document_id)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(versions).encode())
            else:
                if not self.check_permission(user_id, document_id, 'view'):
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(b'Forbidden')
                    return
                content = get_document(document_id)
                if content:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'content': content}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'Document not found')
        elif self.path.startswith('/users/'):
            user_id_path = self.path.split('/')[-2]
            if self.path.endswith('/shared_documents') and user_id_path == str(user_id):
                shared_documents = get_shared_documents(user_id)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(shared_documents).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

# Dictionary to track active users
active_users = {}  # Format: {document_id: {user_id: {'websocket': websocket, 'cursor_pos': 0}}}

# WebSocket server for real-time collaboration
async def handle_connection(websocket, path):
    api_key = websocket.request_headers.get('X-API-Key')
    user_id = get_user_id_by_api_key(api_key)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    document_id = path.split('/')[-1]
    # Track active users and their cursors
    if document_id not in active_users:
        active_users[document_id] = {}
    active_users[document_id][user_id] = {
        'websocket': websocket,
        'cursor_pos': 0
    }

    # Notify other users that this user has joined
    for other_user_id, other_websocket_data in active_users[document_id].items():
        if other_user_id != user_id:
            try:
                await other_websocket_data['websocket'].send(json.dumps({'type': 'user_joined', 'user_id': user_id}))
            except websockets.exceptions.ConnectionClosed:
                # Handle cases where the other user disconnected
                pass

    async for message in websocket:
        data = json.loads(message)
        if data.get('type') == 'operation':
            operation = data.get('operation')
            # Get existing operations
            existing_ops = get_operations(document_id)
            # Transform the new operation against existing operations
            for existing_op in existing_ops:
                operation = transform_operation(operation, existing_op)
            # Insert the transformed operation
            insert_operation(document_id, operation['type'], operation['position'], operation['text'])
            # Broadcast the operation to all connected clients
            for other_user_id, other_websocket_data in active_users[document_id].items():
                try:
                    await other_websocket_data['websocket'].send(json.dumps({'type': 'operation', 'operation': operation}))
                except websockets.exceptions.ConnectionClosed:
                    # Handle cases where the other user disconnected
                    pass
        elif data.get('type') == 'cursor_update':
            active_users[document_id][user_id]['cursor_pos'] = data['position']
            # Broadcast to all other users
            for other_user_id, other_websocket_data in active_users[document_id].items():
                if other_user_id != user_id:
                    try:
                        await other_websocket_data['websocket'].send(json.dumps({
                            'type': 'cursor_update',
                            'user_id': user_id,
                            'position': data['position']
                        }))
                    except websockets.exceptions.ConnectionClosed:
                        # Handle cases where the other user disconnected
                        pass

    # Notify other users that this user has left
    del active_users[document_id][user_id]
    for other_user_id, other_websocket_data in active_users[document_id].items():
        try:
            await other_websocket_data['websocket'].send(json.dumps({'type': 'user_left', 'user_id': user_id}))
        except websockets.exceptions.ConnectionClosed:
            # Handle cases where the other user disconnected
            pass

def transform_operation(op1, op2):
    # op1: New operation
    # op2: Existing operation
    if op1['type'] == 'insert' and op2['type'] == 'insert':
        if op1['position'] <= op2['position']:
            op2['position'] += len(op1['text'])
    elif op1['type'] == 'insert' and op2['type'] == 'delete':
        if op1['position'] <= op2['position']:
            op2['position'] += len(op1['text'])
    elif op1['type'] == 'delete' and op2['type'] == 'insert':
        if op1['position'] < op2['position']:
            op2['position'] -= len(op1['text'])
    elif op1['type'] == 'delete' and op2['type'] == 'delete':
        if op1['position'] < op2['position']:
            op2['position'] -= len(op1['text'])
        elif op1['position'] == op2['position']:
            op2['text'] = ''  # Both deletions cancel each other
    return op2

def run_http_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, DocumentAPIHandler)
    print('Starting HTTP server on port 8000...')
    httpd.serve_forever()

async def run_websocket_server():
    async with websockets.serve(handle_connection, 'localhost', 8765):
        print('Starting WebSocket server on port 8765...')
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    import threading
    http_thread = threading.Thread(target=run_http_server)
    http_thread.start()
    asyncio.run(run_websocket_server())
    