"""
Q&A Generator Module
Generates potential exam questions from text using rule-based templates
"""

import re
from typing import List, Dict, Tuple
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import spacy
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load('en_core_web_sm')
    except:
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None


class QAGenerator:
    """Generate questions and answers from text"""
    
    def __init__(self):
        self.question_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load question templates for different patterns"""
        return {
            'definition': [
                "What is {term}?",
                "Define {term}.",
                "Explain {term}.",
                "What do you mean by {term}?"
            ],
            'explanation': [
                "Explain {concept}.",
                "Describe {concept}.",
                "What is {concept}?",
                "Discuss {concept}."
            ],
            'process': [
                "How does {process} work?",
                "Explain the process of {process}.",
                "Describe how {process} occurs.",
                "What are the steps in {process}?"
            ],
            'comparison': [
                "What is the difference between {term1} and {term2}?",
                "Compare {term1} and {term2}.",
                "How do {term1} and {term2} differ?"
            ],
            'purpose': [
                "What is the purpose of {concept}?",
                "Why is {concept} important?",
                "What is the significance of {concept}?"
            ],
            'application': [
                "What are the applications of {concept}?",
                "How is {concept} used?",
                "Where is {concept} applied?"
            ]
        }
    
    def generate_questions(self, sentences: List[str], 
                          keywords: List[tuple],
                          num_questions: int = 10) -> List[Dict[str, str]]:
        """
        Generate Q&A pairs from sentences
        
        Args:
            sentences: List of sentences
            keywords: List of (keyword, score) tuples
            num_questions: Target number of questions
            
        Returns:
            List of Q&A dictionaries
        """
        qa_pairs = []
        
        # Method 1: Keyword-based questions
        keyword_questions = self._generate_keyword_questions(keywords, sentences)
        qa_pairs.extend(keyword_questions)
        
        # Method 2: Pattern-based questions
        pattern_questions = self._generate_pattern_questions(sentences)
        qa_pairs.extend(pattern_questions)
        
        # Method 3: Sentence transformation questions
        transform_questions = self._generate_transform_questions(sentences)
        qa_pairs.extend(transform_questions)
        
        # Remove duplicates and limit
        qa_pairs = self._deduplicate_questions(qa_pairs)
        qa_pairs = qa_pairs[:num_questions]
        
        logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
        
        return qa_pairs
    
    def _generate_keyword_questions(self, keywords: List[tuple], 
                                   sentences: List[str]) -> List[Dict[str, str]]:
        """Generate questions based on keywords"""
        questions = []
        
        for keyword, score in keywords[:10]:
            # Find sentence containing keyword
            answer_sent = self._find_sentence_with_keyword(keyword, sentences)
            
            if answer_sent:
                # Generate question
                question = random.choice(self.question_templates['definition']).format(
                    term=keyword.title()
                )
                
                questions.append({
                    'question': question,
                    'answer': answer_sent,
                    'type': 'definition',
                    'keyword': keyword
                })
        
        return questions
    
    def _generate_pattern_questions(self, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate questions based on sentence patterns"""
        questions = []
        
        for sentence in sentences:
            # Pattern: "X is Y" -> "What is X?"
            is_pattern = re.match(r'^([A-Z][a-z\s]+)\s+is\s+(.+?)\.', sentence)
            if is_pattern:
                subject = is_pattern.group(1)
                questions.append({
                    'question': f"What is {subject}?",
                    'answer': sentence,
                    'type': 'definition'
                })
            
            # Pattern: "X can Y" -> "What can X do?"
            can_pattern = re.match(r'^([A-Z][a-z\s]+)\s+can\s+(.+?)\.', sentence)
            if can_pattern:
                subject = can_pattern.group(1)
                questions.append({
                    'question': f"What can {subject} do?",
                    'answer': sentence,
                    'type': 'capability'
                })
            
            # Pattern: "X helps Y" -> "How does X help?"
            helps_pattern = re.match(r'^([A-Z][a-z\s]+)\s+helps?\s+(.+?)\.', sentence)
            if helps_pattern:
                subject = helps_pattern.group(1)
                questions.append({
                    'question': f"How does {subject} help?",
                    'answer': sentence,
                    'type': 'purpose'
                })
            
            # Pattern: Contains "because" -> "Why...?"
            if 'because' in sentence.lower():
                parts = sentence.split('because')
                if len(parts) == 2:
                    questions.append({
                        'question': f"Why {parts[0].strip().lower()}?",
                        'answer': sentence,
                        'type': 'explanation'
                    })
        
        return questions
    
    def _generate_transform_questions(self, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate questions by transforming sentences"""
        questions = []
        
        for sentence in sentences:
            # Skip very short or very long sentences
            word_count = len(sentence.split())
            if word_count < 5 or word_count > 30:
                continue
            
            # Simple transformation: statement -> question
            if SPACY_AVAILABLE and nlp:
                qa = self._spacy_transform(sentence)
                if qa:
                    questions.append(qa)
            else:
                # Basic transformation without spacy
                qa = self._basic_transform(sentence)
                if qa:
                    questions.append(qa)
        
        return questions
    
    def _spacy_transform(self, sentence: str) -> Dict[str, str]:
        """Use spaCy to transform sentence to question"""
        try:
            doc = nlp(sentence)
            
            # Find main verb and subject
            verb = None
            subject = None
            
            for token in doc:
                if token.dep_ == "ROOT" and token.pos_ == "VERB":
                    verb = token
                if "subj" in token.dep_:
                    subject = token
            
            if verb and subject:
                # Create question
                question = f"What {verb.lemma_} {subject.text}?"
                return {
                    'question': question,
                    'answer': sentence,
                    'type': 'transformed'
                }
        except Exception as e:
            logger.debug(f"spaCy transform error: {str(e)}")
        
        return None
    
    def _basic_transform(self, sentence: str) -> Dict[str, str]:
        """Basic transformation without NLP"""
        # Simple heuristics
        lower = sentence.lower()
        
        # Contains numbers -> numerical question
        if re.search(r'\d+', sentence):
            return {
                'question': f"What is mentioned about {sentence.split()[0]}?",
                'answer': sentence,
                'type': 'factual'
            }
        
        return None
    
    def _find_sentence_with_keyword(self, keyword: str, 
                                   sentences: List[str]) -> str:
        """Find best sentence containing keyword"""
        keyword_lower = keyword.lower()
        
        for sentence in sentences:
            if keyword_lower in sentence.lower():
                return sentence
        
        return ""
    
    def _deduplicate_questions(self, qa_pairs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate questions"""
        seen_questions = set()
        unique_pairs = []
        
        for qa in qa_pairs:
            q = qa['question'].lower().strip()
            if q not in seen_questions and qa['answer']:
                seen_questions.add(q)
                unique_pairs.append(qa)
        
        return unique_pairs
    
    def generate_exam_questions(self, sentences: List[str],
                               keywords: List[tuple]) -> Dict[str, List[str]]:
        """
        Generate categorized exam questions
        
        Args:
            sentences: List of sentences
            keywords: List of keywords
            
        Returns:
            Dictionary with categorized questions
        """
        qa_pairs = self.generate_questions(sentences, keywords, num_questions=15)
        
        # Categorize questions
        categorized = {
            'short_answer': [],
            'descriptive': [],
            'conceptual': []
        }
        
        for qa in qa_pairs:
            q_type = qa.get('type', 'general')
            
            if q_type in ['definition', 'factual']:
                categorized['short_answer'].append(qa)
            elif q_type in ['explanation', 'process']:
                categorized['descriptive'].append(qa)
            else:
                categorized['conceptual'].append(qa)
        
        return categorized


if __name__ == "__main__":
    # Test the Q&A generator
    generator = QAGenerator()
    sample_sentences = [
        "Machine learning is a subset of artificial intelligence.",
        "Neural networks can learn complex patterns from data.",
        "Deep learning uses multiple layers to extract features.",
        "Training involves adjusting weights to minimize error."
    ]
    sample_keywords = [("machine learning", 0.9), ("neural networks", 0.8)]
    
    qa_pairs = generator.generate_questions(sample_sentences, sample_keywords, num_questions=5)
    for qa in qa_pairs:
        print(f"Q: {qa['question']}")
        print(f"A: {qa['answer']}\n")
