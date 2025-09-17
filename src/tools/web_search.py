"""Web search tools using Exa API."""

import os
from agno.tools.exa import ExaTools
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base import BaseAgnoTool


class WebSearchTools(BaseAgnoTool):
    """Toolkit for web searching using Exa API."""

    def __init__(self, **kwargs):
        super().__init__(
            name="web_search_tools",
            tools=[
                self.search_web,
                self.search_news,
                self.search_financial_news,
                self.get_news_summary
            ],
            **kwargs
        )
        self.exa_tools = ExaTools()
    
    def search_web(self, query: str, max_results: int = 5) -> str:
        """Search the web for general information."""
        try:
            self._log_tool_call("search_web", {"query": query, "max_results": max_results})

            results = self.exa_tools.search_exa(query, num_results=max_results)

            if not results:
                return f"No search results found for: {query}"

            return f"Web Search Results for: '{query}'\n\n{results}"

        except Exception as e:
            return self._handle_error("search_web", e)
    
    def search_news(self, query: str, max_results: int = 5, days_back: int = 7) -> str:
        """Search for recent news articles."""
        try:
            self._log_tool_call("search_news", {
                "query": query,
                "max_results": max_results,
                "days_back": days_back
            })

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            results = self.exa_tools.search_exa(
                query,
                num_results=max_results,
                category="news"
            )

            if not results:
                return f"No recent news found for: {query}"

            return f"Recent News for: '{query}' (Last {days_back} days)\n\n{results}"

        except Exception as e:
            return self._handle_error("search_news", e)
    
    def search_financial_news(self, company_or_symbol: str, max_results: int = 5) -> str:
        """Search for financial news about a specific company or stock."""
        try:
            self._log_tool_call("search_financial_news", {
                "company_or_symbol": company_or_symbol,
                "max_results": max_results
            })

            query = f"{company_or_symbol} earnings stock financial results"

            results = self.exa_tools.search_exa(
                query,
                num_results=max_results,
                category="financial report"
            )

            if not results:
                return f"No recent financial news found for: {company_or_symbol}"

            return f"Financial News for: '{company_or_symbol}'\n\n{results}"

        except Exception as e:
            return self._handle_error("search_financial_news", e)
    
    def get_news_summary(self, topic: str, focus_area: Optional[str] = None) -> str:
        """Get a focused summary of news on a specific topic."""
        try:
            query = f"{topic}"
            if focus_area:
                query += f" {focus_area}"

            self._log_tool_call("get_news_summary", {"topic": topic, "focus_area": focus_area})

            results = self.exa_tools.search_exa(
                query,
                num_results=8,
                category="news"
            )

            if not results:
                return f"No recent news found for: {topic}"

            return f"News Summary for: '{topic}'{f' (Focus: {focus_area})' if focus_area else ''}\n\n{results}"

        except Exception as e:
            return self._handle_error("get_news_summary", e)