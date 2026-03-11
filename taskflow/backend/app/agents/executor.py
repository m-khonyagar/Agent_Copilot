import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)

_INTERPRETER_AVAILABLE = False
try:
    from interpreter import interpreter as _base_interpreter  # open-interpreter

    _INTERPRETER_AVAILABLE = True
except ImportError:
    logger.warning("open-interpreter not installed – executor will simulate step output.")


class ExecutorAgent:
    """Executes a single plan step using Open Interpreter."""

    def __init__(self) -> None:
        if _INTERPRETER_AVAILABLE:
            _base_interpreter.auto_run = True
            _base_interpreter.verbose = False

    async def execute_step(
        self,
        step: Any,
        workspace_dir: str,
        update_callback: Callable[[str, str], Awaitable[None]],
    ) -> str:
        """
        Execute *step* inside *workspace_dir* and stream chunks via *update_callback*.

        Parameters
        ----------
        step:
            An object with attributes ``id`` (str), ``name`` (str), and
            ``description`` (str).
        workspace_dir:
            Absolute path to the task's workspace directory.
        update_callback:
            Async coroutine called with (step_id, output_chunk) for each chunk
            produced by the interpreter.

        Returns
        -------
        str
            Full accumulated output of the step.
        """
        if not _INTERPRETER_AVAILABLE:
            return await self._simulate_step(step, update_callback)

        try:
            return await self._run_with_interpreter(step, workspace_dir, update_callback)
        except Exception as exc:
            logger.error("Executor error for step %s: %s", step.id, exc)
            error_msg = f"Error executing step: {exc}"
            await update_callback(step.id, error_msg)
            return error_msg

    async def _run_with_interpreter(
        self,
        step: Any,
        workspace_dir: str,
        update_callback: Callable[[str, str], Awaitable[None]],
    ) -> str:
        prompt = (
            f"Working directory: {workspace_dir}\n\n"
            f"Task: {step.name}\n\n"
            f"Description: {step.description}\n\n"
            "Complete this task step. Be concise."
        )

        accumulated = []

        def _blocking_stream():
            chunks = []
            for chunk in _base_interpreter.chat(prompt, stream=True, display=False):
                content = ""
                if isinstance(chunk, dict):
                    content = chunk.get("content") or chunk.get("output") or ""
                elif isinstance(chunk, str):
                    content = chunk
                if content:
                    chunks.append(str(content))
            return chunks

        loop = asyncio.get_event_loop()
        chunks = await loop.run_in_executor(None, _blocking_stream)

        for chunk in chunks:
            accumulated.append(chunk)
            await update_callback(step.id, chunk)

        return "".join(accumulated)

    @staticmethod
    async def _simulate_step(
        step: Any,
        update_callback: Callable[[str, str], Awaitable[None]],
    ) -> str:
        """Provide simulated output when open-interpreter is unavailable."""
        simulated_lines = [
            f"[simulated] Starting step: {step.name}",
            f"[simulated] {step.description}",
            "[simulated] Step completed successfully.",
        ]
        for line in simulated_lines:
            await update_callback(step.id, line + "\n")
            await asyncio.sleep(0.05)
        return "\n".join(simulated_lines)
