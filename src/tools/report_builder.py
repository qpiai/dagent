"""Report building and document generation tools."""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base import BaseAgnoTool


class ReportBuilderTools(BaseAgnoTool):
    """Toolkit for building formatted reports and documents."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="report_builder_tools",
            tools=[
                self.create_investment_report,
                self.create_executive_summary,
                self.format_financial_data,
                self.generate_recommendations,
                self.create_markdown_report
            ],
            **kwargs
        )
    
    def create_investment_report(
        self, 
        company_name: str,
        financial_data: str,
        market_analysis: str,
        recommendation: str = "HOLD"
    ) -> str:
        """Create a comprehensive investment report.
        
        Args:
            company_name (str): Name of the company being analyzed
            financial_data (str): Financial data and metrics
            market_analysis (str): Market sentiment and analysis
            recommendation (str): Investment recommendation (BUY/HOLD/SELL)
            
        Returns:
            str: Formatted investment report
        """
        try:
            self._log_tool_call("create_investment_report", {
                "company_name": company_name,
                "recommendation": recommendation
            })
            
            # Extract key metrics from financial data
            revenue_match = re.search(r'revenue[:\s]*\$?([\d,\.]+)\s*([bBmMkK]?)', financial_data.lower())
            pe_match = re.search(r'p\/e[:\s]*(\d+\.?\d*)', financial_data.lower())
            price_match = re.search(r'price[:\s]*\$?([\d,\.]+)', financial_data.lower())
            
            current_price = price_match.group(1) if price_match else "N/A"
            revenue = f"${revenue_match.group(1)}{revenue_match.group(2).upper()}" if revenue_match else "N/A"
            pe_ratio = pe_match.group(1) if pe_match else "N/A"
            
            # Determine recommendation color/symbol
            rec_symbols = {
                "BUY": "🟢 BUY",
                "STRONG BUY": "🟢 STRONG BUY", 
                "HOLD": "🟡 HOLD",
                "SELL": "🔴 SELL",
                "STRONG SELL": "🔴 STRONG SELL"
            }
            
            rec_display = rec_symbols.get(recommendation.upper(), f"🟡 {recommendation}")
            
            report = f"""
# 📊 INVESTMENT ANALYSIS REPORT
## {company_name.upper()}

---

### 🎯 EXECUTIVE SUMMARY

**Investment Recommendation:** {rec_display}  
**Report Date:** {datetime.now().strftime('%B %d, %Y')}  
**Analysis Period:** Q4 2024  

---

### 📈 KEY FINANCIAL METRICS

| Metric | Value |
|--------|-------|
| Current Stock Price | ${current_price} |
| Revenue (TTM) | {revenue} |
| P/E Ratio | {pe_ratio} |
| Analysis Date | {datetime.now().strftime('%Y-%m-%d')} |

---

### 💰 FINANCIAL PERFORMANCE ANALYSIS

{self._format_section_content(financial_data)}

**Key Financial Highlights:**
{self._extract_bullet_points(financial_data)}

---

### 📊 MARKET SENTIMENT & ANALYSIS

{self._format_section_content(market_analysis)}

**Market Sentiment Summary:**
{self._extract_bullet_points(market_analysis)}

---

### 🎯 INVESTMENT RECOMMENDATION

**Recommendation:** {rec_display}

**Rationale:**
{self._generate_recommendation_rationale(recommendation, financial_data, market_analysis)}

**Risk Assessment:**
• **Market Risk:** {self._assess_market_risk(market_analysis)}
• **Company Risk:** {self._assess_company_risk(financial_data)}
• **Sector Risk:** Moderate (subject to market volatility)

---

### 📋 KEY TAKEAWAYS

{self._generate_key_takeaways(financial_data, market_analysis, recommendation)}

---

### ⚠️ IMPORTANT DISCLAIMERS

• This report is for informational purposes only and should not be considered as financial advice
• Past performance does not guarantee future results
• All investments carry risk of loss
• Consult with a qualified financial advisor before making investment decisions
• Data sources: YFinance, market analysis, and public financial statements

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Prepared by:** AI Investment Analysis System  
**Version:** 1.0
            """.strip()
            
            return report
            
        except Exception as e:
            return self._handle_error("create_investment_report", e)
    
    def create_executive_summary(self, content: str, max_points: int = 5) -> str:
        """Create an executive summary from detailed content.
        
        Args:
            content (str): Detailed content to summarize
            max_points (int): Maximum number of key points
            
        Returns:
            str: Executive summary with key points
        """
        try:
            self._log_tool_call("create_executive_summary", {"max_points": max_points})
            
            # Extract key sentences and metrics
            sentences = re.split(r'[.!?]+', content)
            
            # Look for sentences with key financial terms
            key_terms = [
                'revenue', 'profit', 'growth', 'increase', 'decrease',
                'recommendation', 'analysis', 'performance', 'market',
                'positive', 'negative', 'strong', 'weak'
            ]
            
            important_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Filter out very short sentences
                    score = sum(1 for term in key_terms if term.lower() in sentence.lower())
                    if score > 0:
                        important_sentences.append((sentence, score))
            
            # Sort by relevance score and take top sentences
            important_sentences.sort(key=lambda x: x[1], reverse=True)
            top_sentences = [sent[0] for sent in important_sentences[:max_points]]
            
            # Extract numbers for key metrics
            numbers = re.findall(r'\$?[\d,]+\.?\d*[%bBmMkK]?', content)
            
            summary = f"""
## 📋 EXECUTIVE SUMMARY

**Key Findings:**

"""
            
            for i, sentence in enumerate(top_sentences, 1):
                summary += f"{i}. {sentence.strip()}\n"
            
            if numbers:
                summary += f"\n**Key Metrics:**\n"
                unique_numbers = list(set(numbers))[:5]  # Top 5 unique numbers
                for num in unique_numbers:
                    summary += f"• {num}\n"
            
            summary += f"\n**Summary generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return summary.strip()
            
        except Exception as e:
            return self._handle_error("create_executive_summary", e)
    
    def format_financial_data(self, raw_data: str, table_format: bool = True) -> str:
        """Format financial data into structured tables or lists.
        
        Args:
            raw_data (str): Raw financial data
            table_format (bool): Whether to format as table or list
            
        Returns:
            str: Formatted financial data
        """
        try:
            self._log_tool_call("format_financial_data", {"table_format": table_format})
            
            # Extract financial metrics
            metrics = {}
            
            # Common financial patterns
            patterns = {
                'Current Price': r'current price[:\s]*\$?([\d,\.]+)',
                'Revenue': r'revenue[:\s]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'Net Income': r'net income[:\s]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'P/E Ratio': r'p\/e[:\s]*(\d+\.?\d*)',
                'Market Cap': r'market cap[:\s]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'Growth Rate': r'growth[:\s]*(\d+\.?\d*)%?',
                'Profit Margin': r'margin[:\s]*(\d+\.?\d*)%?'
            }
            
            for metric, pattern in patterns.items():
                match = re.search(pattern, raw_data.lower())
                if match:
                    if len(match.groups()) > 1 and match.group(2):
                        metrics[metric] = f"${match.group(1)}{match.group(2).upper()}"
                    else:
                        value = match.group(1)
                        if 'ratio' in metric.lower():
                            metrics[metric] = value
                        elif '%' in pattern or 'rate' in metric.lower() or 'margin' in metric.lower():
                            metrics[metric] = f"{value}%"
                        else:
                            metrics[metric] = f"${value}"
            
            if not metrics:
                return "No structured financial data could be extracted from the provided text."
            
            if table_format:
                formatted = "## 📊 FINANCIAL DATA SUMMARY\n\n"
                formatted += "| Metric | Value |\n"
                formatted += "|--------|-------|\n"
                
                for metric, value in metrics.items():
                    formatted += f"| {metric} | {value} |\n"
                
            else:
                formatted = "## 📊 FINANCIAL DATA SUMMARY\n\n"
                for metric, value in metrics.items():
                    formatted += f"• **{metric}:** {value}\n"
            
            formatted += f"\n*Data formatted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            return formatted
            
        except Exception as e:
            return self._handle_error("format_financial_data", e)
    
    def generate_recommendations(
        self, 
        analysis_data: str, 
        risk_level: str = "moderate",
        investment_horizon: str = "medium-term"
    ) -> str:
        """Generate investment recommendations based on analysis.
        
        Args:
            analysis_data (str): Analysis data to base recommendations on
            risk_level (str): Risk tolerance (conservative/moderate/aggressive)
            investment_horizon (str): Investment timeline (short-term/medium-term/long-term)
            
        Returns:
            str: Structured investment recommendations
        """
        try:
            self._log_tool_call("generate_recommendations", {
                "risk_level": risk_level,
                "investment_horizon": investment_horizon
            })
            
            # Analyze sentiment from the data
            positive_indicators = ['growth', 'increase', 'strong', 'positive', 'beat', 'exceed']
            negative_indicators = ['decline', 'decrease', 'weak', 'negative', 'miss', 'below']
            
            text_lower = analysis_data.lower()
            
            positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
            
            # Determine overall sentiment
            if positive_count > negative_count:
                sentiment = "positive"
                base_recommendation = "BUY"
            elif negative_count > positive_count:
                sentiment = "negative"
                base_recommendation = "SELL"
            else:
                sentiment = "neutral"
                base_recommendation = "HOLD"
            
            # Adjust based on risk level and horizon
            recommendations = self._adjust_recommendation_for_profile(
                base_recommendation, risk_level, investment_horizon
            )
            
            formatted_recs = f"""
## 🎯 INVESTMENT RECOMMENDATIONS

**Overall Sentiment:** {sentiment.title()}  
**Base Recommendation:** {base_recommendation}  
**Risk Profile:** {risk_level.title()}  
**Investment Horizon:** {investment_horizon.replace('-', ' ').title()}  

---

### 📋 SPECIFIC RECOMMENDATIONS

{recommendations}

---

### ⚖️ RISK CONSIDERATIONS

**For {risk_level.title()} Risk Investors:**
{self._generate_risk_considerations(risk_level, sentiment)}

---

### 📅 TIMELINE CONSIDERATIONS

**For {investment_horizon.replace('-', ' ').title()} Investors:**
{self._generate_timeline_considerations(investment_horizon, sentiment)}

---

### 🔄 PORTFOLIO ALLOCATION SUGGESTIONS

{self._generate_allocation_suggestions(risk_level, base_recommendation)}

---

*Recommendations generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
            """.strip()
            
            return formatted_recs
            
        except Exception as e:
            return self._handle_error("generate_recommendations", e)
    
    def create_markdown_report(self, title: str, sections: Dict[str, str]) -> str:
        """Create a well-formatted markdown report.
        
        Args:
            title (str): Report title
            sections (Dict[str, str]): Dictionary of section titles and content
            
        Returns:
            str: Formatted markdown report
        """
        try:
            self._log_tool_call("create_markdown_report", {"title": title, "sections_count": len(sections)})
            
            report = f"""# {title}

*Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}*

---

"""
            
            for section_title, content in sections.items():
                report += f"""## {section_title}

{content}

---

"""
            
            report += f"""
## Report Information

**Generated by:** AI Analysis System  
**Report Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Total Sections:** {len(sections)}  
**Report ID:** {datetime.now().strftime('%Y%m%d_%H%M%S')}

---

*End of Report*
            """.strip()
            
            return report
            
        except Exception as e:
            return self._handle_error("create_markdown_report", e)
    
    # Helper methods
    def _format_section_content(self, content: str) -> str:
        """Format content for better readability."""
        if len(content) > 500:
            return content[:500] + "..."
        return content
    
    def _extract_bullet_points(self, content: str) -> str:
        """Extract key points as bullet points."""
        sentences = re.split(r'[.!?]+', content)
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
        
        bullet_points = ""
        for sentence in key_sentences:
            bullet_points += f"• {sentence}\n"
        
        return bullet_points.strip()
    
    def _generate_recommendation_rationale(self, recommendation: str, financial_data: str, market_data: str) -> str:
        """Generate rationale for the recommendation."""
        rationales = {
            "BUY": "Strong financial performance and positive market sentiment support a buy recommendation.",
            "HOLD": "Mixed signals in financial performance and market sentiment suggest maintaining current position.",
            "SELL": "Concerning financial metrics and negative market sentiment indicate potential downside risk."
        }
        
        base_rationale = rationales.get(recommendation.upper(), "Analysis indicates current recommendation based on available data.")
        return f"• {base_rationale}\n• Based on comprehensive analysis of financial metrics and market conditions."
    
    def _assess_market_risk(self, market_data: str) -> str:
        """Assess market risk from market data."""
        if any(word in market_data.lower() for word in ['volatile', 'uncertain', 'concern']):
            return "High"
        elif any(word in market_data.lower() for word in ['stable', 'positive', 'strong']):
            return "Low"
        else:
            return "Moderate"
    
    def _assess_company_risk(self, financial_data: str) -> str:
        """Assess company-specific risk."""
        if any(word in financial_data.lower() for word in ['decline', 'loss', 'weak']):
            return "High"
        elif any(word in financial_data.lower() for word in ['growth', 'strong', 'increase']):
            return "Low"
        else:
            return "Moderate"
    
    def _generate_key_takeaways(self, financial_data: str, market_data: str, recommendation: str) -> str:
        """Generate key takeaways for the report."""
        takeaways = f"""
• **Financial Health:** {"Strong" if "growth" in financial_data.lower() else "Stable"}
• **Market Position:** {"Favorable" if "positive" in market_data.lower() else "Neutral"}
• **Investment Recommendation:** {recommendation.upper()}
• **Risk Level:** {"Moderate" if recommendation.upper() == "HOLD" else "Varied"}
• **Analysis Confidence:** High (based on comprehensive data analysis)
        """.strip()
        
        return takeaways
    
    def _adjust_recommendation_for_profile(self, base_rec: str, risk_level: str, horizon: str) -> str:
        """Adjust recommendations based on investor profile."""
        adjustments = {
            "conservative": {
                "BUY": "• Consider gradual position building\n• Focus on dividend-paying stocks\n• Limit exposure to 5-10% of portfolio",
                "HOLD": "• Maintain current position\n• Monitor quarterly results closely\n• Consider reducing position if fundamentals deteriorate",
                "SELL": "• Gradual position reduction recommended\n• Consider tax implications\n• Move to more stable alternatives"
            },
            "moderate": {
                "BUY": "• Standard position sizing appropriate\n• Consider dollar-cost averaging\n• Monitor market conditions closely",
                "HOLD": "• Maintain position with periodic review\n• Consider rebalancing quarterly\n• Watch for breakout signals",
                "SELL": "• Reduce position over 30-60 days\n• Consider alternatives in same sector\n• Monitor for reversal signals"
            },
            "aggressive": {
                "BUY": "• Consider larger position sizing\n• May use options for leverage\n• Set clear profit targets",
                "HOLD": "• Look for momentum signals\n• Consider short-term trading opportunities\n• Monitor technical indicators",
                "SELL": "• Exit position quickly\n• Consider short-selling opportunities\n• Look for alternatives with better risk/reward"
            }
        }
        
        return adjustments.get(risk_level, adjustments["moderate"]).get(base_rec, "Standard recommendation applies")
    
    def _generate_risk_considerations(self, risk_level: str, sentiment: str) -> str:
        """Generate risk considerations."""
        if risk_level == "conservative":
            return "• Focus on capital preservation\n• Avoid speculative positions\n• Diversify across sectors and asset classes"
        elif risk_level == "aggressive":
            return "• Higher volatility acceptable\n• Focus on growth potential\n• Consider leveraged positions carefully"
        else:
            return "• Balance growth and stability\n• Regular portfolio review recommended\n• Adjust position sizing based on conviction"
    
    def _generate_timeline_considerations(self, horizon: str, sentiment: str) -> str:
        """Generate timeline-specific considerations."""
        if "short" in horizon:
            return "• Focus on technical analysis\n• Monitor daily price action\n• Be prepared for quick exits"
        elif "long" in horizon:
            return "• Focus on fundamental analysis\n• Ignore short-term volatility\n• Consider dividend reinvestment"
        else:
            return "• Balance technical and fundamental analysis\n• Review position quarterly\n• Adjust based on changing conditions"
    
    def _generate_allocation_suggestions(self, risk_level: str, recommendation: str) -> str:
        """Generate portfolio allocation suggestions."""
        if risk_level == "conservative":
            if recommendation == "BUY":
                return "• 2-5% allocation recommended\n• Consider as satellite holding\n• Balance with bonds and defensive stocks"
            else:
                return "• Minimal allocation if any\n• Focus on dividend aristocrats\n• Maintain high cash position"
        elif risk_level == "aggressive":
            if recommendation == "BUY":
                return "• 10-15% allocation possible\n• Consider concentrated position\n• Use stop-losses for risk management"
            else:
                return "• Avoid or minimal exposure\n• Look for high-growth alternatives\n• Consider sector rotation"
        else:
            return "• 5-10% allocation appropriate\n• Regular rebalancing recommended\n• Monitor correlation with overall portfolio"