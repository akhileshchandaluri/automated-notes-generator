# 📁 Project Structure

Complete directory structure of the Automated PDF Notes Generator project.

```
automated-notes-gen/
│
├── 📄 app.py                          # Main Streamlit web application
├── 📄 setup.py                        # Automated setup script
├── 📄 test.py                         # Test suite for verification
├── 📄 requirements.txt                # Python dependencies
├── 📄 README.md                       # Complete documentation
├── 📄 QUICKSTART.md                   # Quick start guide
├── 📄 LICENSE                         # MIT License
├── 📄 .gitignore                      # Git ignore rules
├── 📄 __init__.py                     # Package initializer
│
├── 📁 modules/                        # Core NLP processing modules
│   ├── __init__.py
│   ├── pdf_extractor.py              # PDF text extraction with pdfplumber
│   ├── text_preprocessor.py          # NLTK-based text cleaning & tokenization
│   ├── keyword_extractor.py          # TF-IDF, RAKE, spaCy keyword extraction
│   ├── sentence_ranker.py            # TextRank & TF-IDF sentence ranking
│   ├── summarizer.py                 # Extractive summarization engine
│   ├── mindmap_builder.py            # KMeans clustering & hierarchy builder
│   ├── qa_generator.py               # Rule-based Q&A generation
│   └── notes_generator.py            # Main pipeline orchestrator
│
├── 📁 config/                         # Configuration files
│   ├── __init__.py
│   └── config.py                     # App settings & parameters
│
├── 📁 utils/                          # Utility functions
│   ├── __init__.py
│   └── helpers.py                    # Helper functions
│
├── 📁 data/                           # Data directory
│   ├── README.md
│   └── uploads/                      # Uploaded PDF files
│       └── .gitkeep
│
└── 📁 output/                         # Generated notes output
    ├── README.md
    └── .gitkeep
```

## 📋 File Descriptions

### Root Level Files

| File | Description | Lines |
|------|-------------|-------|
| `app.py` | Streamlit web UI with multi-tab interface | ~450 |
| `setup.py` | Automated environment setup script | ~150 |
| `test.py` | Comprehensive test suite | ~200 |
| `requirements.txt` | All Python dependencies | ~20 |
| `README.md` | Complete project documentation | ~500 |
| `QUICKSTART.md` | Quick setup & usage guide | ~100 |

### Core Modules (modules/)

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `pdf_extractor.py` | Extract text from PDF | - pdfplumber integration<br>- Header/footer removal<br>- Noise cleaning |
| `text_preprocessor.py` | Clean & tokenize text | - Sentence tokenization<br>- Stopword removal<br>- Text normalization |
| `keyword_extractor.py` | Extract keywords | - TF-IDF scoring<br>- RAKE algorithm<br>- spaCy noun phrases<br>- Combined scoring |
| `sentence_ranker.py` | Rank sentence importance | - TextRank (PageRank)<br>- TF-IDF scoring<br>- Position weighting<br>- Combined algorithm |
| `summarizer.py` | Generate summaries | - Extractive summarization<br>- Multi-level summaries<br>- Key points extraction |
| `mindmap_builder.py` | Build topic hierarchy | - KMeans clustering<br>- Topic extraction<br>- Tree formatting |
| `qa_generator.py` | Generate Q&A pairs | - Rule-based templates<br>- Pattern matching<br>- Question categorization |
| `notes_generator.py` | Main pipeline | - Orchestrates all modules<br>- End-to-end processing<br>- Multi-format output |

### Configuration (config/)

| File | Purpose |
|------|---------|
| `config.py` | All app settings, NLP parameters, output options |

### Utilities (utils/)

| File | Purpose |
|------|---------|
| `helpers.py` | File operations, formatting, timestamp utilities |

## 🔧 Module Dependencies

```
notes_generator.py (Main Pipeline)
    ├── pdf_extractor.py
    ├── text_preprocessor.py
    ├── keyword_extractor.py
    ├── sentence_ranker.py
    ├── summarizer.py
    │   └── sentence_ranker.py
    ├── mindmap_builder.py
    └── qa_generator.py
```

## 📊 Code Statistics

| Category | Count |
|----------|-------|
| Total Python Files | 18 |
| Total Lines of Code | ~3,500 |
| Core Modules | 8 |
| Configuration Files | 2 |
| Documentation Files | 5 |

## 🎯 Module Functionality Map

### Input → Processing → Output

```
PDF File
    ↓
[pdf_extractor.py]
    → Raw Text
    ↓
[text_preprocessor.py]
    → Clean Sentences
    ↓
┌─────────────────────────────────┐
│   Parallel Processing           │
│  ┌──────────────────────────┐  │
│  │ keyword_extractor.py     │  │
│  │ → Keywords & Terms       │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │ sentence_ranker.py       │  │
│  │ → Ranked Sentences       │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│   Content Generation            │
│  ┌──────────────────────────┐  │
│  │ summarizer.py            │  │
│  │ → Summary & Key Points   │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │ mindmap_builder.py       │  │
│  │ → Topic Hierarchy        │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │ qa_generator.py          │  │
│  │ → Questions & Answers    │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
    ↓
[notes_generator.py]
    → Compiled Results
    ↓
Output Files (JSON, TXT, MD)
```

## 🎨 UI Structure (app.py)

```
Streamlit App
├── Header Section
│   ├── Title
│   └── Description
│
├── Sidebar
│   ├── About
│   ├── How to Use
│   └── Tech Stack
│
├── Upload Section
│   ├── File Uploader
│   └── Generate Button
│
├── Statistics Dashboard
│   ├── Page Count
│   ├── Word Count
│   ├── Sentence Count
│   ├── Keywords Count
│   └── Questions Count
│
└── Results Tabs
    ├── Tab 1: Summary
    ├── Tab 2: Key Points
    ├── Tab 3: Keywords
    ├── Tab 4: Mindmap
    ├── Tab 5: Q&A
    └── Tab 6: Download
```

## 📦 Output Structure

Generated files are saved with timestamps:

```
output/
├── filename_20250128_143022.json
├── filename_20250128_143022_notes.txt
└── filename_20250128_143022_notes.md
```

### Output File Contents

**JSON** - Complete structured data
- Metadata
- Summary with sentences
- Key points array
- Keywords with scores
- Mindmap structure
- Q&A pairs
- Top sentences

**TXT** - Formatted plain text
- Section headers
- Numbered lists
- Clean formatting

**Markdown** - GitHub-ready format
- Markdown headers
- Code blocks for keywords
- Collapsible sections

## 🚀 Execution Flow

1. **User uploads PDF** → `app.py`
2. **Save to temp file** → `tempfile`
3. **Call generator** → `notes_generator.py`
4. **Extract text** → `pdf_extractor.py`
5. **Preprocess** → `text_preprocessor.py`
6. **Extract keywords** → `keyword_extractor.py`
7. **Rank sentences** → `sentence_ranker.py`
8. **Generate summary** → `summarizer.py`
9. **Build mindmap** → `mindmap_builder.py`
10. **Generate Q&A** → `qa_generator.py`
11. **Compile results** → `notes_generator.py`
12. **Save outputs** → `output/`
13. **Display in UI** → `app.py`

## 📚 External Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| streamlit | Web UI | ≥1.28.0 |
| pdfplumber | PDF extraction | ≥0.10.0 |
| nltk | Text processing | ≥3.8.0 |
| scikit-learn | ML algorithms | ≥1.3.0 |
| networkx | Graph algorithms | ≥3.1 |
| spacy | Advanced NLP | ≥3.7.0 |
| rake-nltk | Keyword extraction | ≥1.0.6 |
| numpy | Numerical computing | ≥1.24.0 |
| pandas | Data handling | ≥2.0.0 |

## 🔐 Environment Variables

Currently no environment variables required. Future additions:
- API keys (for RAG integration)
- Database credentials (for user storage)
- Cloud storage credentials

## 📝 Configuration Parameters

See `config/config.py` for all adjustable settings:

- Summary ratio (default: 30%)
- Number of keywords (default: 15)
- Max topics for mindmap (default: 5)
- Question count (default: 12)
- Output formats
- Logging settings

## 🧪 Testing

Run `test.py` to verify:
- ✅ All imports
- ✅ Module availability
- ✅ NLTK data
- ✅ Basic functionality

## 📈 Future Structure Additions

Planned additions for v2.0:
```
├── 📁 models/              # Saved ML models
├── 📁 cache/               # Cached embeddings
├── 📁 database/            # User data storage
├── 📁 api/                 # REST API endpoints
└── 📁 tests/               # Unit & integration tests
```
