Realtime Document Collaboration API
 Overview
This project is a real-time collaborative document backend system that allows multiple users to:

Edit documents in real time

Track changes and versions

Share documents with other users

Restore old document versions

Manage everything with a lightweight SQLite database

The backend uses WebSocket for live collaboration and is fully containerized with Docker and docker-compose for easy deployment.

✅ Key Features
Real-time Collaboration — Multiple users can edit the same document live.

Document Operations Tracking — Stores all edits and operations.

Version Control — Automatically saves and restores different versions of documents.

Document Sharing — Share documents and retrieve a list of shared documents.

Active User Tracking — Keeps track of who’s connected to which document.

SQLite Database — Lightweight database to store documents, operations, versions, and sharing permissions.

Docker Support — Easily deploy the app in containers using Docker and Docker Compose.

📁 Project Structure
File/Folder	Description
server.py	The WebSocket server handling real-time collaboration and API endpoints.
database.py	Database setup, queries, and functions to manage operations, versions, and sharing.
documents.db	SQLite database storing documents and their operations.
Dockerfile	Docker configuration to containerize the application.
docker-compose.yml	Docker Compose file to orchestrate services.
requirements.txt	Project dependencies.
README.md	Project documentation (this file!).
.gitignore	Files/folders ignored by git.

API & WebSocket Endpoints (Summary)
Feature	Endpoint Example
Get Document Versions	GET /get_document_versions/<document_id>
Restore Document Version	POST /restore_version
Share Document	POST /share_document
Get Shared Documents	GET /get_shared_documents/<user_id>
WebSocket Document Editing	ws://<host>:<port>/ws/document/<document_id>
🤝 Contributing
Contributions, ideas, and improvements are welcome!

📜 License
This project is licensed under the MIT License. 