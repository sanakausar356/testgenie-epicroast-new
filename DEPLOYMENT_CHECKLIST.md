# ✅ Deployment Checklist

Use this checklist to track your deployment progress.

---

## Pre-Deployment ✅ (COMPLETED)

- [x] Git repository initialized
- [x] Deployment configuration files created
- [x] `.gitignore` configured
- [x] Frontend API endpoints fixed
- [x] Railway config created (`railway.json`, `nixpacks.toml`)
- [x] Vercel config verified (`vercel.json`)
- [x] Procfile updated for Railway
- [x] Documentation created
- [x] All files committed to git

---

## GitHub Setup ⏳ (YOUR ACTION REQUIRED)

### [ ] Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Name: `TestGenie`
3. Visibility: Private
4. **Don't initialize** with README
5. Click "Create repository"

### [ ] Step 2: Add Remote and Push

Run these commands in PowerShell:

```powershell
cd C:\Users\sanak\Downloads\TestGenie\TestGenie\TestGenie

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Checkpoint:** Code visible on GitHub? ✅ Move to Railway deployment

---

## Railway Backend Deployment ⏳ (YOUR ACTION REQUIRED)

### [ ] Step 3: Create Railway Project

1. Go to: https://railway.app/dashboard
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select TestGenie repository

### [ ] Step 4: Add Environment Variables

Add these in Railway Variables tab:

**Required:**
```
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Optional (Jira):**
```
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email
JIRA_API_TOKEN=your_token
```

**Config:**
```
FLASK_ENV=production
PORT=8080
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

### [ ] Step 5: Wait for Deployment

- Monitor "Deployments" tab
- Wait for ✅ "Deploy successful"
- Usually takes 3-5 minutes

### [ ] Step 6: Get Backend URL

- Go to Settings → Domains
- Copy URL: `https://xxx.up.railway.app`
- Save it for Vercel setup

### [ ] Step 7: Test Backend

Visit: `https://your-railway-url.up.railway.app/api/health`

Expected response:
```json
{"status": "healthy", "services": {...}}
```

**Checkpoint:** Backend health check passing? ✅ Move to Vercel deployment

---

## Vercel Frontend Deployment ⏳ (YOUR ACTION REQUIRED)

### [ ] Step 8: Import Project to Vercel

1. Go to: https://vercel.com/new
2. Sign up/login with GitHub
3. Import TestGenie repository

### [ ] Step 9: Configure Build Settings

- Framework: Vite
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Node.js Version: 18.x

### [ ] Step 10: Add Environment Variable

Name: `VITE_API_URL`  
Value: `https://your-railway-url.up.railway.app/api`

⚠️ **Use YOUR Railway URL from Step 6!**  
⚠️ **Must end with `/api`!**

### [ ] Step 11: Deploy

- Click "Deploy"
- Wait 2-3 minutes
- Get your URL: `https://xxx.vercel.app`

**Checkpoint:** Frontend deployed? ✅ Move to testing

---

## Testing & Verification ⏳ (YOUR ACTION REQUIRED)

### [ ] Step 12: Test Frontend

Open your Vercel URL in browser

### [ ] Step 13: Test GroomRoom

1. Go to GroomRoom tab
2. Enter a Jira ticket ID
3. Select mode
4. Click "Analyze"
5. Verify results appear

### [ ] Step 14: Test EpicRoast

1. Go to EpicRoast tab
2. Paste content or ticket ID
3. Click "Roast It!"
4. Verify roast appears

### [ ] Step 15: Test TestGenie

1. Go to TestGenie tab
2. Paste AC or ticket ID
3. Click "Generate"
4. Verify scenarios appear

### [ ] Step 16: Check Browser Console

- Press F12
- Look for errors
- Verify API calls succeed

---

## Post-Deployment ✅ (OPTIONAL)

### [ ] Share URLs

Share with team:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.up.railway.app`

### [ ] Set Up Custom Domain (Optional)

**Vercel:**
- Project Settings → Domains
- Add custom domain
- Update DNS records

**Railway:**
- Service Settings → Custom Domain
- Add custom domain
- Update `VITE_API_URL` in Vercel

### [ ] Monitor Logs

**Railway Logs:**
- Dashboard → Your Service → Logs

**Vercel Logs:**
- Dashboard → Your Project → Deployments → Latest → Logs

---

## 🎉 Deployment Complete!

When all checkboxes above are checked, your deployment is complete!

### Your Live URLs:
- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-backend.up.railway.app`

### Future Updates:
```powershell
git add .
git commit -m "Your changes"
git push origin main
# Auto-deploys to Railway + Vercel! 🚀
```

---

## 🆘 Need Help?

- See `DEPLOY_NOW.md` for detailed commands
- See `DEPLOYMENT_INSTRUCTIONS.md` for comprehensive guide
- See `QUICK_DEPLOY_STEPS.md` for quick reference

---

## 📊 Deployment Status

| Component | Status | URL |
|-----------|--------|-----|
| GitHub | ⏳ Pending | https://github.com/YOUR_USERNAME/TestGenie |
| Railway Backend | ⏳ Pending | TBD |
| Vercel Frontend | ⏳ Pending | TBD |

**Update this table as you complete each step!**

---

*Good luck! You've got this! 🚀*

