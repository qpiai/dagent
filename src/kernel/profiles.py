"""Profile generation for agents based on tasks and tools."""

from typing import List
import logging

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """Generates detailed agent profiles based on tasks and tools."""
    
    def __init__(self):
        pass
    
    def generate_profile(self, profile_type: str, task_description: str, tools: List[str]) -> str:
        """Generate a detailed agent profile.
        
        Args:
            profile_type (str): Type of profile (lightweight/standard/collaborative)
            task_description (str): Description of the task the agent will perform
            tools (List[str]): List of tools available to the agent
            
        Returns:
            str: Generated agent profile/system prompt
        """
        logger.info(f"Generating {profile_type} profile for task: {task_description[:50]}...")
        
        try:
            # For now, use template-based profiles
            # TODO: Replace with LLM-generated profiles later
            profile = self._get_template_profile(profile_type, task_description, tools)
            logger.info(f"Profile generated successfully for {profile_type}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to generate profile: {e}")
            return self._get_fallback_profile(profile_type)
    
    def _get_template_profile(self, profile_type: str, task_description: str, tools: List[str]) -> str:
        """Generate profile from templates based on type and context."""
        
        # Base profile templates
        base_profiles = {
            "lightweight": "You are a fast, efficient agent specialized in data acquisition and straightforward tasks.",
            "standard": "You are an analytical agent with strong reasoning capabilities for complex analysis.",
            "collaborative": "You are a senior advisor with multi-perspective analysis capabilities."
        }
        
        # Tool-specific instructions
        tool_instructions = {
            "YFinanceTools": "Use YFinance tools to retrieve accurate, up-to-date financial data and stock information.",
            "WebSearchTools": "Use web search tools to find recent news, articles, and market information.",
            "DataProcessorTools": "Use data processing tools to extract, analyze, and manipulate numerical data and financial metrics.",
            "ReportBuilderTools": "Use report building tools to create professional, well-formatted investment reports and summaries."
        }
        
        # Task-specific guidance
        task_guidance = self._get_task_guidance(task_description)
        
        # Build the complete profile
        base = base_profiles.get(profile_type, base_profiles["standard"])
        
        profile_parts = [base]
        
        # Add task-specific guidance
        if task_guidance:
            profile_parts.append(f"\nYour specific task: {task_guidance}")
        
        # Add tool instructions
        if tools:
            profile_parts.append(f"\nAvailable tools and how to use them:")
            for tool in tools:
                if tool in tool_instructions:
                    profile_parts.append(f"- {tool_instructions[tool]}")
        
        # Add general instructions based on profile type
        if profile_type == "lightweight":
            profile_parts.append("\nFocus on speed and efficiency. Provide clear, concise results.")
        elif profile_type == "standard":
            profile_parts.append("\nApproach tasks systematically with thorough analysis. Explain your reasoning.")
        elif profile_type == "collaborative":
            profile_parts.append("\nProvide comprehensive insights with multi-perspective analysis. Consider various scenarios and implications.")
        
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
    
    def _get_fallback_profile(self, profile_type: str) -> str:
        """Fallback profiles if generation fails."""
        fallback_profiles = {
            "lightweight": """
You are a fast and efficient AI agent specialized in data acquisition and straightforward tasks. 
Your strengths include quick data retrieval, efficient processing, and clear output formatting.
Focus on speed and accuracy for routine tasks while maintaining high quality standards.
            """.strip(),
            
            "standard": """
You are a versatile AI analyst with strong reasoning and analytical capabilities. 
Your expertise includes complex data analysis, pattern recognition, and synthesis of information.
Approach tasks systematically, ensuring thorough analysis while maintaining efficiency.
            """.strip(),
            
            "collaborative": """
You are a senior AI advisor specializing in comprehensive analysis and strategic recommendations.
Your capabilities include multi-perspective analysis, strategic thinking, and high-level decision support.
Provide well-reasoned, actionable insights based on thorough analysis of all available information.
            """.strip()
        }
        
        return fallback_profiles.get(profile_type, fallback_profiles["standard"])