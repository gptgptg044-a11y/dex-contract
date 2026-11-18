
import os
import secrets
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from app.deepseek_client import (
    send_to_deepseek,
    check_deepseek_config,
)

from app.agent_registry import (
    AgentCreate,
    AgentStatusUpdate,
    register_agent,
    list_agents,
    get_agent,
    update_agent_status,
)


logger = logging.getLogger(__name__)


connector_token_header = APIKeyHeader(
    name="x-dex-token",
    auto_error=False,
)


app = FastAPI(
    title="DEX AI Control Center",
    description="Central API for managing and connecting DEX AI agents",
    version="0.3.0",
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
        "version": "0.3.0",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/connector/message")
async def receive_agent_message(
    payload: AgentMessage,
    x_dex_token: str | None = Depends(connector_token_header),
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
    x_dex_token: str | None = Depends(connector_token_header),
):
    verify_connector(x_dex_token)

    try:
        result = await send_to_deepseek(payload.message)

        return {
            "status": "success",
            "agent_id": payload.agent_id,
            "response": result,
        }

    except Exception as exc:
        logger.exception(
            "DeepSeek request failed. Error type: %s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail="DeepSeek request failed. Check server logs.",
        ) from None


@app.get("/api/v1/agents/deepseek/status")
async def deepseek_status(
    x_dex_token: str | None = Depends(connector_token_header),
):
    verify_connector(x_dex_token)

    return check_deepseek_config()


@app.post("/api/v1/agents/register")
async def create_agent(
    payload: AgentCreate,
    x_dex_token: str | None = Depends(connector_token_header),
):
    verify_connector(x_dex_token)

    try:
        agent = register_agent(payload)
        return {
            "status": "registered",
            "agent": agent,
        }
    except ValueError:
        raise HTTPException(
            status_code=409,
            detail="Agent already exists",
        )


@app.get("/api/v1/agents")
async def get_agents(
    x_dex_token: str | None = Depends(connector_token_header),
):
    verify_connector(x_dex_token)

    agents = list_agents()

    return {
        "count": len(agents),
        "agents": agents,
    }


@app.get("/api/v1/agents/{agent_id}")
async def get_agent_details(
    agent_id: str,
    x_dex_token: str | None = Depends(connector_token_header),
):
    verify_connector(x_dex_token)

    agent = get_agent(agent_id)

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return agent


@app.patch("/api/v1/agents/{agent_id}/status")
async def change_agent_status(
    agent_id: str,
    payload: AgentStatusUpdate,
    x_dex_token: str | None = Depends(connector_token_header),
):
    verify_connector(x_dex_token)

    agent = update_agent_status(
        agent_id,
        payload.status,
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return {
        "status": "updated",
        "agent": agent,
    }
