# 🚀 Deployment Update Workflow (After Collaborator Access)

## Daily Workflow

### Step 1: Make Changes
- Edit your code files
- Test locally if needed

### Step 2: Stage Changes
```bash
cd C:\Users\IbtasamAli\Downloads\TestGenie\TestGenie
git add .
```

### Step 3: Commit Changes
```bash
git commit -m "Your descriptive message"

# Examples:
# git commit -m "Fixed user story detection"
# git commit -m "Improved AC suggestions quality"
# git commit -m "Added new test scenarios"
```

### Step 4: Push to Admin Repo
```bash
git push admin-origin main

# OR (if you renamed):
git push origin main
```

### Step 5: Wait for Auto-Deploy
- **Frontend (Vercel):** 1-2 minutes
  - URL: https://summervibe-testgenie-epicroast.vercel.app/
- **Backend (Railway):** 2-3 minutes
  - URL: https://backend-production-83c6.up.railway.app/

### Step 6: Verify Deployment
- Open frontend URL
- Test your changes
- ✅ Done!

---

## Quick Commands (Copy-Paste)

```bash
# Complete workflow in one go:
cd C:\Users\IbtasamAli\Downloads\TestGenie\TestGenie
git add .
git commit -m "Your message here"
git push admin-origin main
```

---

## Troubleshooting

### Error: Permission Denied
- **Reason:** Collaborator access not added yet
- **Solution:** Ask admin to add you as collaborator

### Error: Conflicts
```bash
# Pull latest changes first
git pull admin-origin main
# Resolve conflicts
git add .
git commit -m "Resolved conflicts"
git push admin-origin main
```

### Deployment Not Updating
- Check Vercel dashboard: https://vercel.com/dashboard
- Check Railway dashboard: https://railway.app/dashboard
- Look for build errors in logs

