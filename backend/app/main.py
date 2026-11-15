
import os
import secrets
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from app.deepseek_client import send_to_deepseek
from app.deepseek_client import check_deepseek_config
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
@app.post("/api/v1/agents/deepseek/message")
async def deepseek_message(
    payload: AgentMessage,
    x_dex_token: str | None = Header(default=None),
):
    verify_connector(x_dex_token)

    try:
        result = await send_to_deepseek(payload.message)
        return {
            "status": "success",
            "agent_id": payload.agent_id,
            "response": result,
        }
        except Exception:
        raise HTTPException(
            status_code=502,
            detail="DeepSeek request failed",
        )
        raise HTTPException(
            status_code=502,
            detail="DeepSeek request failed",
        )


@app.get("/api/v1/agents/deepseek/status")
async def deepseek_status(
    x_dex_token: str | None = Header(default=None),
):
    verify_connector(x_dex_token)
    return check_deepseek_config()
