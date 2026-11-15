from datetime import datetime, timezone
from threading import RLock
from typing import Literal

from pydantic import BaseModel, Field


AgentStatus = Literal["enabled", "disabled"]


class AgentCreate(BaseModel):
    agent_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9._-]+$"
    )
    name: str = Field(min_length=1, max_length=120)
    provider: str = Field(min_length=1, max_length=50)


class AgentStatusUpdate(BaseModel):
    status: AgentStatus


class AgentRecord(BaseModel):
    agent_id: str
    name: str
    provider: str
    status: AgentStatus
    created_at: str
    updated_at: str


_agents: dict[str, AgentRecord] = {}
_lock = RLock()


def register_agent(payload: AgentCreate) -> AgentRecord:
    now = datetime.now(timezone.utc).isoformat()

    with _lock:
        if payload.agent_id in _agents:
            raise ValueError("Agent already exists")

        agent = AgentRecord(
            agent_id=payload.agent_id,
            name=payload.name,
            provider=payload.provider,
            status="disabled",
            created_at=now,
            updated_at=now,
        )

        _agents[payload.agent_id] = agent
        return agent


def list_agents() -> list[AgentRecord]:
    with _lock:
        return list(_agents.values())


def get_agent(agent_id: str) -> AgentRecord | None:
    with _lock:
        return _agents.get(agent_id)


def update_agent_status(
    agent_id: str,
    status: AgentStatus
) -> AgentRecord | None:
    with _lock:
        agent = _agents.get(agent_id)

        if agent is None:
            return None

        updated = agent.model_copy(
            update={
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        _agents[agent_id] = updated
        return updated
