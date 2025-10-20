📄 TestGenie & EpicRoast Vibathon Product Requirements Document (PRD)

🎯 Agent Name:

TestGenie & EpicRoast

🚀 Description:

TestGenie & EpicRoast is a dual-purpose AI-powered web application that combines serious test scenario generation with humorous Jira ticket roasting. TestGenie generates comprehensive test scenarios from acceptance criteria using Azure OpenAI, while EpicRoast provides entertaining but insightful critiques of Jira tickets. The application features both command-line and modern web interfaces, with seamless Jira integration for direct ticket fetching.

🌟 Benefits:

• **Accelerated Test Planning** – Generates comprehensive test scenarios in seconds, reducing manual effort by 80%
• **Improved Ticket Quality** – Humorous roasts encourage better ticket writing and reduce vagueness
• **Team Collaboration** – Shared web interface enables collaborative test planning and backlog grooming
• **Jira Integration** – Direct ticket fetching eliminates copy-paste and ensures accuracy
• **Cross-Platform Accessibility** – Works on desktop, tablet, and mobile browsers
• **Export & Sharing** – Multiple export formats and Teams integration for easy sharing

💻 User Interface:

**Web Application (Primary Interface):**
- **Split-Panel Layout**: TestGenie on left, EpicRoast on right
- **Shared Ticket Input**: Single Jira ticket number field for both tools
- **Modern Design**: Clean, responsive interface with Tailwind CSS styling
- **Real-Time Feedback**: Loading animations, error handling, and success states
- **Export Options**: Copy to clipboard, download as markdown, share to Teams

**Command-Line Interface (Alternative):**
- **Interactive Prompts**: Rich terminal interface with color-coded output
- **File Input/Output**: Support for reading from files and exporting results
- **Jira Integration**: Direct ticket fetching via `--ticket` parameter

⚙️ How It Works:

**TestGenie Process:**
1. User enters Jira ticket number or pastes acceptance criteria
2. System fetches ticket details from Jira API (if ticket number provided)
3. Azure OpenAI processes the input with specialized prompts
4. Generates structured test scenarios including positive, negative, and edge cases
5. Results displayed with export and sharing options

**EpicRoast Process:**
1. User enters Jira ticket number or pastes ticket content
2. System fetches ticket details from Jira API (if ticket number provided)
3. User selects roast level (light, savage, extra crispy) and theme (default, pirate, Shakespeare, Gen Z)
4. Azure OpenAI generates humorous but insightful roast
5. Results displayed with export and sharing options

**Jira Integration:**
1. Authenticates using Jira API token and username
2. Fetches ticket details including summary, description, comments, and metadata
3. Formats ticket information for AI analysis
4. Handles errors gracefully with fallback to manual input

📚 Technology Stack:

**Frontend:**
- React 18 with TypeScript
- Vite for fast development and building
- Tailwind CSS for styling and responsive design
- Lucide React for modern icons
- Headless UI for accessible components

**Backend:**
- Flask 3.0 with Python 3.13
- Flask-CORS for cross-origin requests
- Python-dotenv for environment management
- Rich for terminal output formatting

**AI & APIs:**
- Azure OpenAI (GPT-4o) for text generation
- Jira REST API for ticket fetching
- Custom prompt engineering for specialized outputs

**Development & Deployment:**
- Vite dev server with hot reload
- Flask development server with auto-restart
- Proxy configuration for seamless API communication
- Environment-based configuration management

🎨 UX Considerations:

• **Responsive Design**: Mobile-first approach with adaptive layouts for all screen sizes
• **Loading States**: Smooth animations and progress indicators during AI processing
• **Error Handling**: User-friendly error messages with actionable suggestions
• **Accessibility**: WCAG 2.1 compliance with keyboard navigation and screen reader support
• **Performance**: Fast load times with optimized bundle sizes and lazy loading
• **Dark/Light Theme**: Automatic theme detection with manual toggle option
• **Real-Time Updates**: Live status indicators for API connectivity and service health

✅ Acceptance Criteria:

• **Core Functionality**: Both TestGenie and EpicRoast generate results in ≤ 10 seconds
• **Jira Integration**: Successfully fetches tickets from Jira with proper error handling
• **Web Interface**: Responsive design works on desktop, tablet, and mobile browsers
• **Export Features**: Copy to clipboard, download as markdown, and Teams sharing work correctly
• **Error Resilience**: Graceful handling of API failures, network issues, and invalid input
• **Cross-Browser Compatibility**: Works on Chrome, Firefox, Safari, and Edge
• **Authentication**: Secure handling of API keys and environment variables
• **Documentation**: Comprehensive README with setup, usage, and troubleshooting guides

🚧 Nice-to-Haves (if time allows):

• **User Accounts & History**: Save previous results and user preferences
• **Slack Integration**: Direct sharing to Slack channels with formatted messages
• **Confluence Export**: Generate Confluence-compatible wiki pages from test scenarios
• **Test Case Templates**: Customizable templates for different testing methodologies
• **Analytics Dashboard**: Track usage patterns and popular roast themes
• **Mobile App**: React Native wrapper for native mobile experience
• **Team Collaboration**: Multi-user sessions with real-time collaboration
• **Advanced Roast Features**: Roast GIF generation and leaderboard of worst tickets
• **Internationalization**: Support for multiple languages and regional humor styles
• **API Rate Limiting**: Intelligent caching and rate limit management
• **Webhook Integration**: Automatic triggering based on Jira ticket updates
• **Custom Themes**: User-defined roast themes and personality types

## 🛠️ Implementation Details

### **Project Structure:**
```
TestGenie/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   └── requirements.txt    # Python dependencies
├── frontend/               # React web application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API communication
│   │   └── styles/         # CSS and styling
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── testgenie/              # TestGenie CLI package
├── epicroast/              # EpicRoast CLI package
├── jira_integration.py     # Jira API integration
└── start_web_app.py        # Development startup script
```

### **Environment Configuration:**
```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Jira Integration (Optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@domain.com
JIRA_API_TOKEN=your_jira_api_token
```

### **API Endpoints:**
- `GET /api/health` - Service health check
- `GET /api/jira/ticket/{ticket_number}` - Fetch Jira ticket details
- `POST /api/testgenie/generate` - Generate test scenarios
- `POST /api/epicroast/generate` - Generate epic roast
- `POST /api/teams/share` - Format content for Teams sharing

### **Deployment Options:**
- **Development**: Local development servers with hot reload
- **Production**: Docker containers with nginx reverse proxy
- **Cloud**: Deployable to AWS, Azure, or Google Cloud Platform
- **Serverless**: Convertible to AWS Lambda or Azure Functions

Happy vibing! 🌟😎 