# Quickstart Guide: Gold Tier Autonomous Employee

**Feature**: 001-gold-tier-autonomous
**Date**: 2026-02-20
**Purpose**: Setup, configuration, and testing instructions for Gold Tier implementation

## Prerequisites

### System Requirements
- Python 3.11 or higher
- Windows 10+ or Linux
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space (for logs and data)

### External Services
1. **Odoo 19+ Community Edition**
   - Installed and running at localhost:8069
   - Database created with admin credentials
   - Accounting module enabled

2. **Social Media API Credentials**
   - X (Twitter) API v2 Bearer Token
   - Facebook Page Access Token (long-lived)
   - Instagram Business Account linked to Facebook Page

3. **Existing Silver Tier Setup**
   - Watcher running and monitoring Inbox folder
   - Gmail MCP configured (from Silver Tier)
   - LinkedIn integration functional (from Silver Tier)

## Installation

### Step 1: Install Python Dependencies

```bash
# Navigate to project root
cd Ai_Employee_vault

# Install new Gold Tier dependencies
pip install odoorpc==0.10.0
pip install tweepy==4.14.0
pip install facebook-sdk==3.1.0
pip install instagrapi==4.0.0
pip install textblob==0.17.1
pip install tenacity==8.2.3

# Download TextBlob corpora (for sentiment analysis)
python -m textblob.download_corpora
```

### Step 2: Configure Environment Variables

Edit `.env` file and add Gold Tier credentials:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=your_database_name
ODOO_USERNAME=admin
ODOO_PASSWORD=your_odoo_password

# X (Twitter) Configuration
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Facebook Configuration
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_long_lived_page_token

# Instagram Configuration
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# Gold Tier Configuration
AUTONOMOUS_MODE=false  # Set to true to enable autonomous execution
AUTONOMOUS_WHITELIST=detect_trend,create_post,log_expense  # Comma-separated action names
AUDIT_LOG_RETENTION_DAYS=365
MAX_CONCURRENT_TASKS=10
```

### Step 3: Verify Odoo Connection

```bash
# Test Odoo connectivity
python -c "
import odoorpc
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('your_database_name', 'admin', 'your_password')
print('✅ Odoo connection successful!')
print(f'Odoo version: {odoo.version}')
"
```

Expected output:
```
✅ Odoo connection successful!
Odoo version: 19.0
```

### Step 4: Verify Social Media API Credentials

```bash
# Test X (Twitter) API
python -c "
import tweepy
client = tweepy.Client(bearer_token='your_bearer_token')
me = client.get_me()
print(f'✅ Twitter connected as: {me.data.username}')
"

# Test Facebook API
python -c "
import facebook
graph = facebook.GraphAPI(access_token='your_page_token')
page = graph.get_object('me')
print(f'✅ Facebook connected to page: {page[\"name\"]}')
"

# Test Instagram API
python -c "
from instagrapi import Client
cl = Client()
# Note: Instagram requires username/password login
cl.login('your_username', 'your_password')
print(f'✅ Instagram connected as: {cl.username}')
"
```

### Step 5: Initialize Gold Tier Structure

```bash
# Create Gold Tier directories
mkdir -p src/mcp
mkdir -p src/skills
mkdir -p src/audit
mkdir -p tests/contract
mkdir -p tests/integration
mkdir -p tests/unit
mkdir -p Logs/Audit_Trail

# Create initial audit log file
echo "" > Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl

# Create MCP connections tracking file
echo '{}' > Memory/mcp_connections.json
```

## Configuration

### Autonomous Action Whitelist

Edit `.env` to configure which actions can execute autonomously:

```bash
# Conservative (recommended for initial testing)
AUTONOMOUS_WHITELIST=detect_trend,classify_priority

# Moderate (after testing)
AUTONOMOUS_WHITELIST=detect_trend,classify_priority,create_post,fetch_engagement

# Full autonomy (production)
AUTONOMOUS_WHITELIST=detect_trend,classify_priority,create_post,fetch_engagement,create_invoice,log_expense,generate_briefing
```

### Priority Matrix Configuration

The 4-Tier Priority Matrix is configured in `Company_Handbook.md`:

- **P0 (Critical/Revenue)**: Immediate action + alert
- **P1 (Client Retention)**: Same-day processing
- **P2 (Operational)**: Next 24 hours
- **P3 (General/Growth)**: Weekly batching

### Audit Log Configuration

Configure audit logging in `.env`:

```bash
AUDIT_LOG_RETENTION_DAYS=365  # How long to keep logs
AUDIT_LOG_MAX_SIZE_MB=100     # Max size per log file
AUDIT_TAMPER_CHECK=true       # Enable hash chain verification
```

## Testing

### Test 1: MCP Server Health Checks

```bash
# Test all MCP servers
python -c "
from src.mcp.odoo_client import OdooClient
from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient

# Test Odoo
odoo = OdooClient()
print(f'Odoo: {odoo.health_check()}')

# Test Twitter
twitter = TwitterClient()
print(f'Twitter: {twitter.health_check()}')

# Test Facebook
facebook = FacebookClient()
print(f'Facebook: {facebook.health_check()}')

# Test Instagram
instagram = InstagramClient()
print(f'Instagram: {instagram.health_check()}')
"
```

Expected output:
```
Odoo: {'status': 'HEALTHY', 'authenticated': True, 'response_time_ms': 45.2}
Twitter: {'status': 'HEALTHY', 'authenticated': True, 'rate_limit': {'remaining': 45}}
Facebook: {'status': 'HEALTHY', 'authenticated': True, 'rate_limit': {'remaining': 185}}
Instagram: {'status': 'HEALTHY', 'authenticated': True, 'daily_posts_remaining': 22}
```

### Test 2: Create Test Invoice in Odoo

```bash
# Create a test invoice
python -c "
from src.skills.odoo_create_invoice import create_invoice

result = create_invoice(
    client_reference='Test Client',
    line_items=[
        {'description': 'Test Service', 'quantity': 1, 'unit_price': 100.00}
    ],
    tax_rate=0.10,
    due_date='2026-03-15'
)

print(f'✅ Invoice created: {result[\"invoice_id\"]}')
print(f'Total: ${result[\"total\"]}')
print(f'Odoo ID: {result[\"odoo_id\"]}')
"
```

Expected output:
```
✅ Invoice created: 550e8400-e29b-41d4-a716-446655440000
Total: $110.00
Odoo ID: 1234
```

Verify in Odoo:
1. Open http://localhost:8069
2. Navigate to Accounting → Customers → Invoices
3. Find invoice with ID 1234
4. Verify amount is $110.00

### Test 3: Post to Social Media (Test Mode)

```bash
# Test social media posting (will actually post!)
python -c "
from src.skills.broadcast_marketing import broadcast_post

result = broadcast_post(
    content='🧪 Test post from Gold Tier AI Employee - please ignore!',
    platforms=['twitter', 'facebook', 'instagram'],
    media_urls=['https://example.com/test-image.jpg']
)

print(f'✅ Posted to {len(result[\"successful_platforms\"])} platforms')
for platform, post_id in result['platform_post_ids'].items():
    print(f'  {platform}: {post_id}')
"
```

Expected output:
```
✅ Posted to 3 platforms
  twitter: 1234567890123456789
  facebook: 123456789012345_987654321098765
  instagram: 17895695668004550
```

**⚠️ Warning**: This will create actual posts on your social media accounts. Delete them manually after testing.

### Test 4: Autonomous Workflow Execution

```bash
# Enable autonomous mode temporarily
export AUTONOMOUS_MODE=true
export AUTONOMOUS_WHITELIST=detect_trend,create_post,log_expense

# Create a test task in Inbox
cat > Inbox/test_autonomous_workflow.md << EOF
---
type: marketing_campaign
priority: P2
---

# Test Autonomous Workflow

Create a social media post about AI automation trends and log the marketing expense.

Trend: "AI automation market reaches $50B in 2026"
Platforms: Twitter, Facebook, Instagram
Budget: $50 (social media management tools)
EOF

# Run the watcher (will process autonomously)
python src/watcher.py

# Check audit log
tail -f Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl
```

Expected audit log entries:
```json
{"entry_id":"...", "action_type":"TASK_START", "action_name":"autonomous_workflow", ...}
{"entry_id":"...", "action_type":"STEP_EXECUTE", "action_name":"detect_trend", ...}
{"entry_id":"...", "action_type":"STEP_EXECUTE", "action_name":"create_post", ...}
{"entry_id":"...", "action_type":"MCP_CALL", "action_name":"post_to_twitter", ...}
{"entry_id":"...", "action_type":"MCP_CALL", "action_name":"post_to_facebook", ...}
{"entry_id":"...", "action_type":"MCP_CALL", "action_name":"post_to_instagram", ...}
{"entry_id":"...", "action_type":"STEP_EXECUTE", "action_name":"log_expense", ...}
{"entry_id":"...", "action_type":"TASK_COMPLETE", "execution_result":"SUCCESS", ...}
```

### Test 5: Error Recovery and Graceful Degradation

```bash
# Test with Twitter API disabled (simulate failure)
export TWITTER_BEARER_TOKEN=invalid_token

# Run broadcast (should continue with Facebook and Instagram)
python -c "
from src.skills.broadcast_marketing import broadcast_post

result = broadcast_post(
    content='Testing graceful degradation',
    platforms=['twitter', 'facebook', 'instagram']
)

print(f'✅ Successful: {result[\"successful_platforms\"]}')
print(f'❌ Failed: {result[\"failed_platforms\"]}')
print(f'Status: {result[\"status\"]}')  # Should be PARTIAL
"
```

Expected output:
```
✅ Successful: ['facebook', 'instagram']
❌ Failed: ['twitter']
Status: PARTIAL
```

Check audit log for error recovery:
```bash
grep "error_details" Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl | tail -1
```

## Monitoring

### Dashboard.md

The Dashboard.md file updates in real-time with Gold Tier metrics:

```markdown
## 🤖 Gold Tier Status

**Autonomous Mode**: ✅ Enabled
**Active Workflows**: 3
**Completed Today**: 12
**Success Rate**: 95%

### MCP Server Health
- 🟢 Odoo: HEALTHY (45ms avg)
- 🟢 Twitter: HEALTHY (rate limit: 45/50)
- 🟢 Facebook: HEALTHY (rate limit: 185/200)
- 🟡 Instagram: DEGRADED (rate limit: 2/25 daily posts)

### Recent Autonomous Actions
1. ✅ Created invoice INV-2026-042 ($1,500) - 2 min ago
2. ✅ Posted to 3 platforms (reach: 8,500) - 5 min ago
3. ✅ Logged marketing expense ($250) - 5 min ago
```

### Audit Log Viewer

```bash
# View today's audit log
cat Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl | jq '.'

# Count actions by type
cat Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl | jq -r '.action_type' | sort | uniq -c

# Find all errors
cat Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl | jq 'select(.execution_result == "FAILURE")'

# Verify tamper-evidence (hash chain)
python -c "
import json
import hashlib

with open('Logs/Audit_Trail/gold_audit_$(date +%Y-%m-%d).jsonl') as f:
    entries = [json.loads(line) for line in f]

prev_hash = None
for entry in entries:
    if prev_hash and entry['previous_entry_hash'] != prev_hash:
        print(f'❌ Tamper detected at entry {entry[\"entry_id\"]}')
        break
    prev_hash = entry['entry_hash']
else:
    print('✅ Audit log integrity verified')
"
```

## Troubleshooting

### Issue: Odoo Connection Failed

**Symptoms**: `Connection refused` or `Authentication failed`

**Solutions**:
1. Verify Odoo is running: `curl http://localhost:8069`
2. Check credentials in `.env`
3. Verify database name exists in Odoo
4. Check firewall settings

### Issue: Social Media Rate Limits

**Symptoms**: `Rate limit exceeded` errors

**Solutions**:
1. Check rate limit status: Run health checks
2. Reduce posting frequency in autonomous whitelist
3. Spread posts over time windows (queue management)
4. Upgrade to premium API tiers if needed

### Issue: Autonomous Loop Not Starting

**Symptoms**: Tasks stay in Needs_Action folder

**Solutions**:
1. Verify `AUTONOMOUS_MODE=true` in `.env`
2. Check `AUTONOMOUS_WHITELIST` includes required actions
3. Review audit log for errors: `tail -f Logs/Audit_Trail/gold_audit_*.jsonl`
4. Restart watcher: `python src/watcher.py`

### Issue: Audit Log Tamper Detection

**Symptoms**: Hash chain verification fails

**Solutions**:
1. Check for manual edits to audit log files (not allowed)
2. Verify file permissions (should be append-only)
3. Check for disk corruption
4. Restore from backup if necessary

## Production Deployment

### Pre-Production Checklist

- [ ] All MCP servers health checks passing
- [ ] Test invoice created and verified in Odoo
- [ ] Test social media posts successful on all platforms
- [ ] Autonomous workflow executed successfully
- [ ] Error recovery tested and working
- [ ] Audit log integrity verified
- [ ] Dashboard.md updating in real-time
- [ ] CEO briefing generated successfully
- [ ] All tests passing (contract, integration, unit)
- [ ] Backup strategy configured
- [ ] Monitoring alerts configured

### Enable Full Autonomy

```bash
# Update .env for production
AUTONOMOUS_MODE=true
AUTONOMOUS_WHITELIST=detect_trend,classify_priority,create_post,fetch_engagement,create_invoice,log_expense,generate_briefing

# Restart watcher
python src/watcher.py
```

### Monitoring and Alerts

Set up cron jobs for monitoring:

```bash
# Check MCP server health every 5 minutes
*/5 * * * * python src/utils/health_check.py

# Generate CEO briefing every Sunday at 6 PM
0 18 * * 0 python src/skills/generate_ceo_briefing.py

# Verify audit log integrity daily
0 2 * * * python src/audit/verify_integrity.py

# Clean up old logs (keep 365 days)
0 3 * * * find Logs/Audit_Trail -name "*.jsonl" -mtime +365 -delete
```

## Next Steps

1. **Run Contract Tests**: `pytest tests/contract/`
2. **Run Integration Tests**: `pytest tests/integration/`
3. **Generate Implementation Tasks**: Run `/sp.tasks` command
4. **Begin Milestone 1**: Implement Ralph Wiggum Loop (src/engine_gold.py)

## Support

For issues or questions:
- Review audit logs: `Logs/Audit_Trail/gold_audit_*.jsonl`
- Check Dashboard.md for system status
- Review constitution principles: `.specify/memory/constitution.md`
- Consult implementation plan: `specs/001-gold-tier-autonomous/plan.md`
