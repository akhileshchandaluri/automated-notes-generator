"""
LLM-Based Summarizer using Ollama
Generates intelligent, abstractive summaries using local LLMs
"""

import os
import json
import logging
from typing import List, Dict, Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMSummarizer:
    """Generate intelligent summaries using LLM (Ollama or Groq API)"""
    
    def __init__(self, model: str = "llama3.2:3b", use_groq: bool = False):
        """
        Initialize LLM Summarizer
        
        Args:
            model: Model name (llama3.2:3b for speed, llama3.1:8b for quality)
            use_groq: Use Groq API instead of local Ollama (for deployment)
        """
        self.model = model
        self.use_groq = use_groq or os.getenv('USE_GROQ_API', 'false').lower() == 'true'
        self.ollama_url = "http://localhost:11434/api/generate"
        self.cache = {}  # Cache for repeated content
        
        if self.use_groq:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                self.model = "llama-3.1-8b-instant"  # Groq's free tier model
                logger.info("Using Groq API for LLM")
            except ImportError:
                logger.warning("Groq not installed, falling back to Ollama")
                self.use_groq = False
        else:
            logger.info(f"Using local Ollama with model: {model}")
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """
        Generate text using LLM
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Creativity (0-1, lower = more focused)
            
        Returns:
            Generated text
        """
        if self.use_groq:
            return self._generate_groq(prompt, max_tokens, temperature)
        else:
            return self._generate_ollama(prompt, max_tokens, temperature)
    
    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using local Ollama"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running? Run: ollama serve")
            return ""
        except Exception as e:
            logger.error(f"Error generating with Ollama: {str(e)}")
            return ""
    
    def _generate_groq(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Groq API"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating with Groq: {str(e)}")
            return ""
    
    def extract_page_content(self, page_text: str, page_num: int) -> Dict[str, any]:
        """
        Extract structured content from a single page using LLM
        
        Args:
            page_text: Raw text from page
            page_num: Page number
            
        Returns:
            Dictionary with definitions, concepts, procedures, and points
        """
        # Check cache first
        cache_key = str(page_num) + page_text[:100]
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""Extract key points from this educational page. Format as:

DEFINITIONS:
- [term: meaning]

CONCEPTS:
- [important idea]

PROCEDURES:
- [step]

IMPORTANT_POINTS:
- [key fact]

Content:
{page_text[:2000]}

Be brief and clear."""

        response = self.generate(prompt, max_tokens=400, temperature=0.1)
        
        # Parse and cache
        content = self._parse_response(response, page_num)
        self.cache[cache_key] = content
        return content
    
    def _parse_response(self, response: str, page_num: int) -> Dict[str, any]:
        """Parse LLM response into structured format"""
        
    def _parse_response(self, response: str, page_num: int) -> Dict[str, any]:
        """Parse LLM response into structured format"""
        content = {
            'page': page_num,
            'definitions': self._extract_section(response, 'DEFINITIONS:'),
            'concepts': self._extract_section(response, 'CONCEPTS:'),
            'procedures': self._extract_section(response, 'PROCEDURES:'),
            'important_points': self._extract_section(response, 'IMPORTANT_POINTS:')
        }
        return content
    
    def _extract_section(self, text: str, section_name: str) -> List[str]:
        """Extract bullet points from a section"""
        items = []
        
        if section_name not in text:
            return items
        
        # Find the section
        start = text.find(section_name)
        # Find next section or end
        next_sections = ['DEFINITIONS:', 'CONCEPTS:', 'PROCEDURES:', 'IMPORTANT_POINTS:']
        end = len(text)
        
        for next_section in next_sections:
            if next_section != section_name and next_section in text[start:]:
                pos = text[start:].find(next_section)
                if pos != -1:
                    end = min(end, start + pos)
        
        section_text = text[start:end]
        
        # Extract bullet points
        lines = section_text.split('\n')
        for line in lines[1:]:  # Skip the section header
            line = line.strip()
            # Match bullets: -, •, *, 1., etc.
            if line and (line.startswith('-') or line.startswith('•') or 
                        line.startswith('*') or (line[0].isdigit() and '.' in line[:3])):
                # Remove the bullet/number
                clean_line = line.lstrip('-•*0123456789. ').strip()
                if len(clean_line) > 10:  # Minimum length
                    items.append(clean_line)
        
        return items[:8]  # Max 8 items per section per page
    
    def synthesize_notes(self, all_pages_content: List[Dict]) -> str:
        """
        Synthesize comprehensive notes from all extracted content
        
        Args:
            all_pages_content: List of content dicts from each page
            
        Returns:
            Formatted comprehensive study notes
        """
        # Compile all content
        all_definitions = []
        all_concepts = []
        all_procedures = []
        all_points = []
        
        for page_content in all_pages_content:
            for defn in page_content.get('definitions', []):
                all_definitions.append(f"{defn} (Page {page_content['page']})")
            for concept in page_content.get('concepts', []):
                all_concepts.append(f"{concept} (Page {page_content['page']})")
            for proc in page_content.get('procedures', []):
                all_procedures.append(f"{proc} (Page {page_content['page']})")
            for point in page_content.get('important_points', []):
                all_points.append(f"{point} (Page {page_content['page']})")
        
        # Quick synthesis - just organize by topic
        prompt = f"""Create a clear, well-organized study summary from these points.

Write a coherent 2-3 paragraph summary that:
1. Explains the main topic and its importance
2. Covers key definitions and concepts
3. Mentions practical applications or procedures
4. Is easy to understand for students

Key points to cover:
{chr(10).join(all_definitions[:8])}
{chr(10).join(all_concepts[:8])}
{chr(10).join(all_points[:12])}

Write a clear, flowing summary (not bullet points). Keep it concise but informative."""

        synthesis = self.generate(prompt, max_tokens=500, temperature=0.3)
        
        return synthesis
    
    def generate_qa(self, all_pages_content: List[Dict], num_questions: int = 10) -> List[Dict[str, str]]:
        """
        Generate high-quality Q&A pairs from content
        
        Args:
            all_pages_content: List of content dicts from each page
            num_questions: Number of Q&A pairs to generate
            
        Returns:
            List of {'question': str, 'answer': str} dicts
        """
        # Compile key content
        all_content = []
        for page in all_pages_content:
            all_content.extend(page.get('definitions', []))
            all_content.extend(page.get('concepts', []))
            all_content.extend(page.get('important_points', []))
        
        content_text = chr(10).join(all_content[:20])
        
        prompt = f"""Generate {num_questions} exam-style questions and answers from this educational content.

Content:
{content_text}

Format EXACTLY as:
Q1: [Question]
A1: [Answer]

Q2: [Question]
A2: [Answer]

Make questions:
- Clear and specific
- Test understanding, not just memorization
- Have complete, accurate answers
- Cover different topics from the content"""

        response = self.generate(prompt, max_tokens=800, temperature=0.4)
        
        # Parse Q&A
        qa_pairs = []
        lines = response.split('\n')
        current_q = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q') and ':' in line:
                current_q = line.split(':', 1)[1].strip()
            elif line.startswith('A') and ':' in line and current_q:
                answer = line.split(':', 1)[1].strip()
                qa_pairs.append({'question': current_q, 'answer': answer})
                current_q = None
        
        return qa_pairs[:num_questions]
    
    def test_connection(self) -> bool:
        """Test if LLM is accessible"""
        try:
            response = self.generate("Test", max_tokens=10, temperature=0.1)
            return len(response) > 0
        except:
            return False


if __name__ == "__main__":
    # Test the summarizer
    summarizer = LLMSummarizer()
    
    if summarizer.test_connection():
        print("✅ LLM connection successful!")
        
        # Test extraction
        test_text = """
        Photosynthesis: The process by which green plants convert light energy into chemical energy.
        Plants require three main components: sunlight, water, and carbon dioxide.
        Procedure: 1. Place the plant under light. 2. Measure oxygen output. 3. Record results.
        Chlorophyll is essential for capturing light energy.
        """
        
        result = summarizer.extract_page_content(test_text, 1)
        print("\nTest extraction:")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Cannot connect to LLM. Make sure Ollama is running: ollama serve")
