# Deployment Guide for Render

This guide will help you deploy your Deep Research Agent to Render.

## Prerequisites

1. A Render account (free tier available)
2. Your project code pushed to a Git repository (GitHub, GitLab, etc.)
3. A Google Cloud API key for Gemini access

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository contains all the files created for deployment:
- `render.yaml` - Render configuration
- `app.py` - Web interface
- `start.sh` - Startup script
- `requirements.txt` - Updated dependencies
- `.env.example` - Environment variable template

### 2. Deploy to Render

1. **Create a New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Choose the repository containing your Deep Research Agent

2. **Configure the Service**
   - **Name**: `deep-research-agent` (or your preferred name)
   - **Environment**: `Python`
   - **Region**: Choose your preferred region
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty if code is in root, or specify subfolder
   - **Runtime**: `Python 3`

3. **Build and Start Commands**
   Since we have `render.yaml`, these should be automatically configured:
   - **Build Command**: 
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && python -c "import nltk; nltk.download('punkt')" && python -c "import nltk; nltk.download('stopwords')" && python ingestion.py
     ```
   - **Start Command**: `python app.py`

4. **Environment Variables**
   Add these environment variables in the Render dashboard:
   - `GOOGLE_API_KEY`: Your Google Cloud API key
   - `PORT`: 10000 (automatically set by Render)
   - `PYTHONUNBUFFERED`: 1
   - `RENDER_ENV`: production

### 3. Configure Persistent Storage (Optional)

If you want to persist your knowledge base between deployments:

1. In your service settings, go to "Disks"
2. Add a disk:
   - **Name**: `research-data`
   - **Mount Path**: `/opt/render/project/src/storage`
   - **Size**: 1GB (adjust based on your data size)

### 4. Set Up Your Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gemini API
4. Create an API key
5. Add the API key to your Render environment variables

### 5. Upload Your Data

Since Render doesn't have direct file upload, you have a few options:

**Option A: Include data in your repository**
- Add your PDF files to the `data/` directory
- Commit and push to your repository
- The build process will automatically process them

**Option B: Download data during build**
- Modify the build command to download your data files
- Use `wget` or `curl` to fetch files from a public URL

**Option C: Use external storage**
- Store your PDFs in cloud storage (Google Drive, Dropbox, etc.)
- Modify `ingestion.py` to download files during startup

### 6. Deploy and Test

1. Click "Create Web Service"
2. Wait for the build to complete (this may take 10-15 minutes)
3. Once deployed, you'll get a URL like `https://your-app-name.onrender.com`
4. Test the health endpoint: `https://your-app-name.onrender.com/health`
5. Access the web interface at your app URL

## Troubleshooting

### Common Issues

1. **Build Timeout**
   - The initial build may be slow due to ML model downloads
   - Consider upgrading to a paid plan for faster builds

2. **Memory Issues**
   - Free tier has limited memory (512MB)
   - Consider upgrading to Standard plan (2GB) for better performance

3. **API Key Issues**
   - Verify your Google API key is correctly set
   - Check that the Gemini API is enabled in Google Cloud Console

4. **Data Processing Issues**
   - Ensure your PDF files are in the correct format
   - Check logs for ingestion errors

### Monitoring

- Check service logs in the Render dashboard
- Monitor the `/health` endpoint for service status
- Use the `/status` endpoint to check agent initialization

### Performance Optimization

1. **Upgrade to Standard Plan**
   - More memory and CPU for better performance
   - Faster builds and deployments

2. **Optimize Dependencies**
   - Remove unused packages from `requirements.txt`
   - Use lighter alternatives where possible

3. **Caching**
   - Enable persistent disk for knowledge base
   - Cache processed documents to avoid reprocessing

## Local Testing

Before deploying, test locally:

1. Copy `.env.example` to `.env`
2. Fill in your `GOOGLE_API_KEY`
3. Run: `python app.py`
4. Test at `http://localhost:5000`

## Cost Estimation

- **Free Tier**: 750 hours/month, 512MB RAM (suitable for testing)
- **Starter Plan**: $7/month, 1GB RAM (recommended for production)
- **Standard Plan**: $25/month, 2GB RAM (optimal performance)

## Support

If you encounter issues:
1. Check the Render logs for error messages
2. Verify all environment variables are set correctly
3. Test your application locally first
4. Check the [Render documentation](https://render.com/docs) for platform-specific issues