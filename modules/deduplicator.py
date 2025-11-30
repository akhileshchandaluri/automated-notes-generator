"""
Content Deduplicator
Removes duplicate and near-duplicate content using semantic similarity
"""

import re
from typing import List, Set, Tuple
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentDeduplicator:
    """Remove duplicate and similar content"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Args:
            similarity_threshold: Ratio above which sentences are considered duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.seen_content = set()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using sequence matching"""
        # Normalize texts for comparison
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation except periods
        text = re.sub(r'[^\w\s.]', '', text)
        
        # Remove common filler words that don't affect meaning
        fillers = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
        words = text.split()
        words = [w for w in words if w not in fillers]
        
        return ' '.join(words)
    
    def is_duplicate(self, text: str, reference_texts: List[str] = None) -> bool:
        """
        Check if text is a duplicate or near-duplicate
        
        Args:
            text: Text to check
            reference_texts: List of texts to compare against (if None, uses internal seen_content)
            
        Returns:
            True if duplicate, False otherwise
        """
        if not text or len(text.strip()) < 10:
            return True
        
        # Check against reference texts or seen content
        comparison_set = reference_texts if reference_texts is not None else self.seen_content
        
        for seen in comparison_set:
            similarity = self.calculate_similarity(text, seen)
            if similarity >= self.similarity_threshold:
                logger.debug(f"Found duplicate (similarity: {similarity:.2f}): {text[:50]}...")
                return True
        
        # Add to seen content
        self.seen_content.add(text)
        return False
    
    def deduplicate_list(self, texts: List[str]) -> List[str]:
        """
        Remove duplicates from a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Deduplicated list
        """
        unique_texts = []
        seen_normalized = set()
        
        for text in texts:
            if not text or len(text.strip()) < 10:
                continue
            
            # Check if this is a duplicate
            normalized = self._normalize_text(text)
            
            # Check exact match first (fast)
            if normalized in seen_normalized:
                continue
            
            # Check semantic similarity (slower)
            is_dup = False
            for unique_text in unique_texts:
                if self.calculate_similarity(text, unique_text) >= self.similarity_threshold:
                    is_dup = True
                    break
            
            if not is_dup:
                unique_texts.append(text)
                seen_normalized.add(normalized)
        
        logger.info(f"Deduplicated: {len(texts)} -> {len(unique_texts)} items")
        return unique_texts
    
    def deduplicate_by_page(self, pages_data: List[dict]) -> List[dict]:
        """
        Remove duplicate content from page-wise data
        
        Args:
            pages_data: List of page dictionaries with 'content', 'concepts', etc.
            
        Returns:
            Deduplicated page data
        """
        for page_data in pages_data:
            # Deduplicate concepts
            if 'concepts' in page_data and page_data['concepts']:
                page_data['concepts'] = self.deduplicate_list(page_data['concepts'])
            
            # Deduplicate important points
            if 'important_points' in page_data and page_data['important_points']:
                page_data['important_points'] = self.deduplicate_list(page_data['important_points'])
            
            # Deduplicate procedures
            if 'procedures' in page_data and page_data['procedures']:
                page_data['procedures'] = self.deduplicate_list(page_data['procedures'])
        
        return pages_data
    
    def remove_substrings(self, texts: List[str]) -> List[str]:
        """
        Remove texts that are substrings of other texts
        Useful for removing fragments
        """
        if not texts:
            return []
        
        # Sort by length (longest first)
        sorted_texts = sorted(texts, key=len, reverse=True)
        
        unique_texts = []
        for text in sorted_texts:
            # Check if this text is a substring of any text already added
            is_substring = False
            for unique_text in unique_texts:
                if text.lower() in unique_text.lower():
                    is_substring = True
                    break
            
            if not is_substring:
                unique_texts.append(text)
        
        return unique_texts
    
    def reset(self):
        """Reset seen content"""
        self.seen_content = set()
