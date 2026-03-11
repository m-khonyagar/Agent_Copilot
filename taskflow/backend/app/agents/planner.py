import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class StepPlan:
    id: str
    name: str
    description: str
    order_index: int


@dataclass
class Plan:
    steps: List[StepPlan]
    raw: Optional[str] = None


def _mock_plan(goal: str) -> Plan:
    """Return a simple two-step mock plan when no API key is configured."""
    return Plan(
        steps=[
            StepPlan(
                id=str(uuid.uuid4()),
                name="Analyse goal",
                description=f"Break down the goal and identify requirements: {goal}",
                order_index=0,
            ),
            StepPlan(
                id=str(uuid.uuid4()),
                name="Execute goal",
                description=f"Carry out the necessary actions to achieve: {goal}",
                order_index=1,
            ),
        ],
        raw="[mock plan – no OPENAI_API_KEY set]",
    )


class PlannerAgent:
    """Wraps an AutoGen AssistantAgent to produce structured execution plans."""

    SYSTEM_PROMPT = (
        "You are a task planning assistant. Given a goal, break it down into a list of "
        "clear, concrete, sequential steps. Respond ONLY with a JSON array of objects, "
        "each with keys: 'name' (string) and 'description' (string). "
        "Example: [{\"name\": \"Step 1\", \"description\": \"...\"}]"
    )

    def __init__(self) -> None:
        self._api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self._agent = None
        if self._api_key:
            self._init_agent()

    def _init_agent(self) -> None:
        try:
            import autogen  # pyautogen

            llm_config = {
                "config_list": [
                    {
                        "model": "gpt-4o-mini",
                        "api_key": self._api_key,
                    }
                ]
            }
            self._agent = autogen.AssistantAgent(
                name="planner",
                system_message=self.SYSTEM_PROMPT,
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
            )
        except ImportError:
            logger.warning("pyautogen not installed – planner will use mock plans.")
        except Exception as exc:
            logger.error("Failed to initialise AutoGen planner: %s", exc)

    async def plan_goal(self, goal: str) -> Plan:
        if self._agent is None:
            logger.info("No planner agent available; returning mock plan.")
            return _mock_plan(goal)

        try:
            import asyncio

            # AutoGen's reply mechanism is synchronous; run in thread pool.
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(None, self._call_agent, goal)
            steps = self._parse_steps(response_text)
            return Plan(steps=steps, raw=response_text)
        except Exception as exc:
            logger.error("Planner error – falling back to mock plan: %s", exc)
            return _mock_plan(goal)

    def _call_agent(self, goal: str) -> str:
        """Synchronous AutoGen call executed in a thread pool."""
        import autogen

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
        user_proxy.initiate_chat(self._agent, message=goal, silent=True)
        messages = self._agent.chat_messages.get(user_proxy, [])
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                return msg.get("content", "")
        return "[]"

    @staticmethod
    def _parse_steps(text: str) -> List[StepPlan]:
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array found in response.")
            raw_steps = json.loads(text[start:end])
            return [
                StepPlan(
                    id=str(uuid.uuid4()),
                    name=s.get("name", f"Step {i + 1}"),
                    description=s.get("description", ""),
                    order_index=i,
                )
                for i, s in enumerate(raw_steps)
            ]
        except Exception as exc:
            logger.error("Failed to parse planner response: %s", exc)
            return [
                StepPlan(
                    id=str(uuid.uuid4()),
                    name="Execute goal",
                    description=text or "No description available.",
                    order_index=0,
                )
            ]
