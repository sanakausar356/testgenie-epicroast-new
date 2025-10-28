# 🚀 TestGenie Deployment Guide (Vercel + Render)

**Deployment Method:** Option 1 - Easiest & Free
- **Frontend:** Vercel (Free tier)
- **Backend:** Render (Free tier)

**Total Time:** 15-20 minutes

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure you have:

- ✅ GitHub account
- ✅ Vercel account (sign up at: https://vercel.com)
- ✅ Render account (sign up at: https://render.com)
- ✅ Jira API credentials (URL, Email, API Token)
- ✅ OpenAI API key
- ✅ Figma token (optional)

---

## STEP 1: Push Code to GitHub

### 1.1 Initialize Git (if not already done)

```bash
cd C:\Users\IbtasamAli\Downloads\TestGenie
git init
```

### 1.2 Add all files

```bash
git add .
```

### 1.3 Commit changes

```bash
git commit -m "Ready for deployment - TestGenie v1.0"
```

### 1.4 Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `TestGenie`
3. Description: `AI-powered Jira ticket analysis tool`
4. Visibility: **Private** (recommended) or Public
5. DO NOT initialize with README (already have one)
6. Click "Create repository"

### 1.5 Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git
git branch -M main
git push -u origin main
```

**✅ Checkpoint:** Your code should now be visible on GitHub!

---

## STEP 2: Deploy Backend to Render

### 2.1 Create New Web Service

1. Go to: https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### 2.2 Connect GitHub Repository

1. Click **"Connect account"** if first time
2. Select **"TestGenie"** repository
3. Click **"Connect"**

### 2.3 Configure Web Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `testgenie-backend` |
| **Region** | Choose closest to you (e.g., Oregon, Frankfurt) |
| **Branch** | `main` |
| **Root Directory** | `TestGenie` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Instance Type** | `Free` |

### 2.4 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these one by one:

```
PORT=8080
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token_here
OPENAI_API_KEY=sk-your-openai-api-key-here
FIGMA_TOKEN=figd_your_figma_token_here
NO_PROXY=*
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

**How to get these tokens:** See `ENV_SETUP.md` file

### 2.5 Deploy

1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. Monitor the logs - should see: `✅ Build successful`

### 2.6 Get Backend URL

Once deployed, you'll see:
```
Your service is live at https://testgenie-backend.onrender.com
```

**Copy this URL!** You'll need it for frontend deployment.

### 2.7 Test Backend

Open in browser: `https://testgenie-backend.onrender.com/api/health`

Should see:
```json
{
  "status": "healthy",
  "service": "TestGenie & EpicRoast with GroomRoom",
  "version": "1.0"
}
```

**✅ Checkpoint:** Backend is live!

---

## STEP 3: Deploy Frontend to Vercel

### 3.1 Create New Project

1. Go to: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select **"TestGenie"** repository
4. Click **"Import"**

### 3.2 Configure Project

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` (should auto-detect) |
| **Root Directory** | Click **"Edit"** → Set to: `TestGenie/frontend` |
| **Build Command** | `npm run build` (auto-detected) |
| **Output Directory** | `dist` (auto-detected) |
| **Install Command** | `npm install` (auto-detected) |

### 3.3 Add Environment Variable

Click **"Environment Variables"** section

Add this:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://testgenie-backend.onrender.com/api` |

**Important:** Replace with YOUR backend URL from Step 2.6

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Monitor build logs - should see: `✅ Build completed`

### 3.5 Get Frontend URL

Once deployed, you'll see:
```
🎉 Your project is live at https://testgenie.vercel.app
```

**✅ Checkpoint:** Frontend is live!

---

## STEP 4: Test Full Deployment

### 4.1 Open Your App

Go to: `https://testgenie.vercel.app` (or your custom URL)

### 4.2 Test GroomRoom

1. Click **"GroomRoom"** tab
2. Enter ticket ID: `ODCD-34544` (or any valid ticket)
3. Select Mode: **Actionable**
4. Click **"Analyze"**
5. Should see full groom report in 5-10 seconds

### 4.3 Test EpicRoast

1. Click **"EpicRoast"** tab
2. Paste some ticket content
3. Select Theme: **Medium**
4. Click **"Roast It!"**
5. Should see roast analysis

### 4.4 Test Figma Integration

1. Go to **"GroomRoom"** tab
2. Paste a Figma link in the optional field
3. Click **"Analyze"**
4. Should extract design data

**✅ All working? Congratulations! 🎉**

---

## 🎯 Post-Deployment Tasks

### Custom Domain (Optional)

#### For Vercel (Frontend):
1. Go to: Project Settings → Domains
2. Add your domain (e.g., `testgenie.yourcompany.com`)
3. Update DNS records as shown
4. Wait 24-48 hours for DNS propagation

#### For Render (Backend):
1. Go to: Web Service → Settings → Custom Domains
2. Add your backend domain (e.g., `api.testgenie.yourcompany.com`)
3. Update DNS records
4. Update `VITE_API_URL` in Vercel to use new backend domain

---

## 🔄 Auto-Deployment (CI/CD)

Good news! Both platforms support auto-deployment:

### On Git Push:
```bash
# Make changes to code
git add .
git commit -m "Feature: Added new functionality"
git push origin main

# Automatically:
# 1. Render rebuilds backend (3-5 min)
# 2. Vercel rebuilds frontend (2-3 min)
# 3. Both go live automatically
```

**No manual deployment needed!** ✅

---

## 🐛 Troubleshooting

### Issue: Backend shows "Application Error"

**Solution:**
1. Go to Render → Your Service → Logs
2. Check for errors (missing env variables, import errors)
3. Fix and push changes to GitHub
4. Render will auto-redeploy

### Issue: Frontend shows "Network Error"

**Solution:**
1. Check `VITE_API_URL` is correct in Vercel
2. Test backend health: `https://your-backend.onrender.com/api/health`
3. Check CORS settings in `app.py` (should allow all origins)

### Issue: Jira tickets not fetching

**Solution:**
1. Verify Jira credentials in Render environment variables
2. Check Jira API token is not expired
3. Test Jira connection: `https://your-backend.onrender.com/api/health`

### Issue: Render "Free tier - Spins down with inactivity"

**Note:** Render free tier sleeps after 15 min of inactivity
- **First request:** May take 30-60 seconds (cold start)
- **Subsequent requests:** Fast (< 1 second)

**Solution:** Upgrade to Render paid plan ($7/month) for always-on service

---

## 📊 Monitoring & Logs

### View Backend Logs:
1. Go to: https://dashboard.render.com
2. Click on your service
3. Click **"Logs"** tab
4. See real-time logs

### View Frontend Logs:
1. Go to: https://vercel.com/dashboard
2. Click on your project
3. Click **"Deployments"** → Latest deployment → **"Build Logs"**

---

## 💰 Cost Breakdown

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| **Vercel** | Free | $0/month | 100 GB bandwidth, unlimited deployments |
| **Render** | Free | $0/month | 750 hours/month, sleeps after 15 min inactivity |
| **GitHub** | Free | $0/month | Unlimited public/private repos |
| **TOTAL** | | **$0/month** | ✅ Perfect for MVP/Demo |

### Upgrade Options (if needed):

- **Vercel Pro:** $20/month (more bandwidth, custom domains)
- **Render Starter:** $7/month (always-on, no sleep)

---

## 🎉 You're Done!

Your TestGenie app is now:
- ✅ **Live** on the internet
- ✅ **Secure** (HTTPS enabled)
- ✅ **Auto-deploying** on git push
- ✅ **Free** to run

**Share your app:**
```
Frontend: https://testgenie.vercel.app
Backend API: https://testgenie-backend.onrender.com/api
```

---

## 📞 Need Help?

If you run into issues:
1. Check **Troubleshooting** section above
2. View deployment logs (Render/Vercel dashboards)
3. Test backend health endpoint
4. Verify environment variables are set correctly

**Happy Deploying! 🚀**

