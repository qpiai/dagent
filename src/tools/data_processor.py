"""Data processing and analysis tools."""

import pandas as pd
import numpy as np
import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from .base import BaseAgnoTool


class DataProcessorTools(BaseAgnoTool):
    """Toolkit for data processing, cleaning, and analysis."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="data_processor_tools",
            tools=[
                self.extract_financial_metrics,
                self.calculate_statistics,
                self.analyze_trends,
                self.compare_values,
                self.extract_numbers_from_text
            ],
            **kwargs
        )
    
    def extract_financial_metrics(self, text: str) -> str:
        """Extract financial metrics and numbers from text data.
        
        Args:
            text (str): Text containing financial information
            
        Returns:
            str: Extracted and formatted financial metrics
        """
        try:
            self._log_tool_call("extract_financial_metrics", {"text_length": len(text)})
            
            # Common financial metric patterns
            patterns = {
                'revenue': r'revenue[\s:]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'profit': r'profit[\s:]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'net_income': r'net\s+income[\s:]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'market_cap': r'market\s+cap[\s:]*\$?([\d,\.]+)\s*([bBmMkK]?)',
                'pe_ratio': r'p\/e[\s:]*(\d+\.?\d*)',
                'eps': r'eps[\s:]*\$?([\d,\.]+)',
                'growth': r'growth[\s:]*(\d+\.?\d*)%?',
                'margin': r'margin[\s:]*(\d+\.?\d*)%?',
            }
            
            extracted_metrics = {}
            
            for metric, pattern in patterns.items():
                matches = re.findall(pattern, text.lower(), re.IGNORECASE)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            value, unit = match[0], match[1] if len(match) > 1 else ''
                        else:
                            value, unit = match, ''
                        
                        # Convert to standard format
                        try:
                            num_value = float(value.replace(',', ''))
                            if unit.lower() in ['b', 'billion']:
                                num_value *= 1_000_000_000
                            elif unit.lower() in ['m', 'million']:
                                num_value *= 1_000_000
                            elif unit.lower() in ['k', 'thousand']:
                                num_value *= 1_000
                            
                            extracted_metrics[metric] = {
                                'value': num_value,
                                'formatted': self._format_number(num_value),
                                'original': f"{value}{unit}"
                            }
                        except ValueError:
                            continue
            
            if not extracted_metrics:
                return "No financial metrics found in the provided text."
            
            result = "Extracted Financial Metrics:\n\n"
            for metric, data in extracted_metrics.items():
                result += f"• {metric.replace('_', ' ').title()}: {data['formatted']} (from: {data['original']})\n"
            
            result += f"\nExtraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("extract_financial_metrics", e)
    
    def calculate_statistics(self, data_text: str, metric_name: str = "values") -> str:
        """Calculate statistical metrics from numerical data in text.
        
        Args:
            data_text (str): Text containing numerical data
            metric_name (str): Name of the metric being analyzed
            
        Returns:
            str: Statistical analysis results
        """
        try:
            self._log_tool_call("calculate_statistics", {"metric_name": metric_name})
            
            # Extract all numbers from text
            numbers = re.findall(r'-?\d+\.?\d*', data_text)
            
            if not numbers:
                return f"No numerical data found in the provided text for {metric_name}."
            
            # Convert to float array
            values = []
            for num in numbers:
                try:
                    values.append(float(num))
                except ValueError:
                    continue
            
            if len(values) < 2:
                return f"Insufficient numerical data for statistical analysis of {metric_name}."
            
            # Calculate statistics
            values_array = np.array(values)
            
            stats = {
                'count': len(values),
                'mean': np.mean(values_array),
                'median': np.median(values_array),
                'std_dev': np.std(values_array),
                'variance': np.var(values_array),
                'min': np.min(values_array),
                'max': np.max(values_array),
                'range': np.max(values_array) - np.min(values_array),
                'q1': np.percentile(values_array, 25),
                'q3': np.percentile(values_array, 75)
            }
            
            # Calculate additional metrics
            stats['coefficient_of_variation'] = (stats['std_dev'] / stats['mean']) * 100 if stats['mean'] != 0 else 0
            stats['iqr'] = stats['q3'] - stats['q1']
            
            result = f"Statistical Analysis for: {metric_name}\n\n"
            result += f"Dataset Summary:\n"
            result += f"• Count: {stats['count']} values\n"
            result += f"• Mean: {stats['mean']:.2f}\n"
            result += f"• Median: {stats['median']:.2f}\n"
            result += f"• Standard Deviation: {stats['std_dev']:.2f}\n"
            result += f"• Variance: {stats['variance']:.2f}\n\n"
            
            result += f"Range Analysis:\n"
            result += f"• Minimum: {stats['min']:.2f}\n"
            result += f"• Maximum: {stats['max']:.2f}\n"
            result += f"• Range: {stats['range']:.2f}\n"
            result += f"• Q1 (25th percentile): {stats['q1']:.2f}\n"
            result += f"• Q3 (75th percentile): {stats['q3']:.2f}\n"
            result += f"• IQR: {stats['iqr']:.2f}\n\n"
            
            result += f"Variability Metrics:\n"
            result += f"• Coefficient of Variation: {stats['coefficient_of_variation']:.2f}%\n"
            
            # Interpret the results
            if stats['coefficient_of_variation'] < 15:
                variability = "Low variability"
            elif stats['coefficient_of_variation'] < 30:
                variability = "Moderate variability"
            else:
                variability = "High variability"
            
            result += f"• Interpretation: {variability}\n"
            result += f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("calculate_statistics", e)
    
    def analyze_trends(self, data_text: str, time_series: bool = False) -> str:
        """Analyze trends in numerical data.
        
        Args:
            data_text (str): Text containing numerical data or time series
            time_series (bool): Whether to treat as time series data
            
        Returns:
            str: Trend analysis results
        """
        try:
            self._log_tool_call("analyze_trends", {"time_series": time_series})
            
            # Extract numbers from text
            numbers = re.findall(r'-?\d+\.?\d*', data_text)
            
            if not numbers:
                return "No numerical data found for trend analysis."
            
            values = []
            for num in numbers:
                try:
                    values.append(float(num))
                except ValueError:
                    continue
            
            if len(values) < 3:
                return "Insufficient data points for trend analysis (minimum 3 required)."
            
            values_array = np.array(values)
            
            # Calculate trend metrics
            n = len(values_array)
            x = np.arange(n)
            
            # Linear regression for trend
            slope, intercept = np.polyfit(x, values_array, 1)
            
            # Calculate correlation with time
            correlation = np.corrcoef(x, values_array)[0, 1]
            
            # Calculate period-over-period changes
            changes = np.diff(values_array)
            pct_changes = (changes / values_array[:-1]) * 100
            
            # Trend direction
            if slope > 0:
                trend_direction = "Upward"
            elif slope < 0:
                trend_direction = "Downward"
            else:
                trend_direction = "Flat"
            
            # Trend strength
            abs_corr = abs(correlation)
            if abs_corr > 0.8:
                trend_strength = "Strong"
            elif abs_corr > 0.5:
                trend_strength = "Moderate"
            elif abs_corr > 0.3:
                trend_strength = "Weak"
            else:
                trend_strength = "No clear trend"
            
            result = f"Trend Analysis Results:\n\n"
            result += f"Data Summary:\n"
            result += f"• Data Points: {n}\n"
            result += f"• Start Value: {values_array[0]:.2f}\n"
            result += f"• End Value: {values_array[-1]:.2f}\n"
            result += f"• Total Change: {values_array[-1] - values_array[0]:.2f}\n"
            result += f"• Total Change (%): {((values_array[-1] - values_array[0]) / values_array[0] * 100):.2f}%\n\n"
            
            result += f"Trend Characteristics:\n"
            result += f"• Direction: {trend_direction}\n"
            result += f"• Strength: {trend_strength}\n"
            result += f"• Slope: {slope:.4f}\n"
            result += f"• Correlation: {correlation:.4f}\n\n"
            
            result += f"Change Analysis:\n"
            result += f"• Average Change: {np.mean(changes):.2f}\n"
            result += f"• Average % Change: {np.mean(pct_changes):.2f}%\n"
            result += f"• Largest Increase: {np.max(changes):.2f}\n"
            result += f"• Largest Decrease: {np.min(changes):.2f}\n"
            result += f"• Volatility (Std Dev of changes): {np.std(changes):.2f}\n"
            
            result += f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("analyze_trends", e)
    
    def compare_values(self, baseline_text: str, comparison_text: str, metric_name: str = "values") -> str:
        """Compare numerical values between two data sets.
        
        Args:
            baseline_text (str): Baseline data text
            comparison_text (str): Comparison data text
            metric_name (str): Name of the metric being compared
            
        Returns:
            str: Comparison analysis results
        """
        try:
            self._log_tool_call("compare_values", {"metric_name": metric_name})
            
            # Extract numbers from both texts
            baseline_numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', baseline_text) if x]
            comparison_numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', comparison_text) if x]
            
            if not baseline_numbers or not comparison_numbers:
                return f"Insufficient numerical data found for comparison of {metric_name}."
            
            # Calculate averages for comparison
            baseline_avg = np.mean(baseline_numbers)
            comparison_avg = np.mean(comparison_numbers)
            
            # Calculate changes
            absolute_change = comparison_avg - baseline_avg
            percent_change = (absolute_change / baseline_avg) * 100 if baseline_avg != 0 else 0
            
            # Determine significance
            if abs(percent_change) > 20:
                significance = "Significant"
            elif abs(percent_change) > 10:
                significance = "Moderate"
            elif abs(percent_change) > 5:
                significance = "Slight"
            else:
                significance = "Minimal"
            
            # Determine direction
            if absolute_change > 0:
                direction = "increase"
                trend_icon = "📈"
            elif absolute_change < 0:
                direction = "decrease"
                trend_icon = "📉"
            else:
                direction = "no change"
                trend_icon = "➡️"
            
            result = f"Comparison Analysis for: {metric_name}\n\n"
            result += f"{trend_icon} Summary:\n"
            result += f"• Baseline Average: {baseline_avg:.2f}\n"
            result += f"• Comparison Average: {comparison_avg:.2f}\n"
            result += f"• Absolute Change: {absolute_change:.2f}\n"
            result += f"• Percentage Change: {percent_change:.2f}%\n"
            result += f"• Direction: {direction.title()}\n"
            result += f"• Significance: {significance}\n\n"
            
            result += f"Detailed Statistics:\n"
            result += f"Baseline Data:\n"
            result += f"• Count: {len(baseline_numbers)}\n"
            result += f"• Min: {min(baseline_numbers):.2f}\n"
            result += f"• Max: {max(baseline_numbers):.2f}\n"
            result += f"• Std Dev: {np.std(baseline_numbers):.2f}\n\n"
            
            result += f"Comparison Data:\n"
            result += f"• Count: {len(comparison_numbers)}\n"
            result += f"• Min: {min(comparison_numbers):.2f}\n"
            result += f"• Max: {max(comparison_numbers):.2f}\n"
            result += f"• Std Dev: {np.std(comparison_numbers):.2f}\n"
            
            result += f"\nComparison completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("compare_values", e)
    
    def extract_numbers_from_text(self, text: str, number_type: str = "all") -> str:
        """Extract and categorize numbers from text.
        
        Args:
            text (str): Text to extract numbers from
            number_type (str): Type of numbers to extract ('all', 'currency', 'percentages', 'integers')
            
        Returns:
            str: Extracted numbers with categorization
        """
        try:
            self._log_tool_call("extract_numbers_from_text", {"number_type": number_type})
            
            extracted = {
                'currency': [],
                'percentages': [],
                'decimals': [],
                'integers': [],
                'large_numbers': []
            }
            
            # Currency patterns
            currency_pattern = r'\$[\d,]+\.?\d*[bBmMkK]?'
            extracted['currency'] = re.findall(currency_pattern, text)
            
            # Percentage patterns
            percentage_pattern = r'\d+\.?\d*%'
            extracted['percentages'] = re.findall(percentage_pattern, text)
            
            # All numbers
            all_numbers = re.findall(r'-?\d+\.?\d*', text)
            
            for num_str in all_numbers:
                try:
                    num = float(num_str)
                    if '.' in num_str:
                        extracted['decimals'].append(num_str)
                    else:
                        extracted['integers'].append(num_str)
                    
                    if abs(num) >= 1_000_000:
                        extracted['large_numbers'].append(num_str)
                except ValueError:
                    continue
            
            # Filter based on number_type
            if number_type != "all":
                if number_type in extracted:
                    filtered_result = {number_type: extracted[number_type]}
                    extracted = filtered_result
            
            result = f"Number Extraction Results:\n\n"
            
            for category, numbers in extracted.items():
                if numbers:
                    result += f"{category.replace('_', ' ').title()}:\n"
                    for i, num in enumerate(numbers[:10], 1):  # Limit to first 10
                        result += f"  {i}. {num}\n"
                    if len(numbers) > 10:
                        result += f"  ... and {len(numbers) - 10} more\n"
                    result += f"  Total found: {len(numbers)}\n\n"
            
            if not any(extracted.values()):
                result += "No numbers found matching the specified criteria.\n"
            
            result += f"Extraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("extract_numbers_from_text", e)
    
    def _format_number(self, num: float) -> str:
        """Format large numbers with appropriate suffixes."""
        if abs(num) >= 1_000_000_000_000:  # Trillion
            return f"${num/1_000_000_000_000:.2f}T"
        elif abs(num) >= 1_000_000_000:  # Billion
            return f"${num/1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:  # Million
            return f"${num/1_000_000:.2f}M"
        elif abs(num) >= 1_000:  # Thousand
            return f"${num/1_000:.2f}K"
        else:
            return f"${num:.2f}"