
import streamlit as st
from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class LLMClient:
    """Manages LLM connections and interactions."""
    
    def __init__(self):
        self.llm: Optional[ChatOpenAI] = None
        self.connection_status = "disconnected"
    
    def setup_connection(self, config: Dict) -> bool:
        """Setup LangChain ChatOpenAI connection."""
        try:
            self.llm = ChatOpenAI(
                base_url=config.get('base_url', "http://localhost:8123/v1"),
                api_key=config.get('api_key', "dummy"),
                model=config.get('model', "llama3"),
                temperature=config.get('temperature', 0.3),
                max_tokens=config.get('max_tokens', 4000),
                streaming=config.get('streaming', False)
            )
            
            # Test connection
            test_response = self.llm.invoke([
                SystemMessage(content="You are a Basel SA-CCR expert. Respond with 'Connected' if you receive this."),
                HumanMessage(content="Test")
            ])
            
            if test_response and test_response.content:
                self.connection_status = "connected"
                return True
            else:
                self.connection_status = "disconnected"
                return False
                
        except Exception as e:
            st.error(f"LLM Connection Error: {str(e)}")
            self.connection_status = "disconnected"
            return False
    
    def is_connected(self) -> bool:
        """Check if LLM is connected."""
        return self.connection_status == "connected" and self.llm is not None
    
    def invoke(self, messages: List) -> Optional[str]:
        """Invoke LLM with messages."""
        if not self.is_connected():
            return None
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            st.error(f"LLM invocation error: {str(e)}")
            return None
