"""
Intelligent Content Extractor
Extracts structured, meaningful content from educational PDFs with page tracking
"""

import re
from typing import List, Dict, Tuple, Set
import logging
from .deduplicator import ContentDeduplicator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentExtractor:
    """Extract structured educational content with context"""
    
    def __init__(self):
        self.content_blocks = []
        self.deduplicator = ContentDeduplicator(similarity_threshold=0.85)
        
    def extract_structured_content(self, pdf_pages: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Extract content with page numbers, headings, and structure
        
        Args:
            pdf_pages: List of dicts with 'page_num' and 'text'
            
        Returns:
            Structured content with sections, topics, and page references
        """
        sections = []
        all_important_points = []
        page_summaries = {}
        
        for page_info in pdf_pages:
            page_num = page_info['page_num']
            text = page_info['text']
            
            # Extract content from this page
            page_content = self._extract_page_content(text, page_num)
            
            if page_content['points']:
                page_summaries[page_num] = page_content
                all_important_points.extend(page_content['points'])
            
            # Detect sections
            if page_content['heading']:
                sections.append({
                    'heading': page_content['heading'],
                    'page': page_num,
                    'content': page_content['points']
                })
        
        logger.info(f"Extracted {len(all_important_points)} important points from {len(pdf_pages)} pages")
        
        return {
            'sections': sections,
            'page_summaries': page_summaries,
            'all_points': all_important_points,
            'total_pages': len(pdf_pages),
            'total_points': len(all_important_points)
        }
    
    def _extract_page_content(self, text: str, page_num: int) -> Dict[str, any]:
        """Extract meaningful content from a single page"""
        
        # Detect heading
        heading = self._detect_heading(text)
        
        # Extract important sentences
        sentences = self._split_into_sentences(text)
        
        # Separate into different categories
        definitions = []
        procedures = []
        concepts = []
        general_points = []
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20:
                continue
            
            # Classify the sentence
            if self._is_definition(sent):
                definitions.append(sent)
            elif self._is_procedure(sent):
                procedures.append(sent)
            elif self._is_concept(sent):
                concepts.append(sent)
            elif self._is_important(sent):
                general_points.append(sent)
        
        # Remove duplicates
        definitions = self.deduplicator.deduplicate_list(definitions)
        procedures = self.deduplicator.deduplicate_list(procedures)
        concepts = self.deduplicator.deduplicate_list(concepts)
        general_points = self.deduplicator.deduplicate_list(general_points)
        
        # Compile points with page reference
        points = []
        
        for defn in definitions[:5]:  # Limit per category
            points.append({
                'text': defn,
                'page': page_num,
                'type': 'definition'
            })
        
        for concept in concepts[:5]:
            points.append({
                'text': concept,
                'page': page_num,
                'type': 'concept'
            })
        
        for proc in procedures[:5]:
            points.append({
                'text': proc,
                'page': page_num,
                'type': 'procedure'
            })
        
        for point in general_points[:10]:
            points.append({
                'text': point,
                'page': page_num,
                'type': 'content'
            })
        
        return {
            'heading': heading,
            'points': points,
            'page': page_num,
            'definitions': definitions,
            'concepts': concepts,
            'procedures': procedures
        }
    
    def _detect_heading(self, text: str) -> str:
        """Detect section heading from text"""
        lines = text.split('\n')
        
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            
            # Skip empty or very short lines
            if len(line) < 3 or len(line) > 100:
                continue
            
            # Check for heading patterns
            if re.match(r'^(Aim|Objective|Introduction|Experiment|Design|Implementation|Procedure|Theory|Result|Conclusion)', line, re.IGNORECASE):
                return line
            
            # Check for numbered headings
            if re.match(r'^\d+\.?\s+[A-Z]', line):
                return line
            
            # Check for all caps short lines
            if line.isupper() and 5 < len(line) < 50:
                return line
        
        return None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into meaningful sentences"""
        # Split on punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _is_definition(self, sent: str) -> bool:
        """Check if sentence is a definition"""
        definition_patterns = [
            r'\b(is|are|refers? to|means?|defined as|known as)\b',
            r'\b(definition|defined)\b',
            r'^[A-Z][a-z]+:',  # "Term: definition"
            r'\b(called|termed)\b'
        ]
        return any(re.search(pattern, sent, re.IGNORECASE) for pattern in definition_patterns)
    
    def _is_procedure(self, sent: str) -> bool:
        """Check if sentence describes a procedure or step"""
        procedure_indicators = [
            r'^\d+\.',  # Numbered steps
            r'\b(step|first|second|then|next|finally|procedure)\b',
            r'\b(method|process|technique)\b',
            r'\b(should|must|need to|have to)\b'
        ]
        return any(re.search(pattern, sent, re.IGNORECASE) for pattern in procedure_indicators)
    
    def _is_concept(self, sent: str) -> bool:
        """Check if sentence explains a concept"""
        concept_indicators = [
            r'\b(principle|theory|concept|idea|approach)\b',
            r'\b(because|therefore|thus|hence|since)\b',
            r'\b(allows?|enables?|provides?|ensures?)\b',
            r'\b(advantage|benefit|importance|significance)\b'
        ]
        return any(re.search(pattern, sent, re.IGNORECASE) for pattern in concept_indicators)
    
    def _is_important(self, sent: str) -> bool:
        """Check if sentence contains important information"""
        # Skip noise
        noise_patterns = [
            'dept.', 'signature', 'marks obtained', 'sl.no', 'criteria',
            'page number', 'copyright', 'all rights reserved', 'table', 'figure'
        ]
        if any(pattern in sent.lower() for pattern in noise_patterns):
            return False
        
        # Skip if too many numbers
        if len(re.findall(r'\d', sent)) / max(len(sent), 1) > 0.4:
            return False
        
        # Must have reasonable word count
        word_count = len(sent.split())
        if word_count < 5 or word_count > 50:
            return False
        
        return True
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts and terminology"""
        concepts = []
        
        # Look for definition patterns
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(.{20,100})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+are\s+(.{20,100})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*:\s*(.{20,100})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches[:5]:  # Max 5 per pattern
                term, definition = match
                if len(term.split()) <= 5:  # Reasonable term length
                    concepts.append(f"{term}: {definition}")
        
        return concepts
    
    def _extract_definitions(self, text: str) -> List[str]:
        """Extract formal definitions"""
        definitions = []
        
        # Look for aim/objective patterns
        aim_match = re.search(r'Aim\s*:?\s*(.{30,200})', text, re.IGNORECASE)
        if aim_match:
            definitions.append(f"Aim: {aim_match.group(1).strip()}")
        
        obj_match = re.search(r'Objective\s*:?\s*(.{30,200})', text, re.IGNORECASE)
        if obj_match:
            definitions.append(f"Objective: {obj_match.group(1).strip()}")
        
        return definitions
    
    def _extract_procedures(self, text: str) -> List[str]:
        """Extract procedural steps"""
        procedures = []
        
        # Look for numbered steps
        steps = re.findall(r'\d+\.\s+([^.\n]{20,150})', text)
        for step in steps[:10]:  # Max 10 steps
            if not any(skip in step.lower() for skip in ['marks', 'dept', 'signature']):
                procedures.append(step.strip())
        
        return procedures
    
    def format_organized_notes(self, structured_content: Dict) -> str:
        """Format extracted content into organized study notes"""
        lines = []
        
        lines.append("# 📚 COMPREHENSIVE STUDY NOTES\n")
        lines.append(f"**Pages Analyzed:** {structured_content['total_pages']} | **Important Points Extracted:** {structured_content['total_points']}\n")
        lines.append("---\n")
        
        # Table of Contents
        if structured_content['sections']:
            lines.append("## 📑 TABLE OF CONTENTS\n")
            for i, section in enumerate(structured_content['sections'], 1):
                heading = section['heading'][:60]  # Limit length
                lines.append(f"{i}. **{heading}** _(Page {section['page']})_")
            lines.append("\n---\n")
        
        # Page-by-page content
        lines.append("## 📖 DETAILED NOTES BY PAGE\n")
        
        for page_num in sorted(structured_content['page_summaries'].keys()):
            page_data = structured_content['page_summaries'][page_num]
            
            if not page_data['points']:
                continue
            
            lines.append(f"### 📄 Page {page_num}")
            
            if page_data['heading']:
                heading = page_data['heading'].strip()
                if not heading.endswith((':', '.', '!')):
                    heading += ':'
                lines.append(f"**{heading}**\n")
            
            # Group by type
            definitions = [p for p in page_data['points'] if p['type'] == 'definition']
            concepts = [p for p in page_data['points'] if p['type'] == 'concept']
            procedures = [p for p in page_data['points'] if p['type'] == 'procedure']
            content = [p for p in page_data['points'] if p['type'] == 'content']
            
            # Format definitions
            if definitions:
                lines.append("**📖 Definitions:**\n")
                for defn in definitions:
                    text = defn['text'].strip()
                    # Clean up any bullets or markers
                    text = re.sub(r'^[•○●▪▫■□◦◘◙‣⁃⁌⁍∙]+\s*', '', text)
                    text = re.sub(r'^\d+\.\s*', '', text)
                    lines.append(f"   {text}\n")
                lines.append("")
            
            # Format concepts  
            if concepts:
                lines.append("**💡 Key Concepts:**\n")
                for concept in concepts:
                    text = concept['text'].strip()
                    text = re.sub(r'^[•○●▪▫■□◦◘◙‣⁃⁌⁍∙]+\s*', '', text)
                    text = re.sub(r'^\d+\.\s*', '', text)
                    lines.append(f"   {text}\n")
                lines.append("")
            
            # Format procedures
            if procedures:
                lines.append("**🔧 Procedures/Methods:**\n")
                for i, proc in enumerate(procedures, 1):
                    text = proc['text'].strip()
                    text = re.sub(r'^[•○●▪▫■□◦◘◙‣⁃⁌⁍∙]+\s*', '', text)
                    text = re.sub(r'^\d+\.\s*', '', text)
                    lines.append(f"   {i}. {text}\n")
                lines.append("")
            
            # Format general content
            if content:
                lines.append("**📝 Important Points:**\n")
                for point in content:
                    text = point['text'].strip()
                    text = re.sub(r'^[•○●▪▫■□◦◘◙‣⁃⁌⁍∙]+\s*', '', text)
                    text = re.sub(r'^\d+\.\s*', '', text)
                    lines.append(f"   • {text}\n")
                lines.append("")
            
            lines.append("---\n")
        
        return '\n'.join(lines)


if __name__ == "__main__":
    extractor = IntelligentExtractor()
