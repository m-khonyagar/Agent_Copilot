import asyncio
import logging
import os
from datetime import timedelta
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

_TEMPORAL_AVAILABLE = False
try:
    from temporalio import activity, workflow
    from temporalio.client import Client
    from temporalio.common import RetryPolicy
    from temporalio.worker import Worker

    _TEMPORAL_AVAILABLE = True
except ImportError:
    logger.warning("temporalio not installed – workflows will use direct execution fallback.")


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

if _TEMPORAL_AVAILABLE:
    @activity.defn
    async def generate_plan_activity(goal: str) -> Dict[str, Any]:
        from app.agents.planner import PlannerAgent

        agent = PlannerAgent()
        plan = await agent.plan_goal(goal)
        return {
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

    @activity.defn
    async def execute_step_activity(step_data: Dict[str, Any], workspace_dir: str) -> str:
        from app.agents.executor import ExecutorAgent

        class _StepProxy:
            def __init__(self, data: Dict[str, Any]):
                self.id = data["id"]
                self.name = data["name"]
                self.description = data["description"]

        async def _simple_callback(step_id: str, chunk: str) -> None:
            pass  # Temporal activities stream via heartbeats or result; keep simple here

        agent = ExecutorAgent()
        return await agent.execute_step(_StepProxy(step_data), workspace_dir, _simple_callback)

    @workflow.defn
    class TaskWorkflow:
        """Temporal workflow that plans and executes a task."""

        @workflow.run
        async def run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
            goal: str = task_data["goal"]
            workspace_dir: str = task_data["workspace_dir"]
            retry_policy = RetryPolicy(maximum_attempts=3)

            plan = await workflow.execute_activity(
                generate_plan_activity,
                goal,
                start_to_close_timeout=timedelta(seconds=120),
                retry_policy=retry_policy,
            )

            results = []
            for step in plan["steps"]:
                output = await workflow.execute_activity(
                    execute_step_activity,
                    args=[step, workspace_dir],
                    start_to_close_timeout=timedelta(seconds=300),
                    retry_policy=retry_policy,
                )
                results.append({"step_id": step["id"], "output": output})

            return {"plan": plan, "results": results}


# ---------------------------------------------------------------------------
# WorkflowRunner
# ---------------------------------------------------------------------------

class WorkflowRunner:
    """Start and manage Temporal workflows, with a fallback to direct execution."""

    TASK_QUEUE = "taskflow-queue"

    def __init__(self) -> None:
        self._client: Optional[Any] = None

    async def _get_client(self) -> Optional[Any]:
        if not _TEMPORAL_AVAILABLE:
            return None
        if self._client is not None:
            return self._client
        try:
            temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
            self._client = await Client.connect(f"{temporal_host}:7233")
            return self._client
        except Exception as exc:
            logger.warning("Cannot connect to Temporal server: %s", exc)
            return None

    async def run_task(
        self,
        task_id: str,
        goal: str,
        workspace_dir: str,
        on_plan: Optional[Callable[[Dict[str, Any]], Any]] = None,
        on_step_done: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task via Temporal if available, otherwise fall back to direct execution.

        Callbacks (both optional):
            on_plan(plan_dict)          – called once a plan is generated
            on_step_done(result_dict)   – called after each step finishes
        """
        client = await self._get_client()

        if client is not None:
            return await self._run_via_temporal(
                client, task_id, goal, workspace_dir, on_plan, on_step_done
            )
        return await self._run_direct(goal, workspace_dir, on_plan, on_step_done)

    async def _run_via_temporal(
        self,
        client: Any,
        task_id: str,
        goal: str,
        workspace_dir: str,
        on_plan: Optional[Callable],
        on_step_done: Optional[Callable],
    ) -> Dict[str, Any]:
        try:
            result = await client.execute_workflow(
                TaskWorkflow.run,
                {"goal": goal, "workspace_dir": workspace_dir},
                id=f"task-{task_id}",
                task_queue=self.TASK_QUEUE,
            )
            if on_plan and "plan" in result:
                await _maybe_await(on_plan, result["plan"])
            if on_step_done:
                for r in result.get("results", []):
                    await _maybe_await(on_step_done, r)
            return result
        except Exception as exc:
            logger.error("Temporal workflow error – falling back to direct: %s", exc)
            return await self._run_direct(goal, workspace_dir, on_plan, on_step_done)

    async def _run_direct(
        self,
        goal: str,
        workspace_dir: str,
        on_plan: Optional[Callable],
        on_step_done: Optional[Callable],
    ) -> Dict[str, Any]:
        from app.agents.executor import ExecutorAgent
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

        if on_plan:
            await _maybe_await(on_plan, plan_dict)

        executor = ExecutorAgent()
        results = []
        for step in plan.steps:
            async def _cb(sid: str, chunk: str) -> None:
                pass  # low-level chunks handled upstream via task_service

            output = await executor.execute_step(step, workspace_dir, _cb)
            result = {"step_id": step.id, "output": output}
            results.append(result)
            if on_step_done:
                await _maybe_await(on_step_done, result)

        return {"plan": plan_dict, "results": results}


async def _maybe_await(fn: Callable, *args: Any) -> None:
    result = fn(*args)
    if asyncio.iscoroutine(result):
        await result
