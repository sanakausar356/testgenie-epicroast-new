# 🔷 Vercel Frontend Deployment Steps

## Your GitHub Repository  
**Repo URL:** https://github.com/sanakausar356/testgenie-epicroast-new

## Prerequisites
✅ GitHub repository pushed (DONE)
⏳ Railway backend deployed (IN PROGRESS - complete this first!)
⏳ Railway backend URL copied (you'll need this!)

---

## Step-by-Step Deployment

### 1️⃣ Import Project to Vercel

1. Go to: https://vercel.com/new
2. Sign up/login with GitHub (if not already)
3. Click **"Import Git Repository"**
4. Find and select: **`sanakausar356/testgenie-epicroast-new`**
5. Click **"Import"**

### 2️⃣ Configure Project Settings

Vercel should auto-detect Vite. Verify/set these settings:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` |
| **Root Directory** | Click "Edit" → Type: `frontend` ⚠️ IMPORTANT |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |
| **Node.js Version** | `18.x` (or higher) |

**⚠️ CRITICAL:** Make sure to set **Root Directory** to `frontend`!

### 3️⃣ Add Environment Variable

In the **"Environment Variables"** section:

**Variable Name:**
```
VITE_API_URL
```

**Variable Value:** (Use YOUR Railway URL from backend deployment)
```
https://your-railway-backend-url.up.railway.app/api
```

**Example:**
```
VITE_API_URL=https://testgenie-production-b6141a0a.up.railway.app/api
```

**⚠️ CRITICAL:** 
- Use YOUR actual Railway URL
- Must end with `/api`
- No trailing slash after `/api`

### 4️⃣ Deploy

1. Click **"Deploy"**
2. Vercel will start building
3. Monitor build progress (takes 2-3 minutes)
4. Wait for: ✅ **"Build Completed"**

### 5️⃣ Get Your Frontend URL

Once deployment completes, Vercel will show:

```
🎉 Your project is live at https://testgenie-epicroast-new-xxx.vercel.app
```

Copy this URL - this is your live application!

---

## 🧪 Test Your Application

### Test Backend Connection First

Before testing the frontend, verify backend is working:

```
https://your-railway-url.up.railway.app/api/health
```

Should return:
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

### Test Frontend Application

1. **Open your Vercel URL** in browser

2. **Test GroomRoom:**
   - Click **"GroomRoom"** tab
   - Enter a Jira ticket ID (e.g., `PROJ-1234`)
   - Select mode: **Actionable**
   - Click **"Analyze"**
   - Wait 5-10 seconds for results
   - ✅ Results should appear

3. **Test EpicRoast:**
   - Click **"EpicRoast"** tab
   - Paste some ticket content
   - Select theme: **Medium**
   - Click **"Roast It!"**
   - ✅ Roast should appear

4. **Test TestGenie:**
   - Click **"TestGenie"** tab
   - Paste acceptance criteria
   - Click **"Generate Test Scenarios"**
   - ✅ Test scenarios should appear

### Check Browser Console

- Press **F12** to open Developer Tools
- Go to **"Console"** tab
- Look for any errors
- All API calls should return 200 status

---

## 🐛 Troubleshooting

### Build Failed?

**Error: "Cannot find module"**
- Check that `Root Directory` is set to `frontend`
- Verify `package.json` exists in `frontend/` directory

**Error: "TypeScript errors"**
- Check Vercel build logs
- May need to fix TypeScript errors in code

**Error: "Command failed with exit code 1"**
- Check Node.js version is 18.x or higher
- Verify all dependencies in `package.json`

### Frontend Can't Connect to Backend?

**Error: "Network Error" or "Failed to fetch"**

1. **Check VITE_API_URL:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Verify `VITE_API_URL` is set correctly
   - Must include `/api` at the end
   - Example: `https://xxx.up.railway.app/api`

2. **Test Backend Directly:**
   - Open: `https://your-railway-url.up.railway.app/api/health`
   - Should return JSON response
   - If this fails, backend is not running

3. **Check CORS:**
   - Backend already has CORS enabled
   - Check Railway logs for CORS errors

4. **Redeploy if needed:**
   - If you changed `VITE_API_URL`, redeploy frontend
   - Go to Deployments → Click "..." → "Redeploy"

### API Calls Return 500 Error?

- Check Railway backend logs
- Verify Azure OpenAI credentials in Railway
- Check that all environment variables are set in Railway

---

## 🔄 Update Backend URL (If Changed)

If you need to update the Railway backend URL:

1. **In Vercel Dashboard:**
   - Go to: Project → Settings → Environment Variables
   - Find `VITE_API_URL`
   - Click "Edit"
   - Update to new URL
   - Save

2. **Redeploy:**
   - Go to: Deployments
   - Click latest deployment
   - Click "..." → "Redeploy"
   - Select "Use existing Build Cache" (faster)

---

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ Vercel shows "Deployment Ready"
- ✅ Frontend opens without errors
- ✅ All three tabs are visible (TestGenie, EpicRoast, GroomRoom)
- ✅ Backend health check returns healthy status
- ✅ Can successfully analyze a Jira ticket
- ✅ No errors in browser console
- ✅ API calls complete successfully

---

## 📊 Deployment URLs

Once both are deployed, you'll have:

| Service | URL | Status |
|---------|-----|--------|
| **Frontend (Vercel)** | https://testgenie-epicroast-new-xxx.vercel.app | ⏳ Pending |
| **Backend (Railway)** | https://xxx.up.railway.app | ⏳ Pending |
| **GitHub Repo** | https://github.com/sanakausar356/testgenie-epicroast-new | ✅ Done |

---

## 🚀 Future Updates

To deploy updates:

```powershell
# Make your changes
git add .
git commit -m "Your update message"
git push origin main

# Both Railway and Vercel will auto-deploy!
```

---

## 📞 Need Help?

- Check Vercel build logs: Dashboard → Your Project → Deployments → Latest → "Building"
- Check browser console: Press F12 → Console tab
- Verify backend is working: Test `/api/health` endpoint
- Review this guide: Read through troubleshooting section

---

**Vercel Dashboard:** https://vercel.com/dashboard

**Next:** Once deployed, test all features and share your live URL! 🎉

