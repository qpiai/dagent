"""Kernel agent for orchestrating DAG execution with real Agno agents."""

import asyncio
import logging
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import time

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

from dag import DAG, DAGNode
from tools import YFinanceTools, WebSearchTools
from .profiles import ProfileGenerator

# Import centralized tracing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tracing import langfuse, observe

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a single DAG node."""
    node_id: str
    result: str
    execution_time: float
    agent_profile: str
    tools_used: List[str]
    success: bool
    error: str = None


class KernelAgent:
    """
    Kernel that creates real Agno agents for each DAG node and orchestrates execution.
    """
    
    def __init__(self):
        self.node_agents: Dict[str, Agent] = {}
        self.profile_generator = ProfileGenerator()
        self.tool_registry = self._create_tool_registry()
        
    def _create_tool_registry(self) -> Dict[str, Any]:
        """Create registry of available tool classes."""
        return {
            'YFinanceTools': YFinanceTools,
            'WebSearchTools': WebSearchTools
        }
    
    async def execute_workflow(self, dag: DAG) -> Dict[str, ExecutionResult]:
        """
        Main workflow execution:
        1. Create real Agno agents for each DAG node
        2. Execute DAG with dependency management
        """
        print(f"\n{'='*60}")
        print("KERNEL AGENT: Starting Workflow Execution")
        print(f"{'='*60}")
        
        # Step 1: Create all agents
        await self._create_node_agents(dag)
        
        # Step 2: Execute DAG
        print(f"\n{'='*60}")
        print("KERNEL AGENT: Executing DAG")
        print(f"{'='*60}")
        
        results = await self._execute_dag_with_display(dag)
        
        print(f"\n{'='*60}")
        print("KERNEL AGENT: Workflow Completed")
        print(f"{'='*60}")
        
        return results
    
    async def _create_node_agents(self, dag: DAG):
        """Create real Agno agents for each DAG node."""
        print("\nKERNEL: Creating Real Agno Agents")
        print("-" * 40)
        
        print(f"Creating {len(dag.nodes)} Agno agents (one per subtask)...")
        
        # Create agents in parallel
        creation_tasks = []
        for node in dag.nodes.values():
            task = self._create_single_node_agent(node)
            creation_tasks.append(task)
        
        start_time = time.time()
        
        await asyncio.gather(*creation_tasks)
        
        creation_time = time.time() - start_time
        print(f"All {len(dag.nodes)} Agno agents created in {creation_time:.2f}s")
        
        # Show created agents
        print("\nCreated Agno Agents:")
        for node_id, agent in self.node_agents.items():
            tools_str = ', '.join([tool.__class__.__name__ for tool in agent.tools]) if agent.tools else "No tools"
            print(f"  • {node_id} ({getattr(agent, '_profile_type', 'unknown')}): [{tools_str}]")
    
    async def _create_single_node_agent(self, node: DAGNode) -> Agent:
        """Create a real Agno agent for a specific node."""
        # Simulate realistic agent creation time
        await asyncio.sleep(0.1)

        try:
            # Use pre-generated profile from DAG node
            profile = node.generated_system_prompt
            
            # Create tool instances for this agent
            tools = []
            for tool_name in node.tool_allowlist:
                if tool_name in self.tool_registry:
                    tool_class = self.tool_registry[tool_name]
                    tool_instance = tool_class()
                    tools.append(tool_instance)
                else:
                    logger.warning(f"Tool {tool_name} not found in registry")
            
            # Map complexity levels to model configurations
            model_configs = {
                "QUICK": {"temperature": 0.3, "max_tokens": 2000},
                "THOROUGH": {"temperature": 0.1, "max_tokens": 4000},
                "DEEP": {"temperature": 0.2, "max_tokens": 6000}
            }

            config = model_configs.get(node.agent_profile.complexity, model_configs["THOROUGH"])
            
            # Create the real Agno agent
            # agent = Agent(
            #     model=OpenAIChat(
            #         id="gpt-4o",
            #         temperature=config["temperature"],
            #         max_tokens=config["max_tokens"],
            #         top_p=0.9
            #     ),
            #     tools=tools,
            #     description=profile,
            #     markdown=False,
            #     debug_mode=False,
            #     add_datetime_to_instructions=True,
            #     show_tool_calls=False
            # )

            agent = Agent(
                model=Gemini(
                    id="gemini-2.5-flash"
                ),
                tools=tools,
                description=profile,
                markdown=False,
                debug_mode=False,
                add_datetime_to_instructions=True,
                show_tool_calls=False
            )
            
            # Store profile type for display purposes
            profile_display = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
            agent._profile_type = profile_display
            agent._node_id = node.id
            
            self.node_agents[node.id] = agent
            
            print(f"  Created Agno agent: {node.id}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent for {node.id}: {e}")
            raise e
    
    async def _execute_dag_with_display(self, dag: DAG) -> Dict[str, ExecutionResult]:
        """Execute DAG with real Agno agents."""
        completed = {}
        round_num = 1
        
        while len(completed) < len(dag.nodes):
            # Get ready nodes
            ready_nodes = dag.get_ready_nodes(set(completed.keys()))
            
            if not ready_nodes:
                raise ValueError("No ready nodes - circular dependency detected")
            
            print(f"\nROUND {round_num}: Executing {len(ready_nodes)} tasks in parallel")
            print("-" * 50)
            
            # Show what's executing
            for node in ready_nodes:
                deps = node.dependencies if node.dependencies else ["START"]
                tools_str = ', '.join(node.tool_allowlist)
                profile_str = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
                print(f"  Starting: {node.id} ({profile_str}) [Tools: {tools_str}]")
                if node.dependencies:
                    print(f"    Dependencies: {', '.join(deps)}")
            
            # Execute all ready nodes in parallel
            tasks = []
            for node in ready_nodes:
                task = self._execute_node_with_display(node, completed)
                tasks.append(task)
            
            # Wait for all tasks in this round
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results and show completion
            print(f"\nROUND {round_num} RESULTS:")
            for result in results:
                if isinstance(result, Exception):
                    print(f"  ✗ Task failed with exception: {result}")
                    continue
                    
                completed[result.node_id] = result
                status = "✓" if result.success else "✗"
                print(f"  {status} {result.node_id}: {result.execution_time:.2f}s")
            
            round_num += 1
        
        return completed
    
    @observe()
    async def _execute_node_with_display(self, node: DAGNode, completed: Dict[str, ExecutionResult]) -> ExecutionResult:
        """Execute a single node with its real Agno agent."""
        start_time = time.time()

        try:
            # Build context from dependencies
            context = self._build_context_for_node(node, completed)

            # Get the real Agno agent for this node
            agent = self.node_agents[node.id]

            # Create the prompt with context and task
            prompt_parts = []

            if context:
                prompt_parts.append("Context from previous tasks:")
                prompt_parts.append(context)
                prompt_parts.append("")

            prompt_parts.append(f"Task: {node.task_description}")

            full_prompt = "\n".join(prompt_parts)

            # Execute with the real Agno agent (OpenLIT will auto-trace this)
            logger.info(f"Executing agent {node.id} with {len(agent.tools)} tools")
            response = await agent.arun(full_prompt)

            # Extract result content
            result_content = response.content if hasattr(response, 'content') else str(response)

            langfuse.update_current_trace(
                name=node.id,
                input=full_prompt,
                output=result_content,
                tags=["agent", node.agent_profile.task_type]
            )
            
            execution_time = time.time() - start_time
            
            # Show detailed execution info
            print(f"\n--- EXECUTING: {node.id} ---")
            if node.dependencies:
                print("Input Context:")
                for dep_id in node.dependencies:
                    if dep_id in completed:
                        dep_result = completed[dep_id]
                        preview = dep_result.result[:100] + "..." if len(dep_result.result) > 100 else dep_result.result
                        print(f"  ├─ {dep_id}: {preview}")
            else:
                print("Input Context: None (root task)")
            
            profile_str = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
            print(f"Agent: {node.id} ({profile_str})")
            print(f"Tools: {', '.join(node.tool_allowlist)}")
            print("Output:")
            # Show full output
            output_preview = result_content
            for line in output_preview.split('\n'):
                print(f"  {line}")
            print(f"Execution time: {execution_time:.2f}s")
            print("-" * 50)
            
            return ExecutionResult(
                node_id=node.id,
                result=result_content,
                execution_time=execution_time,
                agent_profile=profile_str,
                tools_used=node.tool_allowlist,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Task {node.id} failed: {str(e)}")
            print(f"ERROR in {node.id}: {str(e)}")
            
            profile_str = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
            return ExecutionResult(
                node_id=node.id,
                result="",
                execution_time=execution_time,
                agent_profile=profile_str,
                tools_used=node.tool_allowlist,
                success=False,
                error=str(e)
            )
    
    def _build_context_for_node(self, node: DAGNode, completed: Dict[str, ExecutionResult]) -> str:
        """Build context from dependency outputs."""
        if not node.dependencies:
            return ""
        
        context_parts = []
        for dep_id in node.dependencies:
            if dep_id in completed:
                dep_result = completed[dep_id]
                if dep_result.success:
                    # Pass full results as context
                    context_parts.append(f"Results from {dep_id}:\n{dep_result.result}")
                else:
                    context_parts.append(f"Task {dep_id} failed: {dep_result.error}")
        
        return "\n\n".join(context_parts)


class WorkflowExecutor:
    """Simple interface for complete workflow execution."""
    
    def __init__(self):
        self.kernel = KernelAgent()
    
    async def execute(self, dag: DAG) -> Dict[str, ExecutionResult]:
        """Execute complete workflow from DAG."""
        return await self.kernel.execute_workflow(dag)