"""Example usage of custom tools with Agno agents."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports (same as main.py)
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Import our custom tools
from tools import YFinanceTools, WebSearchTools, DataProcessorTools, ReportBuilderTools


async def main():
    """Example of using custom tools with Agno agents."""
    
    # Example 1: Financial Agent with YFinance tools
    financial_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.1),
        tools=[YFinanceTools()],
        description="You are a financial analyst that retrieves and analyzes stock data.",
        markdown=True,
        show_tool_calls=True
    )
    
    print("=== Financial Agent Example ===")
    result = await financial_agent.arun("Get Tesla's current stock price and key financial metrics")
    print("Financial Agent Result:", result.content)
    
    
    # Example 2: Research Agent with Web Search tools
    research_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.1),
        tools=[WebSearchTools()],
        description="You are a research analyst that searches for recent news and market information.",
        markdown=True,
        show_tool_calls=True
    )
    
    print("\n=== Research Agent Example ===")
    result = await research_agent.arun("Find recent news about Tesla's Q4 2024 performance")
    print("Research Agent Result:", result.content)
    
    
    # Example 3: Data Analysis Agent
    data_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.1),
        tools=[DataProcessorTools()],
        description="You are a data analyst that processes and analyzes numerical data.",
        markdown=True,
        show_tool_calls=True
    )
    
    print("\n=== Data Analysis Agent Example ===")
    sample_data = "Tesla revenue $28.5B, net income $3.2B, P/E ratio 24.1, growth 12.3%"
    result = await data_agent.arun(f"Extract and analyze the financial metrics from this data: {sample_data}")
    print("Data Agent Result:", result.content)
    
    
    # Example 4: Report Generation Agent
    report_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.1),
        tools=[ReportBuilderTools()],
        description="You are a report writer that creates professional investment reports.",
        markdown=True,
        show_tool_calls=True
    )
    
    print("\n=== Report Agent Example ===")
    financial_data = "Tesla revenue $28.5B, net income $3.2B, current price $248.50"
    market_data = "Positive sentiment, strong Q4 performance, analyst upgrades"
    result = await report_agent.arun(
        f"Create an investment report for Tesla using this data: Financial: {financial_data}, Market: {market_data}"
    )
    print("Report Agent Result:", result.content)
    
    
    # Example 5: Multi-Tool Agent (like our DAG nodes)
    comprehensive_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.1),
        tools=[
            YFinanceTools(), 
            WebSearchTools(), 
            DataProcessorTools(), 
            ReportBuilderTools()
        ],
        description="You are a comprehensive investment analyst with access to financial data, web search, data processing, and report generation tools.",
        markdown=True,
        show_tool_calls=True
    )
    
    print("\n=== Comprehensive Agent Example ===")
    result = await comprehensive_agent.arun(
        "Analyze Tesla's investment potential: get current financial data, search for recent news, process the data, and create a brief investment summary"
    )
    print("Comprehensive Agent Result:", result.content)


if __name__ == "__main__":
    asyncio.run(main())