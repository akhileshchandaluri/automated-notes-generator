"""
Advanced PDF Text Cleaner
Handles badly formatted PDFs with concatenated words, missing spaces, etc.
"""

import re
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedTextCleaner:
    """Clean and normalize badly extracted PDF text"""
    
    def __init__(self):
        self.common_words = set([
            'the', 'and', 'for', 'are', 'but', 'not', 'with', 'from', 'this', 'that',
            'data', 'analysis', 'design', 'system', 'using', 'based', 'method', 'result'
        ])
    
    def clean_concatenated_text(self, text: str) -> str:
        """
        Fix text where words are concatenated without spaces
        Example: "DataVisualization" -> "Data Visualization"
        """
        if not text:
            return ""
        
        # Fix common OCR errors with spaces in words
        # "in g" -> "ing", "at ion" -> "ation", etc.
        text = re.sub(r'\b(\w+)\s+(in|at|on|ed|er|ly|en)\s+g\b', r'\1\2g', text)
        text = re.sub(r'\b(\w+)\s+at\s+ion\b', r'\1ation', text)
        text = re.sub(r'\b(\w+)\s+on\s+s\b', r'\1ons', text)
        text = re.sub(r'\bc\s+on\s+', r'con', text)
        text = re.sub(r'\bin\s+for\s+m', r'inform', text)
        text = re.sub(r'\bto\s+(r|s|w)\b', r'tor', text)
        
        # Step 1: Add space before capital letters in middle of lowercase
        # "dataVisualization" -> "data Visualization"
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Step 2: Add space between lowercase and number
        # "page1" -> "page 1"
        text = re.sub(r'([a-z])(\d)', r'\1 \2', text)
        
        # Step 3: Add space between number and letter
        # "1page" -> "1 page"
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        
        # Step 4: Fix common concatenations - ENHANCED
        text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)
        
        # Step 5: Fix common prepositions concatenated with words
        # "offood" -> "of food", "tothe" -> "to the", "bythe" -> "by the"
        common_preps = ['of', 'to', 'in', 'on', 'at', 'by', 'for', 'from', 'with', 'the', 'and']
        for prep in common_preps:
            # Fix word+preposition+word: "foodofthe" -> "food of the"
            pattern = rf'([a-z])({prep})([a-z])'
            text = re.sub(pattern, rf'\1 \2 \3', text, flags=re.IGNORECASE)
        
        # Step 6: Add period between sentences if missing
        # "end Next" -> "end. Next"
        text = re.sub(r'([a-z])([A-Z][a-z]{2,})', r'\1. \2', text)
        
        # Step 7: Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
        
        return text
    
    def extract_meaningful_sentences(self, text: str) -> List[str]:
        """Extract only meaningful, complete sentences"""
        
        # Clean the text first
        text = self.clean_concatenated_text(text)
        
        # Split by common sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        meaningful = []
        for sent in sentences:
            sent = sent.strip()
            
            # Skip if too short (reduced from 30 to 15)
            if len(sent) < 15:
                continue
            
            # Skip if mostly numbers (increased threshold to be less strict)
            if len(re.findall(r'\d', sent)) / max(len(sent), 1) > 0.6:
                continue
            
            # Skip if mostly special characters (increased threshold)
            if len(re.findall(r'[^\w\s]', sent)) / max(len(sent), 1) > 0.5:
                continue
            
            # Must have at least 3 words (reduced from 4)
            words = sent.split()
            if len(words) < 3:
                continue
            
            # Skip if no vowels (likely garbled)
            if not re.search(r'[aeiouAEIOU]', sent):
                continue
            
            meaningful.append(sent.strip())
        
        return meaningful
    
    def clean_page_content(self, text: str) -> str:
        """Complete cleaning pipeline for one page"""
        
        if not text or len(text.strip()) < 50:
            return ""
        
        # Remove URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        text = re.sub(r'www\.[^\s]+', '', text)
        
        # Remove image sources
        text = re.sub(r'Image\s*(?:Source|Courtesy)\s*:.*', '', text, flags=re.IGNORECASE)
        
        # Remove table markers
        text = re.sub(r'Table\s*:.*', '', text, flags=re.IGNORECASE)
        
        # Remove references
        text = re.sub(r'Courtesy\s*:.*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\d+\]', '', text)
        
        # Fix concatenated text
        cleaned_text = self.clean_concatenated_text(text)
        
        # Only filter sentences if the text looks problematic
        # If we have reasonable content, just return it cleaned
        words = cleaned_text.split()
        if len(words) > 20:  # If decent amount of words, keep it
            return cleaned_text
        
        # For shorter content, do more aggressive filtering
        sentences = self.extract_meaningful_sentences(cleaned_text)
        
        # If filtering removed too much, return the cleaned text anyway
        if not sentences and len(words) > 5:
            return cleaned_text
        
        return '\n'.join(sentences)
    
    def is_content_line(self, line: str) -> bool:
        """Check if a line contains actual content"""
        
        line = line.strip()
        
        # Too short (reduced from 15 to 8)
        if len(line) < 8:
            return False
        
        # Just numbers and special chars
        if re.match(r'^[\d\s.,\-/]+$', line):
            return False
        
        # Mostly special characters (increased threshold to be less strict)
        if len(re.findall(r'[^\w\s]', line)) / max(len(line), 1) > 0.7:
            return False
        
        # No letters at all
        if not re.search(r'[a-zA-Z]', line):
            return False
        
        # Skip common noise patterns
        noise_patterns = [
            r'^\s*\d+\s*$',  # Just page numbers
            r'^(Page|Chapter)\s+\d+',  # Page/Chapter headers
            r'Image\s*(Source|Courtesy)',
            r'^Table\s*:',
            r'^Figure\s*:',
        ]
        
        for pattern in noise_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return False
        
        return True


if __name__ == "__main__":
    cleaner = AdvancedTextCleaner()
    
    # Test
    test_text = "DataVisualizationDr.ArulalanRajan,FounderDirector,vidyakośa,Bangalore"
    cleaned = cleaner.clean_concatenated_text(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned: {cleaned}")
