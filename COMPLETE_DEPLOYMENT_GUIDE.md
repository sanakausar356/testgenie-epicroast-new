# 🚀 Complete Deployment Guide - All Steps

## Overview

This guide walks you through the complete deployment of TestGenie to production.

---

## ✅ Step 1: GitHub (COMPLETED)

**Status:** ✅ DONE

**GitHub Repository:** https://github.com/sanakausar356/testgenie-epicroast-new

Your code has been successfully pushed to GitHub!

---

## ⏳ Step 2: Railway Backend Deployment (IN PROGRESS)

**Railway Project:** https://railway.com/project/b6141a0a-f01c-4f0a-8070-5de5a912a793

### Actions Required (You Must Do These):

#### A. Connect GitHub to Railway

1. Open your Railway project (link above)
2. Click **"+ New"** or **"New Service"**
3. Select **"GitHub Repo"**
4. Authorize Railway if prompted
5. Select: `sanakausar356/testgenie-epicroast-new`

#### B. Add Environment Variables

Click on your service → **"Variables"** tab → Add these:

**🔑 Azure OpenAI (Required):**
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**📋 Jira (Optional):**
```
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_token
```

**⚙️ Configuration:**
```
FLASK_ENV=production
PORT=8080
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

#### C. Wait for Deployment

- Railway will auto-deploy after adding variables
- Monitor **"Deployments"** tab
- Wait 3-5 minutes
- Look for: ✅ "Deploy successful"

#### D. Get Backend URL

1. Go to **"Settings"** → **"Domains"**
2. Copy your URL: `https://xxx.up.railway.app`
3. **SAVE THIS URL** - needed for Vercel!

#### E. Test Backend

Visit: `https://your-railway-url.up.railway.app/api/health`

Expected response:
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

**✅ If you see this, backend is live! Proceed to Step 3.**

---

## ⏳ Step 3: Vercel Frontend Deployment

### Actions Required (You Must Do These):

#### A. Import to Vercel

1. Go to: https://vercel.com/new
2. Sign up/login with GitHub
3. Click **"Import Git Repository"**
4. Select: `sanakausar356/testgenie-epicroast-new`
5. Click **"Import"**

#### B. Configure Settings

**⚠️ CRITICAL SETTINGS:**

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` ⚠️ MUST SET THIS |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Node.js Version** | 18.x |

#### C. Add Environment Variable

**Name:** `VITE_API_URL`

**Value:** (Use YOUR Railway URL from Step 2D)
```
https://your-railway-url.up.railway.app/api
```

**Example:**
```
VITE_API_URL=https://testgenie-production-abc123.up.railway.app/api
```

**⚠️ IMPORTANT:**
- Use YOUR actual Railway backend URL
- Must end with `/api`
- No trailing slash

#### D. Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Monitor build progress

#### E. Get Frontend URL

You'll see: `🎉 Your project is live at https://testgenie-epicroast-new-xxx.vercel.app`

**This is your live application URL!**

---

## 🧪 Step 4: Test Your Application

### Test Checklist:

1. **Open Frontend:**
   - Visit your Vercel URL
   - All three tabs should be visible

2. **Test GroomRoom:**
   - Enter Jira ticket ID
   - Click "Analyze"
   - ✅ Results appear

3. **Test EpicRoast:**
   - Enter content
   - Click "Roast It!"
   - ✅ Roast appears

4. **Test TestGenie:**
   - Enter acceptance criteria
   - Click "Generate"
   - ✅ Scenarios appear

5. **Check Browser Console:**
   - Press F12
   - No errors
   - ✅ API calls succeed

---

## 🎉 Deployment Complete!

When all tests pass, you have:

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend** | https://testgenie-epicroast-new-xxx.vercel.app | ✅ |
| **Backend** | https://xxx.up.railway.app | ✅ |
| **GitHub** | https://github.com/sanakausar356/testgenie-epicroast-new | ✅ |

### Cost: $0/month (Free Tiers)

---

## 🔄 Making Updates

```powershell
cd C:\Users\sanak\Downloads\TestGenie\TestGenie\TestGenie

# Make your changes
# Then:

git add .
git commit -m "Your update message"
git push origin main

# Both Railway and Vercel auto-deploy!
```

---

## 🆘 Troubleshooting

### Railway Issues

**Build Failed:**
- Check logs in Railway dashboard
- Verify environment variables are set
- Check `requirements.txt` has all packages

**Service Won't Start:**
- Verify Azure OpenAI credentials
- Check PORT is set to 8080
- Review logs for errors

### Vercel Issues

**Build Failed:**
- Ensure Root Directory is set to `frontend`
- Check Node.js version is 18+
- Review build logs

**Can't Connect to Backend:**
- Verify `VITE_API_URL` is correct
- Must end with `/api`
- Test backend `/api/health` directly
- Check Railway is running

### Application Issues

**"Network Error":**
- Backend not running → Check Railway
- Wrong API URL → Check Vercel env vars
- CORS issue → Check Railway logs

**"Service Unavailable":**
- Azure OpenAI credentials invalid
- API quota exceeded
- Check Railway logs

---

## 📚 Detailed Guides

For more detailed information, see:

- `RAILWAY_DEPLOYMENT_STEPS.md` - Detailed Railway guide
- `VERCEL_DEPLOYMENT_STEPS.md` - Detailed Vercel guide
- `DEPLOYMENT_INSTRUCTIONS.md` - Comprehensive troubleshooting

---

## 📝 Environment Variables Reference

### Railway Backend:

```bash
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Optional (Jira)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email
JIRA_API_TOKEN=your_token

# Configuration
FLASK_ENV=production
PORT=8080
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

### Vercel Frontend:

```bash
VITE_API_URL=https://your-railway-url.up.railway.app/api
```

---

## ✅ Deployment Checklist

Use this to track your progress:

### GitHub:
- [x] Repository created
- [x] Code pushed
- [x] All files committed

### Railway:
- [ ] Service created from GitHub repo
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Backend URL copied
- [ ] Health endpoint tested

### Vercel:
- [ ] Project imported from GitHub
- [ ] Root directory set to `frontend`
- [ ] VITE_API_URL added
- [ ] Deployment successful
- [ ] Frontend URL received
- [ ] Application tested

### Testing:
- [ ] GroomRoom working
- [ ] EpicRoast working
- [ ] TestGenie working
- [ ] No console errors
- [ ] API calls successful

---

**🎯 Current Status:**

✅ GitHub: COMPLETE  
⏳ Railway: IN PROGRESS (waiting for you to add variables)  
⏳ Vercel: PENDING (do after Railway)

**👉 Next: Complete Railway deployment by adding environment variables!**

---

**Good luck! 🚀**

