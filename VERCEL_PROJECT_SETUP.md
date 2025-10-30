# 🔷 Your Vercel Project Setup

## Your Vercel Project
**URL:** https://vercel.com/newell-dt/testgenie-epicroast-new
**Team:** newell-dt
**Project:** testgenie-epicroast-new

---

## 🔗 Step 1: Connect GitHub Repository

Based on the Vercel page, you need to connect your Git repository:

1. **Click "Connect Git"** button on your Vercel project page

2. **Select GitHub** as the Git provider

3. **Choose your repository:**
   - Repository: `sanakausar356/testgenie-epicroast-new`

4. **Click "Connect"**

---

## ⚙️ Step 2: Configure Deployment Settings

After connecting Git, configure these settings:

### ⚠️ CRITICAL: Root Directory

**Setting:** Root Directory
**Action:** Click "Edit"
**Value:** `frontend`

**This is THE most important setting!**

---

### ✅ Framework & Build Settings

These should auto-detect:

```
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Node.js Version: 18.x
```

---

### 🔑 Environment Variables

Click "Environment Variables" section

**Add this variable:**

**Name:**
```
VITE_API_URL
```

**Value:**
```
https://web-production-8415f.up.railway.app/api
```

**Critical Points:**
- ✅ Includes `https://`
- ✅ Ends with `/api`
- ✅ NO trailing slash after `/api`

---

## 🚀 Step 3: Deploy

1. **Review all settings:**
   - Root Directory = `frontend` ✓
   - VITE_API_URL added ✓
   - Framework = Vite ✓

2. **Click "Deploy"** button

3. **Wait 2-3 minutes** for build to complete

---

## 📊 Your Configuration Summary

| Setting | Value |
|---------|-------|
| **Vercel Team** | newell-dt |
| **Project Name** | testgenie-epicroast-new |
| **GitHub Repo** | sanakausar356/testgenie-epicroast-new |
| **Root Directory** | `frontend` ⚠️ CRITICAL |
| **Framework** | Vite |
| **VITE_API_URL** | `https://web-production-8415f.up.railway.app/api` |

---

## 🌐 After Deployment

Your app will be available at:
```
https://testgenie-epicroast-new-[random].vercel.app
```

Or if you have a custom domain configured:
```
https://[your-domain].vercel.app
```

---

## 🧪 Testing Your Deployment

### 1. Open Your Vercel URL

Visit the URL Vercel provides after deployment

### 2. Test GroomRoom

1. Click **"GroomRoom"** tab
2. Enter ticket: `ODCD-34544`
3. Click **"Analyze"**
4. Should see analysis in 5-10 seconds

### 3. Check Console

Press **F12** → Console tab
- Should see no errors
- API calls should return 200 status

---

## 🐛 Troubleshooting

### Build Fails?

**Check:**
1. Root Directory is set to `frontend`
2. Go to Settings → General → Root Directory
3. Set to `frontend` and redeploy

### Can't Connect to Backend?

**Check:**
1. Settings → Environment Variables
2. Verify `VITE_API_URL` = `https://web-production-8415f.up.railway.app/api`
3. Must end with `/api`

### Need to Redeploy?

1. Go to **"Deployments"** tab
2. Click latest deployment
3. Click **"..."** menu
4. Click **"Redeploy"**

---

## 📋 Deployment Checklist

Before deploying:

- [ ] GitHub repository connected
- [ ] Root Directory set to `frontend` ⚠️
- [ ] Framework detected as Vite
- [ ] VITE_API_URL environment variable added
- [ ] Backend URL is correct (ends with `/api`)
- [ ] No trailing slash after `/api`

---

## 🔗 Your URLs

**GitHub:** https://github.com/sanakausar356/testgenie-epicroast-new

**Railway Backend:**
- Base: https://web-production-8415f.up.railway.app
- Health: https://web-production-8415f.up.railway.app/api/health

**Vercel Project:** https://vercel.com/newell-dt/testgenie-epicroast-new

**Vercel App:** (will be provided after deployment)

---

## ✅ Next Steps

1. ✅ Click "Connect Git" in Vercel
2. ✅ Select your GitHub repository
3. ✅ Set Root Directory to `frontend`
4. ✅ Add VITE_API_URL environment variable
5. ✅ Click Deploy
6. ⏰ Wait 2-3 minutes
7. 📢 Share your deployed URL

---

**Vercel Team:** newell-dt
**Ready to deploy!** 🚀

