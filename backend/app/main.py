
import os
import secrets
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
app = FastAPI(
    title="DEX AI Control Center",
    description="Central API for managing and connecting DEX AI agents",
    version="0.2.0",
)


class AgentMessage(BaseModel):
    agent_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=10000)
    message_type: str = "text"


def verify_connector(token: str | None):
    expected_token = os.getenv("DEX_CONNECTOR_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Connector authentication is not configured",
        )

    if not token or not secrets.compare_digest(token, expected_token):
        raise HTTPException(
            status_code=401,
            detail="Invalid connector token",
        )


@app.get("/")
async def root():
    return {
        "project": "DEX AI Control Center",
        "status": "running",
        "version": "0.2.0",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/connector/message")
async def receive_agent_message(
    payload: AgentMessage,
    x_dex_token: str | None = Header(default=None),
):
    verify_connector(x_dex_token)

    return {
        "status": "received",
        "agent_id": payload.agent_id,
        "message_type": payload.message_type,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "message": "Message received by DEX Control Center",
    }
