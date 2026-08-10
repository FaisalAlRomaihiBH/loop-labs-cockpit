"""FastAPI app for the cockpit.

Step 2: /api/message runs the hard-coded test agent (app/agents.py) and
streams its reply over SSE using the same envelope as Step 1.

Run from the repo root with: uvicorn app.main:app
"""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from . import agents, db

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

# One queue per session, created lazily. Messages for a session are pushed
# here by the echo task and pulled by that session's SSE generator.
_queues: dict[int, asyncio.Queue] = {}

# The event loop keeps only weak references to tasks; hold strong refs so
# fire-and-forget echo tasks can't be garbage-collected mid-stream.
_background_tasks: set[asyncio.Task] = set()


def _get_or_create_queue(session_id: int) -> asyncio.Queue:
    if session_id not in _queues:
        _queues[session_id] = asyncio.Queue()
    return _queues[session_id]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(lifespan=lifespan)


class SessionRequest(BaseModel):
    founder: Optional[Literal["A", "B"]] = None


class MessageRequest(BaseModel):
    session_id: int
    founder: Literal["A", "B"]
    content: str


@app.post("/api/session")
async def create_session(body: SessionRequest):
    session_id = db.create_session(agent="test-agent", founder=body.founder)
    return {"session_id": session_id}


async def _agent_reply(session_id: int, content: str) -> None:
    """Background task: stream the agent's reply, then persist it."""
    queue = _get_or_create_queue(session_id)
    chunks: list[str] = []
    try:
        async for chunk in agents.run_test_agent(content):
            chunks.append(chunk)
            await queue.put({"type": "text", "content": chunk, "timestamp": _now()})
    except Exception as exc:
        await queue.put(
            {"type": "error", "content": f"agent error: {exc}", "timestamp": _now()}
        )
        await queue.put({"type": "done", "content": "", "timestamp": _now()})
        return

    full_reply = "".join(chunks)
    db.add_message(session_id, role="agent", founder=None, content=full_reply)
    await queue.put({"type": "done", "content": "", "timestamp": _now()})


@app.post("/api/message")
async def post_message(body: MessageRequest):
    if not db.session_exists(body.session_id):
        raise HTTPException(status_code=404, detail="session not found")

    db.add_message(
        body.session_id, role="founder", founder=body.founder, content=body.content
    )
    task = asyncio.create_task(_agent_reply(body.session_id, body.content))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return {"ok": True}


@app.get("/api/stream/{session_id}")
async def stream(session_id: int):
    queue = _get_or_create_queue(session_id)

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            # client disconnected; nothing else to clean up
            return

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html")
