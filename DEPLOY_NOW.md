# 🚀 Deploy TestGenie NOW - Command Reference

Your project is ready for deployment! All configuration files have been created.

**Location:** `C:\Users\sanak\Downloads\TestGenie\TestGenie\TestGenie`

---

## ✅ What's Already Done

- ✅ Git repository initialized
- ✅ Deployment configuration files created:
  - `railway.json` - Railway deployment config
  - `nixpacks.toml` - Nixpacks build config
  - `Procfile` - Process configuration
  - `.gitignore` - Git ignore rules
- ✅ Documentation created:
  - `README.md` - Project overview
  - `DEPLOYMENT_INSTRUCTIONS.md` - Detailed guide
  - `QUICK_DEPLOY_STEPS.md` - Quick reference
  - `deploy.ps1` - PowerShell helper script
- ✅ API endpoint fixed in frontend
- ✅ All files committed to git

---

## 📝 Step 1: Push to GitHub (5 minutes)

### 1.1 Check Git Status

Open PowerShell in this directory and run:

```powershell
cd C:\Users\sanak\Downloads\TestGenie\TestGenie\TestGenie
git status
```

### 1.2 Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `TestGenie` (or your preferred name)
3. Description: `AI-powered Jira ticket analysis tool`
4. Visibility: **Private** (recommended)
5. **DO NOT** check: Initialize with README, .gitignore, or license
6. Click **"Create repository"**

### 1.3 Add Remote and Push

Copy the commands GitHub shows you, which will look like:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git
git branch -M main
git push -u origin main
```

**Replace YOUR_USERNAME with your actual GitHub username!**

If you're prompted for credentials:
- Username: Your GitHub username
- Password: Use a Personal Access Token (not your password)
  - Create token at: https://github.com/settings/tokens
  - Select scope: `repo` (full control of private repositories)

---

## 🚂 Step 2: Deploy Backend to Railway (10 minutes)

### 2.1 Create Railway Account

1. Go to: https://railway.app
2. Sign up with GitHub (recommended)
3. Authorize Railway to access your repositories

### 2.2 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **TestGenie** repository
4. Railway will auto-detect Python and start building

### 2.3 Configure Environment Variables

1. Click on your service (should be named after your repo)
2. Go to **"Variables"** tab
3. Click **"New Variable"** for each of these:

**Required Variables:**

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Optional Variables (for Jira integration):**

```bash
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
```

**Configuration Variables:**

```bash
FLASK_ENV=production
PORT=8080
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

### 2.4 Wait for Deployment

- Monitor the **"Deployments"** tab
- Wait 3-5 minutes for build to complete
- Look for: ✅ "Build successful" and ✅ "Deploy successful"

### 2.5 Get Your Backend URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. You'll see a URL like: `https://testgenie-production-xxxx.up.railway.app`
4. **COPY THIS URL** - you'll need it for Vercel!

### 2.6 Test Backend

Open your browser and visit:

```
https://your-railway-url.up.railway.app/api/health
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

If you see this, your backend is live! ✅

---

## 🔷 Step 3: Deploy Frontend to Vercel (5 minutes)

### 3.1 Create Vercel Account

1. Go to: https://vercel.com/signup
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### 3.2 Import Project

1. Go to: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Find and select **TestGenie**
4. Click **"Import"**

### 3.3 Configure Build Settings

Vercel should auto-detect Vite, but verify these settings:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | Click "Edit" → Type: `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |
| **Node.js Version** | 18.x |

### 3.4 Add Environment Variable

In the **"Environment Variables"** section:

1. Click **"Add New"**
2. Name: `VITE_API_URL`
3. Value: `https://your-railway-url.up.railway.app/api`
   - **IMPORTANT:** Use YOUR Railway URL from Step 2.5
   - **IMPORTANT:** Include `/api` at the end!

Example:
```
VITE_API_URL=https://testgenie-production-abc123.up.railway.app/api
```

### 3.5 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Monitor build progress

### 3.6 Get Your Frontend URL

Once complete, you'll see:

```
🎉 Your project is live at https://testgenie-abc123.vercel.app
```

**This is your application URL!**

---

## 🎯 Step 4: Test Your Application

### 4.1 Open Your App

Visit your Vercel URL: `https://your-app.vercel.app`

### 4.2 Test Each Feature

**Test GroomRoom:**
1. Click **"GroomRoom"** tab
2. Enter a Jira ticket ID (e.g., `PROJ-1234`)
3. Select mode: **Actionable**
4. Click **"Analyze"**
5. Wait 5-10 seconds for results

**Test EpicRoast:**
1. Click **"EpicRoast"** tab
2. Paste some ticket content
3. Select theme: **Medium**
4. Click **"Roast It!"**
5. Review the roast

**Test TestGenie:**
1. Click **"TestGenie"** tab
2. Paste acceptance criteria
3. Click **"Generate Test Scenarios"**
4. Review test cases

### 4.3 Check for Errors

If you see any errors:
1. Open browser console (F12)
2. Check for network errors
3. Verify `VITE_API_URL` in Vercel settings
4. Test backend health endpoint directly

---

## 🎉 Success!

Your application is now live at:

**Frontend:** `https://your-app.vercel.app`  
**Backend API:** `https://your-backend.up.railway.app`

---

## 🔄 Making Updates

To deploy changes in the future:

```powershell
# Make your changes
# Then commit and push

git add .
git commit -m "Description of changes"
git push origin main

# Both Railway and Vercel will auto-deploy! 🚀
```

---

## 🐛 Troubleshooting

### Backend Not Working?

**Check Railway Logs:**
1. Go to Railway dashboard
2. Click your service
3. View **"Logs"** tab
4. Look for errors

**Common Issues:**
- Missing environment variables
- Invalid Azure OpenAI credentials
- Jira credentials incorrect

### Frontend Not Working?

**Check Vercel Logs:**
1. Go to Vercel dashboard
2. Click your project
3. Go to **"Deployments"** → Latest → **"Logs"**

**Common Issues:**
- `VITE_API_URL` not set or incorrect
- Backend URL doesn't include `/api`
- CORS errors (should be auto-handled)

### Need More Help?

See:
- `DEPLOYMENT_INSTRUCTIONS.md` - Comprehensive guide
- `QUICK_DEPLOY_STEPS.md` - Quick reference
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs

---

## 💰 Cost

**Total Cost: $0/month**

- GitHub: Free
- Railway: Free tier ($5 credit/month)
- Vercel: Free tier (Hobby plan)

---

## 📞 Support

If you get stuck:

1. ✅ Check the troubleshooting section above
2. ✅ Review deployment logs
3. ✅ Test backend health endpoint
4. ✅ Verify environment variables
5. ✅ Check Azure OpenAI quotas

---

**Good luck with your deployment! 🚀**

*All configuration files have been created and committed.*  
*You're ready to push to GitHub and deploy!*

