# 🚀 Complete Deployment Guide: GitHub + Vercel + Railway

This guide will walk you through deploying TestGenie to production using GitHub, Vercel (frontend), and Railway (backend).

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ GitHub account (https://github.com)
- ✅ Vercel account (https://vercel.com)
- ✅ Railway account (https://railway.app)
- ✅ Git installed on your machine
- ✅ Azure OpenAI credentials (endpoint, API key, deployment name)
- ✅ Jira credentials (URL, email, API token) - optional

---

## STEP 1: Push Code to GitHub

### 1.1 Open PowerShell and Navigate to Project

```powershell
cd C:\Users\sanak\Downloads\TestGenie\TestGenie
```

### 1.2 Initialize Git Repository

```powershell
git init
```

### 1.3 Add All Files

```powershell
git add .
```

### 1.4 Create Initial Commit

```powershell
git commit -m "Initial commit - TestGenie deployment ready"
```

### 1.5 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `TestGenie` (or your preferred name)
3. Description: `AI-powered Jira ticket analysis tool with TestGenie, EpicRoast, and GroomRoom`
4. Visibility: **Private** (recommended) or Public
5. **DO NOT** initialize with README, .gitignore, or license (you already have these)
6. Click **"Create repository"**

### 1.6 Add Remote and Push

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git
git branch -M main
git push -u origin main
```

If prompted, enter your GitHub credentials or use a Personal Access Token.

**✅ Checkpoint:** Your code should now be visible on GitHub!

---

## STEP 2: Deploy Backend to Railway

### 2.1 Create New Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If first time, click **"Connect GitHub"** and authorize Railway

### 2.2 Select Repository

1. Find and select your **TestGenie** repository
2. Click on the repository to deploy it

### 2.3 Configure Service

Railway should auto-detect the Python app. If not, configure manually:

- **Root Directory:** Leave as `/` or set to `backend` if needed
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

### 2.4 Add Environment Variables

Click on your service, then go to **"Variables"** tab. Add these one by one:

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Jira Configuration (Optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token_here

# Flask Configuration
FLASK_ENV=production
PORT=8080

# Python Configuration
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

**Important:** Replace the placeholder values with your actual credentials.

### 2.5 Deploy

1. Click **"Deploy"** (or it may auto-deploy)
2. Wait 3-5 minutes for the build to complete
3. Monitor the logs in the **"Deployments"** tab

### 2.6 Get Backend URL

Once deployed, Railway will provide a public URL like:

```
https://testgenie-backend-production-xxxx.up.railway.app
```

**Copy this URL!** You'll need it for the frontend deployment.

### 2.7 Test Backend

Open your browser and test the health endpoint:

```
https://your-backend-url.up.railway.app/api/health
```

You should see:

```json
{
  "status": "healthy",
  "services": {
    "testgenie": true,
    "epicroast": true,
    "groomroom": true,
    "jira": true
  }
}
```

**✅ Checkpoint:** Backend is live and responding!

---

## STEP 3: Deploy Frontend to Vercel

### 3.1 Create New Project

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your **TestGenie** repository
4. Click **"Import"**

### 3.2 Configure Build Settings

Vercel should auto-detect Vite. Configure these settings:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` |
| **Root Directory** | Click "Edit" → `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |
| **Node.js Version** | `18.x` or higher |

### 3.3 Add Environment Variables

In the **"Environment Variables"** section, add:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-railway-backend-url.up.railway.app/api` |

**Important:** Replace with YOUR actual Railway backend URL from Step 2.6. Make sure to include `/api` at the end!

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for the build to complete
3. Monitor the build logs

### 3.5 Get Frontend URL

Once deployed, Vercel will provide a URL like:

```
https://testgenie-abc123.vercel.app
```

**✅ Checkpoint:** Frontend is live!

---

## STEP 4: Update Frontend API URL (Optional)

If you need to update the backend URL later:

### 4.1 Update vercel.json

Edit `frontend/vercel.json` and update the destination URL:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://YOUR-RAILWAY-URL.up.railway.app/api/$1"
    }
  ]
}
```

### 4.2 Commit and Push

```powershell
git add frontend/vercel.json
git commit -m "Update backend URL"
git push origin main
```

Vercel will automatically redeploy with the new configuration.

---

## STEP 5: Test Full Application

### 5.1 Open Your App

Navigate to your Vercel URL: `https://testgenie-abc123.vercel.app`

### 5.2 Test GroomRoom

1. Click **"GroomRoom"** tab
2. Enter a Jira ticket ID (e.g., `PROJ-1234`)
3. Select analysis mode: **Actionable**, **Insight**, or **Summary**
4. Click **"Analyze"**
5. Wait 5-10 seconds for results

### 5.3 Test EpicRoast

1. Click **"EpicRoast"** tab
2. Paste ticket content or enter a ticket ID
3. Select roast theme
4. Click **"Roast It!"**
5. Review the roast analysis

### 5.4 Test TestGenie

1. Click **"TestGenie"** tab
2. Paste acceptance criteria or enter a ticket ID
3. Click **"Generate Test Scenarios"**
4. Review generated test cases

**✅ All working? Congratulations! 🎉**

---

## 🔄 Continuous Deployment (Auto-Deploy)

Both Railway and Vercel support automatic deployments on git push:

```powershell
# Make your code changes
# Then commit and push

git add .
git commit -m "Feature: Your feature description"
git push origin main

# Automatically:
# - Railway rebuilds backend (3-5 min)
# - Vercel rebuilds frontend (2-3 min)
# - Both services go live automatically
```

No manual deployment needed after initial setup! ✅

---

## 🐛 Troubleshooting

### Backend shows "Application Error"

**Check Railway Logs:**
1. Go to Railway dashboard
2. Click on your service
3. View **"Logs"** tab
4. Look for errors (missing env variables, import errors, etc.)

**Common fixes:**
- Verify all environment variables are set correctly
- Check Azure OpenAI credentials are valid
- Ensure Jira credentials are correct (if using Jira integration)

### Frontend shows "Network Error"

**Solutions:**
1. Verify `VITE_API_URL` in Vercel settings
2. Test backend directly: `https://your-backend.up.railway.app/api/health`
3. Check browser console for CORS errors
4. Ensure backend URL in Vercel environment variables includes `/api`

### Railway "Service Unavailable"

**Cold Start Issue:**
- Railway free tier may sleep after inactivity
- First request after sleep takes 30-60 seconds
- Subsequent requests are fast

**Solution:** Upgrade to Railway Pro ($5/month) for always-on service

### Vercel Build Fails

**Common causes:**
- Node.js version mismatch
- Missing dependencies
- TypeScript errors

**Solution:**
1. Check build logs in Vercel dashboard
2. Ensure `engines` in `package.json` specifies Node 18+
3. Run `npm run build` locally to test

### Jira Integration Not Working

**Solutions:**
1. Verify Jira credentials in Railway environment variables
2. Check Jira API token hasn't expired
3. Test Jira connection manually with curl or Postman
4. Ensure Jira URL format: `https://your-domain.atlassian.net` (no trailing slash)

---

## 💰 Cost Breakdown

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| **GitHub** | Free | $0/month | Unlimited repos |
| **Vercel** | Hobby | $0/month | 100 GB bandwidth, unlimited deployments |
| **Railway** | Free | $0/month | $5 credit/month, may sleep after inactivity |
| **TOTAL** | | **$0/month** | Perfect for MVP/Demo |

### Upgrade Options:

- **Vercel Pro:** $20/month (custom domains, more bandwidth)
- **Railway Pro:** $5/month (always-on, no sleep, better resources)

---

## 📊 Monitoring & Logs

### Railway Logs:
1. Go to https://railway.app/dashboard
2. Click on your service
3. View real-time logs

### Vercel Logs:
1. Go to https://vercel.com/dashboard
2. Click on your project
3. Go to **"Deployments"** → Select deployment → **"Logs"**

---

## 🎯 Custom Domains (Optional)

### For Vercel (Frontend):
1. Project Settings → Domains
2. Add your custom domain (e.g., `testgenie.yourcompany.com`)
3. Update DNS records as shown
4. Wait for DNS propagation

### For Railway (Backend):
1. Service Settings → Custom Domain
2. Add your backend domain (e.g., `api.testgenie.yourcompany.com`)
3. Update DNS records
4. Update `VITE_API_URL` in Vercel with new domain

---

## 🎉 You're Done!

Your TestGenie application is now:

- ✅ **Live** on the internet
- ✅ **Secure** (HTTPS enabled automatically)
- ✅ **Auto-deploying** on every git push
- ✅ **Scalable** (both services auto-scale)
- ✅ **Free** to run (within free tier limits)

**Share your app:**
```
Frontend: https://testgenie-abc123.vercel.app
Backend API: https://your-backend.up.railway.app/api
```

---

## 📞 Need Help?

If you encounter issues:

1. ✅ Check this troubleshooting guide above
2. ✅ View deployment logs (Railway/Vercel dashboards)
3. ✅ Test backend health endpoint directly
4. ✅ Verify all environment variables
5. ✅ Check that Azure OpenAI and Jira credentials are valid

**Happy Deploying! 🚀**

---

## 📚 Additional Resources

- Railway Documentation: https://docs.railway.app
- Vercel Documentation: https://vercel.com/docs
- GitHub Documentation: https://docs.github.com

---

*Last updated: October 2025*

