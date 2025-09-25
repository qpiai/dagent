"""Kernel agent for orchestrating DAG execution with real Agno agents."""

import asyncio
import logging
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import time

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

from dag import DAG, DAGNode
from tools import YFinanceTools, WebSearchTools, FileEditorTools
from .profiles import ProfileGenerator
from .judge import Judge, JudgeEvaluation

# Import centralized tracing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_model
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
        self.judge = Judge()
        self.global_context = {
            "modified_files": [],
            "changes_log": [],
            "current_version": 1
        }
        
    def _create_tool_registry(self) -> Dict[str, Any]:
        """Create registry of available tool classes."""
        return {
            'YFinanceTools': YFinanceTools,
            'WebSearchTools': WebSearchTools,
            'FileEditor': FileEditorTools
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
    
    async def _create_single_node_agent(self, node: DAGNode):
        """Create a real Agno agent or team for a specific node."""
        # Simulate realistic agent creation time
        await asyncio.sleep(0.1)

        try:
            if node.node_type == "AGENT_TEAM":
                # Create agno team
                team = await self._create_team(node)
                self.node_agents[node.id] = team
                print(f"  Created Agno team: {node.id}")
                return team
            else:
                # Create single agent (existing logic)
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
                agent = Agent(
                    model=get_model(temperature=0.5),
                    tools=tools,
                    description=profile,
                    markdown=False,
                    debug_mode=False
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

    async def _create_team(self, node: DAGNode) -> Team:
        """Create an agno team from team config."""
        team_config = node.team_config

        # Create individual agents for the team
        agents = []
        for agent_config in team_config["agents"]:
            # Create tools for this team member
            tools = []
            for tool_name in agent_config.get("tools", []):
                if tool_name in self.tool_registry:
                    tool_class = self.tool_registry[tool_name]
                    tool_instance = tool_class()
                    tools.append(tool_instance)

            # Create team member agent
            agent = Agent(
                name=agent_config["role"],
                role=agent_config.get("description", f"Agent for {agent_config['role']}"),
                model=get_model(),
                tools=tools,
                debug_mode=False
            )
            agents.append(agent)

        # Create the team with generated system prompt
        team = Team(
            name=f"Team_{node.id}",
            mode=team_config.get("collaboration_pattern", "collaborate"),
            members=agents,
            instructions=node.generated_system_prompt,  # Use pre-generated team prompt
            debug_mode=False
        )

        # Store team info for display
        team._profile_type = f"TEAM:{team_config.get('collaboration_pattern', 'collaborate')}"
        team._node_id = node.id

        return team
    
    async def _execute_dag_with_display(self, dag: DAG) -> Dict[str, ExecutionResult]:
        """Execute DAG with real Agno agents."""
        completed = {}
        round_num = 1
        final_nodes = dag.get_final_nodes()  # Get final nodes for judge optimization
        
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
                if node.node_type == "AGENT_TEAM":
                    profile_str = f"TEAM:{node.team_config.get('collaboration_pattern', 'collaborate')}"
                    tools_str = "team tools"
                else:
                    tools_str = ', '.join(node.tool_allowlist)
                    profile_str = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
                print(f"  Starting: {node.id} ({profile_str}) [Tools: {tools_str}]")
                if node.dependencies:
                    print(f"    Dependencies: {', '.join(deps)}")
            
            # Execute all ready nodes in parallel
            tasks = []
            for node in ready_nodes:
                task = self._execute_node_with_display(node, completed, final_nodes)
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
    async def _execute_node_with_display(self, node: DAGNode, completed: Dict[str, ExecutionResult], final_nodes: Set[str]) -> ExecutionResult:
        """Execute a single node with actor-critic retry logic and feedback injection."""
        overall_start_time = time.time()
        judge_feedback_history = []  # Track feedback from previous attempts

        # Actor-Critic Loop: Try up to max_retries + 1 times
        for attempt in range(node.max_retries + 1):
            start_time = time.time()
            is_final_attempt = (attempt == node.max_retries)

            try:
                # Build context from dependencies
                context = self._build_context_for_node(node, completed)

                # Get the real Agno agent for this node
                agent = self.node_agents[node.id]

                # Create the prompt with context and task
                prompt_parts = []

                # Add global context (environment state)
                if self.global_context["changes_log"]:
                    prompt_parts.append("Environment State:")
                    prompt_parts.append(f"Current Version: {self.global_context['current_version']}")
                    if self.global_context["modified_files"]:
                        prompt_parts.append(f"Modified Files: {', '.join(self.global_context['modified_files'])}")
                    recent_changes = self.global_context["changes_log"][-3:]  # Show last 3 changes
                    for change in recent_changes:
                        prompt_parts.append(f"  - {change['type']}: {change.get('file', change.get('description', 'N/A'))}")
                    prompt_parts.append("")

                if context:
                    prompt_parts.append("Context from previous tasks:")
                    prompt_parts.append(context)
                    prompt_parts.append("")

                prompt_parts.append(f"Task: {node.task_description}")

                # Add retry context with specific judge feedback
                if attempt > 0 and judge_feedback_history:
                    prompt_parts.append(f"\n[RETRY ATTEMPT {attempt + 1}/{node.max_retries + 1}]")
                    prompt_parts.append("Your previous attempt was rejected by the quality judge.")

                    # Inject specific feedback from judge
                    latest_feedback = judge_feedback_history[-1]
                    prompt_parts.append(f"\nJudge Feedback: {latest_feedback.feedback}")

                    if latest_feedback.specific_issues:
                        prompt_parts.append(f"Specific Issues to Address: {latest_feedback.specific_issues}")

                    prompt_parts.append("\nPlease address the judge's feedback and improve your response accordingly.")

                full_prompt = "\n".join(prompt_parts)

                # Execute with the real Agno agent
                logger.info(f"Executing agent {node.id} (attempt {attempt + 1}/{node.max_retries + 1})")
                response = await agent.arun(full_prompt)

                # Extract result content
                result_content = response.content if hasattr(response, 'content') else str(response)

                # Update global context for ACT operations
                if (node.node_type == "SINGLE_AGENT" and
                    hasattr(node, 'agent_profile') and
                    node.agent_profile and
                    node.agent_profile.task_type == "ACT"):
                    self._update_global_context_for_act(node, result_content)

                execution_time = time.time() - start_time

                # Show detailed execution info
                retry_info = f" (RETRY {attempt + 1})" if attempt > 0 else ""
                print(f"\n--- EXECUTING: {node.id}{retry_info} ---")
                if node.dependencies:
                    print("Input Context:")
                    for dep_id in node.dependencies:
                        if dep_id in completed:
                            dep_result = completed[dep_id]
                            preview = dep_result.result[:100] + "..." if len(dep_result.result) > 100 else dep_result.result
                            print(f"  ├─ {dep_id}: {preview}")
                else:
                    print("Input Context: None (root task)")

                # Show judge feedback if this is a retry
                if attempt > 0 and judge_feedback_history:
                    latest_feedback = judge_feedback_history[-1]
                    print(f"Judge Feedback: {latest_feedback.feedback}")
                    if latest_feedback.specific_issues:
                        print(f"Issues to Address: {latest_feedback.specific_issues}")

                if node.node_type == "AGENT_TEAM":
                    profile_str = f"TEAM:{node.team_config.get('collaboration_pattern', 'collaborate')}"
                    tools_str = "team tools"
                else:
                    profile_str = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
                    tools_str = ', '.join(node.tool_allowlist)
                print(f"Agent: {node.id} ({profile_str})")
                print(f"Tools: {tools_str}")
                print("Output:")
                # Show full output
                output_preview = result_content
                for line in output_preview.split('\n'):
                    print(f"  {line}")
                print(f"Execution time: {execution_time:.2f}s")

                # Judge evaluation (Actor-Critic) - Skip for final nodes to save tokens
                is_final_node = node.id in final_nodes
                if node.needs_validation and not is_final_attempt and not is_final_node:
                    print("Judge evaluating output...")
                    try:
                        evaluation = await self.judge.evaluate_with_feedback(node.task_description, result_content)

                        if evaluation.is_accepted:
                            print("Judge ACCEPTED the output")
                            print(f"Judge Feedback: {evaluation.feedback}")

                            # Create appropriate tags for langfuse based on node type
                            if node.node_type == "AGENT_TEAM":
                                task_tag = f"team_{node.team_config.get('collaboration_pattern', 'collaborate')}"
                            else:
                                task_tag = node.agent_profile.task_type

                            langfuse.update_current_trace(
                                name=node.id,
                                input=full_prompt,
                                output=result_content,
                                tags=["agent", task_tag, "accepted"]
                            )
                            print("-" * 50)
                            tools_used = node.tool_allowlist if node.node_type == "SINGLE_AGENT" else ["team_tools"]
                            return ExecutionResult(
                                node_id=node.id,
                                result=result_content,
                                execution_time=time.time() - overall_start_time,
                                agent_profile=profile_str,
                                tools_used=tools_used,
                                success=True
                            )
                        else:
                            print("Judge REJECTED the output")
                            print(f"Judge Feedback: {evaluation.feedback}")
                            if evaluation.specific_issues:
                                print(f"Issues to Address: {evaluation.specific_issues}")

                            # Store feedback for next retry attempt
                            judge_feedback_history.append(evaluation)

                            print("Retrying with judge feedback...")
                            print("-" * 50)
                            continue  # Try again with feedback

                    except Exception as judge_error:
                        logger.warning(f"Judge evaluation failed: {judge_error}, accepting output")
                        print("Judge evaluation failed, accepting output")
                else:
                    if is_final_node:
                        print("Skipping judge validation (final node - saves tokens)")
                    else:
                        print("No validation needed or final attempt")

                # Final attempt or no validation needed - return result
                # Create appropriate tags for langfuse based on node type
                if node.node_type == "AGENT_TEAM":
                    task_tag = f"team_{node.team_config.get('collaboration_pattern', 'collaborate')}"
                else:
                    task_tag = node.agent_profile.task_type

                langfuse.update_current_trace(
                    name=node.id,
                    input=full_prompt,
                    output=result_content,
                    tags=["agent", task_tag, "final" if is_final_attempt else "no_validation"]
                )
                print("-" * 50)
                tools_used = node.tool_allowlist if node.node_type == "SINGLE_AGENT" else ["team_tools"]
                return ExecutionResult(
                    node_id=node.id,
                    result=result_content,
                    execution_time=time.time() - overall_start_time,
                    agent_profile=profile_str,
                    tools_used=tools_used,
                    success=True
                )

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Task {node.id} attempt {attempt + 1} failed: {str(e)}")
                print(f"ERROR in {node.id} attempt {attempt + 1}: {str(e)}")

                if is_final_attempt:
                    # Final attempt failed - return error result
                    if node.node_type == "AGENT_TEAM":
                        profile_str = f"TEAM:{node.team_config.get('collaboration_pattern', 'collaborate')}"
                        tools_used = ["team_tools"]
                    else:
                        profile_str = f"{node.agent_profile.task_type}:{node.agent_profile.complexity}"
                        tools_used = node.tool_allowlist
                    print("-" * 50)
                    return ExecutionResult(
                        node_id=node.id,
                        result="",
                        execution_time=time.time() - overall_start_time,
                        agent_profile=profile_str,
                        tools_used=tools_used,
                        success=False,
                        error=str(e)
                    )
                else:
                    print(f"Retrying after error...")
                    continue
    
    def _update_global_context_for_act(self, node: DAGNode, result_content: str):
        """Update global context after ACT operations using tool-based detection."""
        import re
        from datetime import datetime

        # Option 2: Tool-based detection - simple and reliable
        modified_files = []

        # Check if FileEditor tools were used successfully
        if ("FileEditor" in node.tool_allowlist and
            result_content and
            "error" not in result_content.lower() and
            "failed" not in result_content.lower()):

            # Extract filename from task description (more reliable than parsing output)
            filename_patterns = [
                r"['\"]([^'\"]+\.(py|txt|json|csv|md|yaml|yml|js|ts|html|css))['\"]",  # quoted filenames
                r"named?\s+['\"]?([^'\"\s]+\.(py|txt|json|csv|md|yaml|yml|js|ts|html|css))['\"]?",  # "named X" or "name X"
                r"file\s+['\"]?([^'\"\s]+\.(py|txt|json|csv|md|yaml|yml|js|ts|html|css))['\"]?",  # "file X"
                r"([a-zA-Z0-9_-]+\.(py|txt|json|csv|md|yaml|yml|js|ts|html|css))"  # any filename with extension
            ]

            for pattern in filename_patterns:
                matches = re.findall(pattern, node.task_description, re.IGNORECASE)
                if matches:
                    # Extract just the filename (first group for some patterns, full match for others)
                    if isinstance(matches[0], tuple):
                        modified_files.extend([match[0] for match in matches])
                    else:
                        modified_files.extend(matches)
                    break  # Use first matching pattern


        # Update global context if files were detected
        if modified_files:
            for file_path in modified_files:
                if file_path not in self.global_context["modified_files"]:
                    self.global_context["modified_files"].append(file_path)

                # Add to change log
                self.global_context["changes_log"].append({
                    "type": "file_operation",
                    "file": file_path,
                    "node_id": node.id,
                    "timestamp": datetime.now().isoformat()
                })

            # Increment version
            self.global_context["current_version"] += 1

            logger.info(f"Updated global context - Version {self.global_context['current_version']}, Modified files: {modified_files}")

            # Print global context for debugging
            print(f"\n🌐 GLOBAL CONTEXT UPDATED:")
            print(f"   Version: {self.global_context['current_version']}")
            print(f"   Modified Files: {self.global_context['modified_files']}")
            print(f"   Recent Changes:")
            for change in self.global_context['changes_log'][-3:]:
                print(f"     - {change['type']}: {change.get('file', 'N/A')} (by {change.get('node_id', 'unknown')})")
            print()

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