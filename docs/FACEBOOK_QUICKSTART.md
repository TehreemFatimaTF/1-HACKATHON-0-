# Facebook & Instagram Watcher - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install python-dotenv requests
```

### Step 2: Setup Credentials

Run the interactive setup wizard:

```bash
python setup_credentials.py
```

The wizard will guide you through:
- Entering your Facebook Page Access Token
- Entering your Facebook Page ID
- Optionally configuring Instagram
- Creating your `.env` file

**Don't have credentials yet?** See [Full Setup Guide](FACEBOOK_INSTAGRAM_SETUP.md)

### Step 3: Test Integration

```bash
python test_facebook_integration.py
```

This will verify your credentials and test API connections.

### Step 4: Run the Watcher

**Option A: Facebook Watcher Only**
```bash
cd src
python watcher_facebook.py
```

**Option B: All Watchers (including Facebook)**
```bash
cd src
python watcher.py
```

**Option C: Demo Mode**
```bash
python demo_facebook_watcher.py
```

---

## 📋 What You Need

### Facebook Requirements
- Facebook Business Account
- Facebook Page (for posting)
- Facebook Developer App
- Page Access Token
- Page ID

### Instagram Requirements (Optional)
- Instagram Business Account
- Linked to your Facebook Page
- Instagram Business Account ID
- Same Page Access Token as Facebook

---

## 🎯 Features

### Facebook Watcher Capabilities

1. **Content Monitoring**
   - Monitors Facebook trends and business insights
   - Creates inbox files for review
   - Tracks engagement potential

2. **Automated Posting**
   - Posts to Facebook pages
   - Posts to Instagram (with images)
   - Multi-platform broadcasting

3. **Summary Generation**
   - Tracks all posted content
   - Generates performance summaries
   - Creates markdown reports

4. **Rate Limit Management**
   - Facebook: 200 calls/hour
   - Instagram: 25 posts/day
   - Automatic rate limit tracking

---

## 📁 File Structure

```
Ai_Employee_vault/
├── .env                          # Your credentials (create this)
├── .env.example                  # Template file
├── setup_credentials.py          # Interactive setup wizard
├── test_facebook_integration.py  # Test script
├── demo_facebook_watcher.py      # Demo script
├── docs/
│   ├── FACEBOOK_INSTAGRAM_SETUP.md  # Full setup guide
│   └── FACEBOOK_QUICKSTART.md       # This file
├── src/
│   ├── watcher_facebook.py       # Facebook watcher
│   ├── watcher.py                # Main orchestrator
│   └── mcp/
│       ├── facebook_client.py    # Facebook API client
│       └── instagram_client.py   # Instagram API client
├── Inbox/                        # Created content files
├── Done/                         # Summaries and completed items
└── Logs/                         # Log files
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Facebook
FACEBOOK_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Instagram (optional)
INSTAGRAM_ACCESS_TOKEN=your_page_access_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id_here
```

### Watcher Configuration

Edit `src/watcher.py` to enable/disable watchers:

```python
SOURCES_CONFIG = {
    "local_files": True,
    "gmail": True,
    "linkedin": True,
    "whatsapp": True,
    "facebook": True  # Enable Facebook watcher
}
```

---

## 💡 Usage Examples

### Example 1: Manual Post to Facebook

```python
from src.watcher_facebook import FacebookWatcher

watcher = FacebookWatcher()

# Post content
result = watcher.post_to_facebook(
    "Check out our new AI automation features! 🚀 #AI #Automation"
)

if result['success']:
    print(f"Posted! URL: {result['post_url']}")
```

### Example 2: Broadcast to Multiple Platforms

```python
content = {
    "title": "Product Update",
    "content": "New features released today!",
    "platforms": ["facebook", "instagram"],
    "hashtags": "#ProductUpdate #Innovation"
}

results = watcher.broadcast_content(content)
print(f"Posted to {results['summary']}")
```

### Example 3: Generate Summary

```python
# After posting content
summary = watcher.generate_summary()
print(f"Total posts: {summary['total_posts']}")
print(f"Success rate: {summary['success_rate']}")
```

---

## 🐛 Troubleshooting

### "Invalid OAuth access token"
- Token expired → Generate new token
- Wrong token type → Use Page Access Token, not User Token
- Missing permissions → Add required permissions in Facebook App

### "Instagram requires image URL"
- Instagram posts must include an image
- Provide a publicly accessible image URL
- Image must be JPG or PNG format

### "Rate limit exceeded"
- Facebook: Wait for hourly reset (200 calls/hour)
- Instagram: Wait for daily reset (25 posts/day)
- Check rate limit in logs

### "Page not found"
- Verify Page ID is correct
- Ensure token has access to the page
- Check page is published (not draft)

---

## 📊 Monitoring

### Check Logs

```bash
# Facebook watcher logs
tail -f Logs/watcher_facebook.log

# All watchers
tail -f Logs/watcher_main.log
```

### View Summaries

```bash
# Latest summary
cat Done/Facebook_Summary_*.md

# Summary JSON
cat Done/facebook_summary.json
```

### Check Inbox Files

```bash
# List pending content
ls -lt Inbox/Facebook_*.md
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` to Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Rotate tokens regularly**
   - Generate new tokens every 60 days
   - Revoke old tokens after rotation

3. **Use Page Access Tokens**
   - More secure than User Access Tokens
   - Don't expire automatically
   - Limited to specific page permissions

4. **Monitor API usage**
   - Check Facebook Developer Dashboard
   - Set up alerts for unusual activity

---

## 📚 Additional Resources

- [Full Setup Guide](FACEBOOK_INSTAGRAM_SETUP.md) - Detailed credential setup
- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api/)
- [Instagram Graph API Docs](https://developers.facebook.com/docs/instagram-api/)

---

## 🆘 Getting Help

1. Check logs: `Logs/watcher_facebook.log`
2. Run test script: `python test_facebook_integration.py`
3. Verify credentials in `.env` file
4. Review Facebook Developer Dashboard for errors

---

## ✅ Checklist

Before running the watcher, ensure:

- [ ] Facebook Developer App created
- [ ] Required permissions added to app
- [ ] Page Access Token generated
- [ ] Page ID obtained
- [ ] `.env` file created with credentials
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test script passed (`python test_facebook_integration.py`)

---

**Ready to go?** Run `python setup_credentials.py` to get started! 🚀
