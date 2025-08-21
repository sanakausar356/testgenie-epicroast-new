# GroomRoom - Concise Jira Ticket Refinement Guidance

GroomRoom provides concise refinement guidance for Jira tickets, following specific rules for professional ticket analysis.

## 🔒 Core Rules

- **No Given/When/Then** generation
- **No grooming checklist**, dependencies/blockers, sprint readiness scores, or improvement suggestions
- Keep answers **short**, in **UK spelling**, **bullet-based** where possible
- Output should be **≤ 300 words**

## 🔍 Focus Areas

1. **Ticket Summary** - 1–2 lines of story/bug context
2. **Key Gaps (Acceptance Criteria)** - Call out missing/unclear AC, rephrase vague AC into intent-based statements, or give 1–2 short example AC if missing
3. **Definition of Ready Gaps** - List missing essentials: AC, design links, PO sign-off, data/env/config notes
4. **Questions to Ask** - Short, direct clarifications for PO/Dev/QA to unblock
5. **Test Scenarios (High-Level)** - Happy paths, negative/error cases, risk-based checks, cross-browser/device coverage
6. **ADA / Accessibility (If Applicable)** - Screen reader/ARIA, focus order/keyboard navigation, labelling, contrast

## 📋 Output Format

```
# Groom Analysis

## Ticket Summary
...

## Key Gaps (Acceptance Criteria)
...

## Definition of Ready Gaps
...

## Questions to Ask
...

## Test Scenarios (High-Level)
...

## ADA / Accessibility (If Applicable)
...
```

## 🚀 Usage

### Command Line Interface

```bash
# Analyze ticket content directly
python groomroom/cli.py "As a user, I want to reset my password so that I can access my account"

# Read from file
python groomroom/cli.py --file ticket.txt

# Fetch from Jira (if integration configured)
python groomroom/cli.py --ticket PROJ-123

# Save output to file
python groomroom/cli.py --file ticket.txt --output analysis.md
```

### API Endpoint

```bash
# POST request to concise analysis endpoint
curl -X POST http://localhost:5000/api/groomroom/concise \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_content": "As a user, I want to reset my password so that I can access my account"
  }'
```

### Python API

```python
from groomroom.core import GroomRoom

# Initialize GroomRoom
groomroom = GroomRoom()

# Generate concise analysis
ticket_content = """
Summary: Add password reset functionality

Description:
As a user, I want to reset my password when I forget it, so that I can regain access to my account.

Acceptance Criteria:
- User can click "Forgot Password" link
- User receives email with reset link
"""

analysis = groomroom.generate_concise_groom_analysis(ticket_content)
print(analysis)
```

## 🧪 Testing

Run the test script to verify functionality:

```bash
python test_concise_groomroom.py
```

## ⚙️ Configuration

Ensure the following environment variables are set for Azure OpenAI integration:

```bash
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 📝 Example Output

```
# Groom Analysis

## Ticket Summary
User story for password reset functionality allowing users to regain account access when credentials are forgotten.

## Key Gaps (Acceptance Criteria)
• Missing validation criteria for email format
• No specification for password strength requirements
• Unclear timeout period for reset links
• Missing error handling for invalid/expired links

## Definition of Ready Gaps
• Design mockups for reset flow not provided
• PO sign-off status unclear
• Environment configuration details missing
• Data migration considerations not addressed

## Questions to Ask
• What is the password complexity policy?
• How long should reset links remain valid?
• Should users be notified of successful password changes?
• What happens if user enters incorrect email?

## Test Scenarios (High-Level)
• Happy path: Valid email → reset link → new password set
• Negative: Invalid email format, expired link, weak password
• Risk-based: Concurrent reset attempts, rate limiting
• Cross-browser: Chrome, Firefox, Safari, Edge compatibility

## ADA / Accessibility (If Applicable)
• Screen reader compatibility for form fields
• Keyboard navigation through reset flow
• Clear error messaging for assistive technologies
• Sufficient colour contrast for form elements
```
