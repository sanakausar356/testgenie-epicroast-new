# TestGenie & Epic Roast 🎯🔥

**TestGenie**: A command-line tool that takes acceptance criteria as input and generates high-level test scenarios and sample test cases using Azure OpenAI.

**Epic Roast**: A CLI-based fun tool that roasts Jira tickets using AI. The roast is humorous but insightful—calling out vagueness, lack of clarity, and buzzwords.

## 🚀 Quick Start - Web App

The easiest way to use TestGenie & EpicRoast is through the web interface:

### **Option 1: Automated Setup (Recommended)**
```bash
# Run the automated setup script
python deploy_demo.py
```

### **Option 2: Manual Setup**
```bash
# 1. Install dependencies
python -m pip install -r requirements.txt
python -m pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 2. Configure environment
cp env.example .env
# Edit .env with your Azure OpenAI credentials

# 3. Start the web app
python start_web_app.py
```

Then open your browser to: **http://localhost:3000**

### **🔑 Required API Keys:**
- **Azure OpenAI**: Endpoint, API Key, and Deployment Name
- **Jira** (optional): URL, Username, and API Token for ticket integration

### Web App Features
- **Split-panel interface**: TestGenie on the left, EpicRoast on the right
- **Shared ticket input**: Enter a Jira ticket number once, use it for both tools
- **Modern UI**: Clean, responsive design with loading animations
- **Export options**: Copy to clipboard, download as markdown, share to Teams
- **Real-time feedback**: Live error handling and success messages

### Web App Architecture
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: Flask API with CORS support
- **Integration**: Reuses existing TestGenie/EpicRoast core logic
- **Deployment**: Development server with hot reload

## 🌟 Benefits

### TestGenie
- Speeds up test case design
- Reduces missed edge cases
- Standardises QA process across teams

### Epic Roast
- Makes backlog grooming more fun
- Encourages better ticket writing
- Lightens up serious workflows

## 🚀 Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   ```

## 💻 Usage

### TestGenie Usage
```bash
# Using the main script
python testgenie.py

# Using the package directly
python -m testgenie.cli

# If installed with pip
testgenie

# With Jira ticket number
python testgenie.py --ticket PROJ-123

# From file input
python testgenie.py --input acceptance_criteria.txt

# Export results
python testgenie.py --ticket PROJ-123 --export test_scenarios.md
```

### Epic Roast Usage
```bash
# Basic roast
python epicroast.py

# With Jira ticket number
python epicroast.py --ticket PROJ-123

# With theme and level
python epicroast.py --theme pirate --level extra_crispy

# From file input
python epicroast.py --input sample_jira_ticket.txt

# Export roast to file
python epicroast.py --ticket PROJ-123 --export roast.txt

# Generate multiple roasts
python epicroast.py --rerun

# If installed with pip
epicroast
```

### Export to File
```bash
python testgenie.py --export output.md
```

### Input from File
```bash
python testgenie.py --input acceptance_criteria.txt
```

### Specify Scenario Types
```bash
python testgenie.py --scenarios positive negative edge
```

## 📚 Features

### TestGenie
- **Multiline Input**: Accepts complex acceptance criteria
- **Jira Integration**: Fetch tickets directly by ticket number
- **Structured Output**: Generates numbered test scenarios with sample test cases
- **File Export**: Save results to markdown or text files
- **File Input**: Read acceptance criteria from text files
- **Scenario Types**: Toggle between positive, negative, and edge case scenarios
- **Error Handling**: Graceful handling of poorly written input

### Epic Roast
- **Jira Integration**: Fetch tickets directly by ticket number
- **Multiple Themes**: Default, Pirate, Shakespeare, Gen Z styles
- **Roast Levels**: Light, Savage, Extra Crispy intensity
- **File Input/Output**: Read tickets from files and save roasts
- **Rerun Option**: Generate multiple roasts for the same ticket
- **ASCII Art**: Beautiful terminal interface with emojis
- **Insightful Analysis**: Calls out vagueness, buzzwords, and missing details

## 🎨 Output Format

### TestGenie
The tool generates:
1. **Test Scenarios**: High-level test scenarios with specific test cases
2. **Edge Cases**: Potential edge cases and boundary conditions
3. **Cross Browser/Device Testing**: Browser compatibility and device testing requirements

### Epic Roast
The tool generates:
1. **Epic Roast**: Humorous but insightful roast of the Jira ticket
2. **Key Issues Found**: Specific problems identified in the ticket
3. **Suggestions for Improvement**: Constructive feedback for better tickets

## ⚙️ Configuration

### Azure OpenAI Settings
All Azure OpenAI settings are configured via environment variables in the `.env` file.

### Jira Integration (Optional)
To enable Jira integration, add these variables to your `.env` file:

1. **Get your Jira API token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create a new API token
   - Copy the token

2. **Add to .env file**:
   ```
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your_email@example.com
   JIRA_API_TOKEN=your_jira_api_token_here
   ```

3. **Test Jira connection**:
   ```bash
   python -c "from jira_integration import JiraIntegration; j = JiraIntegration(); print('Jira available:', j.is_available())"
   ```

## 🚧 Nice-to-Haves

### TestGenie
- [x] Export results to markdown
- [x] Support for input from .txt files
- [x] Toggle for scenario types
- [ ] CSV export option
- [ ] Interactive mode with history

### Epic Roast
- [x] Multiple roast themes
- [x] Roast level selection
- [x] File input/output
- [x] Rerun functionality
- [ ] Roast GIF generator
- [ ] Slack integration for "Roast of the Day"
- [ ] Leaderboard of worst-written tickets (fake, for fun) 