# 🎯 TestGenie - AI-Powered Jira Ticket Analysis

TestGenie is a comprehensive web application that provides three powerful AI-driven tools for analyzing and improving Jira tickets:

1. **TestGenie** - Generate comprehensive test scenarios from acceptance criteria
2. **EpicRoast** - Get entertaining and insightful ticket quality analysis
3. **GroomRoom** - Professional ticket grooming and analysis

---

## ✨ Features

### TestGenie
- 🧪 Automatic test scenario generation
- ✅ Positive, negative, and edge case coverage
- 📋 Direct Jira ticket integration
- 🎯 Acceptance criteria analysis

### EpicRoast
- 🔥 Humorous ticket quality analysis
- 🎭 Multiple roast themes (gentle, medium, savage)
- 💡 Actionable improvement suggestions
- 🎪 Team-friendly feedback format

### GroomRoom
- 🧹 Professional ticket analysis
- 📊 Multiple analysis modes (Actionable, Insight, Summary)
- 🎨 Figma design integration
- ✨ User story detection and validation
- 📈 Acceptance criteria suggestions
- 🧪 Test scenario generation
- 🚨 Risk assessment and mitigation

---

## 🏗️ Tech Stack

### Frontend
- ⚛️ React 18 with TypeScript
- ⚡ Vite for blazing-fast builds
- 🎨 Tailwind CSS for styling
- 🧩 Lucide React for icons
- 📝 React Markdown for rendering

### Backend
- 🐍 Python 3.11
- 🌶️ Flask web framework
- 🤖 Azure OpenAI integration
- 🔗 Jira REST API integration
- 🎨 Figma API integration (optional)

---

## 🚀 Quick Start

### Local Development

#### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Azure OpenAI account
- Jira account (optional)

#### Backend Setup

```bash
# Navigate to TestGenie directory
cd TestGenie

# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp env.example .env

# Edit .env and add your credentials
# AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, etc.

# Run backend
cd backend
python app.py
```

Backend will run on `http://localhost:5000`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "VITE_API_URL=http://localhost:5000/api" > .env.local

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173`

---

## 🌐 Deployment

### Complete Deployment to Production

This project is configured for deployment to:
- **GitHub** - Version control and code hosting
- **Railway** - Backend hosting (Python/Flask)
- **Vercel** - Frontend hosting (React/Vite)

### Quick Deployment Guide

See [`QUICK_DEPLOY_STEPS.md`](QUICK_DEPLOY_STEPS.md) for a fast 20-minute deployment walkthrough.

Or use the automated script:

```powershell
# Windows PowerShell
.\deploy.ps1
```

### Detailed Deployment Guide

For comprehensive step-by-step instructions with troubleshooting, see [`DEPLOYMENT_INSTRUCTIONS.md`](DEPLOYMENT_INSTRUCTIONS.md).

---

## 📝 Environment Variables

### Backend (.env)

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Jira Integration (Optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_token

# Figma Integration (Optional)
FIGMA_TOKEN=your_figma_token

# Flask Configuration
FLASK_ENV=production
PORT=8080
```

### Frontend (.env.local)

```bash
# API URL (points to backend)
VITE_API_URL=http://localhost:5000/api  # Local development
# or
VITE_API_URL=https://your-backend.up.railway.app/api  # Production
```

---

## 🎮 Usage

### Analyzing a Jira Ticket with GroomRoom

1. Navigate to the **GroomRoom** tab
2. Enter a Jira ticket ID (e.g., `PROJ-1234`)
3. (Optional) Add a Figma link for design analysis
4. Select analysis mode:
   - **Actionable** - Detailed analysis with specific action items
   - **Insight** - Comprehensive insights and observations
   - **Summary** - Quick concise summary
5. Click **"Analyze"**
6. Review the AI-generated analysis

### Generating Test Scenarios with TestGenie

1. Navigate to the **TestGenie** tab
2. Either:
   - Paste acceptance criteria directly, OR
   - Enter a Jira ticket ID
3. Click **"Generate Test Scenarios"**
4. Review generated test cases:
   - ✅ Positive scenarios
   - ❌ Negative scenarios
   - ⚠️ Edge cases

### Roasting a Ticket with EpicRoast

1. Navigate to the **EpicRoast** tab
2. Either:
   - Paste ticket content directly, OR
   - Enter a Jira ticket ID
3. Select roast intensity:
   - 😊 Gentle - Constructive and friendly
   - 😏 Medium - Witty with bite
   - 🔥 Savage - No mercy mode
4. Click **"Roast It!"**
5. Enjoy the roast and improvement suggestions

---

## 📚 API Documentation

### Health Check
```
GET /api/health
```

### Get Jira Ticket
```
GET /api/jira/ticket/<ticket_number>
```

### TestGenie - Generate Test Scenarios
```
POST /api/testgenie/generate
Body: {
  "ticket_number": "PROJ-1234",  // OR
  "acceptance_criteria": "..."
}
```

### EpicRoast - Generate Roast
```
POST /api/epicroast/generate
Body: {
  "ticket_number": "PROJ-1234",  // OR
  "ticket_content": "...",
  "theme": "medium",
  "level": "savage"
}
```

### GroomRoom - Generate Analysis
```
POST /api/groomroom/generate
Body: {
  "ticket_number": "PROJ-1234",  // OR
  "ticket_content": "...",
  "level": "actionable",  // or "insight" or "summary"
  "figma_link": "https://figma.com/..." // optional
}
```

---

## 🏗️ Project Structure

```
TestGenie/
├── backend/              # Flask backend
│   ├── app.py           # Main Flask application
│   ├── requirements.txt # Python dependencies
│   └── Procfile         # Railway deployment config
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── App.tsx      # Main app component
│   ├── package.json     # Node dependencies
│   └── vercel.json      # Vercel deployment config
├── testgenie/           # TestGenie core module
│   ├── core.py          # Test scenario generation
│   └── cli.py           # CLI interface
├── epicroast/           # EpicRoast core module
│   ├── core.py          # Roast generation
│   └── cli.py           # CLI interface
├── groomroom/           # GroomRoom core module
│   ├── core.py          # Ticket analysis
│   └── cli.py           # CLI interface
├── jira_integration.py  # Jira API integration
├── figma_integration.py # Figma API integration
├── requirements.txt     # Root Python dependencies
├── .gitignore          # Git ignore rules
├── railway.json        # Railway configuration
└── nixpacks.toml       # Nixpacks build config
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Backend fails to start
- Check environment variables are set correctly
- Verify Azure OpenAI credentials
- Check Python version (3.11+ required)

**Problem:** Jira integration not working
- Verify Jira credentials
- Check API token hasn't expired
- Ensure Jira URL format is correct

### Frontend Issues

**Problem:** API calls failing
- Verify `VITE_API_URL` is set correctly
- Check backend is running and accessible
- Look for CORS errors in browser console

**Problem:** Build fails
- Verify Node.js version (18+ required)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for TypeScript errors: `npm run build`

---

## 📞 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)
3. Check backend health: `/api/health`
4. Review logs in Railway/Vercel dashboards

---

## 🎉 Acknowledgments

- Built with ❤️ using Azure OpenAI
- Integrated with Jira and Figma APIs
- Deployed on Railway and Vercel

---

## 📊 Status

- ✅ Backend API - Stable
- ✅ Frontend - Stable
- ✅ TestGenie - Working
- ✅ EpicRoast - Working
- ✅ GroomRoom - Working
- ✅ Jira Integration - Working
- ✅ Figma Integration - Working

---

*Last Updated: October 2025*

**Made with ☕ and 🤖 AI**

