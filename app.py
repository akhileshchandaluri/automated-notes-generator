"""
Streamlit Web Application for PDF Notes Generator
"""

import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
import json
from datetime import datetime

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from modules.notes_generator import NotesGenerator

# Page config
st.set_page_config(
    page_title="AI Notes Generator - Transform Your Learning",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-Powered Notes Generator - Transform PDFs into comprehensive study materials"
    }
)

# Clean Stripe-Inspired Premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* ==================== ROOT VARIABLES ==================== */
    :root {
        --bg-primary: #0A0D14;
        --bg-secondary: #12151C;
        --bg-tertiary: #1A1D26;
        --accent-primary: #635BFF;
        --accent-blue: #0073E6;
        --accent-gradient: linear-gradient(135deg, #635BFF 0%, #0073E6 100%);
        --text-primary: #FFFFFF;
        --text-secondary: #A0A8B8;
        --text-muted: #6B7280;
        --border: rgba(99, 91, 255, 0.15);
        --success: #10B981;
        --error: #EF4444;
    }
    
    /* ==================== GLOBAL RESET ==================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* ==================== MAIN APP ==================== */
    .stApp {
        background: var(--bg-primary);
        background-image: 
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 91, 255, 0.1), transparent),
            radial-gradient(ellipse 60% 40% at 100% 100%, rgba(0, 115, 230, 0.08), transparent);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* ==================== CONTAINER ==================== */
    .main .block-container {
        max-width: 1280px;
        padding: 4rem 2rem 2rem 2rem;
    }
    
    /* ==================== SIDEBAR ==================== */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* ==================== TYPOGRAPHY ==================== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    
    h1 { 
        font-size: 4.5rem; 
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #A0A8B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.04em;
    }
    
    h2 { font-size: 2.5rem; }
    h3 { font-size: 1.75rem; }
    
    p, li, span, label {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
        font-weight: 400;
    }
    
    /* ==================== PREMIUM CARDS ==================== */
    .premium-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--accent-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 91, 255, 0.4);
        box-shadow: 0 12px 40px rgba(99, 91, 255, 0.15);
    }
    
    .premium-card:hover::before {
        opacity: 1;
    }
    
    /* ==================== BUTTONS - STRIPE QUALITY ==================== */
    .stButton > button {
        background: var(--accent-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.02em;
        box-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.2),
            0 10px 30px rgba(99, 91, 255, 0.3);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.4s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 2px 5px rgba(0, 0, 0, 0.2),
            0 15px 40px rgba(99, 91, 255, 0.4);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ==================== DOWNLOAD BUTTONS ==================== */
    .stDownloadButton > button {
        background: transparent;
        color: var(--accent-primary);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(99, 91, 255, 0.1);
        border-color: var(--accent-primary);
        transform: translateY(-2px);
    }
    
    /* ==================== TABS - STRIPE STYLE ==================== */
    .stTabs {
        background: transparent;
        padding: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid var(--border);
        gap: 0;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        border-radius: 0;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--accent-primary);
        background: rgba(99, 91, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-primary);
        border-bottom-color: var(--accent-primary);
        background: transparent;
    }
    
    /* ==================== STATS BOXES ==================== */
    .stat-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-box::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: var(--accent-gradient);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .stat-box:hover::after {
        transform: scaleX(1);
    }
    
    .stat-box:hover {
        transform: translateY(-4px);
        border-color: var(--accent-primary);
        box-shadow: 0 12px 40px rgba(99, 91, 255, 0.2);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ==================== FILE UPLOADER ==================== */
    [data-testid="stFileUploader"] {
        background: var(--bg-secondary);
        border: 2px dashed var(--border);
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-primary);
        background: rgba(99, 91, 255, 0.03);
    }
    
    /* ==================== PROGRESS BAR ==================== */
    .stProgress > div > div > div > div {
        background: var(--accent-gradient);
        border-radius: 10px;
    }
    
    .stProgress > div > div > div {
        background: rgba(99, 91, 255, 0.1);
        border-radius: 10px;
    }
    
    /* ==================== ALERTS ==================== */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left: 3px solid var(--success);
        border-radius: 10px;
        color: var(--text-secondary);
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left: 3px solid var(--error);
        border-radius: 10px;
        color: var(--text-secondary);
    }
    
    .stInfo {
        background: rgba(99, 91, 255, 0.1);
        border-left: 3px solid var(--accent-primary);
        border-radius: 10px;
        color: var(--text-secondary);
    }
    
    /* ==================== MARKDOWN ==================== */
    .stMarkdown {
        color: var(--text-secondary);
    }
    
    .stMarkdown strong {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .stMarkdown code {
        background: var(--bg-tertiary);
        color: var(--accent-primary);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.9em;
    }
    
    /* ==================== CHECKBOXES & RADIO ==================== */
    .stCheckbox label, .stRadio label {
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* ==================== EXPANDER ==================== */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text-primary);
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(99, 91, 255, 0.05);
        border-color: var(--accent-primary);
    }
    
    /* ==================== SCROLLBAR ==================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-blue);
    }
    
    /* ==================== ANIMATIONS ==================== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .premium-card, .stat-box {
        animation: fadeInUp 0.6s ease-out backwards;
    }
    
    .premium-card:nth-child(1) { animation-delay: 0.05s; }
    .premium-card:nth-child(2) { animation-delay: 0.1s; }
    .premium-card:nth-child(3) { animation-delay: 0.15s; }
    .premium-card:nth-child(4) { animation-delay: 0.2s; }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'notes_generated' not in st.session_state:
        st.session_state.notes_generated = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'generator' not in st.session_state:
        st.session_state.generator = None
    if 'use_llm' not in st.session_state:
        st.session_state.use_llm = True
    if 'llm_model' not in st.session_state:
        st.session_state.llm_model = "llama3.2:3b"

def display_header():
    """Display premium Stripe-style header"""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem 3rem 2rem; animation: fadeInUp 0.8s ease-out;">
        <div style="
            display: inline-block;
            background: rgba(99, 91, 255, 0.1);
            border: 1px solid rgba(99, 91, 255, 0.3);
            border-radius: 50px;
            padding: 0.5rem 1.2rem;
            margin-bottom: 1.5rem;
        ">
            <span style="font-size: 0.85rem; color: #635BFF; font-weight: 600; letter-spacing: 0.05em;">
                ✨ POWERED BY ADVANCED AI
            </span>
        </div>
        <h1 style="
            font-size: 4.5rem;
            font-weight: 800;
            margin: 0 0 1rem 0;
            letter-spacing: -0.04em;
            line-height: 1.1;
        ">
            AI Notes Generator
        </h1>
        <p style="
            font-size: 1.25rem;
            color: #A0A8B8;
            font-weight: 400;
            margin: 0 auto;
            max-width: 650px;
            line-height: 1.6;
        ">
            Transform PDFs into comprehensive study materials with cutting-edge technology
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display clean Stripe-style sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style='padding: 0 0 2rem 0;'>
            <h2 style='margin: 0; font-size: 1.5rem;'>⚙️ Configuration</h2>
            <p style='color: #A0A8B8; font-size: 0.9rem; margin-top: 0.5rem;'>
                Customize your AI processing settings
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        
        # LLM Mode selector
        use_llm = st.checkbox("🚀 Enable AI Mode", value=True, 
                             help="Uses advanced LLM for best quality. Disable for faster traditional processing.")
        
        if use_llm:
            st.markdown("<div style='margin-top: 1rem; padding: 1rem; background: rgba(99, 91, 255, 0.1); border-radius: 12px; border: 1px solid rgba(99, 91, 255, 0.2);'>", unsafe_allow_html=True)
            quality_mode = st.radio(
                "Model Selection:",
                ["⚡ Fast (3B) — ~20s/page", "🎯 Quality (8B) — ~45s/page"],
                index=0,
                help="Choose between speed and maximum quality"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.session_state.llm_model = "llama3.2:3b" if "Fast" in quality_mode else "llama3.1:8b"
        else:
            st.session_state.llm_model = None
        
        st.session_state.use_llm = use_llm
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='premium-card' style='margin-top: 1.5rem;'>
            <h3 style='margin: 0 0 1rem 0; font-size: 1.1rem;'>📊 Features</h3>
            <div style='display: flex; flex-direction: column; gap: 0.8rem;'>
                <div style='display: flex; align-items: center; gap: 0.7rem;'>
                    <span style='font-size: 1.3rem;'>🧠</span>
                    <span style='font-size: 0.9rem; color: #A0A8B8;'>Deep Learning Analysis</span>
                </div>
                <div style='display: flex; align-items: center; gap: 0.7rem;'>
                    <span style='font-size: 1.3rem;'>📝</span>
                    <span style='font-size: 0.9rem; color: #A0A8B8;'>70% Content Extraction</span>
                </div>
                <div style='display: flex; align-items: center; gap: 0.7rem;'>
                    <span style='font-size: 1.3rem;'>🎯</span>
                    <span style='font-size: 0.9rem; color: #A0A8B8;'>50+ Key Points</span>
                </div>
                <div style='display: flex; align-items: center; gap: 0.7rem;'>
                    <span style='font-size: 1.3rem;'>🔑</span>
                    <span style='font-size: 0.9rem; color: #A0A8B8;'>30+ Keywords</span>
                </div>
                <div style='display: flex; align-items: center; gap: 0.7rem;'>
                    <span style='font-size: 1.3rem;'>❓</span>
                    <span style='font-size: 0.9rem; color: #A0A8B8;'>25+ Practice Questions</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='stripe-card' style='margin-top: 1.5rem;'>
            <h3 style='margin: 0 0 1rem 0; font-size: 1.1rem;'>🚀 Quick Start</h3>
            <ol style='padding-left: 1.2rem; margin: 0; color: var(--text-secondary); font-size: 0.9rem;'>
                <li style='margin-bottom: 0.5rem;'>Upload your PDF document</li>
                <li style='margin-bottom: 0.5rem;'>Configure AI settings above</li>
                <li style='margin-bottom: 0.5rem;'>Click "Generate Notes"</li>
                <li>Download in your preferred format</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border-color); text-align: center;'>
            <p style='font-size: 0.85rem; color: var(--text-muted); margin: 0;'>
                Built with ❤️ using Python & AI
            </p>
        </div>
        """, unsafe_allow_html=True)


def upload_section():
    """PDF upload section"""
    st.markdown("""
    <div class='stripe-card' style='text-align: center;'>
        <h2 style='margin: 0 0 0.5rem 0; font-size: 1.8rem;'>📄 Upload Document</h2>
        <p style='color: var(--text-muted); margin: 0;'>
            Drag and drop your PDF or click to browse
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload any PDF document (textbook, research paper, notes, etc.)",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        generate_button = st.button(
            "Generate Notes →",
            type="primary",
            use_container_width=True,
            disabled=(uploaded_file is None)
        )
    
    return uploaded_file, generate_button


def process_pdf(uploaded_file):
    """Process PDF and generate notes with live progress"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Initialize generator with current settings
        use_llm = st.session_state.get('use_llm', True)
        llm_model = st.session_state.get('llm_model', 'llama3.2:3b')
        
        # Progress container
        st.markdown("""
        <div class='premium-card' style='text-align: center; margin: 2rem 0;'>
            <h3 style='margin: 0 0 0.5rem 0;'>⚡ Processing Your Document</h3>
            <p style='color: #A0A8B8; margin: 0;'>Please wait while we generate your notes...</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        # Progress callback function
        def progress_callback(message):
            """Update progress in real-time"""
            status_container.markdown(f"""
            <div style='
                text-align: center; 
                padding: 1rem;
                background: rgba(99, 91, 255, 0.1);
                border-radius: 12px;
                border: 1px solid rgba(99, 91, 255, 0.2);
                margin: 1rem 0;
            '>
                <p style='
                    font-size: 1rem;
                    color: #635BFF;
                    margin: 0;
                    font-weight: 500;
                '>
                    {message}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        if use_llm:
            status_container.info(f"🤖 Using AI Mode: {llm_model}")
            st.session_state.generator = NotesGenerator(use_llm=True, progress_callback=progress_callback)
            if hasattr(st.session_state.generator, 'llm_summarizer'):
                st.session_state.generator.llm_summarizer.model = llm_model
        else:
            status_container.info("⚡ Using Traditional Mode (Lightning Fast)")
            st.session_state.generator = NotesGenerator(use_llm=False, progress_callback=progress_callback)
        
        progress_bar.progress(10)
        progress_callback("📄 Extracting Text from PDF...")
        
        progress_bar.progress(20)
        
        results = st.session_state.generator.generate_notes(
            tmp_path,
            output_dir=str(output_dir)
        )
        
        progress_bar.progress(90)
        
        # Clean up
        os.unlink(tmp_path)
        
        progress_callback("✅ Generation Complete!")
        progress_bar.progress(100)
        
        # Success message
        st.success("🎉 Success! Your study notes have been generated.")
        
        # Update session state
        st.session_state.results = results
        st.session_state.notes_generated = True
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False


def display_statistics():
    """Display document statistics"""
    if not st.session_state.results:
        return
    
    metadata = st.session_state.results['metadata']
    
    st.markdown("""
    <div style='text-align: center; margin: 3rem 0 2rem 0;'>
        <h2 style='font-size: 2.5rem; margin: 0;'>📊 Document Analysis</h2>
        <p style='color: #A0A8B8; margin-top: 0.5rem;'>Key metrics from your document</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{metadata["page_count"]}</div>'
            f'<div class="stat-label">Pages</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{metadata.get("points_extracted", "N/A")}</div>'
            f'<div class="stat-label">Points Extracted</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{metadata["word_count"]}</div>'
            f'<div class="stat-label">Words</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{len(st.session_state.results["keywords"])}</div>'
            f'<div class="stat-label">Keywords</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col5:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{len(st.session_state.results["qa_pairs"])}</div>'
            f'<div class="stat-label">Questions</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")


def display_results():
    """Display results in tabs"""
    if not st.session_state.results:
        return
    
    results = st.session_state.results
    
    # Create tabs (removed Mindmap)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📖 Page-wise Notes",
        "📘 Summary",
        "📌 Key Points",
        "🔑 Keywords",
        "❓ Q&A",
        "💾 Download"
    ])
    
    # Tab 1: Organized Page-wise Content (NEW - FIRST TAB)
    with tab1:
        st.markdown("<div class='stripe-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin: 0 0 1rem 0;'>Page-by-Page Breakdown</h2>", unsafe_allow_html=True)
        if results['metadata'].get('ai_generated'):
            st.markdown("<div style='margin-bottom: 1rem;'><span class='ai-badge'><span>🤖</span><span>AI Generated</span></span></div>", unsafe_allow_html=True)
        st.info(f"Extracted {results['metadata'].get('points_extracted', 'N/A')} key points from {results['metadata']['page_count']} pages")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if 'organized_content' in results:
            st.markdown("<div class='stripe-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown(results['organized_content'])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Organized content not available. Please regenerate notes.")
    
    # Tab 2: Summary
    with tab2:
        st.markdown("<div class='stripe-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin: 0 0 1rem 0;'>Document Summary</h2>", unsafe_allow_html=True)
        if results['metadata'].get('ai_generated'):
            st.markdown("<div style='margin-bottom: 1rem;'><span class='ai-badge'><span>🤖</span><span>AI Generated</span></span></div>", unsafe_allow_html=True)
        else:
            st.info(f"Compression: {results['summary']['compression_ratio']} ({len(results['summary']['sentences'])} of {results['metadata']['sentence_count']} sentences)")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='stripe-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        st.markdown("### Summary")
        st.write(results['summary']['text'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        if results['summary']['sentences']:
            with st.expander("View Source Sentences"):
                for i, sent in enumerate(results['summary']['sentences'], 1):
                    st.markdown(f"<div style='padding: 0.8rem; margin: 0.5rem 0; background: var(--bg-tertiary); border-radius: 8px; border-left: 3px solid var(--accent-purple);'>{i}. {sent}</div>", unsafe_allow_html=True)
    
    # Tab 3: Key Points
    with tab3:
        st.markdown("<div class='stripe-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin: 0 0 0.5rem 0;'>Key Points</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-muted);'>Most important takeaways from the document</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        for i, point in enumerate(results['key_points'], 1):
            st.markdown(f"""
            <div class='stripe-card' style='margin: 1rem 0; padding: 1.5rem; border-left: 3px solid var(--accent-purple);'>
                <div style='display: flex; gap: 1rem;'>
                    <div style='font-size: 1.2rem; font-weight: 700; color: var(--accent-purple); min-width: 2rem;'>{i}</div>
                    <div style='color: var(--text-primary); line-height: 1.6;'>{point}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 4: Keywords
    with tab4:
        st.markdown("<div class='stripe-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin: 0 0 0.5rem 0;'>Keywords</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-muted);'>Important terms and concepts identified</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display as badges
        st.markdown("<div class='stripe-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        keywords_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.5rem;'>"
        for kw in results['keywords']:
            keywords_html += f'<span class="keyword-badge">{kw["term"]}</span>'
        keywords_html += "</div>"
        st.markdown(keywords_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display with scores
        st.markdown("<div class='stripe-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        st.markdown("### Relevance Scores")
        cols = st.columns(3)
        for i, kw in enumerate(results['keywords']):
            with cols[i % 3]:
                st.metric(label=kw['term'], value=f"{kw['score']:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 5: Q&A
    with tab5:
        st.markdown("<div class='stripe-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin: 0 0 1rem 0;'>Practice Questions</h2>", unsafe_allow_html=True)
        if results['metadata'].get('ai_generated'):
            st.markdown("<div style='margin-bottom: 1rem;'><span class='ai-badge'><span>🤖</span><span>AI Generated</span></span></div>", unsafe_allow_html=True)
        st.info(f"{len(results['qa_pairs'])} questions to test your understanding")
        st.markdown("</div>", unsafe_allow_html=True)
        
        for i, qa in enumerate(results['qa_pairs'], 1):
            st.markdown(f"""
            <div class='stripe-card' style='margin: 1.5rem 0;'>
                <div style='margin-bottom: 1rem;'>
                    <span style='background: var(--accent-gradient); color: white; padding: 0.3rem 0.8rem; border-radius: 6px; font-weight: 600; font-size: 0.85rem;'>Q{i}</span>
                </div>
                <h3 style='margin: 0 0 1rem 0; font-size: 1.2rem; color: var(--text-primary);'>{qa['question']}</h3>
                <div style='background: var(--bg-tertiary); padding: 1.2rem; border-radius: 10px; border-left: 3px solid var(--success-color);'>
                    <div style='color: var(--success-color); font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem;'>ANSWER</div>
                    <p style='color: var(--text-secondary); margin: 0; line-height: 1.6;'>{qa['answer']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 6: Download
    with tab6:
        st.markdown("""
        <div class='stripe-card' style='text-align: center;'>
            <h2 style='margin: 0 0 0.5rem 0;'>Export Your Notes</h2>
            <p style='color: var(--text-muted); margin: 0;'>Download in your preferred format</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Export
        st.markdown("<div class='stripe-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0 0 1rem 0;'>📄 PDF Format</h3>", unsafe_allow_html=True)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            story = []
            styles = getSampleStyleSheet()
            
            # Add content
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                        fontSize=20, spaceAfter=30, alignment=1)
            story.append(Paragraph(f"Study Notes", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            content = results.get('organized_content', '')
            for line in content.split('\\n'):
                if line.strip():
                    clean_line = line.replace('#', '').replace('**', '').replace('*', '')
                    story.append(Paragraph(clean_line, styles['Normal']))
                    story.append(Spacer(1, 0.05*inch))
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            st.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name=f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"PDF generation error: {e}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='stripe-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        st.markdown("### Other Formats")
        col1, col2, col3 = st.columns(3)
        
        # JSON download
        with col1:
            json_str = json.dumps(results, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Text download
        with col2:
            text_notes = st.session_state.generator._format_notes_text()
            st.download_button(
                label="📝 Download TXT",
                data=text_notes,
                file_name=f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Markdown download
        with col3:
            md_notes = st.session_state.generator._format_notes_markdown()
            st.download_button(
                label="📋 Download Markdown",
                data=md_notes,
                file_name=f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Main application"""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # Upload section
    uploaded_file, generate_button = upload_section()
    
    # Process button click
    if generate_button and uploaded_file:
        success = process_pdf(uploaded_file)
        
        if success:
            st.balloons()
            st.markdown("""
            <div class='stripe-card' style='text-align: center; border-color: var(--success-color); animation: fadeIn 0.6s ease;'>
                <h2 style='margin: 0; color: var(--success-color); font-size: 2rem;'>✓ Success</h2>
                <p style='margin: 0.5rem 0 0 0; color: var(--text-secondary);'>Your notes are ready to explore</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Display results if available
    if st.session_state.notes_generated:
        st.markdown("---")
        display_statistics()
        display_results()
    else:
        # Show example/instructions
        st.markdown("---")
        st.markdown("""
        <div class='stripe-card' style='text-align: center; margin-top: 3rem; padding: 3rem 2rem;'>
            <h3 style='margin: 0 0 1rem 0; font-size: 2rem;'>Get started by uploading a document</h3>
            <p style='color: var(--text-muted); font-size: 1.1rem; max-width: 600px; margin: 0 auto;'>
                Upload any PDF to instantly transform it into comprehensive study notes with AI-powered analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='stripe-card' style='margin-top: 2rem;'>
                <h3 style='margin: 0 0 1.5rem 0; font-size: 1.3rem;'>What You Can Upload</h3>
                <div style='display: flex; flex-direction: column; gap: 1rem;'>
                    <div style='display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: var(--bg-tertiary); border-radius: 8px;'>
                        <span style='font-size: 1.8rem;'>📚</span>
                        <div>
                            <div style='font-weight: 600; color: var(--text-primary);'>Textbooks</div>
                            <div style='font-size: 0.85rem; color: var(--text-muted);'>Academic materials</div>
                        </div>
                    </div>
                    <div style='display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: var(--bg-tertiary); border-radius: 8px;'>
                        <span style='font-size: 1.8rem;'>🔬</span>
                        <div>
                            <div style='font-weight: 600; color: var(--text-primary);'>Research Papers</div>
                            <div style='font-size: 0.85rem; color: var(--text-muted);'>Scientific documents</div>
                        </div>
                    </div>
                    <div style='display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: var(--bg-tertiary); border-radius: 8px;'>
                        <span style='font-size: 1.8rem;'>📝</span>
                        <div>
                            <div style='font-weight: 600; color: var(--text-primary);'>Study Materials</div>
                            <div style='font-size: 0.85rem; color: var(--text-muted);'>Any educational content</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='stripe-card' style='margin-top: 2rem;'>
                <h3 style='margin: 0 0 1.5rem 0; font-size: 1.3rem;'>What You Get</h3>
                <div style='display: flex; flex-direction: column; gap: 1rem;'>
                    <div style='display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: var(--bg-tertiary); border-radius: 8px;'>
                        <span style='font-size: 1.8rem;'>📝</span>
                        <div>
                            <div style='font-weight: 600; color: var(--text-primary);'>Smart Summaries</div>
                            <div style='font-size: 0.85rem; color: var(--text-muted);'>AI-generated overviews</div>
                        </div>
                    </div>
                    <div style='display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: var(--bg-tertiary); border-radius: 8px;'>
                        <span style='font-size: 1.8rem;'>🎯</span>
                        <div>
                            <div style='font-weight: 600; color: var(--text-primary);'>Key Points</div>
                            <div style='font-size: 0.85rem; color: var(--text-muted);'>Essential takeaways</div>
                        </div>
                    </div>
                    <div style='display: flex; align-items: center; gap: 1rem; padding: 0.8rem; background: var(--bg-tertiary); border-radius: 8px;'>
                        <span style='font-size: 1.8rem;'>❓</span>
                        <div>
                            <div style='font-weight: 600; color: var(--text-primary);'>Practice Questions</div>
                            <div style='font-size: 0.85rem; color: var(--text-muted);'>Test your knowledge</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
