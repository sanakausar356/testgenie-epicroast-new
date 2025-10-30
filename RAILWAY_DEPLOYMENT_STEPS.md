# 🚂 Railway Deployment Steps

## Your Railway Project
**Project URL:** https://railway.com/project/b6141a0a-f01c-4f0a-8070-5de5a912a793

## Your GitHub Repository  
**Repo URL:** https://github.com/sanakausar356/testgenie-epicroast-new

---

## Step-by-Step Deployment

### 1️⃣ Connect GitHub Repository to Railway

In your Railway project (should be open in browser):

1. Click **"+ New"** or **"New Service"** button
2. Select **"GitHub Repo"**
3. If prompted, authorize Railway to access your GitHub
4. Find and select: **`sanakausar356/testgenie-epicroast-new`**
5. Click **"Add variables"** or continue to configure

### 2️⃣ Configure Build Settings (Auto-detected)

Railway should automatically detect:
- **Root Directory:** `/` (root of repo)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

If not auto-detected, Railway will use the `railway.json` and `nixpacks.toml` files we created.

### 3️⃣ Add Environment Variables

Click on your service, then go to **"Variables"** tab and add these:

#### Required Variables:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

#### Optional Variables (for Jira integration):

```bash
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
```

#### Configuration Variables:

```bash
FLASK_ENV=production
PORT=8080
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

### 4️⃣ Deploy

1. After adding variables, Railway will automatically start deploying
2. Monitor the **"Deployments"** tab
3. Wait 3-5 minutes for build to complete
4. Look for:
   - ✅ **"Build successful"**
   - ✅ **"Deploy successful"**

### 5️⃣ Get Your Backend URL

Once deployed:

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** or **"Domains"** section
3. You'll see a URL like: `https://testgenie-production-xxxx.up.railway.app`
4. **COPY THIS URL** - you'll need it for Vercel!

### 6️⃣ Test Your Backend

Open in browser:
```
https://your-railway-url.up.railway.app/api/health
```

Expected response:
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

---

## 🔍 Environment Variables Checklist

Use this checklist to ensure all required variables are set:

### Azure OpenAI (Required):
- [ ] `AZURE_OPENAI_ENDPOINT`
- [ ] `AZURE_OPENAI_API_KEY`
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME`
- [ ] `AZURE_OPENAI_API_VERSION`

### Jira (Optional):
- [ ] `JIRA_URL`
- [ ] `JIRA_USERNAME`
- [ ] `JIRA_API_TOKEN`

### Configuration:
- [ ] `FLASK_ENV`
- [ ] `PORT`
- [ ] `PYTHONDONTWRITEBYTECODE`
- [ ] `PYTHONIOENCODING`

---

## 🐛 Troubleshooting

### Build Failed?
- Check the **"Logs"** tab for error messages
- Verify all environment variables are set
- Ensure `requirements.txt` is in the root directory

### Deploy Failed?
- Check for import errors in logs
- Verify Azure OpenAI credentials are valid
- Ensure all required Python packages are in `requirements.txt`

### Service Won't Start?
- Check the start command is correct
- Verify `PORT` environment variable is set
- Check logs for application errors

---

## ✅ Once Backend is Deployed

**Save your Railway backend URL!**

You'll need it for Vercel frontend deployment in the next step.

Example URL format:
```
https://testgenie-production-b6141a0a.up.railway.app
```

---

## 📝 Next Steps

After Railway backend is deployed:

1. ✅ Test backend health endpoint
2. ✅ Copy backend URL
3. ➡️ Deploy frontend to Vercel (see `VERCEL_DEPLOYMENT_STEPS.md`)

---

**Railway Project:** https://railway.com/project/b6141a0a-f01c-4f0a-8070-5de5a912a793

**GitHub Repo:** https://github.com/sanakausar356/testgenie-epicroast-new

