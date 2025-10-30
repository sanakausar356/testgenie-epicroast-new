# 🔷 Vercel Frontend Deployment - Step by Step

## Your GitHub Repository
**Repo:** https://github.com/sanakausar356/testgenie-epicroast-new

## Prerequisites
- ✅ GitHub repo is ready
- ⏳ Railway backend (get URL from Railway dashboard)

---

## 🚀 Step-by-Step Deployment

### Step 1: Import Project from GitHub

Vercel should be open in your browser at: https://vercel.com/new

1. **Sign in with GitHub** (if not already signed in)
2. **Import Git Repository:**
   - You'll see "Import Git Repository" section
   - Look for: `sanakausar356/testgenie-epicroast-new`
   - Click **"Import"** button next to it

If you don't see your repository:
- Click **"Add GitHub Account"** or **"Adjust GitHub App Permissions"**
- Select your repository
- Authorize Vercel

---

### Step 2: Configure Project Settings

On the configuration page, set these **CRITICAL** settings:

#### Framework Preset:
```
Vite
```
✅ Should auto-detect, but verify it says "Vite"

#### Root Directory:
⚠️ **MOST IMPORTANT SETTING**
```
Click "Edit" button next to Root Directory
Type: frontend
Click "Continue"
```

**This MUST be set to `frontend` or build will fail!**

#### Build and Output Settings (Auto-detected):
```
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

#### Node.js Version:
```
18.x (or 20.x)
```

---

### Step 3: Add Environment Variable

**CRITICAL: You need your Railway backend URL for this step!**

#### Get Railway Backend URL First:

1. Open Railway dashboard: https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47
2. Click on your service "giving-determination"
3. Go to **"Settings"** tab
4. Find **"Domains"** section
5. Copy the URL (e.g., `https://web-production-8415f.up.railway.app`)

#### Add Environment Variable in Vercel:

Scroll down to **"Environment Variables"** section:

**Variable 1:**
```
Name: VITE_API_URL
Value: https://YOUR-RAILWAY-URL.up.railway.app/api
```

**⚠️ CRITICAL:**
- Replace `YOUR-RAILWAY-URL` with your actual Railway domain
- **MUST end with `/api`**
- **NO trailing slash after `/api`**

**Example:**
```
VITE_API_URL=https://web-production-8415f.up.railway.app/api
```

---

### Step 4: Deploy

1. **Click "Deploy"** button (bottom right)
2. Vercel will start building
3. You'll see the build progress

**Build Timeline:**
- Install dependencies: 1-2 minutes
- Build Vite app: 30 seconds
- Deploy: 10 seconds
- **Total: 2-3 minutes**

---

### Step 5: Get Your Frontend URL

Once deployment completes, you'll see:

```
🎉 Congratulations! Your project is live at:
https://testgenie-epicroast-new-xxx.vercel.app
```

**Copy this URL - this is your live application!**

---

## 🧪 Test Your Application

### 1️⃣ Open Your Vercel URL

Visit: `https://your-app.vercel.app`

You should see the TestGenie interface with three tabs:
- TestGenie
- EpicRoast  
- GroomRoom

### 2️⃣ Test GroomRoom

1. Click **"GroomRoom"** tab
2. Enter a Jira ticket ID: `ODCD-34544`
3. Select mode: **"Actionable"**
4. Click **"Analyze"**
5. Wait 5-10 seconds

**Expected:** Full groom analysis appears

### 3️⃣ Test EpicRoast

1. Click **"EpicRoast"** tab
2. Enter a ticket ID or paste content
3. Select theme: **"Medium"**
4. Click **"Roast It!"**

**Expected:** Roast analysis appears

### 4️⃣ Test TestGenie

1. Click **"TestGenie"** tab
2. Enter a ticket ID or paste acceptance criteria
3. Click **"Generate Test Scenarios"**

**Expected:** Test scenarios appear

### 5️⃣ Check Browser Console

Press **F12** → **Console** tab

- Should see no errors
- API calls should return 200 status
- Look for: "API: Response status: 200"

---

## 🐛 Troubleshooting

### Build Failed?

**Error: "Cannot find module" or "Failed to compile"**

**Solution:**
1. Check that **Root Directory is set to `frontend`**
2. Go to Settings → General → Root Directory
3. Change to `frontend`
4. Redeploy

**Error: "TypeScript errors"**

**Solution:**
- Likely minor type issues
- Check build logs for specific errors
- May need to fix TypeScript errors in code

---

### Frontend Can't Connect to Backend?

**Error: "Network Error" or "Failed to fetch"**

**Solution 1: Check Environment Variable**
1. Go to Vercel Dashboard → Your Project
2. Click **"Settings"** → **"Environment Variables"**
3. Verify `VITE_API_URL` is set correctly:
   - Must include your Railway URL
   - Must end with `/api`
   - Example: `https://web-production-8415f.up.railway.app/api`

**Solution 2: Verify Backend is Running**
1. Test Railway health endpoint directly:
   ```
   https://your-railway-url.up.railway.app/api/health
   ```
2. Should return `{"status": "healthy", ...}`
3. If this fails, backend is not running - check Railway

**Solution 3: CORS Issue**
- Backend already has CORS enabled
- Check Railway logs for CORS errors
- Verify no typos in Railway URL

**Solution 4: Redeploy**
1. If you changed `VITE_API_URL`, you MUST redeploy
2. Go to **"Deployments"** tab
3. Click "..." on latest deployment
4. Click **"Redeploy"**

---

### API Calls Return 500 Error?

**Problem:** Backend is running but returning errors

**Solution:**
1. Check Railway logs for errors
2. Verify Azure OpenAI credentials in Railway
3. Check Azure OpenAI quota/limits
4. Verify Jira credentials if using Jira features

---

## 📋 Configuration Checklist

Use this to verify everything is correct:

### Vercel Settings:
- [ ] Framework: Vite
- [ ] Root Directory: `frontend` ⚠️ CRITICAL
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Node.js Version: 18.x or 20.x

### Environment Variables:
- [ ] `VITE_API_URL` is set
- [ ] Value includes Railway URL
- [ ] Value ends with `/api`
- [ ] No trailing slash after `/api`
- [ ] No typos in URL

### Testing:
- [ ] Frontend opens without errors
- [ ] All three tabs visible
- [ ] Can analyze Jira ticket
- [ ] Can generate roast
- [ ] Can generate test scenarios
- [ ] No console errors
- [ ] API calls return 200 status

---

## 🎯 Quick Command Reference

### Your URLs:

**GitHub:**
```
https://github.com/sanakausar356/testgenie-epicroast-new
```

**Railway (Backend):**
```
https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47
Your backend URL: https://web-production-8415f.up.railway.app (get from Railway)
```

**Vercel (Frontend):**
```
https://vercel.com/new (for deployment)
Your app URL: https://testgenie-epicroast-new-xxx.vercel.app (after deployment)
```

---

## 🔄 Future Updates

To deploy changes:

```powershell
cd C:\Users\sanak\Downloads\TestGenie\TestGenie\TestGenie

# Make changes
git add .
git commit -m "Your update message"
git push origin main

# Vercel auto-deploys! 🚀
```

Both Railway and Vercel will automatically redeploy when you push to GitHub main branch.

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ Vercel shows "Deployment Ready"
- ✅ Frontend URL opens successfully
- ✅ All three tabs (TestGenie, EpicRoast, GroomRoom) are visible
- ✅ Can successfully analyze a Jira ticket in GroomRoom
- ✅ Backend health check returns "healthy"
- ✅ No errors in browser console (F12)
- ✅ API calls complete with 200 status

---

## 📊 Complete Deployment Status

Once Vercel is deployed:

| Component | Status | URL |
|-----------|--------|-----|
| GitHub | ✅ Complete | https://github.com/sanakausar356/testgenie-epicroast-new |
| Railway Backend | ✅ Deployed | Get from Railway dashboard |
| Vercel Frontend | 🎯 Deploying Now | Get after deployment |

---

## 🎉 You're Almost Done!

After Vercel deployment completes:

1. ✅ Copy your Vercel URL
2. ✅ Test all features
3. ✅ Share with your team
4. 🎊 Celebrate! Your app is live!

---

**Vercel Dashboard:** https://vercel.com/dashboard

**Need help?** Check the troubleshooting section above or the detailed guide in `VERCEL_DEPLOYMENT_STEPS.md`

**Good luck!** 🚀

