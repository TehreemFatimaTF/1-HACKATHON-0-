---
skill: execute-action
description: Execute approved actions using MCP tools (Gmail, LinkedIn, etc.)
tags: [automation, mcp, execution, email, linkedin]
---

# Execute Action Skill

This skill scans the `4_Approved/` folder for approved plans and executes them using available MCP tools.

## Workflow

1. **Scan 4_Approved folder** for approved plans
2. **Parse the plan** to identify action type (Email, LinkedIn Post, Report, etc.)
3. **Execute the action** using appropriate MCP tool:
   - Email → Use `gmail__send_email` MCP tool
   - LinkedIn Post → Simulate or use LinkedIn MCP if available
   - Report → Generate and save report
4. **Move plan to Done/** folder after successful execution
5. **Update Logs/external_actions.json** with execution details

## Instructions for Claude

When this skill is invoked:

### Step 1: Scan for Approved Plans
```bash
# List all files in 4_Approved folder
ls -la 4_Approved/
```

### Step 2: Read Each Plan
For each file found:
- Read the plan content
- Look for action indicators:
  - Keywords: "Send Email", "Email to", "LinkedIn Post", "Post on LinkedIn", "Generate Report"
  - Metadata fields: `Action_Type`, `Recipient`, `Subject`, `Content`

### Step 3: Parse Action Details

**For Email Actions:**
- Extract: recipient email, subject, body/content
- Look for patterns like:
  - "Send email to: [email]"
  - "Subject: [subject line]"
  - "Body:" or "Content:" sections

**For LinkedIn Posts:**
- Extract: post content, hashtags
- Look for patterns like:
  - "Post on LinkedIn:"
  - "Content:" or "Message:"
  - Hashtags: #tag1 #tag2

### Step 4: Execute Using MCP Tools

**Gmail MCP Tool:**
```
Use the gmail__send_email tool with:
- to: recipient email address
- subject: email subject
- body: email content
```

**LinkedIn (Simulated):**
Since LinkedIn MCP may not be available, create a simulation:
- Log the post content
- Save to Logs/linkedin_posts.log
- Mark as "Simulated - LinkedIn API not configured"

### Step 5: Move to Done Folder
```bash
# Move the executed plan
mv 4_Approved/[filename] Done/[filename]
```

### Step 6: Update Logs

Update `Logs/external_actions.json`:
```json
{
  "emails_sent": [
    {
      "timestamp": "2026-02-13 23:30:00",
      "plan_file": "plan_name.md",
      "recipient": "user@example.com",
      "subject": "Email subject",
      "status": "success",
      "message_id": "gmail_message_id"
    }
  ],
  "linkedin_posts": [
    {
      "timestamp": "2026-02-13 23:30:00",
      "plan_file": "plan_name.md",
      "content": "Post content...",
      "status": "simulated",
      "hashtags": ["#AI", "#Automation"]
    }
  ]
}
```

## Error Handling

- If MCP tool fails, log error and DO NOT move plan to Done
- Keep plan in 4_Approved with error note
- Update external_actions.json with failure status
- Notify user of failure

## Example Plan Format

```markdown
---
Action_Type: Send_Email
Recipient: client@example.com
Subject: Follow-up on Invoice #12345
Status: Approved
---

# Email Follow-up Plan

Send email to: client@example.com
Subject: Follow-up on Invoice #12345

Body:
Dear Client,

This is a friendly reminder about invoice #12345 which is now 15 days overdue.

Please let us know if you have any questions.

Best regards,
AI Employee
```

## Usage

Invoke this skill when:
- User says "execute approved actions"
- User says "run approved plans"
- User says "send approved emails"
- Scheduled execution (e.g., every hour)

## Safety Checks

Before executing:
1. Verify plan is in 4_Approved folder (not Needs_Action)
2. Check for "Approved" status in metadata
3. Validate email addresses (basic format check)
4. Confirm MCP tools are available
5. Ask user for confirmation if action seems risky

## Output

Provide summary:
```
✅ Executed 2 actions:
  - Email sent to client@example.com (Invoice Follow-up)
  - LinkedIn post simulated (AI Trends Update)

📁 Moved 2 plans to Done/
📊 Updated external_actions.json
```
