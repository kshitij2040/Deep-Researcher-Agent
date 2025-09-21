# /academic-rag-agent/main.py
import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import config

# Load environment variables FIRST
load_dotenv()

def initialize_settings():
    """Initialize Settings with Gemini LLM"""
    
    print("Initializing Deep Research Agent with Gemini...")
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    # Setup Gemini LLM
    try:
        llm = Gemini(model=config.LLM_MODEL, api_key=api_key)
        print(f"✅ Gemini LLM initialized: {config.LLM_MODEL}")
    except Exception as e:
        print(f"⚠️  Gemini not available: {e}")
        print("Please check your API key and internet connection")
        llm = None
    
    # Setup local embeddings
    embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    
    # Set global settings
    Settings.llm = llm
    Settings.embed_model = embed_model
    print("✅ Models initialized successfully")

def main():
    """Main function to run the Deep Research Agent."""
    
    # Initialize local settings
    try:
        initialize_settings()
    except Exception as e:
        print(f"Failed to initialize settings: {e}")
        return
    
    # Check if the knowledge base has been created by the ingestion script
    if not os.path.exists(config.STORAGE_DIR):
        print(
            f"Error: The storage directory '{config.STORAGE_DIR}' was not found.\n"
            "Please run the data ingestion process first by executing:\n"
            "python ingestion.py"
        )
        return
    
    # Import agent AFTER settings are initialized
    from agent import setup_agent, ResearchExporter, create_research_session
    
    try:
        print("Setting up the Deep Research Agent...")
        agent = setup_agent()
        
        # Initialize research session and exporter
        research_session = create_research_session()
        exporter = ResearchExporter(config.RESEARCH_OUTPUT_DIR)
       
        print("\n" + "="*60) 
        print("🔬 Deep Research Agent is ready!")
        print("Advanced features:")
        print("• Multi-step reasoning and query decomposition") 
        print("• Local document synthesis and analysis")
        print("• No external API dependencies")
        print("• Research export capabilities")
        print("\nCommands:")
        print("• Ask any research question")
        print("• Type 'export' to save current session")
        print("• Type 'refine [query]' for follow-up suggestions")
        print("• Type 'deep [query]' for comprehensive analysis")
        print("• Type 'quit' or 'exit' to stop")
        print("="*60 + "\n")
       
        while True:
            try:
                user_input = input("🔍 Research Query: ").strip()
               
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("📄 Exporting final research session...")
                    try:
                        export_path = exporter.export_to_json(research_session)
                        print(f"✅ Session exported to: {export_path}")
                    except Exception as e:
                        print(f"⚠️  Export failed: {e}")
                    print("Goodbye! Happy researching! 🔬")
                    break
               
                if not user_input:
                    print("Please enter a research question.")
                    continue
                
                # Handle special commands
                if user_input.lower().startswith('export'):
                    try:
                        export_path = exporter.export_to_json(research_session)
                        print(f"✅ Research session exported to: {export_path}")
                    except Exception as e:
                        print(f"❌ Export failed: {e}")
                    continue
                
                # Process the query
                print("\n🧠 Analyzing and researching...")
                start_time = datetime.now()
                
                try:
                    response = agent.chat(user_input)
                    
                    # Log the interaction
                    research_session['queries'].append(user_input)
                    research_session['responses'].append(str(response))
                    research_session['reasoning_steps'].append({
                        'timestamp': datetime.now().isoformat(),
                        'query': user_input,
                        'processing_time': str(datetime.now() - start_time)
                    })
                    
                    print(f"\n📋 Research Results:\n{response}")
                    
                    # Offer to export
                    export_choice = input("\n💾 Export this research? (y/n): ").strip().lower()
                    if export_choice in ['y', 'yes']:
                        try:
                            filename = f"research_{user_input[:30].replace(' ', '_')}.md"
                            export_path = exporter.export_to_markdown(str(response), filename)
                            print(f"✅ Research exported to: {export_path}")
                        except Exception as e:
                            print(f"⚠️  Export failed: {e}")
                    
                except Exception as e:
                    error_msg = f"Error processing research query: {e}"
                    print(f"❌ {error_msg}")
                    research_session['responses'].append(error_msg)
                    continue
                
                print("\n" + "-"*50 + "\n")
               
            except KeyboardInterrupt:
                print("\n\n📄 Exporting research session before exit...")
                try:
                    export_path = exporter.export_to_json(research_session)
                    print(f"✅ Session exported to: {export_path}")
                except:
                    pass
                print("Goodbye! 🔬")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
               
    except Exception as e:
        print(f"Failed to set up Deep Research Agent: {e}")
        print("Make sure you've run 'python ingestion.py' first to build the knowledge base.")

if __name__ == "__main__":
    from datetime import datetime
    main()