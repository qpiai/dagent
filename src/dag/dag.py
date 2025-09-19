from typing import Dict, List, Set, Optional, Literal
from dataclasses import dataclass, field
import asyncio


@dataclass
class DAGNode:
    """Represents a single node in the execution DAG."""
    id: str
    task_description: str
    node_type: Literal["SINGLE_AGENT", "AGENT_TEAM"] = "SINGLE_AGENT"

    # Single agent fields
    agent_profile: Optional[str] = None
    generated_system_prompt: Optional[str] = None
    tool_allowlist: Optional[List[str]] = None

    # Team fields
    team_config: Optional[Dict] = None

    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 2
    needs_validation: bool = True

    def __post_init__(self):
        # Ensure all dependencies are strings for consistency
        self.dependencies = [str(dep) for dep in self.dependencies]


class DAG:
    """Directed Acyclic Graph for task execution planning."""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
    
    def add_node(self, node: DAGNode) -> None:
        """Add a node to the DAG."""
        self.nodes[node.id] = node
    
    def get_ready_nodes(self, completed: Set[str]) -> List[DAGNode]:
        """
        Get nodes that are ready to execute (all dependencies completed).
        
        Args:
            completed: Set of completed node IDs
            
        Returns:
            List of nodes ready for execution
        """
        ready = []
        for node in self.nodes.values():
            if node.id not in completed:
                if all(dep in completed for dep in node.dependencies):
                    ready.append(node)
        return ready
    
    def is_complete(self, completed: Set[str]) -> bool:
        """Check if all nodes in the DAG have been completed."""
        return len(completed) == len(self.nodes)

    def get_final_nodes(self) -> Set[str]:
        """Get nodes that have no dependents (leaf nodes)."""
        has_dependents = set()
        for node in self.nodes.values():
            has_dependents.update(node.dependencies)
        return set(self.nodes.keys()) - has_dependents
      
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the DAG for structural integrity.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for missing dependencies
        all_node_ids = set(self.nodes.keys())
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep not in all_node_ids:
                    errors.append(f"Node '{node.id}' has missing dependency '{dep}'")
        
        # Check for cycles using DFS
        if self._has_cycle():
            errors.append("DAG contains circular dependencies")
        
        return len(errors) == 0, errors
    
    def _has_cycle(self) -> bool:
        """Check for cycles in the DAG using DFS."""
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node_id: WHITE for node_id in self.nodes}
        
        def dfs(node_id: str) -> bool:
            if colors[node_id] == GRAY:  # Back edge found
                return True
            if colors[node_id] == BLACK:  # Already processed
                return False
            
            colors[node_id] = GRAY
            
            # Visit dependencies
            for dep in self.nodes[node_id].dependencies:
                if dep in colors and dfs(dep):
                    return True
            
            colors[node_id] = BLACK
            return False
        
        for node_id in self.nodes:
            if colors[node_id] == WHITE:
                if dfs(node_id):
                    return True
        return False


def _extract_node_data(subtask_data):
    """Extract data consistently from dict or SubtaskNode object"""
    if hasattr(subtask_data, 'task_description'):
        # SubtaskNode object
        return {
            'task_description': subtask_data.task_description,
            'node_type': getattr(subtask_data, 'node_type', 'SINGLE_AGENT'),
            'agent_profile': subtask_data.agent_profile,
            'tool_allowlist': subtask_data.tool_allowlist,
            'team_config': getattr(subtask_data, 'team_config', None),
            'dependencies': subtask_data.dependencies or []
        }
    else:
        # Dict format - ensure defaults
        return {
            'task_description': subtask_data['task_description'],
            'node_type': subtask_data.get('node_type', 'SINGLE_AGENT'),
            'agent_profile': subtask_data.get('agent_profile'),
            'tool_allowlist': subtask_data.get('tool_allowlist'),
            'team_config': subtask_data.get('team_config'),
            'dependencies': subtask_data.get('dependencies', [])
        }


async def build_dag_from_plan(plan) -> DAG:
    """
    Build a DAG from planner output (Plan object or dict) with parallel profile generation.

    Args:
        plan: Plan object from planner or dict with 'subtasks' key

    Returns:
        DAG object ready for execution with pre-generated system prompts
    """
    dag = DAG()

    # Handle both Plan object and dict formats
    if hasattr(plan, 'subtasks'):
        subtasks = plan.subtasks
    elif isinstance(plan, dict) and 'subtasks' in plan:
        subtasks = plan['subtasks']
    else:
        raise ValueError("Invalid plan format: missing 'subtasks'")

    # Initialize profile generator
    from kernel.profiles import ProfileGenerator
    profile_generator = ProfileGenerator()

    # Generate profiles for single agent nodes only
    profile_tasks = {}
    for task_id, subtask_data in subtasks.items():
        data = _extract_node_data(subtask_data)

        if data['node_type'] == 'SINGLE_AGENT':
            profile_tasks[task_id] = profile_generator.generate_profile(
                data['agent_profile'],
                data['task_description'],
                data['tool_allowlist'],
                data['dependencies']
            )

    # Wait for all profiles to be generated (only for single agent nodes)
    if profile_tasks:
        profile_results = await asyncio.gather(*profile_tasks.values())
        generated_profiles = dict(zip(profile_tasks.keys(), profile_results))
    else:
        generated_profiles = {}

    # Create DAG nodes with generated profiles
    for task_id, subtask_data in subtasks.items():
        data = _extract_node_data(subtask_data)

        if data['node_type'] == 'AGENT_TEAM':
            # Team node
            node = DAGNode(
                id=task_id,
                task_description=data['task_description'],
                node_type="AGENT_TEAM",
                team_config=data['team_config'],
                dependencies=data['dependencies']
            )
        else:
            # Single agent node
            node = DAGNode(
                id=task_id,
                task_description=data['task_description'],
                node_type="SINGLE_AGENT",
                agent_profile=data['agent_profile'],
                generated_system_prompt=generated_profiles[task_id],
                tool_allowlist=data['tool_allowlist'],
                dependencies=data['dependencies']
            )
        dag.add_node(node)

    # Validate the constructed DAG
    is_valid, errors = dag.validate()
    if not is_valid:
        raise ValueError(f"Invalid DAG structure: {'; '.join(errors)}")

    return dag