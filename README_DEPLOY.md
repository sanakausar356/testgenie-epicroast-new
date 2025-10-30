# 🚀 TestGenie Auto-Deploy Guide

## Quick Start (3 Minutes)

### Option 1: Auto-Deploy via GitHub Actions ⭐ RECOMMENDED

1. **Push Code to GitHub:**
   ```bash
   git add .
   git commit -m "Setup auto-deploy"
   git push personal deploy-updates-1029-1957
   ```
   
   If HTTPS fails, use:
   ```bash
   git remote set-url personal git@github.com:sanakausar356/testgenie-epicroast-new.git
   git push personal deploy-updates-1029-1957
   ```

2. **Setup GitHub Secrets:**
   - Go to: https://github.com/sanakausar356/testgenie-epicroast-new/settings/secrets/actions
   - Add:
     - `RAILWAY_TOKEN` - Get from https://railway.app/account/tokens
     - `VERCEL_TOKEN` - Get from https://vercel.com/account/tokens
     - `VERCEL_ORG_ID` - From Vercel project settings
     - `VERCEL_PROJECT_ID` - From Vercel project settings

3. **Done!** Now every push auto-deploys! 🎉

---

### Option 2: Manual Deploy (No GitHub Actions needed)

1. **Install CLIs:**
   ```bash
   npm install -g @railway/cli vercel
   ```

2. **Deploy Railway (Backend):**
   ```bash
   cd backend
   railway login
   railway link
   railway up
   ```

3. **Deploy Vercel (Frontend):**
   ```bash
   cd frontend
   vercel login
   vercel --prod
   ```

---

### Option 3: One-Click Scripts (Windows)

Just double-click:
- **AUTO_DEPLOY.bat** - Push to GitHub (triggers auto-deploy)
- **MANUAL_DEPLOY.bat** - Deploy directly via CLI
- **COMPLETE_SETUP.bat** - Full setup wizard

---

## Current Repository

🔗 **GitHub:** https://github.com/sanakausar356/testgenie-epicroast-new

### Project Structure:
- **Backend:** `backend/` (Railway)
- **Frontend:** `frontend/` (Vercel)
- **Auto-deploy:** `.github/workflows/deploy.yml`

---

## Troubleshooting

### Push fails with "CONNECT tunnel failed, response 404"
**Solution:** Network/proxy issue. Try:
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
git push personal deploy-updates-1029-1957
```

Or use SSH:
```bash
git remote set-url personal git@github.com:sanakausar356/testgenie-epicroast-new.git
git push personal deploy-updates-1029-1957
```

### Railway deployment fails
**Solution:**
1. Make sure `backend/requirements.txt` exists
2. Check Railway environment variables
3. Verify `railway.json` and `Procfile`

### Vercel deployment fails
**Solution:**
1. Check `frontend/package.json`
2. Verify `vercel.json` config
3. Ensure `frontend/dist` builds successfully

---

## Links

- 🔗 GitHub Repo: https://github.com/sanakausar356/testgenie-epicroast-new
- 🚂 Railway Dashboard: https://railway.app
- ▲ Vercel Dashboard: https://vercel.com/dashboard

---

**Need help?** Check `SETUP_SECRETS.md` for detailed secret setup.

