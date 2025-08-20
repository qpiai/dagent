"""Natural Language Processing tools."""

import re
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime
from .base import BaseAgnoTool


class NaturalLanguageProcessorTools(BaseAgnoTool):
    """Toolkit for natural language processing and text analysis."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="natural_language_processor_tools",
            tools=[
                self.analyze_sentiment,
                self.extract_entities,
                self.analyze_text_metrics,
                self.extract_keywords,
                self.classify_text_tone
            ],
            **kwargs
        )
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text using keyword-based approach.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Sentiment analysis results
        """
        try:
            self._log_tool_call("analyze_sentiment", {"text_length": len(text)})
            
            # Define sentiment keywords
            positive_words = [
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'outstanding',
                'positive', 'strong', 'growth', 'increase', 'profit', 'success', 'beat', 
                'exceed', 'rise', 'gain', 'improve', 'upgrade', 'bullish', 'optimistic',
                'confident', 'robust', 'solid', 'impressive', 'favorable'
            ]
            
            negative_words = [
                'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor', 'weak',
                'negative', 'decline', 'decrease', 'loss', 'fail', 'miss', 'fall', 'drop',
                'concern', 'worry', 'risk', 'downgrade', 'bearish', 'pessimistic',
                'uncertain', 'volatile', 'challenging', 'difficult', 'unfavorable'
            ]
            
            neutral_words = [
                'stable', 'steady', 'maintain', 'hold', 'unchanged', 'flat', 'normal',
                'standard', 'typical', 'average', 'moderate', 'neutral', 'balanced'
            ]
            
            text_lower = text.lower()
            
            # Count sentiment words
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            neutral_count = sum(1 for word in neutral_words if word in text_lower)
            
            total_sentiment_words = positive_count + negative_count + neutral_count
            
            if total_sentiment_words == 0:
                sentiment = "Neutral"
                confidence = 0.5
                dominant_words = []
            else:
                # Calculate sentiment scores
                positive_score = positive_count / total_sentiment_words
                negative_score = negative_count / total_sentiment_words
                neutral_score = neutral_count / total_sentiment_words
                
                # Determine overall sentiment
                if positive_score > negative_score and positive_score > neutral_score:
                    sentiment = "Positive"
                    confidence = positive_score
                    dominant_words = [word for word in positive_words if word in text_lower][:5]
                elif negative_score > positive_score and negative_score > neutral_score:
                    sentiment = "Negative"
                    confidence = negative_score
                    dominant_words = [word for word in negative_words if word in text_lower][:5]
                else:
                    sentiment = "Neutral"
                    confidence = neutral_score
                    dominant_words = [word for word in neutral_words if word in text_lower][:5]
            
            # Calculate additional metrics
            total_words = len(text.split())
            sentiment_density = total_sentiment_words / total_words if total_words > 0 else 0
            
            result = f"""
Sentiment Analysis Results:

Overall Sentiment: {sentiment}
Confidence Score: {confidence:.2f}

Detailed Breakdown:
• Positive indicators: {positive_count} ({positive_count/total_sentiment_words*100:.1f}% of sentiment words)
• Negative indicators: {negative_count} ({negative_count/total_sentiment_words*100:.1f}% of sentiment words)
• Neutral indicators: {neutral_count} ({neutral_count/total_sentiment_words*100:.1f}% of sentiment words)

Text Metrics:
• Total words: {total_words}
• Sentiment words found: {total_sentiment_words}
• Sentiment density: {sentiment_density:.2%}

Key sentiment indicators found: {', '.join(dominant_words[:5])}

Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("analyze_sentiment", e)
    
    def extract_entities(self, text: str) -> str:
        """Extract named entities and important terms from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Entity extraction results
        """
        try:
            self._log_tool_call("extract_entities", {"text_length": len(text)})
            
            # Define entity patterns
            patterns = {
                'companies': r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*(?:\s+(?:Inc|Corp|Corporation|Ltd|Limited|LLC|Co|Company))\b',
                'stock_symbols': r'\b[A-Z]{1,5}\b(?=\s|$|[^a-zA-Z])',
                'money': r'\$[\d,]+(?:\.\d{2})?[BMK]?',
                'percentages': r'\d+(?:\.\d+)?%',
                'dates': r'\b(?:Q[1-4]\s+\d{4}|\d{4}|\w+\s+\d{1,2},?\s+\d{4})\b',
                'financial_terms': r'\b(?:revenue|profit|earnings|EBITDA|margin|P/E|market cap|valuation)\b'
            }
            
            entities = {}
            
            for entity_type, pattern in patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Remove duplicates and clean up
                    cleaned_matches = list(set([match.strip() for match in matches if match.strip()]))
                    entities[entity_type] = cleaned_matches
            
            # Extract potential company names (capitalized words)
            company_candidates = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            common_words = {'The', 'This', 'That', 'With', 'From', 'When', 'Where', 'What', 'How'}
            companies = [comp for comp in set(company_candidates) if comp not in common_words and len(comp) > 2]
            
            if companies:
                if 'potential_companies' not in entities:
                    entities['potential_companies'] = []
                entities['potential_companies'].extend(companies[:5])  # Limit to top 5
            
            if not entities:
                return "No entities found in the provided text."
            
            result = "Entity Extraction Results:\n\n"
            
            for entity_type, entity_list in entities.items():
                if entity_list:
                    result += f"{entity_type.replace('_', ' ').title()}:\n"
                    for i, entity in enumerate(entity_list[:10], 1):  # Limit to 10 per type
                        result += f"  {i}. {entity}\n"
                    if len(entity_list) > 10:
                        result += f"  ... and {len(entity_list) - 10} more\n"
                    result += "\n"
            
            result += f"Extraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("extract_entities", e)
    
    def analyze_text_metrics(self, text: str) -> str:
        """Analyze basic text metrics and readability.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Text metrics analysis
        """
        try:
            self._log_tool_call("analyze_text_metrics", {"text_length": len(text)})
            
            # Basic metrics
            char_count = len(text)
            word_count = len(text.split())
            sentence_count = len(re.findall(r'[.!?]+', text))
            paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Calculate averages
            avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
            avg_chars_per_word = char_count / word_count if word_count > 0 else 0
            
            # Word frequency analysis
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = Counter(words)
            most_common = word_freq.most_common(10)
            
            # Unique word ratio
            unique_words = len(set(words))
            unique_ratio = unique_words / word_count if word_count > 0 else 0
            
            # Simple readability score (based on sentence and word length)
            if avg_words_per_sentence < 15 and avg_chars_per_word < 5:
                readability = "Easy"
            elif avg_words_per_sentence < 20 and avg_chars_per_word < 6:
                readability = "Moderate"
            else:
                readability = "Complex"
            
            result = f"""
Text Metrics Analysis:

Basic Statistics:
• Character count: {char_count:,}
• Word count: {word_count:,}
• Sentence count: {sentence_count}
• Paragraph count: {paragraph_count}

Averages:
• Words per sentence: {avg_words_per_sentence:.1f}
• Characters per word: {avg_chars_per_word:.1f}
• Unique word ratio: {unique_ratio:.2%}

Vocabulary Analysis:
• Total unique words: {unique_words:,}
• Most frequent words: {', '.join([f"{word}({count})" for word, count in most_common[:5]])}

Readability Assessment: {readability}

Text Complexity Indicators:
• Sentence length: {'Long' if avg_words_per_sentence > 20 else 'Medium' if avg_words_per_sentence > 10 else 'Short'}
• Word complexity: {'High' if avg_chars_per_word > 6 else 'Medium' if avg_chars_per_word > 4 else 'Low'}
• Vocabulary diversity: {'High' if unique_ratio > 0.7 else 'Medium' if unique_ratio > 0.5 else 'Low'}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("analyze_text_metrics", e)
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> str:
        """Extract key terms and phrases from text.
        
        Args:
            text (str): Text to analyze
            max_keywords (int): Maximum number of keywords to extract
            
        Returns:
            str: Keyword extraction results
        """
        try:
            self._log_tool_call("extract_keywords", {"max_keywords": max_keywords})
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
                'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
                'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those'
            }
            
            # Extract words and filter
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            filtered_words = [word for word in words if word not in stop_words]
            
            # Count word frequency
            word_freq = Counter(filtered_words)
            
            # Extract phrases (2-3 word combinations)
            phrases = []
            words_list = text.split()
            for i in range(len(words_list) - 1):
                phrase = f"{words_list[i]} {words_list[i+1]}".lower()
                if len(phrase) > 6 and not any(stop in phrase for stop in ['the ', 'and ', 'or ', 'in ', 'on ']):
                    phrases.append(phrase)
            
            phrase_freq = Counter(phrases)
            
            # Get top keywords and phrases
            top_words = word_freq.most_common(max_keywords)
            top_phrases = phrase_freq.most_common(max_keywords // 2)
            
            result = f"""
Keyword Extraction Results:

Top Single Keywords:
"""
            
            for i, (word, count) in enumerate(top_words[:max_keywords], 1):
                result += f"{i}. {word} (frequency: {count})\n"
            
            if top_phrases:
                result += f"\nTop Phrases:\n"
                for i, (phrase, count) in enumerate(top_phrases, 1):
                    result += f"{i}. {phrase} (frequency: {count})\n"
            
            # Calculate keyword density
            total_words = len(filtered_words)
            if top_words:
                top_keyword_density = top_words[0][1] / total_words if total_words > 0 else 0
                result += f"\nKeyword Analysis:\n"
                result += f"• Total filtered words: {total_words}\n"
                result += f"• Top keyword density: {top_keyword_density:.2%}\n"
                result += f"• Unique keywords: {len(word_freq)}\n"
            
            result += f"\nExtraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return self._handle_error("extract_keywords", e)
    
    def classify_text_tone(self, text: str) -> str:
        """Classify the tone and style of text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Tone classification results
        """
        try:
            self._log_tool_call("classify_text_tone", {"text_length": len(text)})
            
            text_lower = text.lower()
            
            # Define tone indicators
            tone_indicators = {
                'professional': ['analysis', 'data', 'report', 'results', 'findings', 'conclusion', 'recommend'],
                'urgent': ['immediate', 'urgent', 'critical', 'important', 'must', 'now', 'quickly'],
                'confident': ['definitely', 'certainly', 'clearly', 'obviously', 'undoubtedly', 'strong', 'solid'],
                'cautious': ['may', 'might', 'could', 'possibly', 'perhaps', 'uncertain', 'potential'],
                'analytical': ['therefore', 'however', 'moreover', 'furthermore', 'consequently', 'analysis'],
                'emotional': ['excited', 'disappointed', 'concerned', 'worried', 'pleased', 'frustrated']
            }
            
            tone_scores = {}
            for tone, indicators in tone_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text_lower)
                tone_scores[tone] = score
            
            # Determine dominant tone
            if not any(tone_scores.values()):
                dominant_tone = "Neutral"
                tone_strength = "Low"
            else:
                dominant_tone = max(tone_scores.keys(), key=lambda x: tone_scores[x])
                max_score = tone_scores[dominant_tone]
                total_indicators = sum(tone_scores.values())
                tone_strength = "High" if max_score > 3 else "Medium" if max_score > 1 else "Low"
            
            # Analyze sentence structure for formality
            avg_sentence_length = len(text.split()) / len(re.findall(r'[.!?]+', text)) if re.findall(r'[.!?]+', text) else 0
            
            if avg_sentence_length > 20:
                formality = "Formal"
            elif avg_sentence_length > 10:
                formality = "Semi-formal"
            else:
                formality = "Informal"
            
            # Check for technical language
            technical_terms = ['analysis', 'data', 'metrics', 'performance', 'optimization', 'implementation']
            technical_count = sum(1 for term in technical_terms if term in text_lower)
            technical_level = "High" if technical_count > 3 else "Medium" if technical_count > 1 else "Low"
            
            result = f"""
Text Tone Classification:

Primary Tone: {dominant_tone}
Tone Strength: {tone_strength}
Formality Level: {formality}
Technical Level: {technical_level}

Tone Breakdown:
"""
            
            for tone, score in sorted(tone_scores.items(), key=lambda x: x[1], reverse=True):
                if score > 0:
                    result += f"• {tone.title()}: {score} indicators\n"
            
            result += f"""
Style Characteristics:
• Average sentence length: {avg_sentence_length:.1f} words
• Communication style: {formality}
• Technical complexity: {technical_level}
• Overall tone confidence: {tone_strength}

Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            return result
            
        except Exception as e:
            return self._handle_error("classify_text_tone", e)