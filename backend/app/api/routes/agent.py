"""
app/api/routes/agent.py — AI agent chat interface endpoints.

The agent is backed by an LLMService abstraction that hides whether we're
calling Claude or OpenAI underneath. It has access to tools for querying
markets, edges, and news embeddings (RAG).

Responses are streamed back to the React frontend using Server-Sent Events (SSE).
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user_id
from app.db.session import get_db
from app.services.llm_service import LLMService

router = APIRouter()


class ChatMessage(BaseModel):
    role: str       # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    session_id: str | None = None   # For future conversation memory


@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI agent and get a streamed response.

    The agent can answer questions about open markets, explain detected edges,
    surface relevant news, and help build trading strategies.

    TODO: Wire up LLMService with tools (market queries, RAG, edge data).
    TODO: Stream the response back as SSE chunks.
    """
    llm = LLMService()

    async def generate():
        # Placeholder: yield chunks as they arrive from the LLM
        # TODO: Replace with actual streaming from LLMService
        yield "data: {\"chunk\": \"Agent not yet implemented.\"}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
