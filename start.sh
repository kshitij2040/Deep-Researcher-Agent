#!/bin/bash
# Startup script for Render deployment
# This script handles data ingestion and starts the web server

set -e  # Exit on any error

echo "🚀 Starting Deep Research Agent deployment..."

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ./storage
mkdir -p ./output/parsed_markdown
mkdir -p ./output/extracted_images
mkdir -p ./research_outputs

# Check if data directory exists and has files
if [ ! -d "./data" ] || [ -z "$(ls -A ./data)" ]; then
    echo "⚠️  Warning: No data files found in ./data directory"
    echo "The application will start but research capabilities may be limited"
else
    echo "📄 Data files found. Proceeding with ingestion..."
    
    # Run data ingestion if storage directory is empty or doesn't exist
    if [ ! -f "./storage/docstore.json" ]; then
        echo "🔄 Running data ingestion process..."
        python ingestion.py
        echo "✅ Data ingestion completed"
    else
        echo "✅ Existing knowledge base found, skipping ingestion"
    fi
fi

# Download required NLTK data
echo "📚 Downloading NLTK data..."
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️  NLTK download failed: {e}')
"

# Verify environment variables
echo "🔑 Checking environment variables..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set. Some features may not work."
else
    echo "✅ GOOGLE_API_KEY found"
fi

# Set default port if not specified
export PORT=${PORT:-10000}
echo "🌐 Starting web server on port $PORT..."

# Start the Flask application
exec python app.py