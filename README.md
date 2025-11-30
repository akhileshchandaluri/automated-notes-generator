# Automated PDF Notes Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> An AI-powered system that automatically generates comprehensive study notes from PDF documents using advanced NLP techniques.

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 📘 **Extractive Summarization** | Generates accurate summaries using TextRank & TF-IDF (no hallucinations) |
| 📌 **Key Points Extraction** | Identifies and extracts the most important sentences |
| 🔑 **Keyword Extraction** | Extracts technical terms using TF-IDF, RAKE, and spaCy |
| 🧠 **Mindmap Generation** | Creates hierarchical topic structure with clustering |
| ❓ **Q&A Generation** | Generates potential exam questions using rule-based templates |
| 💾 **Multiple Export Formats** | Download notes in JSON, TXT, and Markdown |
| 🎨 **Interactive UI** | User-friendly Streamlit web interface |

## 🚀 Demo

![App Screenshot](screenshots/demo.png)

## 🏗️ System Architecture

```
PDF Upload
     ↓
Text Extraction (pdfplumber)
     ↓
Preprocessing (NLTK, spaCy)
     ↓
Keyword Extraction (TF-IDF, RAKE)
     ↓
Sentence Ranking (TextRank)
     ↓
Summarization Engine
     ↓
Mindmap Builder (KMeans Clustering)
     ↓
Q&A Generator
     ↓
Streamlit UI
```

## 📦 Tech Stack

- **Backend:** Python 3.8+
- **NLP Libraries:** NLTK, spaCy, scikit-learn
- **PDF Processing:** pdfplumber
- **Keyword Extraction:** RAKE-NLTK
- **UI Framework:** Streamlit
- **Algorithms:** TextRank, TF-IDF, KMeans Clustering

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/automated-notes-gen.git
cd automated-notes-gen
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
```

### Step 5: Download spaCy Model (Optional but Recommended)

```bash
python -m spacy download en_core_web_sm
```

## 🎯 Usage

### Running the Web App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Python API

```python
from modules.notes_generator import NotesGenerator

# Initialize generator
generator = NotesGenerator()

# Generate notes from PDF
results = generator.generate_notes(
    pdf_path="your_document.pdf",
    output_dir="output"
)

# Access results
print(results['summary']['text'])
print(results['keywords'])
print(results['mindmap']['text'])
```

## 📂 Project Structure

```
automated-notes-gen/
│
├── modules/                    # Core NLP modules
│   ├── __init__.py
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── text_preprocessor.py   # Text cleaning & tokenization
│   ├── keyword_extractor.py   # Keyword extraction
│   ├── sentence_ranker.py     # TextRank & TF-IDF ranking
│   ├── summarizer.py          # Extractive summarization
│   ├── mindmap_builder.py     # Topic clustering & hierarchy
│   ├── qa_generator.py        # Question generation
│   └── notes_generator.py     # Main pipeline
│
├── config/                     # Configuration files
│   └── config.py
│
├── data/                       # Data directory
│   └── uploads/               # Uploaded PDFs
│
├── output/                     # Generated notes
│
├── utils/                      # Utility functions
│
├── app.py                      # Streamlit web app
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔍 How It Works

### 1. **PDF Extraction**
- Uses `pdfplumber` to extract text from PDF
- Removes headers, footers, and page numbers
- Preserves document structure

### 2. **Text Preprocessing**
- Tokenizes text into sentences and words
- Removes noise and special characters
- Normalizes text while preserving meaning

### 3. **Keyword Extraction**
Multiple algorithms combined:
- **TF-IDF:** Statistical importance
- **RAKE:** Rapid Automatic Keyword Extraction
- **spaCy:** Noun phrase extraction

### 4. **Sentence Ranking**
Ranks sentences using:
- **TextRank:** Graph-based ranking (like PageRank)
- **TF-IDF:** Term frequency importance
- **Position Score:** First/last sentence boosting
- **Combined Score:** Weighted combination of all methods

### 5. **Summarization**
- Pure extractive (no generation = no hallucinations)
- Selects top N% of sentences by importance
- Maintains original text order

### 6. **Mindmap Generation**
- Clusters sentences using KMeans
- Extracts topic names from keywords
- Builds hierarchical structure

### 7. **Q&A Generation**
- Rule-based question templates
- Pattern matching (X is Y → What is X?)
- Keyword-based questions
- No generative AI = factually accurate

## 📊 Output Examples

### Summary
```
Natural language processing is a subfield of artificial intelligence 
that focuses on enabling computers to understand human language...
```

### Keywords
```
machine learning, neural networks, natural language processing, 
deep learning, artificial intelligence
```

### Mindmap
```
📚 Document Overview

1. Machine Learning | Neural Networks
   ├── Machine learning is a subset of AI.
   ├── Neural networks process information like the brain.
   └── Deep learning uses multiple layers.

2. Natural Language Processing
   ├── NLP handles text and speech.
   └── Applications include translation and chatbots.
```

### Q&A
```
Q1. What is machine learning?
A1. Machine learning is a subset of artificial intelligence that 
    enables computers to learn from data.

Q2. How do neural networks work?
A2. Neural networks process information using interconnected nodes 
    inspired by biological neurons.
```

## 🎓 Resume Bullet Point

```
Built an automated PDF notes generator that performs extractive text 
summarization using TextRank and TF-IDF-based sentence ranking, keyword 
extraction with RAKE and spaCy, and hierarchical topic clustering to 
generate structured study notes. Implemented end-to-end NLP pipeline 
and deployed interactive Streamlit interface with multi-format export.
```

## 🔧 Configuration

Edit `config/config.py` to customize:

- Summary length ratio
- Number of keywords
- Topic count for mindmap
- Question generation count
- Output formats

## 🚀 Future Enhancements

| Feature | Description |
|---------|-------------|
| 🔍 **RAG Integration** | Add retrieval-augmented generation for Q&A |
| 📷 **OCR Support** | Process scanned/handwritten notes |
| 📚 **Multi-Document** | Merge notes from multiple PDFs |
| 🔐 **User Authentication** | Save notes with Firebase/Auth |
| 🌐 **API Endpoint** | RESTful API for integration |
| 📊 **Advanced Visualization** | Interactive mindmap graphs |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- NLTK for natural language processing
- spaCy for advanced NLP features
- scikit-learn for machine learning algorithms
- Streamlit for the web interface
- pdfplumber for PDF extraction

## 📧 Contact

For questions or feedback, please open an issue or contact [your.email@example.com](mailto:your.email@example.com)

---

⭐ If you find this project helpful, please give it a star!
