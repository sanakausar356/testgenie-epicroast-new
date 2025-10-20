# Railway Deployment Guide

This guide will help you deploy your TestGenie & EpicRoast application to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Environment Variables**: Prepare your API keys and configuration

## Step 1: Verify Local Setup

Before deploying, run the verification script to ensure everything is working locally:

```bash
python verify_railway_deployment.py
```

This script will check:
- Python version compatibility
- Required dependencies
- Environment variables
- File structure
- Import functionality
- Flask app functionality

## Step 2: Environment Variables Setup

### Required Variables

Create a `.env` file in your project root with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Railway Configuration
PORT=5000
```

### Optional Variables

```env
# Jira Configuration (Optional)
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@domain.com
JIRA_API_TOKEN=your_jira_api_token_here

# Microsoft Teams Configuration (Optional)
TEAMS_WEBHOOK_URL=your_teams_webhook_url_here
```

## Step 3: Railway Deployment

### Method 1: Railway CLI (Recommended)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Railway project**:
   ```bash
   railway init
   ```

4. **Set environment variables**:
   ```bash
   railway variables set OPENAI_API_KEY=your_api_key_here
   railway variables set FLASK_ENV=production
   railway variables set FLASK_DEBUG=False
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

### Method 2: Railway Dashboard

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables**:
   - Go to your project dashboard
   - Click on "Variables" tab
   - Add all required environment variables

3. **Deploy**:
   - Railway will automatically deploy when you push to your main branch
   - Or click "Deploy" button in the dashboard

## Step 4: Verify Deployment

After deployment, check:

1. **Health Check Endpoint**: Visit `https://your-app.railway.app/health`
2. **API Health**: Visit `https://your-app.railway.app/api/health`
3. **Root Endpoint**: Visit `https://your-app.railway.app/`

Expected responses:
- `/health` and `/api/health` should return JSON with service status
- `/` should return API information

## Troubleshooting Common Issues

### Issue 1: Import Errors

**Symptoms**: Build fails with import errors
**Solution**: 
- Check that all dependencies are in `requirements.txt`
- Ensure `PYTHONPATH` is set correctly in `railway.toml`
- Verify import paths in your code

### Issue 2: Environment Variables Not Found

**Symptoms**: App starts but services fail to initialize
**Solution**:
- Check Railway dashboard for environment variables
- Ensure variable names match exactly (case-sensitive)
- Use `railway variables list` to verify

### Issue 3: Health Check Fails

**Symptoms**: Railway shows deployment failed due to health check timeout
**Solution**:
- Verify `/health` endpoint returns 200 status
- Check app logs in Railway dashboard
- Ensure app starts within 300 seconds (configured timeout)

### Issue 4: Port Issues

**Symptoms**: App doesn't start or connection refused
**Solution**:
- Ensure app binds to `0.0.0.0` (not `localhost`)
- Use `PORT` environment variable from Railway
- Check `main.py` port configuration

### Issue 5: Dependencies Missing

**Symptoms**: ModuleNotFoundError during startup
**Solution**:
- Update `requirements.txt` with all dependencies
- Check for version conflicts
- Ensure `backend/requirements.txt` exists

## Monitoring and Logs

### View Logs

```bash
railway logs
```

### Monitor in Dashboard

1. Go to your Railway project dashboard
2. Click on your service
3. View "Logs" tab for real-time logs

### Health Monitoring

Railway automatically monitors your app's health at `/health`. The endpoint should return:

```json
{
  "status": "healthy",
  "services": {
    "testgenie": true,
    "epicroast": true,
    "groomroom": true,
    "jira": false
  }
}
```

## Configuration Files

### railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[env]
PYTHONPATH = "."
```

### Procfile
```
web: python main.py
```

### requirements.txt
```
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
requests==2.31.0
openai==1.3.0
rich==13.7.0
prompt-toolkit==3.0.43
```

## Support

If you're still experiencing issues:

1. **Check Railway Status**: Visit [status.railway.app](https://status.railway.app)
2. **View Logs**: Use `railway logs` or dashboard logs
3. **Run Verification**: Use `python verify_railway_deployment.py`
4. **Railway Support**: Contact Railway support through their dashboard

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure CI/CD** for automatic deployments
3. **Set up monitoring** and alerts
4. **Scale resources** as needed 