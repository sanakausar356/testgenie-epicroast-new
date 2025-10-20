# 🐙 GitHub Repository Setup Guide

## 📋 Steps to Create Your GitHub Repository

### **Step 1: Create a New Repository**
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `testgenie-epicroast`
   - **Description**: `AI-Powered Test Scenario Generator & Jira Ticket Roaster`
   - **Visibility**: Public (for demo) or Private
   - **Initialize with**: Don't initialize (we'll push existing code)

### **Step 2: Push Your Code**
```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: TestGenie & EpicRoast web application"

# Add remote repository (replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/testgenie-epicroast.git

# Push to GitHub
git push -u origin main
```

### **Step 3: Update Demo Links**
After pushing to GitHub, update these files with your repository URL:

1. **DEMO_SETUP.md**: Update the clone URL
2. **Pitching Document**: Add your GitHub repository link
3. **README.md**: Add repository badges and links

## 🔒 Security Considerations

### **Environment Variables**
- ✅ **DO** include `env.example` in the repository
- ❌ **DON'T** include `.env` file (it's in .gitignore)
- ✅ **DO** document required environment variables

### **API Keys**
- ❌ **NEVER** commit API keys to the repository
- ✅ **DO** use environment variables for all sensitive data
- ✅ **DO** provide clear setup instructions

## 📝 Repository Structure
```
testgenie-epicroast/
├── README.md                 # Main documentation
├── DEMO_SETUP.md            # Detailed setup guide
├── GITHUB_SETUP.md          # This file
├── PRD_TestGenie_EpicRoast.md # Product requirements
├── deploy_demo.py           # Automated setup script
├── start_web_app.py         # Development startup script
├── requirements.txt         # Python dependencies
├── env.example              # Environment template
├── .gitignore               # Git ignore rules
├── backend/                 # Flask API server
├── frontend/                # React web application
├── testgenie/               # TestGenie CLI package
├── epicroast/               # EpicRoast CLI package
└── jira_integration.py      # Jira API integration
```

## 🚀 Deployment Options

### **Option 1: Vercel (Recommended)**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel

# Deploy backend (separate)
cd ../backend
vercel
```

### **Option 2: Netlify + Railway**
- **Frontend**: Connect GitHub repo to Netlify
- **Backend**: Deploy to Railway with environment variables

### **Option 3: GitHub Pages (Frontend Only)**
```bash
# Build frontend
cd frontend
npm run build

# Deploy to GitHub Pages
# (Configure in repository settings)
```

## 📋 Demo Repository Checklist

- [ ] Repository created on GitHub
- [ ] Code pushed to repository
- [ ] README.md updated with setup instructions
- [ ] DEMO_SETUP.md included
- [ ] Environment variables documented
- [ ] API key requirements clearly stated
- [ ] Demo links updated
- [ ] Repository is public (for demo purposes)
- [ ] License file added (optional)

## 🎯 Demo Links to Include

### **In Your Pitching Document:**
```markdown
**📚 GitHub Repo:** https://github.com/YOUR_USERNAME/testgenie-epicroast

**🚀 Live Demo:** https://your-deployed-url.vercel.app

**📖 Setup Guide:** https://github.com/YOUR_USERNAME/testgenie-epicroast/blob/main/DEMO_SETUP.md
```

### **In README.md:**
```markdown
## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/testgenie-epicroast.git
cd testgenie-epicroast
python deploy_demo.py
```
```

## 🔧 Troubleshooting

### **Common Issues:**

**1. "Repository not found":**
- Check the repository URL is correct
- Ensure the repository is public (for demo)
- Verify your GitHub username

**2. "Permission denied":**
- Check your GitHub authentication
- Use personal access token if needed
- Verify repository permissions

**3. "Large file error":**
- Check .gitignore includes node_modules and .env
- Use git-lfs for large files if needed

---

**🎉 Your repository is ready for demo! 🚀** 