# TestGenie & EpicRoast with GroomRoom 🎯🔥

**TestGenie**: AI-powered test case generation from acceptance criteria  
**EpicRoast**: Humorous but insightful Jira ticket analysis and roasting  
**GroomRoom**: Enhanced ticket grooming and analysis tool

## 🚀 Features

### TestGenie
- Generate comprehensive test scenarios from acceptance criteria
- Support for positive, negative, and edge case testing
- AI-powered analysis using Azure OpenAI

### EpicRoast  
- Roast Jira tickets with humor and insight
- Multiple themes (default, pirate, Shakespeare, Gen Z)
- Identify vagueness, buzzwords, and missing details

### GroomRoom
- Enhanced ticket grooming and analysis
- Dynamic Jira field detection
- Comprehensive ticket improvement suggestions

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.10)
- **AI**: Azure OpenAI GPT models
- **Deployment**: Railway
- **Frontend**: React + TypeScript (planned)

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run the application
python app.py
```

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

## 🔑 Environment Variables

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Jira Configuration (Optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token

# Flask Configuration
FLASK_ENV=production
PORT=8080
```

## 📚 API Endpoints

- `GET /` - API information and status
- `GET /health` - Health check
- `POST /api/groomroom/generate` - Generate GroomRoom analysis
- `POST /api/testgenie/generate` - Generate test cases
- `POST /api/epicroast/roast` - Generate EpicRoast analysis

## 🎯 Use Cases

- **QA Teams**: Generate comprehensive test scenarios
- **Product Teams**: Improve ticket quality through roasting
- **Development Teams**: Better backlog grooming

## 📄 License

MIT License - feel free to use and modify!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with ❤️ for better software development practices