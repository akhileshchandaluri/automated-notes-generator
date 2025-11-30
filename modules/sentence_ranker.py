"""
Sentence Ranking Module
Ranks sentences by importance using TextRank and TF-IDF
"""

import re
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentenceRanker:
    """Rank sentences by importance using multiple algorithms"""
    
    def __init__(self):
        pass
    
    def rank_sentences(self, sentences: List[str], 
                      method: str = 'combined') -> List[Tuple[int, float, str]]:
        """
        Rank sentences using specified method
        
        Args:
            sentences: List of sentences
            method: 'textrank', 'tfidf', 'position', or 'combined'
            
        Returns:
            List of tuples (index, score, sentence) sorted by score
        """
        if not sentences:
            return []
        
        if method == 'textrank':
            scores = self._textrank_scores(sentences)
        elif method == 'tfidf':
            scores = self._tfidf_scores(sentences)
        elif method == 'position':
            scores = self._position_scores(sentences)
        else:  # combined
            scores = self._combined_scores(sentences)
        
        # Create ranked list
        ranked = [(i, scores[i], sentences[i]) for i in range(len(sentences))]
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Ranked {len(sentences)} sentences using {method} method")
        
        return ranked
    
    def _textrank_scores(self, sentences: List[str]) -> np.ndarray:
        """
        Calculate TextRank scores for sentences
        
        TextRank is based on PageRank - sentences are nodes,
        edges weighted by similarity
        """
        try:
            # Build similarity matrix
            similarity_matrix = self._build_similarity_matrix(sentences)
            
            # Convert to graph
            nx_graph = nx.from_numpy_array(similarity_matrix)
            
            # Calculate PageRank scores
            scores = nx.pagerank(nx_graph, max_iter=100)
            
            # Convert to array
            score_array = np.array([scores[i] for i in range(len(sentences))])
            
            return score_array
        except Exception as e:
            logger.error(f"TextRank error: {str(e)}")
            return np.ones(len(sentences))
    
    def _build_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """Build sentence similarity matrix using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            return similarity_matrix
        except Exception as e:
            logger.error(f"Similarity matrix error: {str(e)}")
            return np.eye(len(sentences))
    
    def _tfidf_scores(self, sentences: List[str]) -> np.ndarray:
        """Calculate average TF-IDF score for each sentence"""
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Average TF-IDF score per sentence
            scores = np.asarray(tfidf_matrix.mean(axis=1)).flatten()
            
            return scores
        except Exception as e:
            logger.error(f"TF-IDF scoring error: {str(e)}")
            return np.ones(len(sentences))
    
    def _position_scores(self, sentences: List[str]) -> np.ndarray:
        """
        Score sentences based on position and content quality
        First and last sentences often more important, but penalize low-content
        """
        n = len(sentences)
        scores = np.zeros(n)
        
        for i in range(n):
            # Base position score
            if i < 3:
                base_score = 1.0 - (i * 0.1)
            elif i >= n - 2:
                base_score = 0.8
            else:
                base_score = 0.5
            
            # Content quality multiplier
            sentence = sentences[i]
            word_count = len(sentence.split())
            
            # Penalize very short or very long sentences
            if word_count < 8:
                base_score *= 0.5
            elif word_count > 60:
                base_score *= 0.7
            
            # Penalize sentences with excessive numbers/symbols
            non_word_ratio = len(re.findall(r'[^\w\s]', sentence)) / max(len(sentence), 1)
            if non_word_ratio > 0.3:
                base_score *= 0.6
            
            # Boost sentences with technical terms
            technical_terms = ['design', 'implement', 'analyze', 'evaluate', 'develop',
                             'method', 'approach', 'technique', 'algorithm', 'system',
                             'process', 'function', 'component', 'module', 'architecture']
            if any(term in sentence.lower() for term in technical_terms):
                base_score *= 1.2
            
            scores[i] = min(base_score, 1.0)
        
        return scores
    
    def _combined_scores(self, sentences: List[str]) -> np.ndarray:
        """Combine multiple scoring methods"""
        # Get scores from each method
        textrank = self._textrank_scores(sentences)
        tfidf = self._tfidf_scores(sentences)
        position = self._position_scores(sentences)
        
        # Normalize scores to 0-1 range
        textrank = self._normalize(textrank)
        tfidf = self._normalize(tfidf)
        position = self._normalize(position)
        
        # Weighted combination
        weights = {
            'textrank': 0.4,
            'tfidf': 0.4,
            'position': 0.2
        }
        
        combined = (textrank * weights['textrank'] + 
                   tfidf * weights['tfidf'] + 
                   position * weights['position'])
        
        return combined
    
    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to 0-1 range"""
        if scores.max() == scores.min():
            return np.ones_like(scores)
        return (scores - scores.min()) / (scores.max() - scores.min())
    
    def get_top_sentences(self, sentences: List[str], 
                         top_n: int = None, 
                         top_percent: float = 0.3,
                         method: str = 'combined') -> List[str]:
        """
        Get top N most important sentences
        
        Args:
            sentences: List of sentences
            top_n: Number of sentences to return (overrides top_percent)
            top_percent: Percentage of sentences to return (default 30%)
            method: Ranking method to use
            
        Returns:
            List of top sentences in original order
        """
        if not sentences:
            return []
        
        # Rank sentences
        ranked = self.rank_sentences(sentences, method)
        
        # Determine how many to select
        if top_n is None:
            top_n = max(3, int(len(sentences) * top_percent))
        
        # Get top N sentence indices
        top_indices = [idx for idx, score, sent in ranked[:top_n]]
        top_indices.sort()  # Keep original order
        
        # Return sentences in original order
        return [sentences[i] for i in top_indices]
    
    def score_by_keywords(self, sentences: List[str], 
                         keywords: List[str]) -> np.ndarray:
        """
        Score sentences based on keyword presence
        
        Args:
            sentences: List of sentences
            keywords: List of important keywords
            
        Returns:
            Array of keyword-based scores
        """
        scores = np.zeros(len(sentences))
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            # Count keyword occurrences
            keyword_count = sum(1 for kw in keywords if kw.lower() in sentence_lower)
            scores[i] = keyword_count
        
        return self._normalize(scores)


if __name__ == "__main__":
    # Test the ranker
    ranker = SentenceRanker()
    sample_sentences = [
        "Machine learning is a field of artificial intelligence.",
        "It enables computers to learn from data.",
        "Deep learning uses neural networks with multiple layers.",
        "This is a less important sentence.",
        "Neural networks are inspired by biological neurons."
    ]
    
    top_sentences = ranker.get_top_sentences(sample_sentences, top_n=3)
    print(f"Top 3 sentences: {top_sentences}")
