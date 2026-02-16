# Gmail MCP Server Setup Guide

## Overview
Gmail MCP (Model Context Protocol) server allows Claude Code to directly send emails through your Gmail account. This enables your AI Employee to execute email-related tasks autonomously.

## Prerequisites
- Node.js (v18 or higher)
- Gmail account with 2FA enabled
- Google Cloud Project with Gmail API enabled

## Step 1: Install Gmail MCP Server

```bash
# Install the Gmail MCP server globally
npm install -g @modelcontextprotocol/server-gmail

# Or install locally in your project
npm install @modelcontextprotocol/server-gmail
```

## Step 2: Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as application type
4. Download the credentials JSON file
5. Save it as `gmail_credentials.json` in your project root

## Step 4: Configure Claude Code MCP Settings

Create or update `.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-gmail"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_REDIRECT_URI": "http://localhost:3000/oauth2callback"
      }
    }
  }
}
```

## Step 5: Authenticate Gmail

First time you run the watcher, it will:
1. Open a browser window for Gmail authentication
2. Ask you to grant permissions
3. Save the refresh token for future use

```bash
# Run the watcher to trigger authentication
python src/watcher.py
```

## Step 6: Verify Installation

Test if Gmail MCP is working:

```bash
# In Claude Code terminal
claude mcp list
```

You should see "gmail" in the list of available MCP servers.

## Available Gmail MCP Tools

Once configured, Claude Code can use these tools:

1. **send_email**: Send emails with subject, body, and recipients
2. **read_emails**: Read recent emails from inbox
3. **search_emails**: Search emails by query
4. **get_email**: Get specific email by ID
5. **create_draft**: Create email draft without sending

## Usage in Skills

Example of sending email from a skill:

```markdown
Use the gmail MCP tool to send an email:
- To: client@example.com
- Subject: Invoice Follow-up
- Body: [Generated content]
```

## Security Notes

- Never commit `gmail_credentials.json` to git
- Add it to `.gitignore`
- Refresh tokens are stored securely by MCP
- Revoke access anytime from Google Account settings

## Troubleshooting

**Error: "Invalid credentials"**
- Re-download credentials from Google Cloud Console
- Ensure OAuth consent screen is configured

**Error: "Gmail API not enabled"**
- Go to Google Cloud Console
- Enable Gmail API for your project

**Error: "Token expired"**
- Delete stored tokens
- Re-authenticate by running watcher

## Alternative: Using App Passwords (Simpler but Less Secure)

If you don't want to set up OAuth:

1. Enable 2FA on your Gmail account
2. Generate an App Password
3. Use SMTP directly in Python:

```python
import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your-email@gmail.com'
    msg['To'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('your-email@gmail.com', 'your-app-password')
        smtp.send_message(msg)
```

## Next Steps

After setup:
1. Test sending a sample email
2. Configure the watcher to monitor Gmail inbox
3. Create execution skill to send emails from approved plans
4. Update dashboard to track sent emails

## Support

For issues with Gmail MCP:
- GitHub: https://github.com/modelcontextprotocol/servers
- Documentation: https://modelcontextprotocol.io/

For this AI Employee project:
- Check logs in `Logs/` folder
- Review `Dashboard.md` for system status
