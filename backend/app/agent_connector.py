
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    sender_id: str = Field(min_length=1, max_length=100)
    recipient_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=10000)
    message_type: str = "text"
    message_id: str = Field(min_length=1, max_length=100)


class AgentMessageReceipt(BaseModel):
    status: str = "received"
    message_id: str
    sender_id: str
    recipient_id: str
    received_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def validate_agent_message(payload: AgentMessage) -> dict[str, Any]:
    return payload.model_dump()
