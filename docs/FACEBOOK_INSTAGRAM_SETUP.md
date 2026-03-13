# Facebook & Instagram Integration Setup Guide

This guide will help you set up Facebook and Instagram credentials for the AI Employee watcher system.

## Prerequisites

- Facebook Business Account
- Facebook Page (for posting)
- Instagram Business Account (linked to Facebook Page)
- Facebook Developer Account

## Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" as app type
4. Fill in app details:
   - App Name: "AI Employee Social Manager"
   - App Contact Email: Your email
   - Business Account: Select your business account

## Step 2: Configure App Permissions

1. In your app dashboard, go to "App Settings" → "Basic"
2. Add your app domain (if applicable)
3. Go to "Products" → Add "Facebook Login"
4. Add required permissions:
   - `pages_show_list`        - View list of pages
   - `pages_read_engagement`       - Read page engagement metrics
   - `pages_manage_posts`        - Create and manage posts
   - `instagram_basic`           - Access Instagram account
   - `instagram_content_publish` - Publish Instagram content

## Step 3: Get Facebook Access Token

### Option A: Using Graph API Explorer (Quick Test)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from dropdown
3. Click "Generate Access Token"
4. Select required permissions:
   - pages_show_list
   - pages_read_engagement
   - pages_manage_posts
5. Copy the generated token (valid for 1-2 hours)

### Option B: Long-Lived Access Token (Production)

1. Get short-lived token from Graph API Explorer
2. Exchange for long-lived token using this API call:

```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
```

3. The response will contain a long-lived token (valid for 60 days)

### Option C: Page Access Token (Recommended)

1. Get your User Access Token (long-lived)
2. Get your Page ID:
```bash
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=USER_ACCESS_TOKEN"
```

3. Use the Page Access Token from the response (never expires)

## Step 4: Get Facebook Page ID

1. Go to your Facebook Page
2. Click "About" in left sidebar
3. Scroll down to find "Page ID"
4. Copy the numeric ID

**OR** use Graph API:

```bash
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
```

## Step 5: Get Instagram Credentials

### Link Instagram to Facebook Page

1. Go to your Facebook Page
2. Click "Settings" → "Instagram"
3. Click "Connect Account"
4. Log in to your Instagram Business Account
5. Confirm the connection

### Get Instagram Account ID

```bash
curl -X GET "https://graph.facebook.com/v18.0/PAGE_ID?fields=instagram_business_account&access_token=PAGE_ACCESS_TOKEN"
```

The response will contain your Instagram Business Account ID.

### Get Instagram Access Token

Instagram uses the same access token as your Facebook Page. Use the Page Access Token from Step 3.

## Step 6: Configure Environment Variables

Create or update your `.env` file in the project root:

```env
# Facebook Configuration
FACEBOOK_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here

# Instagram Configuration
INSTAGRAM_ACCESS_TOKEN=your_page_access_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id_here
```

**Important Notes:**
- Instagram uses the same access token as Facebook Page
- Both tokens should be Page Access Tokens (not User Access Tokens)
- Keep these tokens secure and never commit them to version control

## Step 7: Test the Integration

Run the test script to verify your credentials:

```bash
cd src
python test_facebook_integration.py
```

Or start the Facebook watcher:

```bash
cd src
python watcher_facebook.py
```

## Troubleshooting

### Error: "Invalid OAuth access token"
- Your token may have expired
- Generate a new long-lived or page access token
- Verify the token has required permissions

### Error: "Instagram requires image URL"
- Instagram posts must include an image
- Provide a publicly accessible image URL
- Image must be in JPG or PNG format

### Error: "Rate limit exceeded"
- Facebook: 200 calls per hour
- Instagram: 25 posts per day
- Wait for the rate limit to reset

### Error: "Page not found"
- Verify your Page ID is correct
- Ensure your access token has access to the page
- Check that the page is published (not draft)

## API Rate Limits

### Facebook
- **API Calls:** 200 per hour per user
- **Posts:** No specific limit, but excessive posting may trigger spam detection

### Instagram
- **Posts:** 25 per day per account
- **Hashtags:** Maximum 30 per post
- **Caption:** Maximum 2,200 characters

## Security Best Practices

1. **Never commit tokens to Git**
   - Add `.env` to `.gitignore`
   - Use environment variables

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

## Additional Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api/)
- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api/)
- [Facebook Access Token Guide](https://developers.facebook.com/docs/facebook-login/access-tokens/)
- [Instagram Content Publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)

## Support

If you encounter issues:
1. Check the logs in `Logs/watcher_facebook.log`
2. Verify credentials in `.env` file
3. Test API access using Graph API Explorer
4. Review Facebook Developer Dashboard for errors

---

**Ready to start?** Provide your credentials and run the watcher!
