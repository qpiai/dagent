"""Judge agent for evaluating task output quality in actor-critic architecture."""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from .prompts import JUDGE_SYSTEM_PROMPT

# Import centralized tracing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_model
from planner.planner import GOOGLE_API_KEY
from tracing import langfuse, observe

logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")


@dataclass
class JudgeEvaluation:
    """Result of judge evaluation with detailed feedback."""
    is_accepted: bool
    feedback: str
    specific_issues: Optional[str] = None


class Judge:
    """
    Judge agent that evaluates the quality of task outputs.
    Used in actor-critic pattern to determine if work is satisfactory.
    """

    def __init__(self):
        self._agent = None

    @property
    def agent(self):
        if self._agent is None:
            self._agent = Agent(
                model=get_model(),
                description=JUDGE_SYSTEM_PROMPT,
                markdown=False,
                debug_mode=False
            )
        return self._agent

    @observe()
    async def evaluate(self, task_description: str, output: str) -> bool:
        """
        Evaluate if the agent output satisfactorily completes the task.
        Backward compatibility method - returns only boolean.

        Args:
            task_description: The original task that was assigned
            output: The agent's output to evaluate

        Returns:
            True if output is acceptable, False if it needs retry
        """
        evaluation = await self.evaluate_with_feedback(task_description, output)
        return evaluation.is_accepted

    @observe()
    async def evaluate_with_feedback(self, task_description: str, output: str) -> JudgeEvaluation:
        """
        Evaluate with detailed feedback for retry improvement.

        Args:
            task_description: The original task that was assigned
            output: The agent's output to evaluate

        Returns:
            JudgeEvaluation with decision and detailed feedback
        """
        prompt = f"""Task: {task_description}

Agent Output:
{output}

Evaluate this output quality using the specified format."""

        try:
            response = await self.agent.arun(prompt)
            result_content = response.content if hasattr(response, 'content') else str(response)

            # Parse the structured response
            is_accepted = "DECISION: ACCEPT" in result_content.upper()

            # Extract feedback
            feedback = ""
            improvement_suggestions = ""

            lines = result_content.split('\n')
            for line in lines:
                if line.upper().startswith('FEEDBACK:'):
                    feedback = line.split(':', 1)[1].strip()
                elif line.upper().startswith('IMPROVEMENT_SUGGESTIONS:'):
                    improvement_suggestions = line.split(':', 1)[1].strip()

            # Fallback extraction if structured format not followed
            if not feedback:
                feedback = result_content[:200] + "..." if len(result_content) > 200 else result_content

            langfuse.update_current_trace(
                name="judge_evaluation_with_feedback",
                input=f"Task: {task_description[:100]}...\nOutput: {output[:100]}...",
                output=result_content,
                tags=["judge", "evaluation", "feedback"]
            )

            logger.info(f"Judge evaluation: {'ACCEPTED' if is_accepted else 'REJECTED'}")

            return JudgeEvaluation(
                is_accepted=is_accepted,
                feedback=feedback,
                specific_issues=improvement_suggestions if improvement_suggestions else None
            )

        except Exception as e:
            logger.error(f"Judge evaluation failed: {e}")
            # If judge fails, accept the output (graceful degradation)
            return JudgeEvaluation(
                is_accepted=True,
                feedback="Judge evaluation failed - accepting output",
                specific_issues=None
            )