from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import websockets
import asyncio
from database import create_document, update_document, get_document, get_document_history, get_user_role, get_user_id_by_api_key, get_document_permission, insert_operation, get_operations

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
        user = self.authenticate()
        if not user:
            return
        user_id, role = user
        if not self.check_permission(user_id, 'doc1', 'edit'):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Forbidden')
            return
        if self.path == '/documents':
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
        if not self.check_permission(user_id, 'doc1', 'view'):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Forbidden')
            return
        if self.path.startswith('/documents/'):
            document_id = self.path.split('/')[-1]
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
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

# WebSocket server for real-time collaboration
async def handle_connection(websocket, path):
    api_key = websocket.request_headers.get('X-API-Key')
    user_id = get_user_id_by_api_key(api_key)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    document_id = path.split('/')[-1]
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
            await websocket.send(json.dumps({'type': 'operation', 'operation': operation}))
        elif data.get('type') == 'update':
            if not get_document_permission(document_id, user_id) or "edit" not in get_document_permission(document_id, user_id):
                await websocket.send(json.dumps({'type': 'error', 'message': 'Permission denied'}))
                continue
            update_document(document_id, data.get('content'))
            await websocket.send(json.dumps({'type': 'ack', 'message': 'Update received'}))
        elif data.get('type') == 'subscribe':
            if not get_document_permission(document_id, user_id) or "view" not in get_document_permission(document_id, user_id):
                await websocket.send(json.dumps({'type': 'error', 'message': 'Permission denied'}))
                continue
            content = get_document(document_id)
            await websocket.send(json.dumps({'type': 'content', 'content': content}))

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
    