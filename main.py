"""Main Streamlit application entry point."""

import streamlit as st
from config.settings import APP_CONFIG
from ui.styles import apply_custom_styles
from ui.pages.calculator import render_calculator_page
from ui.pages.reference import render_reference_page
from ui.pages.ai_assistant import render_ai_assistant_page
from ui.pages.portfolio import render_portfolio_page
from calculations.saccr_engine import SACCREngine

def main():
    """Main application function."""
    # Configure Streamlit page
    st.set_page_config(**APP_CONFIG)
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize SA-CCR engine
    if 'saccr_engine' not in st.session_state:
        st.session_state.saccr_engine = SACCREngine()
    
    # Render header
    render_header()
    
    # Sidebar navigation
    page = render_sidebar()
    
    # Route to appropriate page
    route_to_page(page)

def render_header():
    """Render application header."""
    st.markdown("""
    <div class="ai-header">
        <div class="executive-title">🤖 AI SA-CCR Platform</div>
        <div class="executive-subtitle">Complete 24-Step Basel SA-CCR Calculator with LLM Integration</div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown("### 🤖 LLM Configuration")
        # LLM configuration logic here
        
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        return st.selectbox(
            "Select Module:",
            ["🧮 Complete SA-CCR Calculator", "📋 Reference Example", 
             "🤖 AI Assistant", "📊 Portfolio Analysis"]
        )

def route_to_page(page: str):
    """Route to the selected page."""
    if page == "🧮 Complete SA-CCR Calculator":
        render_calculator_page()
    elif page == "📋 Reference Example":
        render_reference_page()
    elif page == "🤖 AI Assistant":
        render_ai_assistant_page()
    elif page == "📊 Portfolio Analysis":
        render_portfolio_page()

if __name__ == "__main__":
    main()
