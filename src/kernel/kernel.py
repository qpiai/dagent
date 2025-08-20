import asyncio
import logging
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import time

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


class DummyAgent:
    """Dummy agent that simulates execution without LLM calls."""
    
    def __init__(self, node_id: str, profile_name: str, tools: List[str], task_description: str):
        self.node_id = node_id
        self.profile_name = profile_name
        self.tools = tools
        self.task_description = task_description
        self.system_prompt = self._generate_system_prompt()
        
    def _generate_system_prompt(self) -> str:
        """Generate system prompt based on profile and tools."""
        base_prompts = {
            "lightweight": "You are a fast, efficient agent for data acquisition tasks.",
            "standard": "You are an analytical agent with strong reasoning capabilities.",
            "collaborative": "You are a senior advisor with multi-perspective analysis capabilities."
        }
        
        base = base_prompts.get(self.profile_name, base_prompts["standard"])
        tools_text = ", ".join(self.tools)
        
        return f"{base} You have access to these tools: {tools_text}. Use them to complete: {self.task_description}"
        
    async def execute(self, context: str = "") -> str:
        """Dummy execution with task-specific tools."""
        # Simulate processing time based on profile complexity
        delays = {"lightweight": 0.5, "standard": 1.0, "collaborative": 1.5}
        delay = delays.get(self.profile_name, 1.0)
        await asyncio.sleep(delay)
        
        # Generate task-specific output based on assigned tools
        result_parts = []
        result_parts.append(f"[{self.profile_name.upper()} AGENT: {self.node_id}]")
        
        if context:
            result_parts.append(f"Used context from dependencies: {len(context)} characters")
        
        result_parts.append(f"Task: {self.task_description[:50]}...")
        result_parts.append(f"Tools used: {', '.join(self.tools)}")
        
        # Generate tool-specific outputs (only for assigned tools)
        for tool in self.tools:
            if tool == "YFinanceTools":
                result_parts.append("• Financial data retrieved: Revenue $28.5B, Net Income $3.2B, P/E ratio 24.1")
            elif tool == "WebSearch":
                result_parts.append("• Web search completed: 15 relevant articles found, 3 analyst reports")
            elif tool == "DataProcessor":
                result_parts.append("• Data processed: 1,247 records cleaned and normalized")
            elif tool == "StatisticalAnalysis":
                result_parts.append("• Statistical analysis: Mean growth 12.3%, std dev 2.1%, correlation 0.73")
            elif tool == "NaturalLanguageProcessor":
                result_parts.append("• Sentiment analysis: 68% positive, 22% neutral, 10% negative (confidence: 0.85)")
            elif tool == "MachineLearning":
                result_parts.append("• ML prediction: BUY recommendation (confidence: 0.82)")
            elif tool == "ReportBuilder":
                result_parts.append("• Investment report generated: 12 pages, 5 charts, 3 tables, executive summary")
            elif tool == "APIConnector":
                result_parts.append("• API call completed: 200 OK response")
            elif tool == "FileReader":
                result_parts.append("• Files processed: 2,341 lines read successfully")
            elif tool == "DatabaseQuery":
                result_parts.append("• Database query: 1,523 records returned")
        
        result_parts.append(f"Task completed successfully")
        
        return "\n".join(result_parts)


class KernelAgent:
    """
    Kernel that creates one specialized agent per DAG node.
    """
    
    def __init__(self):
        self.node_agents: Dict[str, DummyAgent] = {}
        
    async def execute_workflow(self, dag) -> Dict[str, ExecutionResult]:
        """
        Main workflow execution:
        1. Create one agent per DAG node
        2. Execute DAG with specialized agents
        """
        print(f"\n{'='*60}")
        print("KERNEL AGENT: Starting Workflow Execution")
        print(f"{'='*60}")
        
        # Step 1: Create one agent per node
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
    
    async def _create_node_agents(self, dag):
        """Create one specialized agent per DAG node."""
        print("\nKERNEL: Creating Specialized Agents")
        print("-" * 40)
        
        print(f"Creating {len(dag.nodes)} specialized agents (one per subtask)...")
        
        # Create agents in parallel
        creation_tasks = []
        for node in dag.nodes.values():
            task = self._create_single_node_agent(node)
            creation_tasks.append(task)
        
        start_time = time.time()
        
        await asyncio.gather(*creation_tasks)
        
        creation_time = time.time() - start_time
        print(f"All {len(dag.nodes)} specialized agents created in {creation_time:.2f}s")
        
        # Show created agents
        print("\nCreated Agents:")
        for node_id, agent in self.node_agents.items():
            tools_str = ', '.join(agent.tools)
            print(f"  • {node_id} ({agent.profile_name}): [{tools_str}]")
    
    async def _create_single_node_agent(self, node) -> DummyAgent:
        """Create a specialized agent for a specific node."""
        # Simulate agent creation time
        await asyncio.sleep(0.2)
        
        agent = DummyAgent(
            node_id=node.id,
            profile_name=node.agent_profile,
            tools=node.tool_allowlist,
            task_description=node.task_description
        )
        
        self.node_agents[node.id] = agent
        
        print(f"  Created specialized agent: {node.id}")
        return agent
    
    async def _execute_dag_with_display(self, dag) -> Dict[str, ExecutionResult]:
        """Execute DAG with specialized agents."""
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
                print(f"  Starting: {node.id} ({node.agent_profile}) [Tools: {tools_str}]")
                if node.dependencies:
                    print(f"    Dependencies: {', '.join(deps)}")
            
            # Execute all ready nodes in parallel
            tasks = []
            for node in ready_nodes:
                task = self._execute_node_with_display(node, completed)
                tasks.append(task)
            
            # Wait for all tasks in this round
            results = await asyncio.gather(*tasks)
            
            # Store results and show completion
            print(f"\nROUND {round_num} RESULTS:")
            for result in results:
                completed[result.node_id] = result
                status = "✓" if result.success else "✗"
                print(f"  {status} {result.node_id}: {result.execution_time:.2f}s")
            
            round_num += 1
        
        return completed
    
    async def _execute_node_with_display(self, node, completed: Dict[str, ExecutionResult]) -> ExecutionResult:
        """Execute a single node with its specialized agent."""
        start_time = time.time()
        
        try:
            # Build context from dependencies
            context = self._build_context_with_display(node, completed)
            
            # Get specialized agent for this exact node
            agent = self.node_agents[node.id]
            
            # Execute with specialized agent
            result = await agent.execute(context=context)
            
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
            
            print(f"Agent: {agent.node_id} ({agent.profile_name})")
            print(f"Tools: {', '.join(agent.tools)}")
            print("Output:")
            # Indent the output for better readability
            for line in result.split('\n'):
                print(f"  {line}")
            print(f"Execution time: {execution_time:.2f}s")
            print("-" * 50)
            
            return ExecutionResult(
                node_id=node.id,
                result=result,
                execution_time=execution_time,
                agent_profile=node.agent_profile,
                tools_used=node.tool_allowlist,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"ERROR in {node.id}: {str(e)}")
            
            return ExecutionResult(
                node_id=node.id,
                result="",
                execution_time=execution_time,
                agent_profile=node.agent_profile,
                tools_used=node.tool_allowlist,
                success=False,
                error=str(e)
            )
    
    def _build_context_with_display(self, node, completed: Dict[str, ExecutionResult]) -> str:
        """Build context from dependency outputs."""
        if not node.dependencies:
            return ""
        
        context_parts = []
        for dep_id in node.dependencies:
            if dep_id in completed:
                dep_result = completed[dep_id]
                if dep_result.success:
                    # Include full result as context
                    context_parts.append(f"=== Results from {dep_id} ===\n{dep_result.result}")
                else:
                    context_parts.append(f"=== {dep_id} FAILED ===\nError: {dep_result.error}")
        
        return "\n\n".join(context_parts)


class WorkflowExecutor:
    """Simple interface for complete workflow execution."""
    
    def __init__(self):
        self.kernel = KernelAgent()
    
    async def execute(self, dag) -> Dict[str, ExecutionResult]:
        """Execute complete workflow from DAG."""
        return await self.kernel.execute_workflow(dag)