import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.database import Artifact, AsyncSessionLocal, Step, Task, init_db

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("./workspace")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ConnectionManager:
    """Manages active WebSocket connections keyed by task_id."""

    def __init__(self) -> None:
        self._connections: Dict[str, List[Any]] = {}

    async def connect(self, task_id: str, websocket: Any) -> None:
        await websocket.accept()
        self._connections.setdefault(task_id, []).append(websocket)

    def disconnect(self, task_id: str, websocket: Any) -> None:
        conns = self._connections.get(task_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, task_id: str, message: Dict[str, Any]) -> None:
        conns = self._connections.get(task_id, [])
        dead = []
        for ws in list(conns):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(task_id, ws)


# Module-level singleton reused by both the service and the router
manager = ConnectionManager()


class TaskService:
    """Business logic for task lifecycle management."""

    def __init__(self, ws_manager: Optional[ConnectionManager] = None) -> None:
        self._manager = ws_manager or manager
        self._running: Dict[str, asyncio.Task] = {}

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    async def create_task(self, goal: str) -> Task:
        task_id = str(uuid.uuid4())
        title = goal[:80] + ("…" if len(goal) > 80 else "")
        workspace_dir = str(WORKSPACE_ROOT / task_id)

        async with AsyncSessionLocal() as session:
            task = Task(
                id=task_id,
                title=title,
                goal=goal,
                status="pending",
                workspace_dir=workspace_dir,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Task)
                .options(selectinload(Task.steps), selectinload(Task.artifacts))
                .where(Task.id == task_id)
            )
            return result.scalar_one_or_none()

    async def list_tasks(self) -> List[Task]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Task)
                .options(selectinload(Task.steps), selectinload(Task.artifacts))
                .order_by(Task.created_at.desc())
            )
            return list(result.scalars().all())

    async def delete_task(self, task_id: str) -> bool:
        await self.cancel_task(task_id)
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            if task is None:
                return False
            await session.delete(task)
            await session.commit()
            return True

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def start_task(self, task_id: str) -> Optional[Task]:
        task = await self.get_task(task_id)
        if task is None:
            return None

        if task.status in ("running", "planning"):
            return task

        await self._update_task_status(task_id, "planning")

        async_task = asyncio.create_task(self._run_task(task_id, task.goal, task.workspace_dir))
        self._running[task_id] = async_task
        async_task.add_done_callback(lambda _: self._running.pop(task_id, None))

        return await self.get_task(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        async_task = self._running.pop(task_id, None)
        if async_task and not async_task.done():
            async_task.cancel()
            try:
                await async_task
            except (asyncio.CancelledError, Exception):
                pass
            await self._update_task_status(task_id, "failed")
            await self._broadcast(task_id, "task_cancelled", {"task_id": task_id, "status": "failed"})
            return True
        return False

    # ------------------------------------------------------------------
    # Internal execution pipeline
    # ------------------------------------------------------------------

    async def _run_task(self, task_id: str, goal: str, workspace_dir: str) -> None:
        try:
            Path(workspace_dir).mkdir(parents=True, exist_ok=True)

            # ---- Planning ----
            from app.agents.planner import PlannerAgent

            planner = PlannerAgent()
            plan = await planner.plan_goal(goal)

            plan_dict = {
                "raw": plan.raw,
                "steps": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "description": s.description,
                        "order_index": s.order_index,
                    }
                    for s in plan.steps
                ],
            }

            # Persist plan & steps
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(plan=plan_dict, status="running", updated_at=_utcnow())
                )
                for s in plan.steps:
                    step = Step(
                        id=s.id,
                        task_id=task_id,
                        name=s.name,
                        description=s.description,
                        status="pending",
                        order_index=s.order_index,
                    )
                    session.add(step)
                await session.commit()

            await self._broadcast(task_id, "plan_ready", {"plan": plan_dict})

            # ---- Execution ----
            from app.agents.executor import ExecutorAgent

            executor = ExecutorAgent()
            all_succeeded = True

            for step_plan in plan.steps:
                step_id = step_plan.id

                await self._update_step_status(step_id, "running", started_at=_utcnow())
                await self._broadcast(
                    task_id,
                    "step_update",
                    {"step_id": step_id, "status": "running", "name": step_plan.name},
                )

                accumulated_output: List[str] = []

                async def _cb(sid: str, chunk: str, _acc=accumulated_output, _tid=task_id) -> None:
                    _acc.append(chunk)
                    await self._broadcast(_tid, "step_output", {"step_id": sid, "chunk": chunk})

                try:
                    output = await executor.execute_step(step_plan, workspace_dir, _cb)
                    await self._update_step_status(
                        step_id,
                        "completed",
                        output=output,
                        completed_at=_utcnow(),
                    )
                    await self._broadcast(
                        task_id,
                        "step_update",
                        {"step_id": step_id, "status": "completed"},
                    )
                except Exception as exc:
                    logger.error("Step %s failed: %s", step_id, exc)
                    all_succeeded = False
                    await self._update_step_status(
                        step_id,
                        "failed",
                        error=str(exc),
                        completed_at=_utcnow(),
                    )
                    await self._broadcast(
                        task_id,
                        "step_update",
                        {"step_id": step_id, "status": "failed", "error": str(exc)},
                    )

            # ---- Collect artifacts ----
            await self._collect_artifacts(task_id, workspace_dir)

            final_status = "completed" if all_succeeded else "failed"
            await self._update_task_status(task_id, final_status)
            await self._broadcast(task_id, "task_complete", {"task_id": task_id, "status": final_status})

        except asyncio.CancelledError:
            logger.info("Task %s was cancelled.", task_id)
            raise
        except Exception as exc:
            logger.error("Task %s failed: %s", task_id, exc)
            await self._update_task_status(task_id, "failed")
            await self._broadcast(task_id, "task_error", {"task_id": task_id, "error": str(exc)})

    # ------------------------------------------------------------------
    # Artifact helpers
    # ------------------------------------------------------------------

    async def _collect_artifacts(self, task_id: str, workspace_dir: str) -> None:
        workspace = Path(workspace_dir)
        if not workspace.exists():
            return

        async with AsyncSessionLocal() as session:
            for entry in workspace.rglob("*"):
                if entry.is_file():
                    try:
                        size = entry.stat().st_size
                        artifact = Artifact(
                            id=str(uuid.uuid4()),
                            task_id=task_id,
                            name=entry.name,
                            path=str(entry),
                            type="file",
                            size=size,
                        )
                        session.add(artifact)
                    except Exception as exc:
                        logger.warning("Could not collect artifact %s: %s", entry, exc)
            await session.commit()

    # ------------------------------------------------------------------
    # DB update helpers
    # ------------------------------------------------------------------

    async def _update_task_status(self, task_id: str, status: str) -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(status=status, updated_at=_utcnow())
            )
            await session.commit()

    async def _update_step_status(
        self,
        step_id: str,
        status: str,
        output: Optional[str] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> None:
        values: Dict[str, Any] = {"status": status}
        if output is not None:
            values["output"] = output
        if error is not None:
            values["error"] = error
        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at

        async with AsyncSessionLocal() as session:
            await session.execute(update(Step).where(Step.id == step_id).values(**values))
            await session.commit()

    # ------------------------------------------------------------------
    # WebSocket broadcast
    # ------------------------------------------------------------------

    async def _broadcast(self, task_id: str, event_type: str, data: Dict[str, Any]) -> None:
        await self._manager.broadcast(task_id, {"type": event_type, "data": data})
