# Complete Task

Mark a task as completed and archive it to the Done folder.

## Description
This skill handles the completion workflow for tasks. It updates the task status, adds completion metadata, moves files to the Done archive, and updates the Dashboard. This ensures proper task lifecycle management and audit trail.

## Instructions

1. **Identify Task to Complete**
   - User will provide either:
     - Full filename (e.g., `FILE_20260110_142301_invoice.md`)
     - Partial identifier (e.g., "invoice task")
     - Task number from Dashboard listing

   - Search in these locations:
     - `AI_Employee_Vault/Needs_Action/` (in-progress tasks)
     - `AI_Employee_Vault/Plans/` (active plans)

2. **Verify Completion Eligibility**
   - Read the task file
   - Check if all required steps are completed:
     - For action files: verify all suggested actions are done
     - For plans: verify all checkboxes are checked

   - If not all steps are complete:
     - Ask user if they want to complete anyway
     - If no, abort and report remaining steps

3. **Update Task File**
   - Add completion metadata to frontmatter:
     ```yaml
     status: completed
     completed_at: [ISO timestamp]
     completed_by: ai_employee
     ```

   - Add completion summary at end of file:
     ```markdown
     ## Completion Summary
     - Completed: [ISO timestamp]
     - Duration: [time from detection to completion]
     - Outcome: [brief description of result]
     ```

4. **Move to Done Folder**
   - Move the updated file to `AI_Employee_Vault/Done/`
   - Maintain original filename for traceability

   - If related plan exists in `/Plans`:
     - Move plan to `/Done` as well
     - Link them in completion notes

5. **Update Dashboard**
   - Increment completion counter
   - Add to "Recent Activity" section
   - Remove from "Pending Actions" list
   - Update "Completed This Week" stat

6. **Log Completion**
   - Append to today's log file
   - Include:
     - Task identifier
     - Completion timestamp
     - Brief outcome description
     - Files moved

## Completion Summary Template

Add this to the end of completed task files:

```markdown
---

## Completion Summary
- Completed: [ISO timestamp]
- Duration: [X hours/days from detection]
- Outcome: [What was accomplished]
- Related Files:
  - Original: [Inbox/filename if applicable]
  - Plan: [Plans/plan_filename.md if applicable]
  - Archive: Done/[this file]

## Performance Metrics
- Response Time: [time from detection to first action]
- Total Time: [time from detection to completion]
- Priority: [original priority level]

*Task completed by AI Employee v0.1*
```

## Success Criteria
- Task file updated with completion metadata
- File moved to Done folder
- Dashboard updated with completion
- Log entry created
- Related files also archived

## Example Usage

**User:** `claude skill complete-task invoice_client_a`

**Expected Behavior:**
1. Find `FILE_20260110_142301_invoice_client_a.md` in /Needs_Action
2. Add completion metadata
3. Move to Done folder
4. Find related `PLAN_20260110_142305_invoice_client_a.md` in /Plans
5. Move plan to Done folder as well
6. Update Dashboard:
   - Remove from Pending Actions
   - Add to Recent Activity: "[2026-01-10 15:30] Processed invoice_client_a"
   - Increment completion counter
7. Log completion event

## Error Handling

If task cannot be found:
```
Error: Could not find task matching "invoice_client_a"

Available tasks in Needs_Action:
1. FILE_20260110_140512_message_from_client.md
2. FILE_20260110_135021_project_proposal.md

Please specify the full filename or select a number.
```

## Related Skills
- Use `process-needs-action` to create tasks from inbox items
- Use `update-dashboard` to refresh the dashboard after completion