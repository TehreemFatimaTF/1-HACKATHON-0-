# 🔐 Credentials Setup Guide

## ⚠️ IMPORTANT: Before Making Code Public

This project contains sensitive credentials that MUST be removed before publishing to GitHub or any public repository.

## 📋 Sensitive Files to Keep Private

### 1. Environment Variables
- **File**: `.env`
- **Contains**: LinkedIn, Gmail, Twitter, Facebook, Instagram, Odoo credentials
- **Action**: Already in `.gitignore` ✅
- **Setup**: Copy `.env.example` to `.env` and fill in your credentials

### 2. Google OAuth Credentials
- **Files**:
  - `credentials.json`
  - `client_secret_*.json`
  - `token.pickle`
- **Contains**: Google OAuth client ID, client secret, access tokens
- **Action**: Already in `.gitignore` ✅
- **Setup**: Download from Google Cloud Console

### 3. Session Files
- **Files**:
  - `linkedin_session.json`
  - `*_session.json`
- **Contains**: Active session cookies and tokens
- **Action**: Now added to `.gitignore` ✅
- **Setup**: Generated automatically on first login

### 4. MCP Configuration
- **Files**:
  - `.claude/mcp.json`
  - `.claude/config.json`
- **Contains**: API credentials for MCP servers
- **Action**: Already in `.gitignore` ✅
- **Setup**: Configure after installing MCP servers

## 🚀 Setup Instructions for New Users

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd Ai_Employee_vault
```

### Step 2: Create Environment File
```bash
cp .env.example .env
```

### Step 3: Configure Credentials

#### LinkedIn
1. Add your LinkedIn email and password to `.env`
2. First run will create `linkedin_session.json` automatically

#### Gmail
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download as `client_secret_*.json`
6. Add Gmail email and app password to `.env`

#### Twitter/X
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app
3. Get API keys and tokens
4. Add to `.env`

#### Facebook & Instagram
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app
3. Get app ID, secret, and page access token
4. Add to `.env`

#### Odoo
1. Install Odoo locally or use cloud instance
2. Get database name, username, password
3. Add to `.env`

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 5: Run Setup Wizard (Optional)
```bash
python Scripts/setup_wizard.py
```

## 🔍 Verify Before Publishing

Run this checklist before making your code public:

- [ ] `.env` file is NOT committed
- [ ] `credentials.json` is NOT committed
- [ ] `client_secret_*.json` files are NOT committed
- [ ] `token.pickle` is NOT committed
- [ ] `linkedin_session.json` is NOT committed
- [ ] `.claude/mcp.json` is NOT committed
- [ ] `.claude/config.json` is NOT committed
- [ ] No hardcoded passwords in Python files
- [ ] `.env.example` is committed (without real credentials)
- [ ] This guide is committed

## 🛡️ Security Best Practices

1. **Never commit real credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate credentials** if accidentally exposed
4. **Use app-specific passwords** instead of main passwords
5. **Enable 2FA** on all accounts
6. **Review `.gitignore`** before each commit

## 📞 Support

If you accidentally committed credentials:
1. Immediately rotate/revoke them
2. Use `git filter-branch` or BFG Repo-Cleaner to remove from history
3. Force push to remote (if already pushed)

## 🔗 Useful Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Twitter Developer Portal](https://developer.twitter.com/)
- [Facebook Developers](https://developers.facebook.com/)
- [LinkedIn API](https://www.linkedin.com/developers/)
- [Odoo Documentation](https://www.odoo.com/documentation/)
