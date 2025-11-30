# 📖 Usage Examples

Complete examples of how to use the Automated PDF Notes Generator.

## 🌐 Web Interface (Recommended)

### Starting the App

```bash
streamlit run app.py
```

Browser opens at: `http://localhost:8501`

### Step-by-Step Usage

1. **Upload PDF**
   - Click "Choose a PDF file"
   - Select your PDF document
   - Supported: Textbooks, research papers, notes, articles

2. **Generate Notes**
   - Click "🚀 Generate Notes" button
   - Wait for processing (progress bar shown)
   - Time varies: 10-30 seconds for typical documents

3. **Explore Results**
   - Navigate through 6 tabs
   - View statistics dashboard
   - Read generated content

4. **Download**
   - Go to "Download" tab
   - Choose format: JSON, TXT, or Markdown
   - Click download button

---

## 🐍 Python API Usage

### Basic Usage

```python
from modules.notes_generator import NotesGenerator

# Initialize generator
generator = NotesGenerator()

# Generate notes from PDF
results = generator.generate_notes(
    pdf_path="documents/chapter1.pdf",
    output_dir="output"
)

# Access results
print("Summary:", results['summary']['text'])
print("Keywords:", results['keywords'])
print("Q&A Count:", len(results['qa_pairs']))
```

### Advanced Usage - Custom Processing

```python
from modules.notes_generator import NotesGenerator
from modules.pdf_extractor import PDFExtractor
from modules.keyword_extractor import KeywordExtractor

# Initialize components separately
pdf_extractor = PDFExtractor()
keyword_extractor = KeywordExtractor()

# Extract text
extraction = pdf_extractor.extract_text("document.pdf")
text = extraction['text']

# Extract keywords
from modules.text_preprocessor import TextPreprocessor
preprocessor = TextPreprocessor()
processed = preprocessor.preprocess(text)

keywords = keyword_extractor.extract_keywords(
    text, 
    processed['sentences'], 
    top_n=20
)

print("Top Keywords:", keywords['combined'][:10])
```

### Extracting Specific Components

#### 1. Summary Only

```python
from modules.text_preprocessor import TextPreprocessor
from modules.summarizer import Summarizer

preprocessor = TextPreprocessor()
summarizer = Summarizer()

# Read your text file
with open("text_content.txt", "r") as f:
    text = f.read()

# Preprocess
processed = preprocessor.preprocess(text)

# Generate summary
summary = summarizer.generate_summary(
    processed['sentences'],
    summary_ratio=0.25  # 25% of sentences
)

print(summary['summary'])
```

#### 2. Keywords Only

```python
from modules.text_preprocessor import TextPreprocessor
from modules.keyword_extractor import KeywordExtractor

text = "Your document text here..."

preprocessor = TextPreprocessor()
processed = preprocessor.preprocess(text)

extractor = KeywordExtractor()
keywords = extractor.extract_keywords(
    text, 
    processed['sentences'], 
    top_n=15
)

# Different extraction methods
print("TF-IDF Keywords:", keywords['tfidf'][:5])
print("RAKE Keywords:", keywords['rake'][:5])
print("Combined Keywords:", keywords['combined'][:5])
```

#### 3. Q&A Only

```python
from modules.text_preprocessor import TextPreprocessor
from modules.keyword_extractor import KeywordExtractor
from modules.qa_generator import QAGenerator

text = "Your document text..."

preprocessor = TextPreprocessor()
processed = preprocessor.preprocess(text)

extractor = KeywordExtractor()
keywords = extractor.extract_keywords(text, processed['sentences'])

qa_gen = QAGenerator()
questions = qa_gen.generate_questions(
    processed['sentences'],
    keywords['combined'],
    num_questions=10
)

for i, qa in enumerate(questions, 1):
    print(f"\nQ{i}: {qa['question']}")
    print(f"A{i}: {qa['answer']}")
```

#### 4. Mindmap Only

```python
from modules.text_preprocessor import TextPreprocessor
from modules.keyword_extractor import KeywordExtractor
from modules.mindmap_builder import MindmapBuilder

text = "Your document text..."

preprocessor = TextPreprocessor()
processed = preprocessor.preprocess(text)

extractor = KeywordExtractor()
keywords = extractor.extract_keywords(text, processed['sentences'])

builder = MindmapBuilder()
mindmap = builder.build_mindmap(
    processed['sentences'],
    keywords['combined'],
    max_topics=5
)

# Display as tree
print(builder.format_as_tree(mindmap))

# Or as markdown
print(builder.format_as_markdown(mindmap))
```

---

## 📝 Working with Different PDF Types

### Research Papers

```python
generator = NotesGenerator()

results = generator.generate_notes(
    pdf_path="research_paper.pdf",
    output_dir="output/research"
)

# Research papers often have technical terms
technical_keywords = [kw for kw in results['keywords'] 
                     if kw['score'] > 0.5]
print("Technical Terms:", technical_keywords)
```

### Textbook Chapters

```python
generator = NotesGenerator()

# Process multiple chapters
chapters = ["ch1.pdf", "ch2.pdf", "ch3.pdf"]

all_keywords = []
for chapter in chapters:
    results = generator.generate_notes(chapter, "output/textbook")
    all_keywords.extend(results['keywords'])

# Find common keywords across chapters
from collections import Counter
keyword_freq = Counter([kw['term'] for kw in all_keywords])
print("Most Common Topics:", keyword_freq.most_common(10))
```

### Lecture Notes

```python
generator = NotesGenerator()

results = generator.generate_notes(
    pdf_path="lecture_notes.pdf",
    output_dir="output/lectures"
)

# Lecture notes benefit from Q&A generation
print(f"Generated {len(results['qa_pairs'])} study questions")

# Save questions separately
with open("study_questions.txt", "w") as f:
    for i, qa in enumerate(results['qa_pairs'], 1):
        f.write(f"Q{i}. {qa['question']}\n")
        f.write(f"A{i}. {qa['answer']}\n\n")
```

---

## 🔧 Customization Examples

### Custom Summary Length

```python
from modules.summarizer import Summarizer

summarizer = Summarizer()

# Very brief summary (10% of sentences)
brief_summary = summarizer.generate_summary(
    sentences,
    summary_ratio=0.1,
    min_sentences=2,
    max_sentences=5
)

# Detailed summary (50% of sentences)
detailed_summary = summarizer.generate_summary(
    sentences,
    summary_ratio=0.5,
    min_sentences=10,
    max_sentences=30
)
```

### Custom Keyword Count

```python
from modules.keyword_extractor import KeywordExtractor

extractor = KeywordExtractor()

# Extract many keywords
keywords = extractor.extract_keywords(
    text, 
    sentences, 
    top_n=50  # Get top 50 keywords
)

# Filter by score
high_confidence = [kw for kw, score in keywords['combined'] 
                  if score > 0.7]
```

### Custom Ranking Method

```python
from modules.sentence_ranker import SentenceRanker

ranker = SentenceRanker()

# Try different ranking methods
textrank_results = ranker.rank_sentences(sentences, method='textrank')
tfidf_results = ranker.rank_sentences(sentences, method='tfidf')
combined_results = ranker.rank_sentences(sentences, method='combined')

# Compare results
print("TextRank top sentence:", textrank_results[0][2])
print("TF-IDF top sentence:", tfidf_results[0][2])
print("Combined top sentence:", combined_results[0][2])
```

---

## 💾 Output Format Examples

### JSON Output Structure

```json
{
  "metadata": {
    "filename": "chapter1.pdf",
    "generated_at": "2025-01-28T14:30:22",
    "page_count": 15,
    "word_count": 3542,
    "sentence_count": 178
  },
  "summary": {
    "text": "Complete summary text...",
    "sentences": ["Sentence 1", "Sentence 2"],
    "compression_ratio": "30.0%"
  },
  "key_points": [
    "First key point...",
    "Second key point..."
  ],
  "keywords": [
    {"term": "machine learning", "score": "0.892"},
    {"term": "neural networks", "score": "0.847"}
  ],
  "mindmap": {
    "structure": {...},
    "text": "Tree formatted mindmap...",
    "markdown": "# Mindmap..."
  },
  "qa_pairs": [
    {
      "question": "What is...?",
      "answer": "Answer text...",
      "type": "definition"
    }
  ]
}
```

### TXT Output Format

```
================================================================================
AUTOMATED NOTES
================================================================================

Document: chapter1.pdf
Generated: 2025-01-28T14:30:22
Pages: 15
Words: 3542

================================================================================

📘 SUMMARY
--------------------------------------------------------------------------------
Complete summary text here...

📌 KEY POINTS
--------------------------------------------------------------------------------
1. First key point
2. Second key point
3. Third key point

🔑 KEYWORDS
--------------------------------------------------------------------------------
machine learning, neural networks, deep learning, AI

🧠 MINDMAP
--------------------------------------------------------------------------------
📚 Document Overview

1. Main Topic
   ├── Subtopic 1
   ├── Subtopic 2
   └── Subtopic 3

📚 POSSIBLE QUESTIONS & ANSWERS
--------------------------------------------------------------------------------

Q1. What is machine learning?
A1. Machine learning is...
```

### Markdown Output Format

```markdown
# Automated Notes: chapter1.pdf

**Generated:** 2025-01-28T14:30:22  
**Pages:** 15 | **Words:** 3542

---

## 📘 Summary

Complete summary text here...

## 📌 Key Points

1. First key point
2. Second key point
3. Third key point

## 🔑 Keywords

`machine learning`, `neural networks`, `deep learning`

## 🧠 Mindmap

### 1. Main Topic

- Subtopic 1
- Subtopic 2
- Subtopic 3

## 📚 Possible Questions & Answers

### Q1. What is machine learning?

Machine learning is...
```

---

## 🎯 Real-World Scenarios

### Scenario 1: Exam Preparation

```python
# Process your course material
generator = NotesGenerator()
results = generator.generate_notes("course_material.pdf", "output")

# Focus on Q&A for practice
questions = results['qa_pairs']

# Create flashcards
with open("flashcards.txt", "w") as f:
    for qa in questions:
        f.write(f"Q: {qa['question']}\n")
        f.write(f"A: {qa['answer']}\n")
        f.write("-" * 50 + "\n")

# Review key points
key_points = results['key_points']
print("\n📌 Study These Points:\n")
for i, point in enumerate(key_points, 1):
    print(f"{i}. {point}")
```

### Scenario 2: Research Paper Review

```python
# Process research paper
generator = NotesGenerator()
results = generator.generate_notes("research_paper.pdf", "output")

# Extract methodology and findings
summary = results['summary']['text']
keywords = [kw['term'] for kw in results['keywords']]

# Create literature review notes
review = f"""
Paper Summary:
{summary}

Key Concepts:
{', '.join(keywords[:10])}

Important Points:
{''.join([f'- {p}' for p in results['key_points'][:5]])}
"""

with open("literature_review.md", "w") as f:
    f.write(review)
```

### Scenario 3: Meeting Notes

```python
# If you have meeting minutes as PDF
generator = NotesGenerator()
results = generator.generate_notes("meeting_notes.pdf", "output")

# Extract action items (key points)
action_items = results['key_points']

# Create task list
print("🎯 Action Items:")
for i, item in enumerate(action_items, 1):
    print(f"[ ] {i}. {item}")

# Key topics discussed
topics = results['mindmap']['structure']['topics']
print("\n📋 Topics Discussed:")
for topic in topics:
    print(f"- {topic['name']}")
```

---

## 🐛 Troubleshooting Examples

### Handling Errors

```python
from modules.notes_generator import NotesGenerator
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

generator = NotesGenerator()

try:
    results = generator.generate_notes("document.pdf", "output")
except ValueError as e:
    print(f"Document issue: {e}")
    # Try with different settings
except Exception as e:
    print(f"Processing error: {e}")
    logging.exception("Full error details:")
```

### Testing with Sample Text

```python
# Test without PDF
from modules.text_preprocessor import TextPreprocessor
from modules.summarizer import Summarizer

sample_text = """
Machine learning is a subset of artificial intelligence.
It enables computers to learn from data without explicit programming.
Deep learning is a specialized form of machine learning.
Neural networks are the foundation of deep learning.
"""

preprocessor = TextPreprocessor()
processed = preprocessor.preprocess(sample_text)

summarizer = Summarizer()
summary = summarizer.generate_summary(processed['sentences'])

print("Test Summary:", summary['summary'])
```

---

## 📚 More Examples

See the `test.py` file for additional working examples of all modules.

For API reference, see `README.md` and `PROJECT_STRUCTURE.md`.
