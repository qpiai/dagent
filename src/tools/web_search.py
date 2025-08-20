"""Web search tools using DuckDuckGo API."""

import requests
from duckduckgo_search import DDGS
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base import BaseAgnoTool


class WebSearchTools(BaseAgnoTool):
    """Toolkit for web searching using DuckDuckGo."""
    
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
    
    def search_web(self, query: str, max_results: int = 5) -> str:
        """Search the web for general information.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Search results with titles, URLs, and snippets
        """
        try:
            self._log_tool_call("search_web", {"query": query, "max_results": max_results})
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return f"No search results found for: {query}"
            
            formatted_results = f"Web Search Results for: '{query}'\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                href = result.get('href', 'No URL')
                
                formatted_results += f"{i}. {title}\n"
                formatted_results += f"   URL: {href}\n"
                formatted_results += f"   Description: {body[:200]}...\n\n"
            
            formatted_results += f"Search completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return formatted_results
            
        except Exception as e:
            return self._handle_error("search_web", e)
    
    def search_news(self, query: str, max_results: int = 5, days_back: int = 7) -> str:
        """Search for recent news articles.
        
        Args:
            query (str): News search query
            max_results (int): Maximum number of results to return
            days_back (int): How many days back to search
            
        Returns:
            str: Recent news articles with titles, sources, and summaries
        """
        try:
            self._log_tool_call("search_news", {
                "query": query, 
                "max_results": max_results, 
                "days_back": days_back
            })
            
            # Calculate time range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    query, 
                    max_results=max_results,
                    timelimit=f"{days_back}d"
                ))
            
            if not results:
                return f"No recent news found for: {query}"
            
            formatted_results = f"Recent News for: '{query}' (Last {days_back} days)\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                source = result.get('source', 'Unknown source')
                date = result.get('date', 'Unknown date')
                url = result.get('url', 'No URL')
                
                formatted_results += f"{i}. {title}\n"
                formatted_results += f"   Source: {source}\n"
                formatted_results += f"   Date: {date}\n"
                formatted_results += f"   URL: {url}\n"
                formatted_results += f"   Summary: {body[:200]}...\n\n"
            
            formatted_results += f"News search completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return formatted_results
            
        except Exception as e:
            return self._handle_error("search_news", e)
    
    def search_financial_news(self, company_or_symbol: str, max_results: int = 5) -> str:
        """Search for financial news about a specific company or stock.
        
        Args:
            company_or_symbol (str): Company name or stock symbol
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Financial news articles related to the company
        """
        try:
            self._log_tool_call("search_financial_news", {
                "company_or_symbol": company_or_symbol,
                "max_results": max_results
            })
            
            # Create financial-focused search query
            query = f"{company_or_symbol} earnings stock financial results"
            
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    query, 
                    max_results=max_results,
                    timelimit="1m"  # Last month
                ))
            
            if not results:
                return f"No recent financial news found for: {company_or_symbol}"
            
            formatted_results = f"Financial News for: '{company_or_symbol}'\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                source = result.get('source', 'Unknown source')
                date = result.get('date', 'Unknown date')
                url = result.get('url', 'No URL')
                
                # Check if this is likely financial news
                financial_keywords = ['earnings', 'revenue', 'profit', 'stock', 'shares', 'financial', 'quarterly', 'investment']
                is_financial = any(keyword in title.lower() or keyword in body.lower() for keyword in financial_keywords)
                
                marker = "📈" if is_financial else "📰"
                
                formatted_results += f"{i}. {marker} {title}\n"
                formatted_results += f"   Source: {source}\n"
                formatted_results += f"   Date: {date}\n"
                formatted_results += f"   URL: {url}\n"
                formatted_results += f"   Summary: {body[:200]}...\n\n"
            
            formatted_results += f"Financial news search completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return formatted_results
            
        except Exception as e:
            return self._handle_error("search_financial_news", e)
    
    def get_news_summary(self, topic: str, focus_area: Optional[str] = None) -> str:
        """Get a focused summary of news on a specific topic.
        
        Args:
            topic (str): Topic to search for
            focus_area (str, optional): Specific area to focus on
            
        Returns:
            str: Summarized news findings
        """
        try:
            query = f"{topic}"
            if focus_area:
                query += f" {focus_area}"
            
            self._log_tool_call("get_news_summary", {"topic": topic, "focus_area": focus_area})
            
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=8, timelimit="2w"))
            
            if not results:
                return f"No recent news found for: {topic}"
            
            # Analyze news sentiment and themes
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            sources = set()
            key_themes = []
            
            for result in results:
                title = result.get('title', '').lower()
                body = result.get('body', '').lower()
                source = result.get('source', 'Unknown')
                
                sources.add(source)
                
                # Simple sentiment analysis based on keywords
                positive_words = ['growth', 'increase', 'profit', 'success', 'strong', 'beat', 'exceeds', 'rise']
                negative_words = ['decline', 'loss', 'fall', 'drop', 'weak', 'miss', 'below', 'concern']
                
                text = f"{title} {body}"
                
                pos_score = sum(1 for word in positive_words if word in text)
                neg_score = sum(1 for word in negative_words if word in text)
                
                if pos_score > neg_score:
                    positive_count += 1
                elif neg_score > pos_score:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            # Determine overall sentiment
            total_articles = len(results)
            if positive_count > negative_count:
                overall_sentiment = "Positive"
            elif negative_count > positive_count:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Mixed/Neutral"
            
            summary = f"""
News Summary for: '{topic}' {f'(Focus: {focus_area})' if focus_area else ''}

Overall Sentiment: {overall_sentiment}

Article Breakdown:
• Positive: {positive_count}/{total_articles} articles
• Negative: {negative_count}/{total_articles} articles  
• Neutral: {neutral_count}/{total_articles} articles

Sources Covered: {', '.join(list(sources)[:5])}{'...' if len(sources) > 5 else ''}

Key Headlines:
            """
            
            # Add top 3 headlines
            for i, result in enumerate(results[:3], 1):
                title = result.get('title', 'No title')
                date = result.get('date', 'Unknown date')
                summary += f"{i}. {title} ({date})\n"
            
            summary += f"\nSummary generated from {total_articles} articles at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return summary.strip()
            
        except Exception as e:
            return self._handle_error("get_news_summary", e)