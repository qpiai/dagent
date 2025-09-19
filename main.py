import asyncio
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from planner import Planner
from dag import build_dag_from_plan
from kernel import WorkflowExecutor
from planner.prompts import AVAILABLE_AGENT_PROFILES, AVAILABLE_TOOLS


async def main():
    """Simple test: Planner -> DAG -> Kernel execution"""

    try:
        # Step 1: Create plan
        print("Creating plan...")
        planner = Planner()
        query = """test workflow to test teams, create team nodes"""


        plan = await planner.create_plan(query, AVAILABLE_AGENT_PROFILES, AVAILABLE_TOOLS)
        print(f"Plan created: {len(plan.subtasks)} subtasks")

        # Print and save plan for debugging
        print("\n" + "="*60)
        print("GENERATED PLAN")
        print("="*60)
        print(f"Query: {query}")
        print(f"\nRationale:\n{plan.planning_rationale}")
        print(f"\nExpected Output:\n{plan.expected_final_output}")

        print(f"\nSubtasks ({len(plan.subtasks)}):")
        for task_id, subtask in plan.subtasks.items():
            deps = subtask.dependencies if subtask.dependencies else ["None"]
            print(f"\n{task_id}:")
            if hasattr(subtask, 'node_type') and subtask.node_type == "AGENT_TEAM":
                print(f"  Type: AGENT_TEAM")
                print(f"  Team: {len(subtask.team_config.get('agents', []))} agents")
                print(f"  Pattern: {subtask.team_config.get('collaboration_pattern', 'collaborate')}")
            else:
                print(f"  Type: SINGLE_AGENT")
                print(f"  Agent: {subtask.agent_profile}")
                tools = subtask.tool_allowlist if subtask.tool_allowlist else []
                print(f"  Tools: {', '.join(tools)}")
            print(f"  Dependencies: {', '.join(deps)}")
            print(f"  Task: {subtask.task_description}")

        # Save plan to file
        import json

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
        print(f"\nPlan saved to: generated_plan.json")

        # Step 2: Convert to DAG with profile generation
        print("Converting to DAG and generating profiles...")
        dag = await build_dag_from_plan(plan)
        print(f"DAG created: {len(dag.nodes)} nodes with pre-generated profiles")

        # Step 3: Execute workflow
        print("Executing workflow...")
        executor = WorkflowExecutor()
        results = await executor.execute(dag)

        # Show summary
        successful = sum(1 for r in results.values() if r.success)
        print(f"\nWorkflow completed: {successful}/{len(results)} tasks successful")

    except Exception as e:
        print(f"Error during execution: {e}")
        raise
    finally:
        # Clean up any open connections - aiohttp requires this for graceful shutdown
        await asyncio.sleep(0.25)  # Give time for SSL and HTTP connections to close pr


if __name__ == "__main__":
    asyncio.run(main())