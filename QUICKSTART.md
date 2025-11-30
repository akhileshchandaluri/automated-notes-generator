# Quick Start Guide

## Installation (3 steps)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download NLTK data:**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
   ```

3. **Download spaCy model (optional):**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Run the App

```bash
streamlit run app.py
```

## Or use the automated setup:

```bash
python setup.py
```

## Test Installation

```bash
python test.py
```

## Usage

1. Open browser at `http://localhost:8501`
2. Upload PDF file
3. Click "Generate Notes"
4. Explore tabs and download results

## Troubleshooting

**Import errors?**
- Run `pip install -r requirements.txt`

**NLTK errors?**
- Run NLTK download commands above

**spaCy errors?**
- Install model: `python -m spacy download en_core_web_sm`
- Or skip (some features will be limited)

**PDF not processing?**
- Ensure PDF is text-based (not scanned image)
- Try smaller PDF first to test

## Features Overview

| Feature | What it does |
|---------|--------------|
| Summary | Extracts top 30% most important sentences |
| Key Points | Top 10 critical points in bullet format |
| Keywords | 15 most important terms identified |
| Mindmap | Hierarchical topic structure (5 main topics) |
| Q&A | 12 potential exam questions generated |

## Project Structure

```
automated-notes-gen/
├── app.py                  # Run this to start web app
├── modules/                # Core NLP processing
├── config/                 # Configuration
├── data/uploads/          # Place PDFs here
├── output/                # Generated notes saved here
└── requirements.txt       # Dependencies
```

## API Usage (Python)

```python
from modules.notes_generator import NotesGenerator

generator = NotesGenerator()
results = generator.generate_notes("document.pdf", "output")

print(results['summary']['text'])
print(results['keywords'])
```

## Support

See full documentation in README.md
