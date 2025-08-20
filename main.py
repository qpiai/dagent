import asyncio
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from planner import Planner
from dag import build_dag_from_plan
from kernel import WorkflowExecutor


async def main():
    """Simple test: Planner -> DAG -> Kernel execution"""
    
    # Step 1: Create plan
    print("Creating plan...")
    planner = Planner()
    query = "Analyze Tesla's Q4 2024 performance and provide an investment recommendation."
    
    from planner.prompts import AVAILABLE_AGENT_PROFILES, AVAILABLE_TOOLS
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
        print(f"  Agent: {subtask.agent_profile}")
        print(f"  Dependencies: {', '.join(deps)}")
        print(f"  Tools: {', '.join(subtask.tool_allowlist)}")
        print(f"  Task: {subtask.task_description}")
    
    # Save plan to file
    import json
    plan_data = {
        "query": query,
        "planning_rationale": plan.planning_rationale,
        "expected_final_output": plan.expected_final_output,
        "subtasks": {
            task_id: {
                "task_description": subtask.task_description,
                "agent_profile": subtask.agent_profile,
                "tool_allowlist": subtask.tool_allowlist,
                "dependencies": subtask.dependencies
            }
            for task_id, subtask in plan.subtasks.items()
        }
    }
    
    with open('generated_plan.json', 'w') as f:
        json.dump(plan_data, f, indent=2)
    print(f"\nPlan saved to: generated_plan.json")
    
    # Step 2: Convert to DAG
    print("Converting to DAG...")
    dag = build_dag_from_plan(plan)
    print(f"DAG created: {len(dag.nodes)} nodes")
    
    # Step 3: Execute workflow
    print("Executing workflow...")
    executor = WorkflowExecutor()
    results = await executor.execute(dag)
    
    # Show summary
    successful = sum(1 for r in results.values() if r.success)
    print(f"\nWorkflow completed: {successful}/{len(results)} tasks successful")
    
    # Print parameters analysis
    print_parameters_analysis(plan, dag, results)


def print_parameters_analysis(plan, dag, results):
    """Analyze and print explicit and implicit parameters from the workflow."""
    print(f"\n{'='*60}")
    print("PARAMETERS ANALYSIS")
    print(f"{'='*60}")
    
    # EXPLICIT PARAMETERS (directly specified in plan)
    print("\nEXPLICIT PARAMETERS:")
    print("-" * 30)
    
    # Agent profile distribution
    profile_counts = {}
    for subtask in plan.subtasks.values():
        profile = subtask.agent_profile
        profile_counts[profile] = profile_counts.get(profile, 0) + 1
    
    print("Agent Profile Distribution:")
    for profile, count in profile_counts.items():
        print(f"  {profile}: {count} tasks")
    
    # Tool usage distribution
    tool_usage = {}
    total_tools = 0
    for subtask in plan.subtasks.values():
        for tool in subtask.tool_allowlist:
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
            total_tools += 1
    
    print(f"\nTool Usage Distribution ({total_tools} total assignments):")
    for tool, count in sorted(tool_usage.items()):
        print(f"  {tool}: {count} tasks")
    
    # Dependency structure
    dependency_counts = {}
    for subtask in plan.subtasks.values():
        dep_count = len(subtask.dependencies)
        dependency_counts[dep_count] = dependency_counts.get(dep_count, 0) + 1
    
    print("\nDependency Pattern:")
    for dep_count, task_count in sorted(dependency_counts.items()):
        dep_type = "root" if dep_count == 0 else f"{dep_count} dependencies"
        print(f"  {task_count} tasks with {dep_type}")
    
    # IMPLICIT PARAMETERS (derived from execution)
    print(f"\nIMPLICIT PARAMETERS:")
    print("-" * 30)
    
    # Execution structure analysis
    execution_rounds = analyze_execution_rounds(dag)
    print(f"Execution Structure:")
    print(f"  Total rounds: {len(execution_rounds)}")
    print(f"  Max parallelism: {max(len(round_tasks) for round_tasks in execution_rounds)}")
    print(f"  Parallelism efficiency: {len(dag.nodes)/len(execution_rounds):.1f} tasks/round")
    
    # Performance metrics
    total_time = sum(r.execution_time for r in results.values())
    avg_time_by_profile = {}
    for result in results.values():
        profile = result.agent_profile
        if profile not in avg_time_by_profile:
            avg_time_by_profile[profile] = []
        avg_time_by_profile[profile].append(result.execution_time)
    
    print(f"\nPerformance Characteristics:")
    print(f"  Total execution time: {total_time:.2f}s")
    for profile, times in avg_time_by_profile.items():
        avg_time = sum(times) / len(times)
        print(f"  Avg {profile} agent time: {avg_time:.2f}s ({len(times)} tasks)")
    
    # Critical path analysis
    critical_path = find_critical_path(dag, results)
    critical_time = sum(results[node_id].execution_time for node_id in critical_path)
    print(f"  Critical path: {len(critical_path)} tasks, {critical_time:.2f}s")
    print(f"  Critical path: {' → '.join(critical_path)}")
    
    # Resource utilization patterns
    print(f"\nResource Utilization Patterns:")
    
    # Tools per agent complexity
    tools_by_profile = {}
    for subtask in plan.subtasks.values():
        profile = subtask.agent_profile
        tool_count = len(subtask.tool_allowlist)
        if profile not in tools_by_profile:
            tools_by_profile[profile] = []
        tools_by_profile[profile].append(tool_count)
    
    for profile, tool_counts in tools_by_profile.items():
        avg_tools = sum(tool_counts) / len(tool_counts)
        print(f"  {profile} agents: avg {avg_tools:.1f} tools/task")
    
    # Workflow complexity indicators
    print(f"\nWorkflow Complexity Indicators:")
    print(f"  Task specialization: {len(set(tuple(sorted(s.tool_allowlist)) for s in plan.subtasks.values()))} unique tool combinations")
    print(f"  Dependency depth: {len(execution_rounds)} levels")
    print(f"  Profile diversity: {len(profile_counts)} different agent types")
    
    # Optimization potential metrics
    print(f"\nOptimization Potential:")
    sequential_time = sum(r.execution_time for r in results.values())
    parallel_time = max(sum(results[node_id].execution_time for node_id in round_tasks) 
                       for round_tasks in execution_rounds)
    speedup = sequential_time / parallel_time if parallel_time > 0 else 1
    print(f"  Theoretical speedup: {speedup:.2f}x (parallel vs sequential)")
    print(f"  Parallelization efficiency: {(speedup / len(dag.nodes)) * 100:.1f}%")


def analyze_execution_rounds(dag):
    """Simulate execution rounds to understand parallelism."""
    rounds = []
    completed = set()
    
    while len(completed) < len(dag.nodes):
        ready_nodes = dag.get_ready_nodes(completed)
        if not ready_nodes:
            break
        
        round_tasks = [node.id for node in ready_nodes]
        rounds.append(round_tasks)
        
        for node in ready_nodes:
            completed.add(node.id)
    
    return rounds


def find_critical_path(dag, results):
    """Find the critical path (longest time path) through the DAG."""
    # Simple implementation: find path with maximum total time
    def get_max_path_from_node(node_id, visited):
        if node_id in visited:
            return [], 0
        
        visited.add(node_id)
        node_time = results[node_id].execution_time
        
        # Find all nodes that depend on this one
        dependents = []
        for other_node in dag.nodes.values():
            if node_id in other_node.dependencies:
                dependents.append(other_node.id)
        
        if not dependents:
            visited.remove(node_id)
            return [node_id], node_time
        
        max_path = []
        max_time = 0
        
        for dependent in dependents:
            path, time = get_max_path_from_node(dependent, visited.copy())
            total_time = node_time + time
            if total_time > max_time:
                max_time = total_time
                max_path = [node_id] + path
        
        visited.remove(node_id)
        return max_path, max_time
    
    # Find root nodes and calculate paths from each
    root_nodes = [node.id for node in dag.nodes.values() if not node.dependencies]
    
    best_path = []
    best_time = 0
    
    for root in root_nodes:
        path, time = get_max_path_from_node(root, set())
        if time > best_time:
            best_time = time
            best_path = path
    
    return best_path


if __name__ == "__main__":
    asyncio.run(main())