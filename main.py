# ==============================================================================
# MAIN.PY - Modular SA-CCR Application Entry Point
# ==============================================================================

"""
Main Streamlit application for the AI-powered SA-CCR Platform.
Integrates all modular components into a cohesive application.
"""

import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core imports
from config.settings import STREAMLIT_CONFIG, DEFAULT_LLM_CONFIG
from config.ui_styles import get_custom_css
from calculations.saccr_engine import UnifiedSACCREngine
from ai.llm_client import LLMClient

# UI page imports
from ui.pages.calculator import render_calculator_page
from ui.pages.reference import render_reference_page
from ui.pages.ai_assistant import render_ai_assistant_page
from ui.pages.portfolio import render_portfolio_page


def main():
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Apply custom styles
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize application components
    initialize_session_state()
    
    # Render application header
    render_application_header()
    
    # Render sidebar with navigation and LLM config
    selected_page = render_sidebar()
    
    # Route to selected page
    route_to_page(selected_page)


def initialize_session_state():
    """Initialize all session state variables."""
    
    # Initialize SA-CCR calculation engine
    if 'saccr_engine' not in st.session_state:
        st.session_state.saccr_engine = UnifiedSACCREngine()
    
    # Initialize LLM client
    if 'llm_client' not in st.session_state:
        st.session_state.llm_client = LLMClient()
    
    # Initialize trade and collateral inputs
    if 'trades_input' not in st.session_state:
        st.session_state.trades_input = []
    
    if 'collateral_input' not in st.session_state:
        st.session_state.collateral_input = []
    
    # Initialize AI chat history
    if 'saccr_chat_history' not in st.session_state:
        st.session_state.saccr_chat_history = []
    
    # Initialize calculation results cache
    if 'last_calculation_result' not in st.session_state:
        st.session_state.last_calculation_result = None


def render_application_header():
    """Render the main application header."""
    st.markdown("""
    <div class="ai-header">
        <div class="executive-title">🤖 AI SA-CCR Platform</div>
        <div class="executive-subtitle">Complete 24-Step Basel SA-CCR Calculator with LLM Integration</div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with navigation and configuration options."""
    with st.sidebar:
        # LLM Configuration Section
        st.markdown("### 🤖 LLM Configuration")
        render_llm_configuration()
        
        # Navigation Section
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        
        page_options = [
            "🧮 Complete SA-CCR Calculator",
            "📋 Reference Example", 
            "🤖 AI Assistant",
            "📊 Portfolio Analysis"
        ]
        
        selected_page = st.selectbox(
            "Select Module:",
            page_options,
            help="Choose the module you want to use"
        )
        
        # Application Status Section
        st.markdown("---")
        render_application_status()
        
        # Quick Stats Section
        render_quick_stats()
        
        return selected_page


def render_llm_configuration():
    """Render LLM configuration and connection management."""
    with st.expander("🔧 LLM Setup", expanded=False):
        # Configuration inputs
        col1, col2 = st.columns(2)
        
        with col1:
            base_url = st.text_input(
                "Base URL", 
                value=DEFAULT_LLM_CONFIG['base_url'],
                help="URL of the LLM API endpoint"
            )
            api_key = st.text_input(
                "API Key", 
                value=DEFAULT_LLM_CONFIG['api_key'], 
                type="password",
                help="API key for authentication"
            )
        
        with col2:
            model = st.text_input(
                "Model", 
                value=DEFAULT_LLM_CONFIG['model'],
                help="Model name to use"
            )
            temperature = st.slider(
                "Temperature", 
                0.0, 1.0, 
                DEFAULT_LLM_CONFIG['temperature'], 
                0.1,
                help="Controls randomness in responses"
            )
        
        max_tokens = st.number_input(
            "Max Tokens", 
            1000, 8000, 
            DEFAULT_LLM_CONFIG['max_tokens'], 
            100,
            help="Maximum tokens in response"
        )
        
        # Connection button
        if st.button("🔗 Connect LLM", help="Test and establish LLM connection"):
            config = {
                'base_url': base_url,
                'api_key': api_key,
                'model': model,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'streaming': False
            }
            
            with st.spinner("Connecting to LLM..."):
                success = st.session_state.llm_client.setup_connection(config)
                if success:
                    st.success("✅ LLM Connected!")
                else:
                    st.error("❌ Connection Failed")
    
    # Connection status indicator
    render_connection_status()


def render_connection_status():
    """Render current LLM connection status."""
    if st.session_state.llm_client.is_connected():
        st.markdown("""
        <div class="connection-status connected">
            🟢 LLM Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="connection-status disconnected">
            🔴 LLM Disconnected
        </div>
        """, unsafe_allow_html=True)


def render_application_status():
    """Render application status and key metrics."""
    st.markdown("### 📈 Application Status")
    
    # Current portfolio status
    trade_count = len(st.session_state.trades_input)
    collateral_count = len(st.session_state.collateral_input)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Trades", trade_count)
    with col2:
        st.metric("Collateral", collateral_count)
    
    # Calculation status
    if st.session_state.last_calculation_result:
        st.success("✅ Last calculation completed")
        final_results = st.session_state.last_calculation_result.get('final_results', {})
        if final_results:
            ead = final_results.get('exposure_at_default', 0)
            capital = final_results.get('capital_requirement', 0)
            st.write(f"EAD: ${ead/1_000_000:.1f}M")
            st.write(f"Capital: ${capital/1_000:.0f}K")
    else:
        st.info("ℹ️ No calculations performed yet")


def render_quick_stats():
    """Render quick portfolio statistics."""
    if st.session_state.trades_input:
        st.markdown("### 📊 Portfolio Quick Stats")
        
        trades = st.session_state.trades_input
        total_notional = sum(abs(t.notional) for t in trades)
        asset_classes = len(set(t.asset_class for t in trades))
        currencies = len(set(t.currency for t in trades))
        
        st.write(f"**Total Notional:** ${total_notional/1_000_000:.0f}M")
        st.write(f"**Asset Classes:** {asset_classes}")
        st.write(f"**Currencies:** {currencies}")
        
        # Show asset class distribution
        if len(trades) > 1:
            ac_distribution = {}
            for trade in trades:
                ac = trade.asset_class.value
                ac_distribution[ac] = ac_distribution.get(ac, 0) + 1
            
            st.write("**Distribution:**")
            for ac, count in ac_distribution.items():
                st.write(f"• {ac}: {count} trade{'s' if count > 1 else ''}")


def route_to_page(selected_page: str):
    """Route user to the selected page."""
    
    # Clear any existing error states
    if hasattr(st.session_state, 'page_error'):
        del st.session_state.page_error
    
    try:
        if selected_page == "🧮 Complete SA-CCR Calculator":
            render_calculator_page()
        
        elif selected_page == "📋 Reference Example":
            render_reference_page()
        
        elif selected_page == "🤖 AI Assistant":
            render_ai_assistant_page()
        
        elif selected_page == "📊 Portfolio Analysis":
            render_portfolio_page()
        
        else:
            st.error(f"Unknown page: {selected_page}")
    
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.exception(e)  # For debugging in development


def render_footer():
    """Render application footer with additional information."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>
            AI SA-CCR Platform | Basel III Compliant | 
            <a href="https://www.bis.org/bcbs/publ/d279.htm" target="_blank">Basel Framework Reference</a>
        </small>
    </div>
    """, unsafe_allow_html=True)


def handle_application_errors():
    """Global error handler for the application."""
    if 'app_error' in st.session_state:
        st.error(f"Application Error: {st.session_state.app_error}")
        if st.button("Clear Error"):
            del st.session_state.app_error
            st.rerun()


def main_with_error_handling():
    """Main function with comprehensive error handling."""
    try:
        main()
        render_footer()
    except Exception as e:
        st.error("Critical Application Error")
        st.exception(e)
        
        # Provide recovery options
        st.markdown("### Recovery Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Restart Application"):
                # Clear session state and restart
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear Data"):
                # Clear only data, keep configuration
                keys_to_clear = ['trades_input', 'collateral_input', 'last_calculation_result', 'saccr_chat_history']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col3:
            if st.button("📋 Show Debug Info"):
                st.json({
                    'error': str(e),
                    'session_state_keys': list(st.session_state.keys()),
                    'streamlit_version': st.__version__
                })


# ==============================================================================
# APPLICATION CONFIGURATION AND UTILITIES
# ==============================================================================

def configure_page_layout():
    """Configure additional page layout options."""
    # Hide Streamlit style elements (optional)
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    # Uncomment the line below to hide Streamlit branding
    # st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Add custom favicon (if you have one)
    # st.markdown('<link rel="icon" type="image/png" href="favicon.png">', unsafe_allow_html=True)


def setup_logging():
    """Setup application logging (for production deployment)."""
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('saccr_app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Log application startup
    logger = logging.getLogger(__name__)
    logger.info("SA-CCR Application starting up")
    
    return logger


def health_check():
    """Application health check for monitoring."""
    health_status = {
        'status': 'healthy',
        'components': {
            'saccr_engine': 'ok' if 'saccr_engine' in st.session_state else 'not_initialized',
            'llm_client': 'connected' if st.session_state.get('llm_client', {}).is_connected() else 'disconnected',
            'trade_data': f"{len(st.session_state.get('trades_input', []))} trades loaded",
            'collateral_data': f"{len(st.session_state.get('collateral_input', []))} collateral items"
        }
    }
    return health_status


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # For production, you might want to add additional configuration
    # setup_logging()
    # configure_page_layout()
    
    # Run the application with error handling
    main_with_error_handling()


# ==============================================================================
# DEPLOYMENT NOTES
# ==============================================================================

"""
Deployment Instructions:

1. Local Development:
   streamlit run main.py

2. Production Deployment:
   - Set environment variables for LLM configuration
   - Use requirements.txt for dependencies
   - Consider using Docker for containerization
   - Set up proper logging and monitoring

3. Docker Deployment:
   FROM python:3.9-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "main.py"]

4. Cloud Deployment:
   - Streamlit Cloud: Connect GitHub repo
   - AWS/GCP/Azure: Use container services
   - Heroku: Add Procfile with "web: streamlit run main.py"

5. Environment Variables:
   - STREAMLIT_SERVER_PORT=8501
   - STREAMLIT_SERVER_ADDRESS=0.0.0.0
   - LLM_BASE_URL=your_llm_endpoint
   - LLM_API_KEY=your_api_key
"""
