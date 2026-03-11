import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.task_service import TaskService, manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Shared service instance (uses the module-level WebSocket manager)
_service = TaskService(ws_manager=manager)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    goal: str


class StepOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    output: Optional[str]
    error: Optional[str]
    started_at: Optional[Any]
    completed_at: Optional[Any]
    order_index: int

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: str
    title: str
    goal: str
    status: str
    created_at: Any
    updated_at: Any
    plan: Optional[Dict[str, Any]]
    workspace_dir: Optional[str]
    steps: List[StepOut] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[TaskOut])
async def list_tasks():
    tasks = await _service.list_tasks()
    return [TaskOut.model_validate(t) for t in tasks]


@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(body: TaskCreate):
    task = await _service.create_task(body.goal)
    return TaskOut.model_validate(task)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str):
    task = await _service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str):
    deleted = await _service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/start", response_model=TaskOut)
async def start_task(task_id: str):
    task = await _service.start_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut.model_validate(task)


@router.post("/{task_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(task_id: str):
    cancelled = await _service.cancel_task(task_id)
    return {"task_id": task_id, "cancelled": cancelled}


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(task_id: str, websocket: WebSocket):
    await manager.connect(task_id, websocket)
    try:
        while True:
            # Keep connection alive; the server pushes updates via broadcast.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id, websocket)
    except Exception as exc:
        logger.warning("WebSocket error for task %s: %s", task_id, exc)
        manager.disconnect(task_id, websocket)
