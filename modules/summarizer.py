"""
Summarization Module
Generates extractive summaries using ranked sentences
"""

from typing import List, Dict
from .sentence_ranker import SentenceRanker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Summarizer:
    """Generate extractive summaries from text"""
    
    def __init__(self):
        self.ranker = SentenceRanker()
    
    def generate_summary(self, sentences: List[str], 
                        summary_ratio: float = 0.7,
                        min_sentences: int = 20,
                        max_sentences: int = None) -> Dict[str, any]:
        """
        Generate comprehensive extractive summary (like ChatGPT study notes)
        
        Args:
            sentences: List of sentences from document
            summary_ratio: Ratio of sentences to include (0-1) - default 70%
            min_sentences: Minimum number of sentences
            max_sentences: Maximum number of sentences (None for no limit)
            
        Returns:
            Dictionary with summary text and metadata
        """
        if not sentences:
            return {'summary': '', 'sentences': [], 'ratio': 0}
        
        # Calculate target - we want comprehensive coverage, not brief summary
        total_sentences = len(sentences)
        target_count = max(min_sentences, int(total_sentences * summary_ratio))
        
        if max_sentences:
            target_count = min(target_count, max_sentences)
        
        # Get top sentences - comprehensive selection
        summary_sentences = self.ranker.get_top_sentences(
            sentences, 
            top_n=target_count,
            method='combined'
        )
        
        # Combine into paragraph
        summary_text = ' '.join(summary_sentences)
        
        logger.info(f"Generated comprehensive summary with {len(summary_sentences)} sentences "
                   f"from {len(sentences)} total ({len(summary_sentences)/len(sentences)*100:.1f}% coverage)")
        
        return {
            'summary': summary_text,
            'sentences': summary_sentences,
            'original_count': len(sentences),
            'summary_count': len(summary_sentences),
            'ratio': len(summary_sentences) / len(sentences)
        }
    
    def generate_key_points(self, sentences: List[str], 
                           top_n: int = 50) -> List[str]:
        """
        Generate comprehensive key points (bullet format) - like study notes
        
        Args:
            sentences: List of sentences
            top_n: Number of key points (default 50 for comprehensive coverage)
            
        Returns:
            List of key point sentences
        """
        if not sentences:
            return []
        
        # Calculate adaptive number based on document length
        total = len(sentences)
        adaptive_n = min(top_n, max(30, int(total * 0.6)))  # 60% coverage, min 30 points
        
        # Get top N sentences
        key_sentences = self.ranker.get_top_sentences(
            sentences,
            top_n=min(adaptive_n, len(sentences)),
            method='combined'
        )
        
        logger.info(f"Generated {len(key_sentences)} comprehensive key points")
        
        return key_sentences
    
    def generate_layered_summary(self, sentences: List[str]) -> Dict[str, any]:
        """
        Generate multi-level summary (brief, medium, comprehensive)
        
        Args:
            sentences: List of sentences
            
        Returns:
            Dictionary with summaries at different lengths
        """
        total = len(sentences)
        
        # Brief: 20% of sentences (min 10, no max)
        brief_count = max(10, int(total * 0.2))
        
        # Medium: 50% of sentences (min 30, no max)
        medium_count = max(30, int(total * 0.5))
        
        # Comprehensive: 75% of sentences (min 50, no max)
        detailed_count = max(50, int(total * 0.75))
        
        # Generate each level
        brief = self.ranker.get_top_sentences(sentences, top_n=brief_count)
        medium = self.ranker.get_top_sentences(sentences, top_n=medium_count)
        detailed = self.ranker.get_top_sentences(sentences, top_n=detailed_count)
        
        return {
            'brief': {
                'text': ' '.join(brief),
                'sentences': brief,
                'count': len(brief)
            },
            'medium': {
                'text': ' '.join(medium),
                'sentences': medium,
                'count': len(medium)
            },
            'detailed': {
                'text': ' '.join(detailed),
                'sentences': detailed,
                'count': len(detailed)
            }
        }
    
    def generate_sectional_summary(self, sections: List[Dict[str, str]],
                                  sentences_per_section: int = 3) -> List[Dict[str, any]]:
        """
        Generate summary for each section separately
        
        Args:
            sections: List of dicts with 'title' and 'content'
            sentences_per_section: Number of sentences per section summary
            
        Returns:
            List of section summaries
        """
        summaries = []
        
        for section in sections:
            title = section.get('title', 'Section')
            content = section.get('content', '')
            
            # Split into sentences
            from .text_preprocessor import TextPreprocessor
            preprocessor = TextPreprocessor()
            sentences = preprocessor.tokenize_sentences(content)
            
            if not sentences:
                continue
            
            # Generate summary for this section
            top_sentences = self.ranker.get_top_sentences(
                sentences,
                top_n=min(sentences_per_section, len(sentences))
            )
            
            summaries.append({
                'title': title,
                'summary': ' '.join(top_sentences),
                'sentences': top_sentences
            })
        
        logger.info(f"Generated summaries for {len(summaries)} sections")
        
        return summaries


if __name__ == "__main__":
    # Test the summarizer
    summarizer = Summarizer()
    sample_sentences = [
        "Natural language processing is a subfield of artificial intelligence.",
        "It focuses on the interaction between computers and human language.",
        "NLP combines computational linguistics with machine learning.",
        "Applications include translation, sentiment analysis, and chatbots.",
        "Deep learning has revolutionized NLP in recent years.",
        "Models like BERT and GPT have achieved remarkable results.",
        "Text preprocessing is an important first step.",
        "Tokenization breaks text into words or subwords."
    ]
    
    result = summarizer.generate_summary(sample_sentences, summary_ratio=0.4)
    print(f"Summary ({result['summary_count']} sentences): {result['summary']}")
