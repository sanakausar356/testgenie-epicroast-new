# Environment Variables Setup

## Required Environment Variables

Create a `.env` file in the `TestGenie` directory with the following variables:

### Flask Configuration
```
PORT=8080
```

### Jira Configuration (Required)
```
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token_here
```

**How to get Jira API Token:**
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "TestGenie")
4. Copy the token

### OpenAI Configuration (Required)
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**How to get OpenAI API Key:**
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Figma Configuration (Optional)
```
FIGMA_TOKEN=figd_your_figma_token_here
```

**How to get Figma Token:**
1. Go to: https://www.figma.com/developers/api#access-tokens
2. Generate a personal access token
3. Copy the token (starts with `figd_`)

### Network Configuration (Optional)
```
NO_PROXY=*
HTTP_PROXY=
HTTPS_PROXY=
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
```

## For Production Deployment

When deploying to Render, Vercel, or other cloud platforms, add these environment variables in their dashboard instead of creating a `.env` file.

