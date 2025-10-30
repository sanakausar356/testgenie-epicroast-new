# 🚀 Quick Deployment Steps

Follow these steps to deploy TestGenie to GitHub, Railway, and Vercel.

---

## Step 1: Push to GitHub (5 minutes)

### Option A: Using PowerShell (Windows)

Open PowerShell in the TestGenie directory and run:

```powershell
# Navigate to project directory
cd C:\Users\sanak\Downloads\TestGenie\TestGenie

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - TestGenie deployment ready"

# Create a GitHub repository at https://github.com/new
# Name it "TestGenie" and DO NOT initialize with README

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Desktop

1. Open GitHub Desktop
2. Add the `TestGenie` folder as a repository
3. Commit all files
4. Publish to GitHub

---

## Step 2: Deploy Backend to Railway (10 minutes)

### 2.1 Create Project

1. Go to https://railway.app/dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect GitHub and select TestGenie repository
4. Railway will auto-detect Python and start deploying

### 2.2 Configure Environment Variables

Click on your service → "Variables" tab → Add these:

**Required Variables:**
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
FLASK_ENV=production
PORT=8080
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

**Optional (for Jira integration):**
```
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_token
```

### 2.3 Get Backend URL

After deployment completes (3-5 minutes), copy your Railway URL:
```
https://your-project-name.up.railway.app
```

### 2.4 Test Backend

Open in browser:
```
https://your-project-name.up.railway.app/api/health
```

Should return: `{"status": "healthy", ...}`

---

## Step 3: Deploy Frontend to Vercel (5 minutes)

### 3.1 Create Project

1. Go to https://vercel.com/new
2. Import your TestGenie repository from GitHub
3. Configure build settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

### 3.2 Add Environment Variable

In "Environment Variables" section, add:

```
VITE_API_URL=https://your-railway-url.up.railway.app/api
```

**IMPORTANT:** Replace with YOUR actual Railway URL from Step 2.3, and include `/api` at the end!

### 3.3 Deploy

Click "Deploy" and wait 2-3 minutes.

### 3.4 Get Frontend URL

Vercel will provide a URL like:
```
https://testgenie-abc123.vercel.app
```

---

## Step 4: Test Your Application

1. Open your Vercel URL in a browser
2. Try each tab:
   - **TestGenie:** Generate test scenarios
   - **EpicRoast:** Generate roasts
   - **GroomRoom:** Analyze tickets

---

## 🎉 Done!

Your application is now live at:
- **Frontend:** https://your-app.vercel.app
- **Backend:** https://your-backend.up.railway.app

### Future Updates

To deploy updates, just push to GitHub:

```powershell
git add .
git commit -m "Your update message"
git push origin main
```

Both Railway and Vercel will automatically redeploy! 🚀

---

## 🐛 Quick Troubleshooting

### Backend Error?
- Check Railway logs
- Verify environment variables
- Test health endpoint: `/api/health`

### Frontend Error?
- Check Vercel build logs
- Verify `VITE_API_URL` is set correctly
- Test backend URL directly

### Need detailed help?
See `DEPLOYMENT_INSTRUCTIONS.md` for comprehensive troubleshooting guide.

---

**Total Time:** ~20 minutes
**Cost:** $0/month (free tiers)

Happy deploying! 🎊

