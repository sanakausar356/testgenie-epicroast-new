# ⚡ Quick Deploy Commands

**For when you just want the commands, no explanations.**

---

## 🔥 STEP 1: GitHub (5 min)

```bash
# Navigate to project
cd C:\Users\IbtasamAli\Downloads\TestGenie

# Initialize and commit
git init
git add .
git commit -m "Ready for deployment - TestGenie v1.0"

# Create repo on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git
git branch -M main
git push -u origin main
```

**✅ Code on GitHub**

---

## 🚀 STEP 2: Render Backend (5 min)

### In Render Dashboard:
1. New Web Service → Connect GitHub `TestGenie` repo
2. **Settings:**
   ```
   Name: testgenie-backend
   Root Directory: TestGenie
   Build: pip install -r requirements.txt
   Start: gunicorn app:app --bind 0.0.0.0:$PORT
   Instance: Free
   ```

3. **Environment Variables:**
   ```
   PORT=8080
   JIRA_URL=https://your-company.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your_token
   OPENAI_API_KEY=sk-your_key
   FIGMA_TOKEN=figd_your_token
   NO_PROXY=*
   PYTHONDONTWRITEBYTECODE=1
   PYTHONIOENCODING=utf-8
   ```

4. **Deploy** → Copy URL: `https://testgenie-backend.onrender.com`

**✅ Backend Live**

---

## 🌐 STEP 3: Vercel Frontend (5 min)

### In Vercel Dashboard:
1. New Project → Import `TestGenie` repo
2. **Settings:**
   ```
   Framework: Vite
   Root Directory: TestGenie/frontend
   Build: npm run build
   Output: dist
   ```

3. **Environment Variable:**
   ```
   VITE_API_URL=https://testgenie-backend.onrender.com/api
   ```
   *(Replace with YOUR backend URL from Step 2)*

4. **Deploy** → Copy URL: `https://testgenie.vercel.app`

**✅ Frontend Live**

---

## 🧪 STEP 4: Test (2 min)

Open: `https://testgenie.vercel.app`

- Test GroomRoom analysis
- Test EpicRoast
- Test Figma integration

**✅ ALL DONE! 🎉**

---

## 🔄 Future Updates

```bash
# Make changes
git add .
git commit -m "Feature: Added new functionality"
git push origin main

# Auto-deploys to both Render & Vercel (3-5 min)
```

**No manual deployment needed!**

---

## 🆘 Quick Troubleshooting

### Backend Error?
- Check logs: Render Dashboard → Your Service → Logs
- Verify env variables are set

### Frontend Error?
- Check `VITE_API_URL` in Vercel settings
- Test backend: `https://your-backend.onrender.com/api/health`

### Jira Not Working?
- Verify Jira credentials in Render env variables
- Check API token not expired

---

**That's it! For detailed guide, see: `DEPLOYMENT_GUIDE.md`**

