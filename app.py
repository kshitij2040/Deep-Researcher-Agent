#!/usr/bin/env python3
"""
Flask web interface for the Deep Research Agent
Converts the CLI application to a web API for Render deployment
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for agent and session
agent = None
research_session = None
exporter = None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Research Agent</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .input-section { margin-bottom: 30px; }
        textarea { width: 100%; height: 120px; padding: 15px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 10px 5px; }
        button:hover { background: #2980b9; }
        button:disabled { background: #bdc3c7; cursor: not-allowed; }
        .response-section { margin-top: 30px; }
        .response { background: #ecf0f1; padding: 20px; border-radius: 5px; border-left: 4px solid #3498db; white-space: pre-wrap; }
        .error { border-left: 4px solid #e74c3c; background: #fdf2f2; }
        .loading { text-align: center; color: #3498db; font-style: italic; }
        .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .features { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .features h3 { margin-top: 0; color: #495057; }
        .features ul { margin: 0; padding-left: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Deep Research Agent</h1>
        
        <div class="features">
            <h3>Advanced Research Features:</h3>
            <ul>
                <li>Multi-step reasoning and query decomposition</li>
                <li>Local document synthesis and analysis</li>
                <li>Research export capabilities</li>
                <li>No external API dependencies for core functionality</li>
            </ul>
        </div>

        <div id="status"></div>

        <div class="input-section">
            <textarea id="query" placeholder="Enter your research question here..."></textarea>
            <br>
            <button onclick="submitQuery()" id="submitBtn">🔍 Research</button>
            <button onclick="exportSession()" id="exportBtn">💾 Export Session</button>
            <button onclick="clearResponse()" id="clearBtn">🗑️ Clear</button>
        </div>

        <div class="response-section">
            <div id="response"></div>
        </div>
    </div>

    <script>
        let isProcessing = false;

        function showStatus(message, type = 'success') {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => statusDiv.innerHTML = '', 5000);
        }

        function setLoading(loading) {
            isProcessing = loading;
            const submitBtn = document.getElementById('submitBtn');
            const responseDiv = document.getElementById('response');
            
            submitBtn.disabled = loading;
            submitBtn.textContent = loading ? '🔄 Processing...' : '🔍 Research';
            
            if (loading) {
                responseDiv.innerHTML = '<div class="loading">🧠 Analyzing and researching...</div>';
            }
        }

        async function submitQuery() {
            const query = document.getElementById('query').value.trim();
            if (!query) {
                showStatus('Please enter a research question.', 'error');
                return;
            }

            if (isProcessing) return;

            setLoading(true);
            
            try {
                const response = await fetch('/research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                const data = await response.json();
                const responseDiv = document.getElementById('response');

                if (response.ok) {
                    responseDiv.innerHTML = `<div class="response">${data.response}</div>`;
                    showStatus('Research completed successfully!');
                } else {
                    responseDiv.innerHTML = `<div class="response error">Error: ${data.error}</div>`;
                    showStatus('Research failed. Please try again.', 'error');
                }
            } catch (error) {
                document.getElementById('response').innerHTML = `<div class="response error">Network error: ${error.message}</div>`;
                showStatus('Network error occurred.', 'error');
            } finally {
                setLoading(false);
            }
        }

        async function exportSession() {
            try {
                const response = await fetch('/export', { method: 'POST' });
                const data = await response.json();
                
                if (response.ok) {
                    showStatus(`Session exported to: ${data.filename}`);
                } else {
                    showStatus(`Export failed: ${data.error}`, 'error');
                }
            } catch (error) {
                showStatus('Export failed due to network error.', 'error');
            }
        }

        function clearResponse() {
            document.getElementById('response').innerHTML = '';
            document.getElementById('query').value = '';
        }

        // Allow Enter key submission
        document.getElementById('query').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                submitQuery();
            }
        });
    </script>
</body>
</html>
"""

def initialize_agent():
    """Initialize the research agent and related components"""
    global agent, research_session, exporter
    
    try:
        # Import and initialize settings
        from main import initialize_settings
        initialize_settings()
        
        # Import agent components
        from agent import setup_agent, ResearchExporter, create_research_session
        import config
        
        # Setup agent and session
        agent = setup_agent()
        research_session = create_research_session()
        exporter = ResearchExporter(config.RESEARCH_OUTPUT_DIR)
        
        logger.info("✅ Deep Research Agent initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return False

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    if agent is None:
        return jsonify({'status': 'initializing', 'message': 'Agent is starting up'}), 503
    return jsonify({'status': 'healthy', 'message': 'Deep Research Agent is running'})

@app.route('/research', methods=['POST'])
def research():
    """Process research queries"""
    global agent, research_session
    
    if agent is None:
        return jsonify({'error': 'Agent not initialized. Please wait for startup to complete.'}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Process the query
        logger.info(f"Processing query: {query[:100]}...")
        start_time = datetime.now()
        
        response = agent.chat(query)
        
        # Log the interaction
        if research_session:
            research_session['queries'].append(query)
            research_session['responses'].append(str(response))
            research_session['reasoning_steps'].append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'processing_time': str(datetime.now() - start_time)
            })
        
        return jsonify({
            'response': str(response),
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': f'Error processing research query: {str(e)}'}), 500

@app.route('/export', methods=['POST'])
def export_session():
    """Export current research session"""
    global exporter, research_session
    
    if not exporter or not research_session:
        return jsonify({'error': 'Export functionality not available'}), 503
    
    try:
        export_path = exporter.export_to_json(research_session)
        filename = os.path.basename(export_path)
        
        return jsonify({
            'message': 'Session exported successfully',
            'filename': filename,
            'path': export_path
        })
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/status')
def status():
    """Get current application status"""
    return jsonify({
        'agent_ready': agent is not None,
        'session_active': research_session is not None,
        'exporter_ready': exporter is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Initialize the agent on startup
    logger.info("Starting Deep Research Agent web interface...")
    
    # Check if storage directory exists
    if not os.path.exists('./storage'):
        logger.warning("Storage directory not found. Make sure to run data ingestion first.")
    
    # Initialize agent
    init_success = initialize_agent()
    if not init_success:
        logger.warning("Agent initialization failed. Some features may not be available.")
    
    # Get port from environment (Render sets PORT environment variable)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('RENDER_ENV') != 'production')