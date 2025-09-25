"""Profile generation for agents based on tasks and tools."""

from typing import List
import logging
from planner.planner import AgentProfile
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from .prompts import PROFILE_GENERATOR_SYSTEM_PROMPT, PROFILE_GENERATOR_TASK_PROMPT

# Import centralized tracing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_model
from tracing import langfuse, observe

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """Generates detailed agent profiles based on tasks and tools."""

    def __init__(self):
        # self._llm_agent = Agent(
        #     model=OpenAIChat(id="gpt-4o-mini"),
        #     description="You are a system prompt generator for AI agents. Generate clear, focused system prompts based on agent profiles and tasks.",
        #     markdown=False,
        #     debug_mode=False
        # )

        self._llm_agent = Agent(
            model=get_model(),
            description=PROFILE_GENERATOR_SYSTEM_PROMPT,
            markdown=False,
            debug_mode=False
        )

    @observe()
    async def generate_profile(self, agent_profile: AgentProfile, task_description: str, tools: List[str], dependencies: List[str] = None) -> str:
        """Generate a detailed agent profile using LLM.

        Args:
            agent_profile (AgentProfile): Structured agent profile with semantic fields
            task_description (str): Description of the task the agent will perform
            tools (List[str]): List of tools available to the agent
            dependencies (List[str]): List of dependency task IDs

        Returns:
            str: Generated agent profile/system prompt
        """
        profile_str = f"{agent_profile.task_type}:{agent_profile.complexity}"
        logger.info(f"Generating {profile_str} profile for task: {task_description[:50]}...")

        # Build tool descriptions
        tool_descriptions = self._get_tool_descriptions(tools)

        # Build dependency context
        dependency_context = self._get_dependency_context(dependencies, agent_profile.task_type)

        prompt = PROFILE_GENERATOR_TASK_PROMPT.format(
            task_type=agent_profile.task_type,
            task_type_description=self._get_task_type_description(agent_profile.task_type),
            complexity=agent_profile.complexity,
            complexity_description=self._get_complexity_description(agent_profile.complexity),
            output_format=agent_profile.output_format,
            output_format_description=self._get_output_format_description(agent_profile.output_format),
            reasoning_style=agent_profile.reasoning_style,
            reasoning_style_description=self._get_reasoning_style_description(agent_profile.reasoning_style),
            task_description=task_description,
            tools_description=tool_descriptions,
            dependency_context=dependency_context
        )

        response = await self._llm_agent.arun(prompt)
        generated_profile = response.content.strip()

        langfuse.update_current_trace(
            name=f"generate_profile_{agent_profile.task_type}_{agent_profile.complexity}",
            input=prompt,
            output=generated_profile,
            tags=["profile_generation", agent_profile.task_type]
        )

        logger.info(f"Profile generated successfully for {profile_str}")
        return generated_profile

    @observe()
    async def generate_team_profile(self, task_description: str, team_config: dict) -> str:
        """Generate system prompt for team coordination."""
        # Build member descriptions
        member_descriptions = []
        for member in team_config["agents"]:
            tools = ", ".join(member.get("tools", ["none"]))
            member_descriptions.append(f"- {member['role']}: {member['description']} (Tools: {tools})")

        members_text = "\n".join(member_descriptions)
        collaboration_pattern = team_config.get("collaboration_pattern", "collaborate")

        prompt = f"""Generate a system prompt for a team coordinator managing this task:

Task: {task_description}
Collaboration Pattern: {collaboration_pattern}

Team Members:
{members_text}

The system prompt should:
1. Define the coordinator's role in managing team collaboration
2. Explain how to coordinate the {collaboration_pattern} pattern
3. Specify how to delegate work to appropriate team members
4. Be concise (1-2 paragraphs)

Your response should be ONLY the system prompt text."""

        response = await self._llm_agent.arun(prompt)
        generated_profile = response.content.strip()

        langfuse.update_current_trace(
            name=f"generate_team_profile_{collaboration_pattern}",
            input=prompt,
            output=generated_profile,
            tags=["profile_generation", "team"]
        )

        logger.info(f"Team profile generated for {collaboration_pattern} pattern")
        return generated_profile
    
    def _get_task_type_description(self, task_type: str) -> str:
        """Get description for task type."""
        descriptions = {
            "SEARCH": "Information retrieval, data gathering, web search, API calls",
            "THINK": "Analysis, reasoning, processing existing data, decision making",
            "AGGREGATE": "Synthesis, combining results, final report generation",
            "ACT": "Environment modifications, file operations, external actions"
        }
        return descriptions.get(task_type, "General task execution")

    def _get_complexity_description(self, complexity: str) -> str:
        """Get description for complexity level."""
        descriptions = {
            "QUICK": "Simple, straightforward tasks with minimal reasoning",
            "THOROUGH": "Systematic analysis requiring detailed reasoning and validation",
            "DEEP": "Comprehensive multi-perspective analysis with extensive reasoning"
        }
        return descriptions.get(complexity, "Standard complexity")

    def _get_output_format_description(self, output_format: str) -> str:
        """Get description for output format."""
        descriptions = {
            "DATA": "Raw facts, structured information, search results, extracted data",
            "ANALYSIS": "Insights, patterns, conclusions, comparative analysis",
            "REPORT": "Final formatted answers, summaries, recommendations"
        }
        return descriptions.get(output_format, "Standard output")

    def _get_reasoning_style_description(self, reasoning_style: str) -> str:
        """Get description for reasoning style."""
        descriptions = {
            "DIRECT": "Fact-focused, straightforward, minimal interpretation",
            "ANALYTICAL": "Step-by-step methodology, systematic reasoning",
            "CREATIVE": "Multi-angle exploration, alternative perspectives, comprehensive synthesis"
        }
        return descriptions.get(reasoning_style, "Standard reasoning")
    
    def _get_tool_descriptions(self, tools: List[str]) -> str:
        """Get detailed descriptions for tools."""
        tool_info = {
            "YFinanceTools": "Financial data from Yahoo Finance - get stock prices, company info, financial statements, analyst recommendations, price history",
            "WebSearchTools": "Web search using Exa API - search general web content, recent news articles, financial news, get news summaries",
            "FileEditor": "File operations - create, read, write, modify files, save content, create scripts, manage file system"
        }

        if not tools:
            return "No tools available"

        descriptions = []
        for tool in tools:
            desc = tool_info.get(tool, f"{tool} - tool description not available")
            descriptions.append(f"- {tool}: {desc}")

        return "\n".join(descriptions)

    def _get_dependency_context(self, dependencies: List[str], task_type: str) -> str:
        """Get context about dependencies."""
        if not dependencies:
            if task_type == "SEARCH":
                return "DEPENDENCY CONTEXT: You are a starting node in the workflow. Your output will be used by downstream agents."
            else:
                return "DEPENDENCY CONTEXT: You are a starting node in the workflow."

        dep_context = f"DEPENDENCY CONTEXT: You will receive input from {len(dependencies)} upstream task(s): {', '.join(dependencies)}."

        if task_type == "SEARCH":
            dep_context += " Use this context to inform your search strategy."
        elif task_type == "THINK":
            dep_context += " Analyze and process the provided information."
        elif task_type == "AGGREGATE":
            dep_context += " Synthesize all inputs into a comprehensive final output."
        elif task_type == "ACT":
            dep_context += " Use this context to inform your actions and file operations."

        return dep_context

