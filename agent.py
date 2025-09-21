# /academic-rag-agent/agent.py
import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.agent import ReActAgent
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Local Imports
from retrieval import setup_query_engine
import config

# Load environment variables
load_dotenv()

class QueryDecomposer:
    """Handles breaking down complex queries into smaller, manageable sub-tasks."""
    
    def __init__(self):
        self.reasoning_steps = []
    
    def decompose_query(self, query: str) -> List[Dict[str, str]]:
        """
        Decomposes a complex query into sub-queries based on patterns and keywords.
        Returns a list of sub-tasks with their reasoning.
        """
        self.reasoning_steps = []
        subtasks = []
        
        # Clear previous steps
        self.reasoning_steps.append(f"Original query: {query}")
        
        # Pattern-based decomposition
        if any(keyword in query.lower() for keyword in ['compare', 'versus', 'vs', 'difference']):
            # Comparison query
            self.reasoning_steps.append("Detected comparison query - need to analyze multiple concepts")
            concepts = self._extract_comparison_concepts(query)
            for concept in concepts:
                subtasks.append({
                    "type": "concept_analysis",
                    "query": f"What are the key characteristics and properties of {concept}?",
                    "reasoning": f"Need to understand {concept} for comparison"
                })
            
        elif any(keyword in query.lower() for keyword in ['steps', 'process', 'how to', 'methodology']):
            # Process query
            self.reasoning_steps.append("Detected process/methodology query - need step-by-step breakdown")
            subtasks.append({
                "type": "process_analysis",
                "query": f"What are the detailed steps or methodology for: {query}",
                "reasoning": "Breaking down the process into sequential steps"
            })
            
        elif any(keyword in query.lower() for keyword in ['advantages', 'benefits', 'disadvantages', 'limitations']):
            # Pros/cons analysis
            self.reasoning_steps.append("Detected pros/cons analysis query")
            main_topic = self._extract_main_topic(query)
            subtasks.extend([
                {
                    "type": "advantages_analysis", 
                    "query": f"What are the advantages and benefits of {main_topic}?",
                    "reasoning": "Analyzing positive aspects"
                },
                {
                    "type": "limitations_analysis",
                    "query": f"What are the limitations and challenges of {main_topic}?", 
                    "reasoning": "Analyzing negative aspects or challenges"
                }
            ])
            
        elif any(keyword in query.lower() for keyword in ['applications', 'use cases', 'examples']):
            # Applications query
            self.reasoning_steps.append("Detected applications/use cases query")
            main_topic = self._extract_main_topic(query)
            subtasks.extend([
                {
                    "type": "theoretical_analysis",
                    "query": f"What is the theoretical foundation of {main_topic}?",
                    "reasoning": "Understanding the theoretical background"
                },
                {
                    "type": "practical_applications",
                    "query": f"What are real-world applications and use cases of {main_topic}?",
                    "reasoning": "Finding practical implementations"
                }
            ])
        else:
            # General query - break into background and specific aspects
            self.reasoning_steps.append("General query - breaking into background and specific analysis")
            main_topic = self._extract_main_topic(query)
            subtasks.extend([
                {
                    "type": "background_research",
                    "query": f"What is the background and fundamental concepts of {main_topic}?",
                    "reasoning": "Establishing foundational understanding"
                },
                {
                    "type": "detailed_analysis", 
                    "query": query,
                    "reasoning": "Detailed analysis based on original query"
                }
            ])
        
        self.reasoning_steps.append(f"Generated {len(subtasks)} sub-tasks for systematic analysis")
        return subtasks
    
    def _extract_comparison_concepts(self, query: str) -> List[str]:
        """Extract concepts being compared from the query."""
        # Simple extraction - can be enhanced with NLP
        words = query.split()
        concepts = []
        
        # Look for patterns like "A vs B", "A and B", etc.
        for i, word in enumerate(words):
            if word.lower() in ['vs', 'versus', 'and', 'compared']:
                if i > 0: concepts.append(words[i-1])
                if i < len(words)-1: concepts.append(words[i+1])
        
        # Remove duplicates and clean
        concepts = list(set([c.strip('.,?!').lower() for c in concepts if len(c) > 2]))
        return concepts if concepts else [query]  # fallback to full query
    
    def _extract_main_topic(self, query: str) -> str:
        """Extract the main topic from a query."""
        # Remove question words and common phrases
        stop_patterns = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'the', 'of']
        words = [w for w in query.lower().split() if w not in stop_patterns and len(w) > 2]
        
        # Take first few meaningful words
        return ' '.join(words[:3]) if words else query

def document_synthesis_search(query: str, query_engine) -> str:
    """
    Enhanced local document search that synthesizes information from multiple sources.
    """
    try:
        # Get initial results
        response = query_engine.query(query)
        
        # Extract source information and synthesize
        synthesis = f"Research Synthesis for: {query}\n\n"
        synthesis += f"Primary Analysis:\n{response.response}\n\n"
        
        # Get source documents for additional context
        if hasattr(response, 'source_nodes') and response.source_nodes:
            synthesis += "Sources Analyzed:\n"
            for i, node in enumerate(response.source_nodes[:3], 1):
                metadata = node.metadata if hasattr(node, 'metadata') else {}
                source = metadata.get('file_name', f'Document {i}')
                synthesis += f"{i}. {source}\n"
            synthesis += "\n"
        
        # Add reasoning about information quality
        synthesis += "Information Assessment:\n"
        synthesis += f"- Found {len(response.source_nodes) if hasattr(response, 'source_nodes') else 0} relevant sources\n"
        synthesis += "- Synthesized information from local document collection\n"
        synthesis += "- Analysis based on semantic similarity and keyword matching\n"
        
        return synthesis
        
    except Exception as e:
        return f"Error in document synthesis search: {str(e)}"

def deep_research_analysis(query: str, query_engine) -> str:
    """
    Performs deep research analysis by decomposing queries and synthesizing results.
    """
    decomposer = QueryDecomposer()
    subtasks = decomposer.decompose_query(query)
    
    research_report = f"Deep Research Analysis: {query}\n"
    research_report += "="*50 + "\n\n"
    
    # Add reasoning steps
    research_report += "Research Strategy:\n"
    for i, step in enumerate(decomposer.reasoning_steps, 1):
        research_report += f"{i}. {step}\n"
    research_report += "\n"
    
    # Process each subtask
    research_report += "Detailed Analysis:\n\n"
    for i, subtask in enumerate(subtasks, 1):
        research_report += f"Sub-Analysis {i}: {subtask['type'].replace('_', ' ').title()}\n"
        research_report += f"Reasoning: {subtask['reasoning']}\n"
        research_report += f"Query: {subtask['query']}\n\n"
        
        # Get results for this subtask
        try:
            result = query_engine.query(subtask['query'])
            research_report += f"Findings:\n{result.response}\n\n"
        except Exception as e:
            research_report += f"Error processing sub-task: {str(e)}\n\n"
        
        research_report += "-" * 30 + "\n\n"
    
    # Add synthesis conclusion
    research_report += "Research Synthesis:\n"
    research_report += f"Completed comprehensive analysis of '{query}' through {len(subtasks)} sub-analyses. "
    research_report += "This systematic approach ensures thorough coverage of the topic from multiple angles.\n"
    
    return research_report

def setup_agent():
    """
    Sets up a ReAct Agent with Gemini LLM and enhanced research capabilities.
    """
    
    # Verify API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    # Configure Settings with Gemini
    if not hasattr(Settings, 'llm') or Settings.llm is None:
        try:
            Settings.llm = Gemini(model=config.LLM_MODEL, api_key=api_key)
            print("✅ Using Gemini LLM")
        except Exception as e:
            print(f"⚠️  Gemini not available: {e}")
            print("Please check your API key and internet connection")
            Settings.llm = None
    
    if not hasattr(Settings, 'embed_model') or Settings.embed_model is None:
        Settings.embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
        print("✅ Using local HuggingFace embeddings")
    
    print("Setting up local query engine...")
    try:
        query_engine = setup_query_engine()
    except Exception as e:
        print(f"⚠️  Query engine setup failed: {e}")
        print("Please ensure you have run 'python ingestion.py' first.")
        raise
    
    # Create enhanced tools for deep research
    document_synthesis_tool = FunctionTool.from_defaults(
        fn=lambda query: document_synthesis_search(query, query_engine),
        name="document_synthesizer",
        description="Synthesizes information from multiple local documents with detailed source analysis. Use for comprehensive research on topics covered in your local collection."
    )
   
    deep_research_tool = FunctionTool.from_defaults(
        fn=lambda query: deep_research_analysis(query, query_engine),
        name="deep_researcher", 
        description="Performs deep research analysis by breaking down complex queries into sub-tasks and providing systematic analysis. Use for complex research questions that need multi-step reasoning."
    )
    
    # Create query refinement tool
    def query_refinement_suggestions(original_query: str) -> str:
        """Suggests follow-up questions and refinements for deeper exploration."""
        suggestions = f"Follow-up Research Suggestions for: '{original_query}'\n\n"
        
        # Generate refinement suggestions based on query analysis
        decomposer = QueryDecomposer()
        subtasks = decomposer.decompose_query(original_query)
        
        suggestions += "Suggested deeper exploration paths:\n"
        for i, subtask in enumerate(subtasks, 1):
            suggestions += f"{i}. {subtask['query']}\n"
        
        # Add general refinement suggestions
        suggestions += "\nGeneral refinement directions:\n"
        suggestions += f"• What are the practical applications of concepts in '{original_query}'?\n"
        suggestions += f"• What are the limitations or challenges related to '{original_query}'?\n"
        suggestions += f"• How has '{original_query}' evolved over time?\n"
        suggestions += f"• What are alternative approaches to '{original_query}'?\n"
        
        return suggestions
    
    query_refinement_tool = FunctionTool.from_defaults(
        fn=query_refinement_suggestions,
        name="query_refiner",
        description="Suggests follow-up questions and refinements to help users dig deeper into research topics. Use when users want to explore a topic more thoroughly."
    )
   
    # Create the agent with enhanced tools
    tools = [document_synthesis_tool, deep_research_tool, query_refinement_tool]
    
    if Settings.llm is not None:
        agent = ReActAgent.from_tools(
            tools=tools,
            llm=Settings.llm,
            verbose=True
        )
        print("✅ ReAct agent with local LLM is ready for deep research.")
    else:
        # Simple fallback agent implementation
        class SimpleResearchAgent:
            def __init__(self, tools):
                self.tools = {tool.metadata.name: tool for tool in tools}
                
            def chat(self, message: str) -> str:
                """Simple chat implementation using tools directly."""
                try:
                    # Route to appropriate tool based on message content
                    if any(word in message.lower() for word in ['deep', 'complex', 'analyze', 'breakdown']):
                        return self.tools['deep_researcher'].fn(message)
                    elif any(word in message.lower() for word in ['follow', 'refine', 'explore', 'suggestions']):
                        return self.tools['query_refiner'].fn(message)
                    else:
                        return self.tools['document_synthesizer'].fn(message)
                except Exception as e:
                    return f"Error processing query: {str(e)}"
        
        agent = SimpleResearchAgent(tools)
        print("✅ Simple research agent ready (no LLM required).")
   
    return agent

class ResearchExporter:
    """Handles exporting research results in various formats."""
    
    def __init__(self, output_dir: str = "./research_outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_markdown(self, research_content: str, filename: str = None) -> str:
        """Export research results to Markdown format."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Format content for markdown
        formatted_content = f"# Research Report\n\n"
        formatted_content += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        formatted_content += research_content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        return filepath
    
    def export_to_json(self, research_data: Dict[str, Any], filename: str = None) -> str:
        """Export structured research data to JSON format."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_data_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Add metadata
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "export_format": "json",
                "agent_version": "deep_researcher_v1.0"
            },
            "research_data": research_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath

def create_research_session() -> Dict[str, Any]:
    """Creates a research session with conversation history and export capabilities."""
    return {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "start_time": datetime.now().isoformat(),
        "queries": [],
        "responses": [],
        "reasoning_steps": [],
        "export_history": []
    }