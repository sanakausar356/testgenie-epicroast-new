# ✅ Environment Variables Checklist

**Railway Project:** giving-determination  
**Project URL:** https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47

---

## 📋 Instructions

1. Open your Railway project (link above)
2. Click on your service: **giving-determination**
3. Go to **"Variables"** tab
4. Click **"New Variable"** for each item below
5. Check off each variable as you add it

---

## 🔑 Azure OpenAI Variables (REQUIRED)

### [ ] AZURE_OPENAI_ENDPOINT
```
Name: AZURE_OPENAI_ENDPOINT
Value: https://YOUR-RESOURCE.openai.azure.com/
```
⚠️ Must end with `/`  
ℹ️ Find at: Azure Portal → Your OpenAI Resource → Keys and Endpoint

---

### [ ] AZURE_OPENAI_API_KEY
```
Name: AZURE_OPENAI_API_KEY
Value: YOUR_API_KEY_HERE
```
⚠️ This is a long alphanumeric string  
ℹ️ Find at: Azure Portal → Your OpenAI Resource → Keys and Endpoint

---

### [ ] AZURE_OPENAI_DEPLOYMENT_NAME
```
Name: AZURE_OPENAI_DEPLOYMENT_NAME
Value: YOUR_DEPLOYMENT_NAME
```
⚠️ This is your model deployment name (e.g., gpt-4, gpt-35-turbo)  
ℹ️ Find at: Azure OpenAI Studio → Deployments

---

### [ ] AZURE_OPENAI_API_VERSION
```
Name: AZURE_OPENAI_API_VERSION
Value: 2024-12-01-preview
```
✅ Use exactly as shown (no changes needed)

---

## 📋 Jira Variables (OPTIONAL - Skip if not using Jira)

### [ ] JIRA_URL
```
Name: JIRA_URL
Value: https://your-domain.atlassian.net
```
⚠️ NO trailing slash  
Example: `https://mycompany.atlassian.net`

---

### [ ] JIRA_USERNAME
```
Name: JIRA_USERNAME
Value: your.email@example.com
```
ℹ️ Your Jira account email address

---

### [ ] JIRA_API_TOKEN
```
Name: JIRA_API_TOKEN
Value: YOUR_JIRA_TOKEN
```
ℹ️ Create at: https://id.atlassian.com/manage-profile/security/api-tokens

---

## ⚙️ Configuration Variables (REQUIRED)

### [ ] FLASK_ENV
```
Name: FLASK_ENV
Value: production
```
✅ Use exactly as shown

---

### [ ] PORT
```
Name: PORT
Value: 8080
```
✅ Use exactly as shown

---

### [ ] PYTHONDONTWRITEBYTECODE
```
Name: PYTHONDONTWRITEBYTECODE
Value: 1
```
✅ Use exactly as shown

---

### [ ] PYTHONIOENCODING
```
Name: PYTHONIOENCODING
Value: utf-8
```
✅ Use exactly as shown

---

## 📊 Summary

**Minimum Required:** 8 variables  
**With Jira:** 11 variables  
**Current Progress:** 0/8 (or 0/11)

### Required Variables (Must Complete):
- [ ] AZURE_OPENAI_ENDPOINT
- [ ] AZURE_OPENAI_API_KEY
- [ ] AZURE_OPENAI_DEPLOYMENT_NAME
- [ ] AZURE_OPENAI_API_VERSION
- [ ] FLASK_ENV
- [ ] PORT
- [ ] PYTHONDONTWRITEBYTECODE
- [ ] PYTHONIOENCODING

### Optional Variables (For Jira):
- [ ] JIRA_URL
- [ ] JIRA_USERNAME
- [ ] JIRA_API_TOKEN

---

## ⚠️ Common Mistakes to Avoid

1. ❌ Adding quotes around values  
   ✅ Correct: `FLASK_ENV=production`  
   ❌ Wrong: `FLASK_ENV="production"`

2. ❌ Forgetting slash on Azure endpoint  
   ✅ Correct: `https://xxx.openai.azure.com/`  
   ❌ Wrong: `https://xxx.openai.azure.com`

3. ❌ Adding slash to Jira URL  
   ✅ Correct: `https://company.atlassian.net`  
   ❌ Wrong: `https://company.atlassian.net/`

4. ❌ Wrong variable name capitalization  
   ✅ Correct: `AZURE_OPENAI_ENDPOINT`  
   ❌ Wrong: `azure_openai_endpoint`

---

## 🧪 After Adding Variables

### [ ] Wait for Railway to Redeploy
- Railway automatically redeploys when variables change
- Monitor the **"Deployments"** tab
- Wait for ✅ "Deploy successful"

### [ ] Get Your Backend URL
1. Go to **"Settings"** tab
2. Find **"Domains"** section
3. Copy URL (e.g., `https://giving-determination-production-xxx.up.railway.app`)
4. Save this URL - needed for Vercel!

### [ ] Test Health Endpoint
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

### [ ] All Tests Pass
- [ ] Health endpoint returns 200 OK
- [ ] Response shows "healthy" status
- [ ] All services show `true` (or Jira shows `false` if not configured)

---

## ✅ Once Complete

When all variables are added and tests pass:

1. ✅ Mark this checklist as complete
2. 📋 Copy your Railway backend URL
3. ➡️ Proceed to Vercel frontend deployment
4. 📄 See: `VERCEL_DEPLOYMENT_STEPS.md`

---

**Railway Project:** https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47  
**Detailed Reference:** See `RAILWAY_ENV_VARIABLES.txt` for copy-paste format

---

**Good luck! Let me know when you're done and I'll help with Vercel deployment!** 🚀

