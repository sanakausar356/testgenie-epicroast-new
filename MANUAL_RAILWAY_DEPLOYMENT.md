# Manual Railway Deployment Guide

## Current Issue
Railway is not automatically deploying from git pushes. You need to trigger a manual deployment.

## Option 1: Railway Dashboard (Recommended)

1. **Go to Railway Dashboard:**
   - Visit: https://railway.app/dashboard
   - Login to your account

2. **Find Your Project:**
   - Look for project: `craven-worm-production` or similar
   - Click on the project

3. **Trigger Manual Deployment:**
   - Go to the "Deployments" tab
   - Click "Redeploy" on the latest deployment
   - Or click "Deploy" if no deployments exist

4. **Monitor the Build:**
   - Watch the build logs
   - Look for successful completion
   - Note the deployment URL

## Option 2: Railway CLI (If Available)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Navigate to Backend:**
   ```bash
   cd backend
   ```

4. **Deploy:**
   ```bash
   railway up --detach
   ```

## Option 3: Connect GitHub Repository

If Railway isn't connected to your git repository:

1. **In Railway Dashboard:**
   - Go to your project settings
   - Look for "Source" or "Repository" section
   - Connect your GitHub repository
   - Enable automatic deployments

2. **Push to Trigger Deployment:**
   ```bash
   git push origin main
   ```

## Option 4: Manual File Upload

If all else fails, you can manually upload the backend files:

1. **Create a ZIP file** of the `backend` directory
2. **In Railway Dashboard:**
   - Go to your project
   - Look for "Upload" or "Deploy from files" option
   - Upload the ZIP file

## Verification Steps

After deployment:

1. **Check Health Endpoint:**
   ```bash
   curl https://craven-worm-production.up.railway.app/health
   ```

2. **Test GroomRoom API:**
   ```bash
   curl -X POST https://craven-worm-production.up.railway.app/api/groomroom/generate \
     -H "Content-Type: application/json" \
     -d '{"ticket_content": "Test ticket", "level": "updated"}'
   ```

3. **Test Frontend:**
   - Visit: https://summervibe-testgenie-epicroast.vercel.app/
   - Try GroomRoom functionality

## Expected Results

- ✅ Railway build should succeed (no more Nixpacks errors)
- ✅ Backend should be accessible at Railway URL
- ✅ GroomRoom functionality should work without attribute errors
- ✅ Frontend should connect to backend successfully

## Troubleshooting

If deployment still fails:

1. **Check Railway Logs:**
   - Look for specific error messages
   - Check if all dependencies are installing correctly

2. **Verify Environment Variables:**
   - Ensure Azure OpenAI credentials are set
   - Check Jira integration variables if needed

3. **Check File Structure:**
   - Ensure `app.py` is in the root of backend directory
   - Verify `requirements.txt` exists and is correct

## Contact Support

If you continue having issues:
- Check Railway documentation: https://docs.railway.app/
- Contact Railway support through their dashboard
- Verify your Railway plan allows deployments
