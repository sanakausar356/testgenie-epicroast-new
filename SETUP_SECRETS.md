# Setup GitHub Secrets for Auto-Deploy

## Quick Setup Steps:

### 1. Go to GitHub Repository Settings
Visit: https://github.com/sanakausar356/testgenie-epicroast-new/settings/secrets/actions

### 2. Add These Secrets:

#### Railway Token:
1. Go to: https://railway.app/account/tokens
2. Click "Create Token"
3. Copy the token
4. Add as `RAILWAY_TOKEN` in GitHub Secrets

#### Vercel Tokens:
1. Go to: https://vercel.com/account/tokens
2. Create a new token
3. Add as `VERCEL_TOKEN` in GitHub Secrets

4. Get your Org ID:
   - Go to: https://vercel.com/[your-username]/settings
   - Copy your Org ID
   - Add as `VERCEL_ORG_ID`

5. Get Project ID:
   - Go to your project settings in Vercel
   - Copy Project ID
   - Add as `VERCEL_PROJECT_ID`

### 3. Alternative: Simple Push Method (No GitHub Actions)

If you don't want to use GitHub Actions, you can use:

#### Railway CLI:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

#### Vercel CLI:
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

## Quick Deploy Commands:

### Option 1: Using GitHub Actions (Automatic)
Just run `AUTO_DEPLOY.bat` - It will push to GitHub and trigger auto-deploy

### Option 2: Manual CLI Deploy
Run `MANUAL_DEPLOY.bat` - It will deploy directly using Railway & Vercel CLI

### Option 3: Push Only
```bash
git add .
git commit -m "your message"
git push personal deploy-updates-1029-1957
```

Then manually deploy from Railway/Vercel dashboard.

