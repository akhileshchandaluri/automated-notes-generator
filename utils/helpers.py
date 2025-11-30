"""
Utility functions for the Notes Generator
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size(file_path: str) -> str:
    """
    Get human-readable file size
    
    Args:
        file_path: Path to file
        
    Returns:
        Formatted file size string
    """
    size_bytes = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"


def format_timestamp(timestamp: datetime = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp
    
    Args:
        timestamp: Datetime object (defaults to now)
        fmt: Format string
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(fmt)


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2):
    """
    Save data as JSON file
    
    Args:
        data: Dictionary to save
        file_path: Output file path
        indent: JSON indentation
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        file_path: Input file path
        
    Returns:
        Loaded dictionary
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def calculate_reading_time(word_count: int, words_per_minute: int = 200) -> str:
    """
    Calculate estimated reading time
    
    Args:
        word_count: Number of words
        words_per_minute: Average reading speed
        
    Returns:
        Formatted reading time
    """
    minutes = word_count / words_per_minute
    
    if minutes < 1:
        return "< 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minutes"
    else:
        hours = int(minutes / 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m"
