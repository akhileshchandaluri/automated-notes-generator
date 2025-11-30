"""
Text Preprocessing Module
Cleans, tokenizes, and prepares text for NLP processing
"""

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


class TextPreprocessor:
    """Preprocess and clean text for NLP tasks"""
    
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()
        
    def preprocess(self, text: str, remove_stopwords: bool = False) -> Dict[str, any]:
        """
        Complete preprocessing pipeline
        
        Args:
            text: Input text
            remove_stopwords: Whether to remove stopwords
            
        Returns:
            Dictionary with processed components
        """
        # Sentence tokenization
        sentences = self.tokenize_sentences(text)
        
        # Clean sentences
        cleaned_sentences = [self.clean_sentence(s) for s in sentences]
        
        # Word tokenization
        words = self.tokenize_words(text)
        
        # Clean words
        cleaned_words = self.clean_words(words, remove_stopwords)
        
        logger.info(f"Preprocessed {len(sentences)} sentences, {len(cleaned_words)} words")
        
        return {
            'sentences': cleaned_sentences,
            'words': cleaned_words,
            'sentence_count': len(sentences),
            'word_count': len(cleaned_words),
            'original_text': text
        }
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        sentences = sent_tokenize(text)
        
        # Filter out noise patterns
        filtered_sentences = []
        seen_sentences = set()  # Track duplicates
        
        for s in sentences:
            s = s.strip()
            
            # Skip too short or too long sentences
            word_count = len(s.split())
            if word_count < 5 or word_count > 150:  # Increased max to 150
                continue
            
            # Skip repetitive institutional text
            if any(pattern in s.lower() for pattern in [
                'rv college of engineering',
                'department of electronics',
                'laboratory manual',
                'observation book',
                'autonomous institution',
                'analysis and design of digital circuits with hdl',
                'criteria max marks marks obtained',
                'problem statement design specifications',
                'simulation conduction of the experiment'
            ]):
                continue
            
            # Skip sentences that are mostly page numbers or formatting
            if re.match(r'^[\d\s.]+$', s) or len(re.findall(r'\d', s)) / max(len(s), 1) > 0.5:
                continue
            
            # Skip duplicates (case-insensitive)
            s_lower = s.lower()
            if s_lower in seen_sentences:
                continue
            
            seen_sentences.add(s_lower)
            filtered_sentences.append(s)
        
        return filtered_sentences
    
    def tokenize_words(self, text: str) -> List[str]:
        """
        Split text into words
        
        Args:
            text: Input text
            
        Returns:
            List of words
        """
        return word_tokenize(text.lower())
    
    def clean_sentence(self, sentence: str) -> str:
        """
        Clean a single sentence
        
        Args:
            sentence: Input sentence
            
        Returns:
            Cleaned sentence
        """
        # Remove extra whitespace
        sentence = ' '.join(sentence.split())
        
        # Fix common punctuation issues
        sentence = re.sub(r'\s+([.,;:!?])', r'\1', sentence)
        
        # Ensure sentence ends with punctuation
        if sentence and sentence[-1] not in '.!?':
            sentence += '.'
        
        return sentence.strip()
    
    def clean_words(self, words: List[str], remove_stopwords: bool = False) -> List[str]:
        """
        Clean word list
        
        Args:
            words: List of words
            remove_stopwords: Whether to remove stopwords
            
        Returns:
            Cleaned word list
        """
        cleaned = []
        
        for word in words:
            # Remove punctuation
            word = word.translate(str.maketrans('', '', string.punctuation))
            
            # Skip empty, very short, or purely numeric
            if len(word) <= 2 or word.isdigit():
                continue
            
            # Remove stopwords if requested
            if remove_stopwords and word.lower() in self.stop_words:
                continue
            
            cleaned.append(word.lower())
        
        return cleaned
    
    def lemmatize_words(self, words: List[str]) -> List[str]:
        """
        Lemmatize words to base form
        
        Args:
            words: List of words
            
        Returns:
            Lemmatized words
        """
        return [self.lemmatizer.lemmatize(word) for word in words]
    
    def get_sentence_lengths(self, sentences: List[str]) -> List[int]:
        """Get word count for each sentence"""
        return [len(s.split()) for s in sentences]
    
    def filter_sentences_by_length(self, sentences: List[str], 
                                   min_length: int = 5, 
                                   max_length: int = 50) -> List[str]:
        """
        Filter sentences by word count
        
        Args:
            sentences: List of sentences
            min_length: Minimum word count
            max_length: Maximum word count
            
        Returns:
            Filtered sentences
        """
        return [s for s in sentences if min_length <= len(s.split()) <= max_length]
    
    def remove_citations(self, text: str) -> str:
        """Remove common citation patterns"""
        # Remove [1], [2,3], etc.
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        
        # Remove (Author, Year) patterns
        text = re.sub(r'\([A-Z][a-z]+(?:\s+et\s+al\.)?,?\s+\d{4}\)', '', text)
        
        return text


if __name__ == "__main__":
    # Test the preprocessor
    preprocessor = TextPreprocessor()
    sample_text = """
    Natural Language Processing is a field of AI. It deals with text analysis.
    This is a test sentence for demonstration purposes.
    """
    result = preprocessor.preprocess(sample_text)
    print(f"Sentences: {result['sentence_count']}, Words: {result['word_count']}")
