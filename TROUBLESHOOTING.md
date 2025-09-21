# 🚨 Troubleshooting: "Agent not initialized" Error

## Common Causes and Solutions

### 1. **Missing Google API Key** ⚠️
**Error**: `GOOGLE_API_KEY not found in environment variables`

**Solution**:
1. Go to your Render dashboard
2. Navigate to your service → Environment
3. Add environment variable:
   - **Key**: `GOOGLE_API_KEY`
   - **Value**: Your Google Cloud API key
4. Redeploy the service

### 2. **No Knowledge Base** 📚
**Error**: `Knowledge base not found`

**Cause**: No PDF files were processed during deployment

**Solutions**:
- **Option A**: Add PDF files to your `data/` folder and redeploy
- **Option B**: Use fallback mode (basic functionality without document search)

### 3. **Build/Ingestion Failed** 🔧
**Error**: Data ingestion failed during build

**Check**:
1. Go to Render dashboard → Build Logs
2. Look for errors in the ingestion step
3. Common issues:
   - Large PDF files (>100MB)
   - Corrupted PDF files
   - Memory limits exceeded

### 4. **Dependency Issues** 📦
**Error**: Import errors or missing packages

**Solution**:
1. Check build logs for package installation errors
2. Consider upgrading to Standard plan for more build resources
3. Use `requirements-minimal.txt` for lighter deployment

## Diagnostic Steps

### Step 1: Check System Status
Visit: `https://your-app-name.onrender.com/debug`

This shows:
- Environment variables status
- File system status
- Agent initialization status

### Step 2: Check Health Endpoint
Visit: `https://your-app-name.onrender.com/health`

Response meanings:
- **200 + "healthy"**: Everything working
- **503 + "initializing"**: Agent failed to start

### Step 3: Check Logs
1. Go to Render dashboard
2. Click your service
3. Check "Logs" tab for error messages

## Fallback Mode

If the main agent fails, the system automatically switches to **fallback mode**:

✅ **Available**:
- Basic LLM chat functionality
- General research assistance
- Export capabilities

❌ **Not Available**:
- Document search
- Local knowledge base queries
- Advanced research tools

## Quick Fixes

### Fix 1: Environment Variables
```bash
# In Render dashboard, add:
GOOGLE_API_KEY=your_api_key_here
PYTHONUNBUFFERED=1
RENDER_ENV=production
```

### Fix 2: Data Upload
1. Add PDF files to `/data` folder in your repository
2. Commit and push changes
3. Redeploy on Render

### Fix 3: Minimal Deployment
If build keeps failing:
1. Replace `requirements.txt` with `requirements-minimal.txt`
2. Commit and redeploy

### Fix 4: Upgrade Plan
- Free tier: 512MB RAM (limited)
- Starter: $7/month, 1GB RAM (recommended)
- Standard: $25/month, 2GB RAM (optimal)

## Getting Help

1. **Check the logs first** - most issues are visible there
2. **Use the debug endpoint** - `/debug` shows system status
3. **Try fallback mode** - basic functionality should still work
4. **Verify API key** - most common issue

## Emergency Fallback

If nothing works, create a minimal `app.py`:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Emergency fallback - check logs for details"

@app.route('/health')
def health():
    return jsonify({'status': 'emergency_mode'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

This will at least get your service running so you can diagnose the issues.