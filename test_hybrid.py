"""
Test script for hybrid single agent vs team implementation
"""
import asyncio
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dag.dag import build_dag_from_plan
from kernel.kernel import WorkflowExecutor

async def test_hybrid_execution():
    """Test the hybrid agent/team execution"""

    # Load our test plan
    with open('test_hybrid.json', 'r') as f:
        plan_data = json.load(f)

    print("=" * 60)
    print("TESTING HYBRID SINGLE AGENT + TEAM IMPLEMENTATION")
    print("=" * 60)

    print(f"\nTest Plan: {plan_data['query']}")
    print(f"Expected Output: {plan_data['expected_final_output']}")

    # Build DAG from plan
    print(f"\nBuilding DAG from hybrid plan...")
    dag = await build_dag_from_plan(plan_data)

    # Show DAG structure
    print(f"\nDAG Structure:")
    for node_id, node in dag.nodes.items():
        if node.node_type == "AGENT_TEAM":
            team_agents = len(node.team_config["agents"])
            pattern = node.team_config.get("collaboration_pattern", "collaborate")
            print(f"  • {node_id} (TEAM: {team_agents} agents, {pattern} mode)")
        else:
            profile = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
            tools = ', '.join(node.tool_allowlist)
            print(f"  • {node_id} (SINGLE: {profile}, tools: {tools})")

        if node.dependencies:
            print(f"    └─ Dependencies: {', '.join(node.dependencies)}")

    # Execute workflow
    print(f"\nExecuting hybrid workflow...")
    executor = WorkflowExecutor()
    results = await executor.execute(dag)

    # Show results
    print(f"\nExecution Results:")
    for node_id, result in results.items():
        status = "✓" if result.success else "✗"
        print(f"  {status} {node_id}: {result.execution_time:.2f}s ({result.agent_profile})")
        if result.error:
            print(f"    Error: {result.error}")

    print(f"\nFinal Result:")
    final_node = "team_analysis_recommendation"
    if final_node in results and results[final_node].success:
        final_output = results[final_node].result
        print(f"Team Output Preview: {final_output[:200]}...")

    print(f"\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_hybrid_execution())