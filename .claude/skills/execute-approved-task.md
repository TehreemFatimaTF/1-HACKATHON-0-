# Execute Approved Task (Action Executor)

## Description
This skill executes approved plans from the `4_Approved/` folder by performing real-world actions like sending emails, posting to LinkedIn, or updating systems. It implements the final step of the Silver Tier workflow: Human approves → AI executes.

## Instructions

When this skill is invoked, follow these steps:

### 1. Scan 4_Approved Folder

Check for approved plans ready for execution:

```bash
ls -1 4_Approved/ | head -5
```

If folder is empty:
- Inform user: "No approved plans found. Use /request-approval to approve plans first."
- Exit gracefully

### 2. Select Plan to Execute

**If specific plan name provided:**
- Execute that plan directly

**If no plan specified:**
- Show list of approved plans
- Ask user which one to execute
- Or execute the oldest plan first (FIFO)

### 3. Parse Plan Content

Read the approved plan file and extract:
- **Action Type**: Email, LinkedIn Post, Report, Meeting Schedule, etc.
- **Recipients/Target**: Email addresses, LinkedIn audience, etc.
- **Content**: Subject, body, message text
- **Priority**: Urgent, High, Normal
- **Metadata**: Any special instructions

Look for these patterns in the plan:

```markdown
**Action:** Send Email
**To:** client@example.com
**Subject:** Invoice Follow-up
**Body:** [content here]
```

Or:

```markdown
**Action:** LinkedIn Post
**Content:** [post content]
**Hashtags:** #AI #Automation
```

### 4. Determine Execution Method

Based on action type, choose the appropriate tool:

| Action Type | Execution Method | Tool/Command |
|-------------|------------------|--------------|
| Send Email | Gmail MCP | Use gmail MCP send_email tool |
| LinkedIn Post | LinkedIn API | Use linkedin MCP or API |
| Create Report | File Generation | Write markdown/PDF to Done/ |
| Schedule Meeting | Calendar API | Use calendar MCP |
| Update CRM | CRM API | Use appropriate MCP |

### 5. Execute the Action

**For Email Actions:**

If Gmail MCP is configured:
```
Use the gmail MCP tool:
- send_email(
    to: [recipient],
    subject: [subject],
    body: [body],
    cc: [optional],
    attachments: [optional]
  )
```

If Gmail MCP not available (fallback):
- Create a draft in `Done/` folder
- Log: "Email draft created (MCP not configured)"
- Notify user to send manually

**For LinkedIn Posts:**

If LinkedIn MCP is configured:
```
Use linkedin MCP tool:
- create_post(
    content: [post text],
    visibility: "public",
    hashtags: [tags]
  )
```

If not available (fallback):
- Create post draft in `Done/` folder
- Log: "LinkedIn post draft created"

**For Reports/Documents:**

- Generate the document
- Save to `Done/` folder
- Log completion

### 6. Log the Execution

Create or append to `Logs/executions.log`:

```
[YYYY-MM-DD HH:MM:SS] EXECUTED: [plan_filename]
- Action Type: [Email/LinkedIn/etc]
- Status: [Success/Failed/Draft]
- Target: [recipient/audience]
- Details: [brief description]
- Error: [if any]
```

### 7. Update External Actions Tracker

Create or update `Logs/external_actions.json`:

```json
{
  "emails_sent": [
    {
      "timestamp": "2026-02-11 21:30:00",
      "to": "client@example.com",
      "subject": "Invoice Follow-up",
      "status": "sent",
      "plan_file": "plan_invoice_followup.md"
    }
  ],
  "linkedin_posts": [
    {
      "timestamp": "2026-02-11 21:35:00",
      "content": "Excited to share...",
      "status": "posted",
      "plan_file": "plan_linkedin_post.md"
    }
  ],
  "total_emails": 1,
  "total_posts": 1,
  "last_updated": "2026-02-11 21:35:00"
}
```

### 8. Move Plan to Done Folder

After successful execution:

```bash
mv "4_Approved/[plan_filename]" "Done/[plan_filename]"
```

Add execution metadata to the file:

```markdown
---
**Status:** ✅ EXECUTED
**Executed At:** [timestamp]
**Execution Status:** [Success/Failed]
**Action Taken:** [description]
---

[Original plan content]
```

### 9. Trigger Dashboard Update

Automatically invoke `update-dashboard` skill to reflect:
- Decreased approved plans count
- Increased completed tasks count
- Updated external actions log

### 10. Confirm to User

Provide detailed confirmation:

```
✅ Task Executed Successfully!

📋 Plan: [plan_name]
🎯 Action: [action_type]
📧 Target: [recipient/audience]
⏰ Executed: [timestamp]
📊 Status: [Success/Draft/Failed]

External Actions Summary:
- Emails sent today: [count]
- LinkedIn posts today: [count]

Next Steps:
- Plan moved to Done/ folder
- Dashboard updated
- Execution logged

[If failed:]
❌ Execution Failed: [error message]
- Plan remains in 4_Approved/
- Check logs for details
- Retry with: /execute-approved-task [plan_name]
```

## Execution Examples

### Example 1: Send Email

```markdown
Plan content:
**Action:** Send Email
**To:** john@example.com
**Subject:** Quarterly Report Ready
**Body:** Hi John, The Q4 report is ready for review...

Execution:
→ Use Gmail MCP send_email
→ Log to external_actions.json
→ Move to Done/
→ Update dashboard
```

### Example 2: LinkedIn Post

```markdown
Plan content:
**Action:** LinkedIn Post
**Content:** Excited to announce our new AI automation tool...
**Hashtags:** #AI #Automation #Productivity

Execution:
→ Use LinkedIn MCP create_post
→ Log to external_actions.json
→ Move to Done/
→ Update dashboard
```

### Example 3: Fallback (No MCP)

```markdown
If MCP not configured:
→ Create draft in Done/email_draft_[timestamp].md
→ Log as "draft_created"
→ Notify user to send manually
→ Still move plan to Done/
```

## Error Handling

**Email sending fails:**
- Log error details
- Keep plan in 4_Approved/
- Notify user with specific error
- Suggest fixes (check credentials, MCP config, etc.)

**Invalid plan format:**
- Log parsing error
- Move to a `Failed/` folder (create if needed)
- Notify user to fix plan format

**MCP not available:**
- Create draft instead
- Log as "draft_created"
- Continue workflow (don't block)

## Safety Checks

Before executing:
1. **Verify approval metadata** - Ensure plan has "APPROVED" status
2. **Check for sensitive data** - Warn if plan contains passwords, API keys
3. **Validate recipients** - Ensure email addresses are valid
4. **Rate limiting** - Don't send more than 10 emails per minute
5. **Duplicate detection** - Check if same email was sent recently

## Integration with Other Skills

- **After execution:** Automatically call `update-dashboard`
- **On failure:** Create task in `Needs_Action/` for manual review
- **On success:** Log to `external_actions.json` for dashboard

## Configuration

Create `.env` file for sensitive data:

```env
GMAIL_ENABLED=true
LINKEDIN_ENABLED=false
MAX_EMAILS_PER_HOUR=50
EXECUTION_MODE=production  # or "draft_only" for testing
```

## Usage Examples

**Execute specific plan:**
```bash
claude skill execute-approved-task plan_invoice_followup_2026-02-11
```

**Execute next plan (FIFO):**
```bash
claude skill execute-approved-task
```

**Execute all approved plans:**
```bash
claude skill execute-approved-task --all
```

**Dry run (test without executing):**
```bash
claude skill execute-approved-task --dry-run
```

## Notes

- This is the final step in the Silver Tier workflow
- Requires human approval before any action is taken
- Maintains complete audit trail of all actions
- Supports fallback to drafts if MCP not available
- Integrates with dashboard for real-time tracking
- Implements safety checks to prevent accidental actions

## Future Enhancements

- Scheduled execution (execute at specific time)
- Batch execution (execute multiple plans at once)
- Rollback capability (undo sent emails if possible)
- A/B testing for LinkedIn posts
- Email template library
- Sentiment analysis before sending
