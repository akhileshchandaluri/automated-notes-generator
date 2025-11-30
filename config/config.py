"""
Configuration settings for the Notes Generator
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# NLP Settings
NLP_CONFIG = {
    'language': 'english',
    'min_sentence_length': 5,
    'max_sentence_length': 50,
    'summary_ratio': 0.3,
    'min_summary_sentences': 3,
    'max_summary_sentences': 15,
    'top_keywords': 15,
    'max_topics': 5,
    'questions_count': 12
}

# Processing Settings
PROCESSING_CONFIG = {
    'remove_stopwords': False,
    'use_lemmatization': False,
    'ranking_method': 'combined',  # 'textrank', 'tfidf', 'combined'
    'clustering_method': 'kmeans'  # 'kmeans', 'hierarchical'
}

# Model Settings
MODEL_CONFIG = {
    'spacy_model': 'en_core_web_sm',
    'tfidf_max_features': 100,
    'tfidf_ngram_range': (1, 2)
}

# Output Settings
OUTPUT_CONFIG = {
    'save_json': True,
    'save_txt': True,
    'save_markdown': True,
    'include_metadata': True,
    'timestamp_format': '%Y%m%d_%H%M%S'
}

# Logging Settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': BASE_DIR / 'app.log'
}

# Streamlit Settings
STREAMLIT_CONFIG = {
    'page_title': 'AI PDF Notes Generator',
    'page_icon': '📚',
    'layout': 'wide',
    'max_upload_size': 50  # MB
}
