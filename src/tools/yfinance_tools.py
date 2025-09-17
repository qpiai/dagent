"""YFinance tools for financial data retrieval."""

import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
from .base import BaseAgnoTool


class YFinanceTools(BaseAgnoTool):
    """Toolkit for retrieving financial data using YFinance API."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="yfinance_tools",
            tools=[
                self.get_stock_price,
                self.get_company_info,
                self.get_financial_statements,
                self.get_analyst_recommendations,
                self.get_price_history
            ],
            **kwargs
        )
    
    def get_stock_price(self, symbol: str) -> str:
        """Get current stock price and basic metrics.
        
        Args:
            symbol (str): Stock symbol (e.g., 'TSLA', 'AAPL')
            
        Returns:
            str: Current price and basic metrics
        """
        try:
            self._log_tool_call("get_stock_price", {"symbol": symbol})
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and key metrics
            current_price = info.get('currentPrice', 'N/A')
            previous_close = info.get('previousClose', 'N/A')
            market_cap = info.get('marketCap', 'N/A')
            pe_ratio = info.get('trailingPE', 'N/A')
            
            # Calculate change
            if current_price != 'N/A' and previous_close != 'N/A':
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                change = 'N/A'
                change_percent = 'N/A'
            
            result = f"""
Stock Price Information for {symbol.upper()}:
• Current Price: ${current_price}
• Previous Close: ${previous_close}
• Change: ${change} ({change_percent:.2f}%)
• Market Cap: {self._format_number(market_cap)}
• P/E Ratio: {pe_ratio}
• Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("get_stock_price", e)
    
    def get_company_info(self, symbol: str) -> str:
        """Get detailed company information.
        
        Args:
            symbol (str): Stock symbol (e.g., 'TSLA', 'AAPL')
            
        Returns:
            str: Company information including business summary
        """
        try:
            self._log_tool_call("get_company_info", {"symbol": symbol})
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            company_name = info.get('longName', 'N/A')
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            employees = info.get('fullTimeEmployees', 'N/A')
            website = info.get('website', 'N/A')
            summary = info.get('businessSummary', 'N/A')
            
            result = f"""
Company Information for {symbol.upper()}:
• Company Name: {company_name}
• Sector: {sector}
• Industry: {industry}
• Full-time Employees: {self._format_number(employees)}
• Website: {website}
• Business Summary: {summary}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("get_company_info", e)
    
    def get_financial_statements(self, symbol: str) -> str:
        """Get key financial statement data.
        
        Args:
            symbol (str): Stock symbol (e.g., 'TSLA', 'AAPL')
            
        Returns:
            str: Key financial metrics from latest statements
        """
        try:
            self._log_tool_call("get_financial_statements", {"symbol": symbol})
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Key financial metrics
            revenue = info.get('totalRevenue', 'N/A')
            gross_profit = info.get('grossProfits', 'N/A')
            net_income = info.get('netIncomeToCommon', 'N/A')
            total_cash = info.get('totalCash', 'N/A')
            total_debt = info.get('totalDebt', 'N/A')
            revenue_growth = info.get('revenueGrowth', 'N/A')
            
            result = f"""
Financial Statement Data for {symbol.upper()}:
• Total Revenue: {self._format_number(revenue)}
• Gross Profit: {self._format_number(gross_profit)}
• Net Income: {self._format_number(net_income)}
• Total Cash: {self._format_number(total_cash)}
• Total Debt: {self._format_number(total_debt)}
• Revenue Growth: {revenue_growth:.2%} if revenue_growth != 'N/A' else 'N/A'
• Data as of: {datetime.now().strftime('%Y-%m-%d')}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("get_financial_statements", e)
    
    def get_analyst_recommendations(self, symbol: str) -> str:
        """Get analyst recommendations and price targets.
        
        Args:
            symbol (str): Stock symbol (e.g., 'TSLA', 'AAPL')
            
        Returns:
            str: Analyst recommendations and price targets
        """
        try:
            self._log_tool_call("get_analyst_recommendations", {"symbol": symbol})
            
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is None or recommendations.empty:
                return f"No analyst recommendations available for {symbol.upper()}"
            
            # Get most recent recommendations
            recent_recommendations = recommendations.tail(5)
            
            result = f"""
Analyst Recommendations for {symbol.upper()}:
Recent Recommendations:
            """
            
            for date, row in recent_recommendations.iterrows():
                try:
                    date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
                except (AttributeError, TypeError):
                    date_str = str(date)
                result += f"• {date_str}: {row.get('To Grade', 'N/A')} by {row.get('Firm', 'N/A')}\n"
            
            # Get price targets if available
            info = ticker.info
            target_mean = info.get('targetMeanPrice', 'N/A')
            target_high = info.get('targetHighPrice', 'N/A')
            target_low = info.get('targetLowPrice', 'N/A')
            
            result += f"""
Price Targets:
• Mean Target: ${target_mean}
• High Target: ${target_high}
• Low Target: ${target_low}
            """
            
            return result.strip()
            
        except Exception as e:
            return self._handle_error("get_analyst_recommendations", e)
    
    def get_price_history(self, symbol: str, period: str = "3mo") -> str:
        """Get historical price data and calculate key statistics.
        
        Args:
            symbol (str): Stock symbol (e.g., 'TSLA', 'AAPL')
            period (str): Time period ('1mo', '3mo', '6mo', '1y')
            
        Returns:
            str: Historical price statistics
        """
        try:
            self._log_tool_call("get_price_history", {"symbol": symbol, "period": period})
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return f"No historical data available for {symbol.upper()}"
            
            # Calculate statistics
            current_price = hist['Close'].iloc[-1]
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            avg_volume = hist['Volume'].mean()
            volatility = hist['Close'].pct_change().std() * 100
            
            # Calculate returns
            start_price = hist['Close'].iloc[0]
            total_return = ((current_price - start_price) / start_price) * 100
            
            result = f"""
Price History for {symbol.upper()} ({period}):
• Current Price: ${current_price:.2f}
• Period High: ${high_52w:.2f}
• Period Low: ${low_52w:.2f}
• Period Return: {total_return:.2f}%
• Average Volume: {self._format_number(int(avg_volume))}
• Volatility: {volatility:.2f}%
• Data from: {hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("get_price_history", e)
    
    def _format_number(self, num) -> str:
        """Format large numbers with appropriate suffixes."""
        if num == 'N/A' or num is None:
            return 'N/A'
        
        try:
            num = float(num)
            if num >= 1_000_000_000_000:  # Trillion
                return f"${num/1_000_000_000_000:.2f}T"
            elif num >= 1_000_000_000:  # Billion
                return f"${num/1_000_000_000:.2f}B"
            elif num >= 1_000_000:  # Million
                return f"${num/1_000_000:.2f}M"
            elif num >= 1_000:  # Thousand
                return f"${num/1_000:.2f}K"
            else:
                return f"${num:.2f}"
        except:
            return str(num)