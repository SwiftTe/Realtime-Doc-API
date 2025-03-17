from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import websockets
import asyncio
from database import create_document, update_document, get_document, get_document_history

# RESTful API
class DocumentAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
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
    document_id = path.split('/')[-1]
    async for message in websocket:
        data = json.loads(message)
        if data.get('type') == 'update':
            update_document(document_id, data.get('content'))
            await websocket.send(json.dumps({'type': 'ack', 'message': 'Update received'}))
        elif data.get('type') == 'subscribe':
            content = get_document(document_id)
            await websocket.send(json.dumps({'type': 'content', 'content': content}))

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