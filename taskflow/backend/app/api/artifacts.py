import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.models.database import Artifact, AsyncSessionLocal, Task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ArtifactOut(BaseModel):
    id: str
    task_id: str
    name: str
    path: str
    type: str
    size: Optional[int]
    created_at: Any

    class Config:
        from_attributes = True


class FileNode(BaseModel):
    name: str
    path: str
    type: str  # "file" | "directory"
    size: Optional[int] = None
    children: Optional[List["FileNode"]] = None


FileNode.model_rebuild()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/{task_id}", response_model=List[ArtifactOut])
async def list_artifacts(task_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Artifact).where(Artifact.task_id == task_id).order_by(Artifact.created_at)
        )
        artifacts = result.scalars().all()
    return [ArtifactOut.model_validate(a) for a in artifacts]


@router.get("/{task_id}/{artifact_id}/download")
async def download_artifact(task_id: str, artifact_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Artifact).where(
                Artifact.id == artifact_id, Artifact.task_id == task_id
            )
        )
        artifact = result.scalar_one_or_none()

    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = Path(artifact.path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=artifact.name,
        media_type="application/octet-stream",
    )


@router.get("/{task_id}/browse", response_model=List[FileNode])
async def browse_workspace(task_id: str):
    """Return a recursive file-tree of the task's workspace directory."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    workspace = Path(task.workspace_dir) if task.workspace_dir else None
    if workspace is None or not workspace.exists():
        return []

    return _build_tree(workspace)


def _build_tree(path: Path) -> List[FileNode]:
    nodes: List[FileNode] = []
    try:
        for entry in sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name)):
            if entry.is_dir():
                nodes.append(
                    FileNode(
                        name=entry.name,
                        path=str(entry),
                        type="directory",
                        children=_build_tree(entry),
                    )
                )
            elif entry.is_file():
                try:
                    size = entry.stat().st_size
                except OSError:
                    size = None
                nodes.append(
                    FileNode(name=entry.name, path=str(entry), type="file", size=size)
                )
    except PermissionError as exc:
        logger.warning("Cannot read directory %s: %s", path, exc)
    return nodes
