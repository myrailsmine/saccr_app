# ui/pages/ai_assistant.py
"""AI assistant page for SA-CCR questions and analysis."""

import streamlit as st
from datetime import datetime
from typing import Dict, List

from ai.llm_client import LLMClient
from ai.enhanced_saccr_assistant import EnhancedSACCRAssistant
from ai.response_generators import generate_template_response


def render_ai_assistant_page():
    """Render the enhanced AI assistant page."""
    st.markdown("## 🤖 Enhanced SA-CCR AI Assistant")
    st.markdown("""
    *Expert guidance with complete regulatory knowledge of **12 CFR 217.132** and the **24-step calculation process***
    
    **New Capabilities:**
    - 📊 **EAD Estimation** from natural language trade descriptions
    - 📋 **Step-by-step guidance** through the complete 24-step process
    - 🎯 **Conversational support** with human-in-the-loop capabilities
    - 📖 **Regulatory citations** with specific CFR references
    """)
    
    # Tabs for different modes
    tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📈 EAD Estimator", "📋 24-Step Guide"])
    
    with tab1:
        # Quick question templates
        _render_sample_questions()
        
        # Chat interface
        _render_chat_interface()
        
        # Display chat history
        _render_chat_history()
    
    with tab2:
        _render_ead_estimator()
    
    with tab3:
        _render_step_guide()


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
    """Process user question using Enhanced SA-CCR Assistant."""
    # Add user question to history
    st.session_state.saccr_chat_history.append({
        'type': 'user',
        'content': user_question,
        'timestamp': datetime.now()
    })
    
    # Get portfolio context if available
    portfolio_context = _get_portfolio_context()
    
    # Generate AI response using Enhanced Assistant
    with st.spinner("🤖 Enhanced SA-CCR AI is analyzing your question..."):
        try:
            # Initialize enhanced assistant if not exists
            if 'enhanced_assistant' not in st.session_state:
                st.session_state.enhanced_assistant = EnhancedSACCRAssistant()
            
            assistant = st.session_state.enhanced_assistant
            
            # Get conversational response with regulatory expertise
            response_data = assistant.get_conversational_response(user_question, portfolio_context)
            
            # Format response for display
            ai_response = _format_enhanced_response(response_data)
            
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


def _format_enhanced_response(response_data: Dict) -> str:
    """Format enhanced assistant response for display."""
    response_text = response_data.get('response_text', 'No response generated')
    
    # Add regulatory guidance if available
    if 'regulatory_guidance' in response_data and response_data['regulatory_guidance']:
        guidance = response_data['regulatory_guidance']
        response_text += f"\n\n**📋 Regulatory References:**\n" + "\n".join([f"• {g}" for g in guidance])
    
    # Add follow-up questions if available
    if 'follow_up_questions' in response_data and response_data['follow_up_questions']:
        questions = response_data['follow_up_questions']
        response_text += f"\n\n**❓ Follow-up Questions:**\n" + "\n".join([f"• {q}" for q in questions])
    
    # Add suggested actions if available
    if 'suggested_actions' in response_data and response_data['suggested_actions']:
        actions = response_data['suggested_actions']
        response_text += f"\n\n**🎯 Suggested Next Steps:**\n" + "\n".join([f"• {a}" for a in actions])
    
    return response_text


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
                    <strong>🤖 Enhanced SA-CCR Expert:</strong><br>
                    {chat['content']}
                    <br><small style="color: rgba(255,255,255,0.7);">{chat['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)


def _render_ead_estimator():
    """Render EAD estimation from natural language."""
    st.markdown("### 📈 EAD Estimation from Trade Description")
    st.markdown("Describe your trade in natural language and get an EAD estimate based on SA-CCR methodology.")
    
    # Trade description input
    trade_description = st.text_area(
        "Describe your derivative trade:",
        placeholder="e.g., 5-year USD interest rate swap, receive fixed 3.5%, pay SOFR, notional $50 million, counterparty is JPMorgan",
        height=100
    )
    
    # Counterparty information (optional)
    with st.expander("Optional: Counterparty Information"):
        col1, col2 = st.columns(2)
        with col1:
            cp_name = st.text_input("Counterparty Name", placeholder="e.g., JPMorgan Chase")
            cp_threshold = st.number_input("Threshold ($)", value=12000000, step=1000000)
        with col2:
            cp_type = st.selectbox("Counterparty Type", ["Corporate", "Bank", "Sovereign", "Non-Profit Org"])
            cp_mta = st.number_input("MTA ($)", value=1000000, step=100000)
    
    if st.button("🎯 Estimate EAD", type="primary"):
        if trade_description.strip():
            with st.spinner("🤖 Analyzing trade description and calculating EAD..."):
                try:
                    # Initialize enhanced assistant
                    if 'enhanced_assistant' not in st.session_state:
                        st.session_state.enhanced_assistant = EnhancedSACCRAssistant()
                    
                    assistant = st.session_state.enhanced_assistant
                    
                    # Prepare counterparty info
                    counterparty_info = {
                        'name': cp_name if cp_name else 'Estimated Counterparty',
                        'type': cp_type,
                        'threshold': cp_threshold,
                        'mta': cp_mta,
                        'nica': 0
                    }
                    
                    # Get EAD estimation
                    estimation_result = assistant.estimate_ead_from_description(trade_description, counterparty_info)
                    
                    # Display results
                    if 'error' not in estimation_result:
                        st.success("✅ EAD Estimation Complete!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("💰 EAD Estimate", f"${estimation_result['ead_estimate']:,.0f}")
                        with col2:
                            st.metric("🏛️ Capital Estimate", f"${estimation_result['capital_estimate']:,.0f}")
                        with col3:
                            st.metric("🎯 Confidence Level", estimation_result['confidence_level'])
                        
                        # Show assumptions
                        with st.expander("📋 Assumptions Made"):
                            for assumption in estimation_result['trade_assumptions']:
                                st.write(f"• {assumption}")
                        
                        # Show next steps
                        with st.expander("🔍 Refinement Steps"):
                            for step in estimation_result['next_steps']:
                                st.write(f"• {step}")
                    
                    else:
                        st.error(f"❌ {estimation_result['error']}")
                        st.info(estimation_result.get('recommendation', 'Please provide more specific details.'))
                
                except Exception as e:
                    st.error(f"Error during EAD estimation: {str(e)}")
        else:
            st.warning("Please describe your trade first.")


def _render_step_guide():
    """Render 24-step calculation guide."""
    st.markdown("### 📋 24-Step SA-CCR Calculation Guide")
    st.markdown("Get guided support through each step of the complete SA-CCR calculation process.")
    
    # Current step selection
    current_step = st.number_input("Current Step", min_value=1, max_value=24, value=1)
    
    # Show step information
    step_titles = {
        1: "Netting Set Data", 2: "Asset Class Classification", 3: "Hedging Set Determination",
        4: "Time Parameters (S, E, M)", 5: "Adjusted Notional", 6: "Maturity Factor",
        7: "Supervisory Delta", 8: "Supervisory Factor", 9: "Adjusted Derivatives Contract Amount",
        10: "Supervisory Correlation", 11: "Hedging Set Add-On", 12: "Asset Class Add-On",
        13: "Aggregate Add-On", 14: "V, C Calculation", 15: "PFE Multiplier",
        16: "PFE Calculation", 17: "CSA Parameters", 18: "Replacement Cost",
        19: "CEU Flag", 20: "Alpha Calculation", 21: "EAD Calculation",
        22: "Counterparty Information", 23: "Risk Weight Determination", 24: "RWA Calculation"
    }
    
    st.markdown(f"#### Step {current_step}: {step_titles.get(current_step, 'Unknown Step')}")
    
    # Progress bar
    progress = current_step / 24
    st.progress(progress)
    st.caption(f"Progress: {progress:.1%} complete")
    
    # Get guidance for current step
    if st.button("📖 Get Step Guidance", type="primary"):
        with st.spinner(f"🤖 Getting guidance for Step {current_step}..."):
            try:
                # Initialize enhanced assistant
                if 'enhanced_assistant' not in st.session_state:
                    st.session_state.enhanced_assistant = EnhancedSACCRAssistant()
                
                assistant = st.session_state.enhanced_assistant
                
                # Get step guidance
                user_input = {
                    'current_step': current_step,
                    'data': {}  # Could be populated from previous steps
                }
                
                guidance_result = assistant.guide_through_calculation(user_input)
                
                if 'error' not in guidance_result:
                    st.success(f"✅ Guidance for Step {current_step}")
                    
                    # Display guidance
                    st.markdown("**Step Explanation:**")
                    st.write(guidance_result['guidance'])
                    
                    # Show required inputs
                    if guidance_result.get('required_inputs'):
                        st.markdown("**Required Inputs:**")
                        for inp in guidance_result['required_inputs']:
                            st.write(f"• {inp}")
                    
                    # Show example values
                    if guidance_result.get('example_values'):
                        with st.expander("📋 Reference Example (Lowell Hotel Properties)"):
                            for key, value in guidance_result['example_values'].items():
                                st.write(f"**{key}**: {value}")
                
                else:
                    st.error(f"❌ {guidance_result['error']}")
            
            except Exception as e:
                st.error(f"Error getting step guidance: {str(e)}")
    
    # Quick navigation
    st.markdown("**Quick Navigation:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Previous Step") and current_step > 1:
            st.rerun()
    with col2:
        if st.button("🏠 Reset to Step 1"):
            st.rerun()
    with col3:
        if st.button("➡️ Next Step") and current_step < 24:
            st.rerun()
