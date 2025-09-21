#!/usr/bin/env python3
"""
Test script to debug the agent setup issue
"""

import os
from dotenv import load_dotenv
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import config

# Load environment variables
load_dotenv()

def test_simple_tool():
    """Simple test function"""
    return "Test tool works!"

def main():
    print("Testing agent setup...")
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found")
        return
    
    print("✅ API key found")
    
    # Setup LLM
    try:
        llm = Gemini(model=config.LLM_MODEL, api_key=api_key)
        Settings.llm = llm
        print("✅ Gemini LLM initialized")
    except Exception as e:
        print(f"❌ LLM setup failed: {e}")
        return
    
    # Setup embedding model
    try:
        embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
        Settings.embed_model = embed_model
        print("✅ Embeddings initialized")
    except Exception as e:
        print(f"❌ Embeddings setup failed: {e}")
        return
    
    # Create simple tool
    try:
        simple_tool = FunctionTool.from_defaults(
            fn=test_simple_tool,
            name="test_tool",
            description="A simple test tool"
        )
        print("✅ Tool created successfully")
    except Exception as e:
        print(f"❌ Tool creation failed: {e}")
        return
    
    # Try to create agent
    try:
        agent = ReActAgent.from_tools(
            tools=[simple_tool],
            llm=Settings.llm,
            verbose=True
        )
        print("✅ Agent created successfully!")
        
        # Test the agent
        response = agent.chat("Hello, can you run the test tool?")
        print(f"Agent response: {response}")
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()