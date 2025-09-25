"""
Simple framework entry point for Agentic DAG execution.
Wraps the existing main.py logic in a clean API.
"""

from typing import Dict, Any
from pathlib import Path
import sys
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from planner import Planner
from dag import build_dag_from_plan
from kernel import WorkflowExecutor
from planner.prompts import AVAILABLE_AGENT_PROFILES, AVAILABLE_TOOLS


class AgenticDAG:
    """
    Main framework class for executing agentic DAG workflows.

    Usage:
        framework = AgenticDAG()
        result = await framework.execute("Create a Python hello world script")
    """

    def __init__(self):
        """Initialize the Agentic DAG framework."""
        self.planner = Planner()
        self.executor = WorkflowExecutor()

    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute a query using the agentic DAG framework.

        Args:
            query: The user query to execute

        Returns:
            Dict with execution results and metadata
        """
        try:
            print("Creating plan...")
            plan = await self.planner.create_plan(query, AVAILABLE_AGENT_PROFILES, AVAILABLE_TOOLS)
            print(f"Plan created: {len(plan.subtasks)} subtasks")

            # Save plan to file
            self._save_plan(query, plan)

            print("Converting to DAG and generating profiles...")
            dag = await build_dag_from_plan(plan)
            print(f"DAG created: {len(dag.nodes)} nodes with pre-generated profiles")

            print("Executing workflow...")
            results = await self.executor.execute(dag)

            # Show summary
            successful = sum(1 for r in results.values() if r.success)
            print(f"Workflow completed: {successful}/{len(results)} tasks successful")

            return {
                "success": successful == len(results),
                "query": query,
                "plan": plan,
                "dag": dag,
                "execution_results": results,
                "summary": {
                    "total_tasks": len(results),
                    "successful_tasks": successful,
                    "failed_tasks": len(results) - successful,
                }
            }

        except Exception as e:
            print(f"Error during execution: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def _save_plan(self, query: str, plan) -> None:
        """Save the generated plan to file for debugging."""
        def serialize_subtask(subtask):
            data = {
                "task_description": subtask.task_description,
                "dependencies": subtask.dependencies
            }

            if hasattr(subtask, 'node_type') and subtask.node_type == "AGENT_TEAM":
                data["node_type"] = "AGENT_TEAM"
                data["team_config"] = subtask.team_config
            else:
                data["node_type"] = "SINGLE_AGENT"
                data["agent_profile"] = {
                    "task_type": subtask.agent_profile.task_type,
                    "complexity": subtask.agent_profile.complexity,
                    "output_format": subtask.agent_profile.output_format,
                    "reasoning_style": subtask.agent_profile.reasoning_style
                }
                data["tool_allowlist"] = subtask.tool_allowlist or []

            return data

        plan_data = {
            "query": query,
            "planning_rationale": plan.planning_rationale,
            "expected_final_output": plan.expected_final_output,
            "subtasks": {
                task_id: serialize_subtask(subtask)
                for task_id, subtask in plan.subtasks.items()
            }
        }

        with open('generated_plan.json', 'w') as f:
            json.dump(plan_data, f, indent=2)
        print("Plan saved to: generated_plan.json")


# Convenience function for simple usage
async def execute_query(query: str) -> Dict[str, Any]:
    """
    Simple function to execute a query with default settings.

    Usage:
        result = await execute_query("Create a hello world Python script")
    """
    framework = AgenticDAG()
    return await framework.execute(query)