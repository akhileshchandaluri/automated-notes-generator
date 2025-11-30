"""
Keyword Extraction Module
Extracts important keywords and keyphrases using multiple methods
"""

import re
from collections import Counter
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import spacy, but make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load('en_core_web_sm')
    except:
        logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    logger.warning("spaCy not installed. Some features will be limited.")
    SPACY_AVAILABLE = False
    nlp = None

# Try to import RAKE
try:
    from rake_nltk import Rake
    RAKE_AVAILABLE = True
except ImportError:
    logger.warning("RAKE not installed. Install with: pip install rake-nltk")
    RAKE_AVAILABLE = False


class KeywordExtractor:
    """Extract keywords and key phrases from text"""
    
    def __init__(self):
        self.rake = Rake() if RAKE_AVAILABLE else None
        
    def extract_keywords(self, text: str, sentences: List[str], 
                        top_n: int = 15) -> Dict[str, any]:
        """
        Extract keywords using multiple methods
        
        Args:
            text: Full text
            sentences: List of sentences
            top_n: Number of top keywords to return
            
        Returns:
            Dictionary with keywords from different methods
        """
        results = {}
        
        # Method 1: TF-IDF
        tfidf_keywords = self._extract_tfidf_keywords(sentences, top_n)
        results['tfidf'] = tfidf_keywords
        
        # Method 2: RAKE (if available)
        if self.rake:
            rake_keywords = self._extract_rake_keywords(text, top_n)
            results['rake'] = rake_keywords
        
        # Method 3: spaCy noun chunks (if available)
        if SPACY_AVAILABLE and nlp:
            noun_phrases = self._extract_noun_phrases(text, top_n)
            results['noun_phrases'] = noun_phrases
        
        # Method 4: Simple frequency-based
        freq_keywords = self._extract_frequency_keywords(text, top_n)
        results['frequency'] = freq_keywords
        
        # Combine and rank all keywords
        combined = self._combine_keywords(results, top_n)
        results['combined'] = combined
        
        logger.info(f"Extracted {len(combined)} combined keywords")
        
        return results
    
    def _extract_tfidf_keywords(self, sentences: List[str], top_n: int) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF"""
        try:
            if len(sentences) < 2:
                return []
            
            vectorizer = TfidfVectorizer(
                max_features=top_n * 2,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
            
            # Sort by score
            top_indices = avg_scores.argsort()[-top_n:][::-1]
            keywords = [(feature_names[i], avg_scores[i]) for i in top_indices]
            
            return keywords
        except Exception as e:
            logger.error(f"TF-IDF extraction error: {str(e)}")
            return []
    
    def _extract_rake_keywords(self, text: str, top_n: int) -> List[Tuple[str, float]]:
        """Extract keywords using RAKE algorithm"""
        try:
            self.rake.extract_keywords_from_text(text)
            keywords_scores = self.rake.get_ranked_phrases_with_scores()
            return keywords_scores[:top_n]
        except Exception as e:
            logger.error(f"RAKE extraction error: {str(e)}")
            return []
    
    def _extract_noun_phrases(self, text: str, top_n: int) -> List[str]:
        """Extract noun phrases using spaCy"""
        try:
            doc = nlp(text[:1000000])  # Limit text length for spaCy
            
            # Extract noun chunks
            noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks 
                          if len(chunk.text.split()) <= 4]
            
            # Count frequency
            chunk_freq = Counter(noun_chunks)
            
            return [phrase for phrase, _ in chunk_freq.most_common(top_n)]
        except Exception as e:
            logger.error(f"spaCy extraction error: {str(e)}")
            return []
    
    def _extract_frequency_keywords(self, text: str, top_n: int) -> List[Tuple[str, int]]:
        """Extract keywords based on frequency"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Common stopwords
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 
                    'will', 'would', 'could', 'should', 'their', 'there', 
                    'which', 'when', 'where', 'what', 'these', 'those'}
        
        words = [w for w in words if w not in stopwords]
        
        # Count frequency
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)
    
    def _combine_keywords(self, results: Dict[str, any], top_n: int) -> List[Tuple[str, float]]:
        """Combine keywords from all methods with weighted scoring"""
        keyword_scores = {}
        
        # Weight for each method
        weights = {
            'tfidf': 0.35,
            'rake': 0.25,
            'noun_phrases': 0.20,
            'frequency': 0.20
        }
        
        # Process TF-IDF
        if 'tfidf' in results:
            for keyword, score in results['tfidf']:
                keyword_scores[keyword] = keyword_scores.get(keyword, 0) + score * weights['tfidf']
        
        # Process RAKE
        if 'rake' in results:
            for score, keyword in results['rake']:
                # Normalize RAKE scores (they can be large)
                normalized_score = min(score / 10, 1.0)
                keyword_scores[keyword] = keyword_scores.get(keyword, 0) + normalized_score * weights['rake']
        
        # Process noun phrases
        if 'noun_phrases' in results:
            max_rank = len(results['noun_phrases'])
            for rank, phrase in enumerate(results['noun_phrases']):
                score = (max_rank - rank) / max_rank
                keyword_scores[phrase] = keyword_scores.get(phrase, 0) + score * weights['noun_phrases']
        
        # Process frequency
        if 'frequency' in results:
            max_freq = results['frequency'][0][1] if results['frequency'] else 1
            for word, freq in results['frequency']:
                score = freq / max_freq
                keyword_scores[word] = keyword_scores.get(word, 0) + score * weights['frequency']
        
        # Sort by combined score
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:top_n]
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms (capitalized, hyphenated, or special patterns)"""
        terms = set()
        
        # Capitalized terms (likely technical)
        caps_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        terms.update(caps_terms)
        
        # Hyphenated terms
        hyphenated = re.findall(r'\b\w+-\w+\b', text)
        terms.update(hyphenated)
        
        # Terms with special characters (equations, formulas)
        special_terms = re.findall(r'\b\w+[°²³±≈≠≤≥]\w*\b', text)
        terms.update(special_terms)
        
        return list(terms)


if __name__ == "__main__":
    # Test the extractor
    extractor = KeywordExtractor()
    sample_text = """
    Machine learning is a subset of artificial intelligence. 
    Neural networks are used for deep learning applications.
    Natural language processing helps computers understand human language.
    """
    sentences = sample_text.split('. ')
    results = extractor.extract_keywords(sample_text, sentences, top_n=5)
    print(f"Top keywords: {results['combined']}")
