"""Profile generation for agents based on tasks and tools."""

from typing import List
import logging
from planner.planner import AgentProfile

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """Generates detailed agent profiles based on tasks and tools."""

    def __init__(self):
        pass

    def generate_profile(self, agent_profile: AgentProfile, task_description: str, tools: List[str]) -> str:
        """Generate a detailed agent profile.

        Args:
            agent_profile (AgentProfile): Structured agent profile with semantic fields
            task_description (str): Description of the task the agent will perform
            tools (List[str]): List of tools available to the agent

        Returns:
            str: Generated agent profile/system prompt
        """
        profile_str = f"{agent_profile.task_type}:{agent_profile.complexity}"
        logger.info(f"Generating {profile_str} profile for task: {task_description[:50]}...")

        try:
            # For now, use template-based profiles
            # TODO: Replace with LLM-generated profiles later
            profile = self._get_template_profile(agent_profile, task_description, tools)
            logger.info(f"Profile generated successfully for {profile_str}")
            return profile

        except Exception as e:
            logger.error(f"Failed to generate profile: {e}")
            return self._get_fallback_profile(agent_profile)
    
    def _get_template_profile(self, agent_profile: AgentProfile, task_description: str, tools: List[str]) -> str:
        """Generate profile from templates based on agent profile and context."""

        # Base profiles by task type
        task_type_profiles = {
            "SEARCH": "You are a specialized information retrieval agent focused on finding and collecting relevant data.",
            "THINK": "You are an analytical agent specialized in processing information and generating insights.",
            "AGGREGATE": "You are a synthesis agent specialized in combining information and creating comprehensive outputs."
        }

        # Complexity modifiers
        complexity_modifiers = {
            "QUICK": "Work efficiently and provide concise, direct results.",
            "THOROUGH": "Apply systematic analysis with detailed reasoning and validation.",
            "DEEP": "Conduct comprehensive multi-perspective analysis with extensive reasoning."
        }
        
        # Output format guidelines
        output_format_guidelines = {
            "DATA": "Provide structured, factual information in a clear, organized format.",
            "ANALYSIS": "Present insights, patterns, and conclusions with supporting evidence.",
            "REPORT": "Create comprehensive, well-formatted final outputs with executive summaries."
        }

        # Reasoning style instructions
        reasoning_style_instructions = {
            "DIRECT": "Be straightforward and fact-focused with minimal interpretation.",
            "ANALYTICAL": "Use step-by-step methodology and show your reasoning process.",
            "CREATIVE": "Explore multiple perspectives and provide comprehensive synthesis."
        }

        # Tool-specific instructions
        tool_instructions = {
            "YFinanceTools": "Use YFinance tools to retrieve accurate, up-to-date financial data and stock information.",
            "WebSearchTools": "Use web search tools to find recent news, articles, and market information."
        }

        # Build the complete profile using the structured fields
        base_task_profile = task_type_profiles.get(agent_profile.task_type,
                                                   task_type_profiles["THINK"])

        profile_parts = [base_task_profile]

        # Add complexity modifier
        complexity_instruction = complexity_modifiers.get(agent_profile.complexity,
                                                          complexity_modifiers["THOROUGH"])
        profile_parts.append(complexity_instruction)

        # Add output format guidance
        output_instruction = output_format_guidelines.get(agent_profile.output_format,
                                                          output_format_guidelines["ANALYSIS"])
        profile_parts.append(output_instruction)

        # Add reasoning style
        reasoning_instruction = reasoning_style_instructions.get(agent_profile.reasoning_style,
                                                                reasoning_style_instructions["ANALYTICAL"])
        profile_parts.append(reasoning_instruction)

        # Add task-specific guidance
        task_guidance = self._get_task_guidance(task_description)
        if task_guidance:
            profile_parts.append(f"Task-specific guidance: {task_guidance}")

        # Add tool instructions
        if tools:
            profile_parts.append("Available tools:")
            for tool in tools:
                if tool in tool_instructions:
                    profile_parts.append(f"- {tool_instructions[tool]}")

        return " ".join(profile_parts)
    
    def _get_task_guidance(self, task_description: str) -> str:
        """Generate task-specific guidance based on the task description."""
        task_lower = task_description.lower()
        
        if "fetch" in task_lower or "retrieve" in task_lower or "get" in task_lower:
            return "Focus on accurate data retrieval and proper formatting of the information."
        elif "analyze" in task_lower or "analysis" in task_lower:
            return "Perform thorough analysis, identify key patterns, and provide clear insights."
        elif "search" in task_lower or "find" in task_lower:
            return "Conduct comprehensive searches and filter results for relevance and quality."
        elif "report" in task_lower or "generate" in task_lower or "create" in task_lower:
            return "Create well-structured, professional output with clear formatting and actionable insights."
        elif "compare" in task_lower or "comparison" in task_lower:
            return "Perform detailed comparisons highlighting key differences and similarities."
        else:
            return "Execute the task efficiently while maintaining high quality standards."
    
    def _get_fallback_profile(self, agent_profile: AgentProfile) -> str:
        """Simple fallback if generation fails."""
        return "You are a helpful AI agent. Execute the given task efficiently and accurately."