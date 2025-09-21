#!/usr/bin/env python3
"""
Fallback agent for when the main agent fails to initialize
Provides basic functionality without requiring a knowledge base
"""

import os
from datetime import datetime
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
import config

class FallbackAgent:
    """Simple fallback agent that works without a knowledge base"""
    
    def __init__(self):
        self.initialized = False
        self.llm = None
        self._setup_llm()
    
    def _setup_llm(self):
        """Setup just the LLM without requiring a knowledge base"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.llm = Gemini(model=config.LLM_MODEL, api_key=api_key)
                Settings.llm = self.llm
                self.initialized = True
        except Exception as e:
            print(f"Failed to initialize fallback LLM: {e}")
    
    def chat(self, message: str) -> str:
        """Handle chat without knowledge base"""
        if not self.initialized:
            return "❌ The research agent is not fully initialized. Please check the system logs and ensure your GOOGLE_API_KEY is set correctly."
        
        try:
            if not self.llm:
                return "❌ Language model not available. Please check your GOOGLE_API_KEY configuration."
            
            # Simple response without knowledge base
            prompt = f"""You are a helpful research assistant. The user asked: "{message}"

Please provide a helpful response. Note that you don't have access to the local document collection at the moment, but you can still provide general information and guidance.

User question: {message}"""
            
            response = self.llm.complete(prompt)
            
            return f"""🤖 **Fallback Mode Response**

{response.text}

---
⚠️ **Note**: The system is running in fallback mode. For full research capabilities with document analysis, please ensure:
1. Your data files are uploaded and processed
2. The knowledge base is properly initialized
3. All dependencies are correctly installed

You can check system status at `/debug` endpoint."""
            
        except Exception as e:
            return f"❌ Error generating response: {str(e)}"

def create_fallback_session():
    """Create a basic research session for fallback mode"""
    return {
        'session_id': f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'created_at': datetime.now().isoformat(),
        'mode': 'fallback',
        'queries': [],
        'responses': [],
        'reasoning_steps': []
    }

class FallbackExporter:
    """Simple exporter for fallback mode"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_json(self, session):
        """Export session data to JSON"""
        import json
        filename = f"fallback_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(session, f, indent=2)
        
        return filepath