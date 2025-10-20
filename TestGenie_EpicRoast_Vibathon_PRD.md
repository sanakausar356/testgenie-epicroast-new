# TestGenie & EpicRoast Vibathon PRD

## 🎯 **Agent Name:** EpicRoast 🤖🔥 & 🧙‍♂️ TestGenie

## 🚀 **Description:**
EpicRoast & TestGenie is a dual-purpose AI-powered web application combining entertaining Jira ticket critiques with comprehensive test scenario generation. EpicRoast provides humorous yet insightful feedback on Jira tickets, while TestGenie leverages Azure OpenAI to generate detailed test scenarios directly from acceptance criteria. It includes command-line and web interfaces with seamless Jira integration for ticket fetching.

## 🌟 **Benefits:**
- **Improved Ticket Quality:** Humorous critiques encourage clearer ticket writing
- **Accelerated Test Planning:** Generates test scenarios quickly, reducing manual effort by 80%
- **Enhanced Collaboration:** Shared interface for team planning and backlog refinement
- **Direct Jira Integration:** Ensures accuracy by eliminating manual copy-paste
- **Cross-Platform Accessibility:** Accessible via desktop, tablet, and mobile browsers
- **Export & Sharing Capabilities:** Multiple formats and integration with Teams
- **Local Network Sharing:** Easy sharing with colleagues on the same network

## 💻 **User Interface:**

### **Web Application (Primary Interface):**
- **Split-panel:** EpicRoast (left), TestGenie (right)
- **Responsive design:** Side-by-side on desktop, tabbed on mobile
- **Warm gradient background** with glassmorphism effects
- **Real-time API connection status** indicator
- **Unified Jira ticket input** with validation
- **Modern UI** with emoji branding (🤖 EpicRoast, 🧙‍♂️ TestGenie)
- **Export options:** clipboard, markdown downloads, Teams sharing
- **Real-time feedback,** loading states, and clear error handling

### **Command-Line Interface (Alternative):**
- Rich interactive prompts
- File input/output support
- Jira integration via CLI parameters

## ✅ **Current Implementation Status:**
- ✅ **Web UI** with warm gradient design
- ✅ **Responsive tabbed/mobile layout**
- ✅ **Real-time API health monitoring**
- ✅ **Jira integration** fully functional
- ✅ **Azure OpenAI integration** complete
- ✅ **Local network sharing** capability
- ✅ **Export to clipboard** functionality
- ✅ **Teams sharing** integration
- ✅ **Input validation** with visual feedback
- ✅ **Success animations** and engaging UI elements
- 🚧 **Cloud deployment** (Railway/Vercel) - explored

## ✅ **Implemented Features:**
- **Dual-panel web interface** with responsive design
- **Jira ticket fetching** and validation
- **Azure OpenAI integration** for both tools
- **Real-time loading states** and error handling
- **Clipboard export** functionality
- **Teams sharing** integration
- **Local network accessibility** (10.76.78.101:3000)
- **API health monitoring** with status indicators
- **Input validation** with visual feedback
- **Success animations** and engaging UI elements
- **Warm color scheme** with glassmorphism effects
- **Mobile-responsive** tabbed layout

## ⚙️ **How It Works:**

### **EpicRoast Workflow:**
1. Input Jira ticket number or content
2. Jira API fetches ticket details
3. User selects roast intensity and theme
4. Azure OpenAI generates roast
5. Results displayed with sharing/export options

### **TestGenie Workflow:**
1. Input Jira ticket number or acceptance criteria
2. Jira API fetches ticket details
3. Azure OpenAI generates structured test scenarios (positive, negative, edge cases)
4. Results displayed with sharing/export options

### **Jira Integration:**
- Authenticates via API token
- Fetches detailed ticket info for analysis
- Graceful error handling

## 📚 **Technology Stack:**

### **Frontend:**
- React 18, TypeScript, Vite
- Tailwind CSS
- Lucide React Icons
- Headless UI Components

### **Backend:**
- Flask 2.3+, Python 3.8+
- Flask-CORS, Python-dotenv
- Rich (terminal output)

### **AI & APIs:**
- Azure OpenAI GPT-4o
- Jira REST API
- Specialized prompt engineering

### **Development & Deployment:**
- Vite and Flask dev servers with hot reload
- Proxy for API calls
- Environment-based config management

## 🎨 **UX Considerations:**
- **Responsive, adaptive layout** with mobile-first design
- **Clear loading and error states** with visual feedback
- **WCAG 2.1 compliant** accessibility
- **Optimized performance** and load times
- **Warm gradient theme** with glassmorphism effects
- **Real-time status indicators** for API connectivity
- **Auto-focus** on input fields for better UX
- **Success animations** for user feedback

## ✅ **Acceptance Criteria:**
- **Core functionality** within ≤ 10 seconds
- **Robust Jira integration** and error handling
- **Responsive web design** across all devices
- **Reliable export/sharing** features
- **Comprehensive error resilience**
- **Cross-browser compatibility**
- **Secure API key management**
- **Detailed documentation**
- **Local network accessibility**

## ✅ **Performance Achievements:**
- **API response time:** < 5 seconds
- **UI load time:** < 2 seconds
- **Cross-browser compatibility:** Chrome, Firefox, Safari, Edge
- **Mobile responsiveness:** iOS Safari, Android Chrome
- **Network accessibility:** Local network sharing enabled

## 🚧 **Nice-to-Haves (Optional):**
- User accounts/history
- Slack integration
- Confluence export
- Custom test templates
- Analytics dashboard
- Mobile app (React Native)
- Real-time multi-user collaboration
- Advanced roast features (GIFs, leaderboard)
- Multi-language support
- API caching/rate-limiting
- Webhook integrations
- Custom roast themes
- Dark/light theme toggle
- Advanced export formats (PDF, Word)

## 🛠️ **Implementation Details:**

### **Project Structure:**
```
TestGenie/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │  ├── components/
│   │  ├── services/
│   │  └── styles/
│   ├── package.json
│   └── vite.config.ts
├── epicroast/
├── testgenie/
├── jira_integration.py
├── LOCAL_SETUP.md
├── .env
└── README.md
```

### **Environment Configuration:**
```
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email@domain.com
JIRA_API_TOKEN=your_jira_api_token
```

### **API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/jira/ticket/{ticket_number}` - Fetch Jira details
- `POST /api/epicroast/generate` - Generate roast
- `POST /api/testgenie/generate` - Test scenarios
- `POST /api/teams/share` - Share via Teams

### **Deployment:**
- **Development:** Local servers with hot reload
- **Local Network:** Accessible via local IP (10.76.78.101:3000)
- **Production:** Docker, nginx (planned)
- **Cloud deployment:** Railway/Vercel (explored)
- **Serverless compatible** (planned)

## 🎯 **Current Access URLs:**
- **Local:** http://localhost:3000
- **Network:** http://10.76.78.101:3000
- **Backend API:** http://localhost:5000

## 🌟 **Success Metrics:**
- **User Engagement:** Time spent in application
- **Feature Usage:** TestGenie vs EpicRoast usage ratio
- **Export Rate:** Percentage of results exported/shared
- **Error Rate:** API failure and user error rates
- **Performance:** Load times and response times
- **Accessibility:** Cross-device and cross-browser compatibility

---

**Happy vibing! 🌟😎**

**Dan & Sana** 