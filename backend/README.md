# DEX Backend

The backend is the central API server of the DEX AI Control Center.

## Technology
- Python
- FastAPI
- Uvicorn

## Current Status
- Backend successfully deployed on Railway.
- Public API is operational.
- Health check endpoint is working.
- API documentation is available through Swagger.

## Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Project status |
| GET | /health | Health check |
| GET | /docs | API documentation |

## Core Modules (Planned)
- Agent Management
- Task Management
- Agent Communication
- Report Collection
- Approval Workflow
- API Orchestration
- Audit Logging
- Security and Access Control

## Security
- Never store API keys in source code.
- Use environment variables for credentials.
- Apply least-privilege access.
- Require human approval for sensitive actions.

## Development Roadmap
1. Backend foundation - Completed
2. Agent Management - Planned
3. Task Management - Planned
4. Agent Communication - Planned
5. Security and Testing - Planned