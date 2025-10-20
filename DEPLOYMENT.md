# TestGenie Deployment Guide

This guide covers deploying TestGenie to Vercel (frontend) and Railway (backend).

## Prerequisites

- Node.js (v18 or higher)
- npm (v8 or higher)
- Python (v3.11 or higher)
- Git

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

Run the complete deployment script:

```bash
python deploy_all.py
```

This script will:
1. Check prerequisites
2. Install CLI tools (Vercel & Railway)
3. Deploy backend to Railway
4. Deploy frontend to Vercel
5. Provide next steps

### Option 2: Manual Deployment

#### Backend Deployment (Railway)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Deploy backend:**
   ```bash
   python deploy_backend.py
   ```

   Or manually:
   ```bash
   cd backend
   railway up --detach
   ```

#### Frontend Deployment (Vercel)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy frontend:**
   ```bash
   python deploy_vercel.py
   ```

   Or manually:
   ```bash
   cd frontend
   npm install
   npm run build
   vercel --prod --yes
   ```

## Configuration

### Environment Variables

Set these environment variables in your Railway dashboard:

#### Required for Azure OpenAI:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Your Azure OpenAI deployment name

#### Required for Jira Integration:
- `JIRA_SERVER_URL` - Your Jira server URL
- `JIRA_EMAIL` - Your Jira email
- `JIRA_API_TOKEN` - Your Jira API token

### API URL Configuration

After deployment, update the API URL in `frontend/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-railway-app.up.railway.app/api/$1"
    }
  ]
}
```

Replace `your-railway-app.up.railway.app` with your actual Railway deployment URL.

## Deployment Files

### Backend Files
- `backend/requirements.txt` - Python dependencies
- `backend/Procfile` - Railway process configuration
- `backend/runtime.txt` - Python version specification
- `backend/railway.toml` - Railway deployment configuration

### Frontend Files
- `frontend/vercel.json` - Vercel deployment configuration
- `frontend/package.json` - Node.js dependencies and scripts

## Troubleshooting

### Common Issues

1. **CLI Tools Not Found**
   - Ensure Node.js and npm are installed
   - Run: `npm install -g vercel @railway/cli`

2. **Build Failures**
   - Check Node.js version: `node --version`
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

3. **Environment Variables**
   - Verify all required environment variables are set in Railway dashboard
   - Check variable names match exactly (case-sensitive)

4. **API Connection Issues**
   - Verify Railway deployment URL is correct in `vercel.json`
   - Check Railway service is running: `railway status`
   - Test API endpoint: `curl https://your-railway-app.up.railway.app/health`

### Health Checks

Test your deployment:

```bash
# Backend health check
curl https://your-railway-app.up.railway.app/health

# Frontend (should redirect to Railway API)
curl https://your-vercel-app.vercel.app/api/health
```

## Manual Deployment Steps

If automated deployment fails, follow these manual steps:

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
railway login
railway up --detach
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run build
vercel login
vercel --prod --yes
```

### 3. Update Configuration

1. Get Railway URL: `railway status`
2. Update `frontend/vercel.json` with Railway URL
3. Set environment variables in Railway dashboard

## Support

For deployment issues:
1. Check Railway logs: `railway logs`
2. Check Vercel logs in dashboard
3. Verify environment variables
4. Test API endpoints manually

## Security Notes

- Never commit API keys or sensitive environment variables
- Use Railway's environment variable system
- Enable HTTPS for all deployments
- Regularly rotate API keys and tokens
