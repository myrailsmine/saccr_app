
import streamlit as st
from config.settings import STREAMLIT_CONFIG
from config.ui_styles import get_custom_css
from calculations.saccr_engine import ComprehensiveSACCREngine
from ai.llm_client import LLMClient
from ui.pages.calculator import render_calculator_page
from ui.pages.reference import render_reference_page
from ui.pages.ai_assistant import render_ai_assistant_page
from ui.pages.portfolio import render_portfolio_page

def main():
    """Main application function."""
    # Configure Streamlit
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Apply custom styles
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize components
    if 'saccr_engine' not in st.session_state:
        st.session_state.saccr_engine = ComprehensiveSACCREngine()
    
    if 'llm_client' not in st.session_state:
        st.session_state.llm_client = LLMClient()
    
    # Render header
    render_header()
    
    # Sidebar navigation
    page = render_sidebar()
    
    # Route to pages
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
        render_llm_config()
        
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        return st.selectbox(
            "Select Module:",
            ["🧮 Complete SA-CCR Calculator", "📋 Reference Example", 
             "🤖 AI Assistant", "📊 Portfolio Analysis"]
        )

def render_llm_config():
    """Render LLM configuration section."""
    with st.expander("🔧 LLM Setup", expanded=True):
        base_url = st.text_input("Base URL", value="http://localhost:8123/v1")
        api_key = st.text_input("API Key", value="dummy", type="password")
        model = st.text_input("Model", value="llama3")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
        max_tokens = st.number_input("Max Tokens", 1000, 8000, 4000, 100)
        
        if st.button("🔗 Connect LLM"):
            config = {
                'base_url': base_url,
                'api_key': api_key,
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'streaming': False
            }
            
            success = st.session_state.llm_client.setup_connection(config)
            if success:
                st.success("✅ LLM Connected!")
            else:
                st.error("❌ Connection Failed")
    
    # Connection status
    if st.session_state.llm_client.is_connected():
        st.markdown('<div class="connection-status connected">🟢 LLM Connected</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="connection-status disconnected">🔴 LLM Disconnected</div>', 
                   unsafe_allow_html=True)

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
