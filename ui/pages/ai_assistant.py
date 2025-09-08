# ui/pages/ai_assistant.py
"""AI assistant page for SA-CCR questions and analysis."""

import streamlit as st
from datetime import datetime
from typing import Dict, List

from ai.llm_client import LLMClient
from ai.enhanced_saccr_assistant import EnhancedSACCRAssistant
from ai.response_generators import generate_template_response


def render_ai_assistant_page():
    """Render the AI assistant page."""
    st.markdown("## AI SA-CCR Expert Assistant")
    st.markdown("*Ask detailed questions about SA-CCR calculations, Basel regulations, and optimization strategies*")
    
    # Quick question templates
    _render_sample_questions()
    
    # Chat interface
    _render_chat_interface()
    
    # Display chat history
    _render_chat_history()


def _render_sample_questions():
    """Render sample questions section."""
    with st.expander("Sample Questions", expanded=True):
        st.markdown("""
        **Try these SA-CCR specific questions:**
        - "Explain how the PFE multiplier works and what drives it"
        - "What's the difference between margined and unmargined RC calculation?"
        - "How do supervisory correlations affect my add-on calculations?"
        - "What optimization strategies can reduce my SA-CCR capital?"
        - "Walk me through the 24-step calculation methodology"
        - "How does central clearing affect my Alpha multiplier?"
        """)


def _render_chat_interface():
    """Render the main chat interface."""
    st.markdown("### Ask the AI Expert")
    
    if 'saccr_chat_history' not in st.session_state:
        st.session_state.saccr_chat_history = []
    
    user_question = st.text_area(
        "Your SA-CCR Question:",
        placeholder="e.g., How can I optimize my derivatives portfolio to reduce SA-CCR capital requirements?",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Ask AI Expert", type="primary"):
            if user_question.strip():
                _process_ai_question(user_question)
    
    with col2:
        if st.button("Clear Chat History"):
            st.session_state.saccr_chat_history = []
            st.rerun()


def _process_ai_question(user_question: str):
    """Process user question and generate AI response."""
    # Add user question to history
    st.session_state.saccr_chat_history.append({
        'type': 'user',
        'content': user_question,
        'timestamp': datetime.now()
    })
    
    # Get portfolio context if available
    portfolio_context = _get_portfolio_context()
    
    # Generate AI response
    with st.spinner("AI is analyzing your SA-CCR question..."):
        try:
            if hasattr(st.session_state, 'llm_client') and st.session_state.llm_client.is_connected():
                ai_response = _generate_llm_response(user_question, portfolio_context)
            else:
                ai_response = generate_template_response(user_question, portfolio_context)
            
            # Add AI response to history
            st.session_state.saccr_chat_history.append({
                'type': 'ai',
                'content': ai_response,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            st.error(f"AI response error: {str(e)}")


def _get_portfolio_context() -> Dict:
    """Get current portfolio context if available."""
    portfolio_context = {}
    if 'trades_input' in st.session_state and st.session_state.trades_input:
        portfolio_context = {
            'trade_count': len(st.session_state.trades_input),
            'asset_classes': list(set(t.asset_class.value for t in st.session_state.trades_input)),
            'total_notional': sum(abs(t.notional) for t in st.session_state.trades_input),
            'currencies': list(set(t.currency for t in st.session_state.trades_input))
        }
    return portfolio_context


def _generate_llm_response(user_question: str, portfolio_context: Dict) -> str:
    """Generate LLM response using connected AI."""
    from langchain.schema import HumanMessage, SystemMessage
    
    system_prompt = """You are a Basel SA-CCR regulatory expert with deep knowledge of:
    - Complete 24-step SA-CCR calculation methodology
    - Supervisory factors, correlations, and regulatory parameters
    - PFE multiplier calculations and netting benefits
    - Replacement cost calculations with collateral
    - EAD, RWA, and capital requirement calculations
    - Portfolio optimization strategies for SA-CCR
    - Central clearing benefits and Alpha multipliers
    
    Provide detailed, technical answers with specific formulas and examples."""
    
    context_info = f"\nCurrent Portfolio Context: {portfolio_context}" if portfolio_context else ""
    
    user_prompt = f"""
    SA-CCR Question: {user_question}
    {context_info}
    
    Please provide a comprehensive answer including:
    - Technical explanation with relevant formulas
    - Specific regulatory references (Basel framework)
    - Practical examples or scenarios
    - Actionable recommendations
    - Impact quantification where possible
    """
    
    response = st.session_state.llm_client.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return response if response else "AI response generation failed."


def _render_chat_history():
    """Render chat history."""
    if st.session_state.saccr_chat_history:
        st.markdown("### Conversation History")
        
        for chat in reversed(st.session_state.saccr_chat_history[-6:]):
            if chat['type'] == 'user':
                st.markdown(f"""
                <div class="user-query">
                    <strong>You:</strong> {chat['content']}
                    <br><small style="color: #666;">{chat['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-response">
                    <strong>SA-CCR Expert:</strong><br>
                    {chat['content']}
                    <br><small style="color: rgba(255,255,255,0.7);">{chat['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
