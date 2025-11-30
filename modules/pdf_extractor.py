"""
PDF Extraction Module
Extracts text from PDF files while removing noise and preserving structure
"""

import pdfplumber
import re
from typing import Dict, List, Tuple
import logging
from .advanced_cleaner import AdvancedTextCleaner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract and clean text from PDF files"""
    
    def __init__(self):
        self.text = ""
        self.metadata = {}
        self.page_count = 0
        self.cleaner = AdvancedTextCleaner()  # NEW
        
    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file with page tracking
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text, pages, and metadata
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.page_count = len(pdf.pages)
                self.metadata = pdf.metadata
                
                all_text = []
                pages_data = []  # Store page-wise data
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # Use advanced cleaner for badly formatted PDFs
                        cleaned_text = self.cleaner.clean_page_content(page_text)
                        if cleaned_text.strip():  # Only if there's actual content
                            all_text.append(cleaned_text)
                            pages_data.append({
                                'page_num': page_num,
                                'text': cleaned_text,
                                'word_count': len(cleaned_text.split())
                            })
                
                self.text = "\n\n".join(all_text)
                
                logger.info(f"Successfully extracted text from {self.page_count} pages")
                
                return {
                    'text': self.text,
                    'pages': pages_data,  # Add page-wise data
                    'page_count': self.page_count,
                    'metadata': self.metadata,
                    'word_count': len(self.text.split())
                }
                
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
    
    def _clean_page_text(self, text: str, page_num: int) -> str:
        """
        Clean extracted text from a single page
        
        Args:
            text: Raw extracted text
            page_num: Page number
            
        Returns:
            Cleaned text
        """
        # Remove page numbers at top/bottom
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+\d+\s+Analysis and Design', ' Analysis and Design', text)
        
        # Remove common headers/footers patterns
        text = re.sub(r'^Page\s+\d+.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^Chapter\s+\d+.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove repetitive institutional headers
        text = re.sub(r'RV College of Engineering,?\s+Bengaluru[-–]?\s*\d*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(Autonomous Institution.*?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'affiliated to VTU,?\s+Belgaum', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Department of Electronics.*?Engineering', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Laboratory Manual and Observation Book', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Academic Year\s+\d{4}-\d{4}', '', text)
        text = re.sub(r'Autonomous Scheme\s+\d{4}', '', text)
        
        # Remove rubric tables and repetitive criteria
        text = re.sub(r'Sl\.No\s+Criteria\s+(?:Excellent\s+Good\s+Average\s+)?(?:Max\s+)?Marks.*?(?:result|Result)', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'(?:Data sheet|Record|Simulation|Conduction)\s+[A-Z]\s+(?:Problem statement|Design specifications|Expected output|Analysis).*?\d+', '', text, flags=re.IGNORECASE)
        
        # Remove certificate boilerplate
        text = re.sub(r'This is to certify that.*?USN No\.', '', text, flags=re.DOTALL)
        text = re.sub(r'Name of the Candidate:?.*?_+', '', text)
        
        # Remove standalone underscores/fill-in-blanks
        text = re.sub(r'_{3,}', '', text)
        
        # Fix hyphenated words at line breaks
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()\[\]{}\-–—\'\"°%$€£¥+=/<>\n]', '', text)
        
        return text.strip()
    
    def extract_by_sections(self, pdf_path: str) -> List[Dict[str, str]]:
        """
        Extract text and attempt to identify sections
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of sections with titles and content
        """
        extraction_result = self.extract_text(pdf_path)
        text = extraction_result['text']
        
        # Simple section detection based on capitalized lines or numbered headings
        sections = []
        lines = text.split('\n')
        current_section = {'title': 'Introduction', 'content': ''}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a heading (all caps, short, or numbered)
            if (self._is_heading(line)):
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'title': line, 'content': ''}
            else:
                current_section['content'] += line + ' '
        
        # Add last section
        if current_section['content']:
            sections.append(current_section)
        
        return sections if sections else [{'title': 'Content', 'content': text}]
    
    def _is_heading(self, line: str) -> bool:
        """Check if a line is likely a heading"""
        if len(line) > 100:
            return False
        
        # Check for numbered headings (1. , 1.1 , Chapter 1, etc)
        if re.match(r'^\d+\.?\s+[A-Z]', line):
            return True
        
        # Check for all caps headings (at least 50% caps)
        caps_ratio = sum(1 for c in line if c.isupper()) / len(line) if line else 0
        if caps_ratio > 0.5 and len(line) < 50:
            return True
        
        # Check for title case with common heading words
        heading_words = ['introduction', 'conclusion', 'abstract', 'summary', 
                        'chapter', 'section', 'overview', 'background', 'method']
        if any(word in line.lower() for word in heading_words) and len(line) < 60:
            return True
        
        return False


if __name__ == "__main__":
    # Test the extractor
    extractor = PDFExtractor()
    # result = extractor.extract_text("sample.pdf")
    # print(f"Extracted {result['word_count']} words from {result['page_count']} pages")
