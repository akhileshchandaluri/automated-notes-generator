"""
Notes Generator - Main Pipeline
Orchestrates all modules to generate complete notes from PDF
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

from .pdf_extractor import PDFExtractor
from .text_preprocessor import TextPreprocessor
from .keyword_extractor import KeywordExtractor
from .sentence_ranker import SentenceRanker
from .summarizer import Summarizer
from .qa_generator import QAGenerator
from .intelligent_extractor import IntelligentExtractor
from .llm_summarizer import LLMSummarizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotesGenerator:
    """Main pipeline to generate notes from PDF"""
    
    def __init__(self, use_llm: bool = True, progress_callback=None):
        self.pdf_extractor = PDFExtractor()
        self.preprocessor = TextPreprocessor()
        self.keyword_extractor = KeywordExtractor()
        self.progress_callback = progress_callback
        self.sentence_ranker = SentenceRanker()
        self.summarizer = Summarizer()
        self.qa_generator = QAGenerator()
        self.intelligent_extractor = IntelligentExtractor()
        
        # LLM-based summarizer for best quality
        self.use_llm = use_llm
        if use_llm:
            try:
                self.llm_summarizer = LLMSummarizer()
                if self.llm_summarizer.test_connection():
                    logger.info("✅ LLM Summarizer enabled - BEST QUALITY MODE")
                else:
                    logger.warning("⚠️ LLM not available, using traditional methods")
                    self.use_llm = False
            except Exception as e:
                logger.warning(f"⚠️ LLM init failed: {e}, using traditional methods")
                self.use_llm = False
        
        self.results = {}
    
    def generate_notes(self, pdf_path: str, 
                      output_dir: str = None) -> Dict[str, Any]:
        """
        Generate complete notes from PDF
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary with all generated components
        """
        logger.info(f"Starting notes generation for: {pdf_path}")
        start_time = datetime.now()
        
        try:
            # Step 1: Extract text from PDF
            logger.info("Step 1: Extracting text from PDF with page tracking...")
            extraction_result = self.pdf_extractor.extract_text(pdf_path)
            text = extraction_result['text']
            pages_data = extraction_result['pages']  # NEW: Page-wise data
            
            logger.info(f"PDF extraction: {len(pages_data)} pages, {len(text.split())} words")
            
            if not text or len(text.split()) < 10:  # Need at least 10 words
                raise ValueError(f"Insufficient text extracted from PDF. Only got {len(text.split())} words. Preview: {text[:200]}")
            
            # ===== LLM-BASED PIPELINE (BEST QUALITY) =====
            if self.use_llm and hasattr(self, 'llm_summarizer'):
                logger.info("🚀 Using LLM-based extraction for BEST QUALITY")
                
                # STAGE 1: Extract from each page using LLM
                logger.info("Stage 1: LLM extracting content from each page...")
                llm_pages_content = []
                for i, page_data in enumerate(pages_data[:20], 1):  # Process up to 20 pages
                    if self.progress_callback:
                        self.progress_callback(f"🎬 Processing Page {i}/{min(len(pages_data), 20)}...")
                    logger.info(f"  Processing page {i}/{min(len(pages_data), 20)}...")
                    page_content = self.llm_summarizer.extract_page_content(
                        page_data['text'], 
                        page_data['page_num']
                    )
                    llm_pages_content.append(page_content)
                
                # STAGE 2: Synthesize comprehensive notes
                if self.progress_callback:
                    self.progress_callback("🎭 Synthesizing Comprehensive Notes...")
                logger.info("Stage 2: Synthesizing comprehensive study notes...")
                llm_comprehensive_notes = self.llm_summarizer.synthesize_notes(llm_pages_content)
                
                # STAGE 3: Generate Q&A from content
                if self.progress_callback:
                    self.progress_callback("📝 Generating Practice Questions...")
                logger.info("Stage 3: Generating Q&A pairs...")
                llm_qa_pairs = self.llm_summarizer.generate_qa(llm_pages_content, num_questions=15)
                
                # Format LLM results
                organized_notes = self._format_llm_notes(llm_pages_content, llm_comprehensive_notes)
                structured_content = {
                    'llm_generated': True,
                    'pages_content': llm_pages_content,
                    'synthesis': llm_comprehensive_notes,
                    'qa_pairs': llm_qa_pairs,
                    'total_pages': len(pages_data),
                    'total_points': sum(len(p.get('definitions', [])) + 
                                      len(p.get('concepts', [])) + 
                                      len(p.get('procedures', [])) + 
                                      len(p.get('important_points', [])) 
                                      for p in llm_pages_content)
                }
            else:
                # FALLBACK: Traditional extraction
                logger.info("Using traditional extraction methods...")
                structured_content = self.intelligent_extractor.extract_structured_content(pages_data)
                organized_notes = self.intelligent_extractor.format_organized_notes(structured_content)
            
            # Step 2: Preprocess text (for traditional methods)
            logger.info("Step 2: Preprocessing text...")
            preprocessed = self.preprocessor.preprocess(text, remove_stopwords=False)
            sentences = preprocessed['sentences']
            
            logger.info(f"Extracted {len(sentences)} sentences from {len(text.split())} words")
            
            if len(sentences) < 2:  # Lowered from 3 to 2
                raise ValueError(f"Not enough content to generate notes. Only found {len(sentences)} sentences from {len(text.split())} words. Text preview: {text[:200]}...")
            
            # Step 3: Extract keywords
            logger.info("Step 3: Extracting keywords...")
            keyword_results = self.keyword_extractor.extract_keywords(
                text, sentences, top_n=30  # More keywords for comprehensive coverage
            )
            keywords = keyword_results['combined']
            
            # Step 4: Rank sentences
            logger.info("Step 4: Ranking sentences...")
            ranked_sentences = self.sentence_ranker.rank_sentences(
                sentences, method='combined'
            )
            
            # Step 5: Generate summary
            logger.info("Step 5: Generating comprehensive summary...")
            summary_result = self.summarizer.generate_summary(
                sentences, summary_ratio=0.7  # 70% coverage for comprehensive notes
            )
            
            # Step 6: Generate key points
            logger.info("Step 6: Generating comprehensive key points...")
            key_points = self.summarizer.generate_key_points(sentences, top_n=50)
            
            # Step 7: Generate Q&A (use LLM if available, otherwise traditional)
            logger.info("Step 7: Generating Q&A...")
            if self.use_llm and hasattr(self, 'llm_summarizer') and 'qa_pairs' in structured_content:
                qa_pairs = structured_content['qa_pairs']
            else:
                qa_pairs = self.qa_generator.generate_questions(
                    sentences, keywords, num_questions=15
                )
            
            # Compile results
            self.results = {
                'metadata': {
                    'filename': os.path.basename(pdf_path),
                    'generated_at': datetime.now().isoformat(),
                    'processing_time': str(datetime.now() - start_time),
                    'page_count': extraction_result['page_count'],
                    'word_count': extraction_result['word_count'],
                    'sentence_count': len(sentences),
                    'points_extracted': structured_content['total_points'],  # NEW
                    'ai_generated': structured_content.get('llm_generated', False)
                },
                'organized_content': organized_notes,  # NEW: Main content with page numbers
                'structured_data': structured_content,  # NEW: Structured sections
                'summary': {
                    'text': structured_content.get('synthesis', summary_result['summary']) if self.use_llm else summary_result['summary'],
                    'sentences': summary_result['sentences'] if not self.use_llm else [],
                    'compression_ratio': f"{summary_result['ratio']:.1%}" if not self.use_llm else "AI Generated"
                },
                'key_points': key_points,
                'keywords': [{'term': kw, 'score': f"{score:.3f}"} 
                           for kw, score in keywords[:30]],  # Show 30 keywords
                'qa_pairs': qa_pairs,
                'top_sentences': [
                    {'rank': i+1, 'score': f"{score:.3f}", 'text': sent}
                    for i, (idx, score, sent) in enumerate(ranked_sentences[:10])
                ]
            }
            
            # Save to file if output directory specified
            if output_dir:
                self._save_results(output_dir, pdf_path)
            
            logger.info(f"Notes generation completed in {datetime.now() - start_time}")
            
            return self.results
            
        except Exception as e:
            logger.error(f"Error generating notes: {str(e)}")
            raise
    
    def _save_results(self, output_dir: str, pdf_path: str):
        """Save results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Base filename
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_path = os.path.join(output_dir, f"{base_name}_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON to: {json_path}")
        
        # Save formatted text
        txt_path = os.path.join(output_dir, f"{base_name}_{timestamp}_notes.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self._format_notes_text())
        logger.info(f"Saved text notes to: {txt_path}")
        
        # Save markdown
        md_path = os.path.join(output_dir, f"{base_name}_{timestamp}_notes.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._format_notes_markdown())
        logger.info(f"Saved markdown to: {md_path}")
    
    def _format_notes_text(self) -> str:
        """Format results as readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append("AUTOMATED NOTES")
        lines.append("=" * 80)
        lines.append(f"\nDocument: {self.results['metadata']['filename']}")
        lines.append(f"Generated: {self.results['metadata']['generated_at']}")
        lines.append(f"Pages: {self.results['metadata']['page_count']}")
        lines.append(f"Words: {self.results['metadata']['word_count']}")
        lines.append("\n" + "=" * 80)
        
        # Summary
        lines.append("\n📘 SUMMARY")
        lines.append("-" * 80)
        lines.append(self.results['summary']['text'])
        
        # Key Points
        lines.append("\n\n📌 KEY POINTS")
        lines.append("-" * 80)
        for i, point in enumerate(self.results['key_points'], 1):
            lines.append(f"{i}. {point}")
        
        # Keywords
        lines.append("\n\n🔑 KEYWORDS")
        lines.append("-" * 80)
        keywords_str = ", ".join([kw['term'] for kw in self.results['keywords']])
        lines.append(keywords_str)
        
        # Q&A
        lines.append("\n📚 POSSIBLE QUESTIONS & ANSWERS")
        lines.append("-" * 80)
        for i, qa in enumerate(self.results['qa_pairs'], 1):
            lines.append(f"\nQ{i}. {qa['question']}")
            lines.append(f"A{i}. {qa['answer']}")
        
        lines.append("\n" + "=" * 80)
        return '\n'.join(lines)
    
    def _format_llm_notes(self, pages_content: List[Dict], synthesis: str) -> str:
        """Format LLM-generated notes with beautiful markdown"""
        lines = []
        
        lines.append("# 📚 AI-GENERATED COMPREHENSIVE STUDY NOTES\n")
        lines.append(f"**Powered by:** Llama 3.1 LLM 🤖 | **Quality:** Production-Grade\n")
        lines.append("---\n")
        
        # Comprehensive synthesis first
        lines.append("## 🎯 COMPREHENSIVE OVERVIEW\n")
        lines.append(synthesis)
        lines.append("\n---\n")
        
        # Page-by-page detailed notes
        lines.append("## 📖 DETAILED NOTES BY PAGE\n")
        
        for page_data in pages_content:
            page_num = page_data['page']
            lines.append(f"### 📄 Page {page_num}\n")
            
            # Definitions
            if page_data.get('definitions'):
                lines.append("**📖 Definitions:**\n")
                for defn in page_data['definitions']:
                    lines.append(f"   • {defn}\n")
                lines.append("")
            
            # Concepts
            if page_data.get('concepts'):
                lines.append("**💡 Key Concepts:**\n")
                for concept in page_data['concepts']:
                    lines.append(f"   • {concept}\n")
                lines.append("")
            
            # Procedures
            if page_data.get('procedures'):
                lines.append("**🔧 Procedures/Methods:**\n")
                for i, proc in enumerate(page_data['procedures'], 1):
                    lines.append(f"   {i}. {proc}\n")
                lines.append("")
            
            # Important points
            if page_data.get('important_points'):
                lines.append("**📝 Important Points:**\n")
                for point in page_data['important_points']:
                    lines.append(f"   • {point}\n")
                lines.append("")
            
            lines.append("---\n")
        
        return '\n'.join(lines)
    
    def _format_notes_markdown(self) -> str:
        """Format results as comprehensive markdown study notes with page numbers"""
        lines = []
        lines.append(f"# 📚 COMPLETE STUDY GUIDE: {self.results['metadata']['filename']}\n")
        lines.append(f"**Generated:** {self.results['metadata']['generated_at']}  ")
        lines.append(f"**Pages:** {self.results['metadata']['page_count']} | "
                    f"**Total Points Extracted:** {self.results['metadata']['points_extracted']} | "
                    f"**Processing Time:** {self.results['metadata']['processing_time']}\n")
        lines.append("---\n")
        
        # Add the organized content (page-by-page breakdown)
        lines.append(self.results['organized_content'])
        lines.append("\n---\n")
        
        # Additional Analysis Sections
        lines.append("## 🔍 ADDITIONAL ANALYSIS\n")
        
        # Executive Summary
        lines.append("### 📋 Executive Summary\n")
        lines.append(f"*Coverage: {self.results['summary']['compression_ratio']} of original content*\n")
        # Show first 500 chars of summary
        summary_preview = self.results['summary']['text'][:500] + "..." if len(self.results['summary']['text']) > 500 else self.results['summary']['text']
        lines.append(summary_preview + "\n")
        
        # Top Keywords
        lines.append("### 🔑 Key Technical Terms\n")
        keywords_by_row = 5
        keywords = [f"**{kw['term']}**" for kw in self.results['keywords'][:20]]
        for i in range(0, len(keywords), keywords_by_row):
            row = keywords[i:i+keywords_by_row]
            lines.append(" • ".join(row))
        lines.append("")
        
        # Practice Questions
        lines.append("### ❓ Practice Questions for Revision\n")
        lines.append(f"*{len(self.results['qa_pairs'])} questions for self-assessment*\n")
        
        for i, qa in enumerate(self.results['qa_pairs'][:15], 1):  # Show first 15
            lines.append(f"**Q{i}. {qa['question']}**\n")
            lines.append(f"<details><summary>Show Answer</summary>\n\n{qa['answer']}\n\n</details>\n")
        
        # Footer
        lines.append("---\n")
        lines.append(f"*Generated by Comprehensive Study Notes Generator | {self.results['metadata']['points_extracted']} points from {self.results['metadata']['page_count']} pages*")
        
        return '\n'.join(lines)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about generated notes"""
        if not self.results:
            return {}
        
        return {
            'total_sentences': self.results['metadata']['sentence_count'],
            'summary_sentences': len(self.results['summary']['sentences']),
            'key_points': len(self.results['key_points']),
            'keywords': len(self.results['keywords']),
            'questions': len(self.results['qa_pairs']),
            'compression_ratio': self.results['summary']['compression_ratio']
        }


if __name__ == "__main__":
    # Test the notes generator
    generator = NotesGenerator()
    # result = generator.generate_notes("sample.pdf", output_dir="output")
    # print(generator.get_stats())
