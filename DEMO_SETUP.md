# 🚀 TestGenie & EpicRoast - Demo Setup Guide

## 📋 Prerequisites

### **Required:**
- Python 3.13+ installed
- Node.js 18+ installed
- Git installed
- Azure OpenAI account with API access
- Jira account (optional, for ticket fetching)

### **Optional:**
- Jira API token (for ticket integration)

## 🔑 API Keys Setup

### **1. Azure OpenAI Setup**
1. Go to [Azure OpenAI Studio](https://oai.azure.com/)
2. Create a new deployment or use existing one
3. Get your credentials:
   - **Endpoint**: `https://your-resource.openai.azure.com/`
   - **API Key**: Your Azure OpenAI API key
   - **Deployment Name**: Your model deployment name

### **2. Jira Setup (Optional)**
1. Go to your Jira profile settings
2. Generate an API token
3. Note your Jira URL and username

## 🛠️ Installation Steps

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/yourusername/testgenie-epicroast.git
cd testgenie-epicroast
```

### **Step 2: Environment Configuration**
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your credentials
notepad .env  # or use your preferred editor
```

**Fill in your `.env` file:**
```env
# Azure OpenAI Configuration (REQUIRED)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Jira Integration (OPTIONAL - for ticket fetching)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@domain.com
JIRA_API_TOKEN=your_jira_api_token
```

### **Step 3: Install Dependencies**
```bash
# Install Python dependencies
python -m pip install -r requirements.txt
python -m pip install -r backend/requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..
```

### **Step 4: Start the Application**
```bash
# Option A: Use the startup script (Recommended)
python start_web_app.py

# Option B: Start manually
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### **Step 5: Access the Application**
Open your browser and go to: **http://localhost:3000**

## 🎯 Demo Instructions

### **TestGenie Demo:**
1. **With Jira Ticket**: Enter a ticket number (e.g., `ODCD-33741`)
2. **With Manual Input**: Paste acceptance criteria in the text area
3. Click "Generate Test Scenarios"
4. View comprehensive test scenarios with positive, negative, and edge cases

### **EpicRoast Demo:**
1. **With Jira Ticket**: Enter the same ticket number
2. **With Manual Input**: Paste ticket content to roast
3. Select roast level (Light, Savage, Extra Crispy)
4. Choose theme (Default, Pirate, Shakespeare, Gen Z)
5. Click "Generate Epic Roast"
6. Enjoy the humorous but insightful roast!

### **Export & Share:**
- **Copy**: Copy results to clipboard
- **Download**: Save as markdown file
- **Teams**: Share formatted content to Teams

## 🔧 Troubleshooting

### **Common Issues:**

**1. "Module not found" errors:**
```bash
# Reinstall dependencies
python -m pip install -r requirements.txt
cd frontend && npm install
```

**2. "Azure OpenAI configuration missing":**
- Check your `.env` file exists and has correct values
- Verify API key and endpoint are correct

**3. "Jira connection failed":**
- Verify Jira credentials in `.env` file
- Check if ticket exists and you have access

**4. "Port already in use":**
```bash
# Kill processes on ports 3000 and 5000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different ports in vite.config.ts and app.py
```

**5. "Frontend not loading":**
```bash
# Check if backend is running on port 5000
# Check browser console for errors
# Verify proxy configuration in vite.config.ts
```

## 📱 Demo Tips

### **For Live Demo:**
1. **Prepare Test Data**: Have a few Jira ticket numbers ready
2. **Show Both Interfaces**: Demonstrate CLI and web app
3. **Highlight Features**: Show export, sharing, and error handling
4. **Use Real Examples**: Use actual team tickets for authenticity

### **For Video Demo:**
1. **Screen Recording**: Record the entire process from setup to usage
2. **Show Error Handling**: Demonstrate what happens with invalid input
3. **Compare Results**: Show before/after of ticket quality improvement
4. **Highlight Speed**: Emphasize the 10-second generation time

## 🌐 Deployment Options

### **Quick Demo Deployment:**
```bash
# Deploy to Vercel (Free)
npm install -g vercel
cd frontend && vercel
cd ../backend && vercel
```

### **Local Network Sharing:**
```bash
# Make accessible on local network
python -m http.server 8000 --bind 0.0.0.0
# Share your IP address with others
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check the browser console and terminal for error messages

## 🎉 Success Indicators

You know it's working when:
- ✅ Web app loads at http://localhost:3000
- ✅ Backend responds at http://localhost:5000/api/health
- ✅ TestGenie generates test scenarios in < 10 seconds
- ✅ EpicRoast generates humorous roasts
- ✅ Export and copy functions work
- ✅ Jira integration fetches ticket details (if configured)

---

**Happy Demo-ing! 🚀✨** 