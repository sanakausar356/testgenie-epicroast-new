# 🚀 Deployment Guide - Enhanced GroomRoom

## Overview
This guide will help you deploy the enhanced GroomRoom application to both Vercel (frontend) and Railway (backend).

## Prerequisites
- Node.js 18+ installed
- Python 3.8+ installed
- Git repository with all changes committed
- Vercel account (free)
- Railway account (free)

## 🎯 Deployment Steps

### 1. **Deploy Backend to Railway**

#### Option A: Using Railway CLI (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to existing project or create new one
railway link

# Deploy
railway up
```

#### Option B: Using Python Script
```bash
python deploy_to_railway.py
```

#### Option C: Manual Railway Deployment
1. Go to [Railway.app](https://railway.app)
2. Create new project
3. Connect your GitHub repository
4. Railway will automatically detect the Python app and deploy

### 2. **Deploy Frontend to Vercel**

#### Option A: Using Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build the project
npm run build

# Deploy to Vercel
vercel --prod
```

#### Option B: Using Python Script
```bash
python deploy_to_vercel.py
```

#### Option C: Manual Vercel Deployment
1. Go to [Vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set build settings:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
4. Deploy

### 3. **Update API Endpoint**

After Railway deployment, update the frontend API endpoint:

1. Get your Railway backend URL (e.g., `https://your-app.up.railway.app`)
2. Update `frontend/vercel.json`:
```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-app.up.railway.app/api/$1"
    }
  ]
}
```
3. Redeploy frontend to Vercel

## 🔧 Environment Variables

### Railway Backend Environment Variables
Set these in your Railway project dashboard:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@domain.com
JIRA_API_TOKEN=your-api-token

# Python Configuration
PYTHONPATH=.
PORT=8080
```

### Vercel Frontend Environment Variables
No additional environment variables needed for frontend.

## 🧪 Testing Deployment

### 1. **Test Backend (Railway)**
```bash
# Health check
curl https://your-app.up.railway.app/health

# API health check
curl https://your-app.up.railway.app/api/health

# Test GroomRoom endpoint
curl -X POST https://your-app.up.railway.app/api/groomroom/generate \
  -H "Content-Type: application/json" \
  -d '{"ticket_content": "Test ticket content"}'
```

### 2. **Test Frontend (Vercel)**
1. Visit your Vercel URL
2. Test the GroomRoom panel
3. Verify API calls are working

## 🎯 Expected Results

### Backend (Railway)
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ API health shows all services status
- ✅ GroomRoom analysis returns structured JSON
- ✅ Jira field mapping works automatically
- ✅ Enhanced analysis with DOR, AC review, test scenarios

### Frontend (Vercel)
- ✅ React app loads successfully
- ✅ GroomRoom panel displays
- ✅ API calls to Railway backend work
- ✅ Analysis results display properly

## 🚨 Troubleshooting

### Common Issues

#### Railway Deployment Issues
```bash
# Check Railway logs
railway logs

# Check Railway status
railway status

# Redeploy
railway up
```

#### Vercel Deployment Issues
```bash
# Check Vercel logs
vercel logs

# Check build locally
cd frontend
npm run build

# Redeploy
vercel --prod
```

#### API Connection Issues
1. Verify Railway backend URL is correct in `vercel.json`
2. Check CORS settings in backend
3. Verify environment variables are set
4. Check Railway logs for errors

### Environment Variable Issues
- Ensure all required environment variables are set in Railway
- Check that Jira credentials are valid
- Verify Azure OpenAI configuration

## 📊 Deployment Checklist

### Backend (Railway)
- [ ] Railway CLI installed and logged in
- [ ] Environment variables configured
- [ ] Deployment successful
- [ ] Health endpoint responding
- [ ] GroomRoom API working
- [ ] Jira field mapping functional

### Frontend (Vercel)
- [ ] Vercel CLI installed and logged in
- [ ] Dependencies installed
- [ ] Build successful
- [ ] Deployment successful
- [ ] API endpoint updated
- [ ] Frontend connecting to backend

## 🎉 Success!

Once both deployments are complete:

1. **Backend URL**: `https://your-app.up.railway.app`
2. **Frontend URL**: `https://your-app.vercel.app`
3. **Enhanced GroomRoom**: Fully functional with automatic Jira field detection
4. **API Integration**: Frontend successfully calling Railway backend

Your enhanced GroomRoom application is now live and ready to use! 🚀

## 📞 Support

If you encounter any issues:
1. Check the logs in Railway and Vercel dashboards
2. Verify environment variables are set correctly
3. Test endpoints individually
4. Check network connectivity between services
