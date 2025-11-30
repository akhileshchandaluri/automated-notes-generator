"""
Setup Script - Automated PDF Notes Generator
Run this script to set up the environment
"""

import subprocess
import sys
import os


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"⏳ {description}...")
    try:
        subprocess.check_call(command, shell=True)
        print(f"✅ {description} - DONE\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}\n")
        return False


def main():
    """Main setup process"""
    print_header("Automated PDF Notes Generator - Setup")
    
    print("This script will:")
    print("1. Install Python dependencies")
    print("2. Download NLTK data")
    print("3. Download spaCy model (optional)")
    print("4. Verify installation")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Install dependencies
    print_header("Step 1: Installing Python Dependencies")
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing packages from requirements.txt"
    )
    
    if not success:
        print("⚠️ Warning: Some packages may have failed to install.")
        print("You may need to install them manually.")
    
    # Step 2: Download NLTK data
    print_header("Step 2: Downloading NLTK Data")
    
    nltk_downloads = [
        ('punkt', 'Punkt tokenizer'),
        ('stopwords', 'Stopwords corpus'),
        ('wordnet', 'WordNet lemmatizer'),
        ('punkt_tab', 'Punkt tokenizer tables')
    ]
    
    for package, description in nltk_downloads:
        run_command(
            f"{sys.executable} -c \"import nltk; nltk.download('{package}', quiet=True)\"",
            f"Downloading {description}"
        )
    
    # Step 3: Download spaCy model (optional)
    print_header("Step 3: Downloading spaCy Model (Optional)")
    print("The spaCy model (en_core_web_sm) enables advanced NLP features.")
    print("It's about 50MB. You can skip this if you want.")
    print()
    
    choice = input("Download spaCy model? (y/n): ").lower().strip()
    
    if choice == 'y':
        run_command(
            f"{sys.executable} -m spacy download en_core_web_sm",
            "Downloading spaCy English model"
        )
    else:
        print("⏭️ Skipping spaCy model download")
        print("Note: Some features may be limited without spaCy\n")
    
    # Step 4: Verify installation
    print_header("Step 4: Verifying Installation")
    
    try:
        import streamlit
        print("✅ Streamlit:", streamlit.__version__)
    except ImportError:
        print("❌ Streamlit: NOT INSTALLED")
    
    try:
        import pdfplumber
        print("✅ pdfplumber:", pdfplumber.__version__)
    except ImportError:
        print("❌ pdfplumber: NOT INSTALLED")
    
    try:
        import nltk
        print("✅ NLTK:", nltk.__version__)
    except ImportError:
        print("❌ NLTK: NOT INSTALLED")
    
    try:
        import sklearn
        print("✅ scikit-learn:", sklearn.__version__)
    except ImportError:
        print("❌ scikit-learn: NOT INSTALLED")
    
    try:
        import spacy
        print("✅ spaCy:", spacy.__version__)
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✅ spaCy model: LOADED")
        except:
            print("⚠️ spaCy model: NOT LOADED (some features may be limited)")
    except ImportError:
        print("⚠️ spaCy: NOT INSTALLED (optional)")
    
    try:
        from rake_nltk import Rake
        print("✅ RAKE-NLTK: INSTALLED")
    except ImportError:
        print("❌ RAKE-NLTK: NOT INSTALLED")
    
    # Final message
    print_header("Setup Complete!")
    print("🎉 Your environment is ready!")
    print()
    print("To run the application:")
    print("  streamlit run app.py")
    print()
    print("For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
