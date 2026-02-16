# Request Approval (Human-in-the-Loop)

## Description
This skill enables human approval workflow for AI-generated plans. When invoked, it moves approved plans from `Plans/` folder to `4_Approved/` folder, ensuring human oversight before execution.

## Instructions

When this skill is invoked with "Approve [plan_name]" or just "Approve", follow these steps:

### 1. Identify the Plan to Approve

**If specific plan name is provided:**
- Look for the exact file in `Plans/` folder
- Match by filename (case-insensitive)

**If no specific plan is provided:**
- List all files in `Plans/` folder
- Ask user which plan they want to approve
- Show a numbered list with plan names and creation dates

### 2. Validate the Plan Exists

```bash
ls -1 Plans/ | grep -i "[plan_name]"
```

If plan not found:
- Inform user the plan doesn't exist
- List available plans in `Plans/` folder
- Ask for correct plan name

### 3. Move Plan to 4_Approved Folder

Once plan is identified:

```bash
mv "Plans/[plan_filename]" "4_Approved/[plan_filename]"
```

### 4. Update Plan Metadata

Add approval timestamp to the moved file:
- Read the file content
- Add approval metadata at the top:

```markdown
---
**Status:** ✅ APPROVED
**Approved By:** Human
**Approval Date:** [Current Date and Time]
**Original Location:** Plans/[filename]
---

[Original plan content]
```

### 5. Log the Approval

Create or append to `Logs/approvals.log`:

```
[YYYY-MM-DD HH:MM:SS] APPROVED: [plan_filename]
- Approved by: Human
- Moved from: Plans/
- Moved to: 4_Approved/
- Status: Ready for Execution
```

### 6. Trigger Dashboard Update

After approval, automatically invoke the `update-dashboard` skill to reflect the change in pending approvals count.

### 7. Confirm to User

Provide clear confirmation:

```
✅ Plan Approved Successfully!

📋 Plan: [plan_name]
📁 Location: 4_Approved/[filename]
⏰ Approved: [timestamp]
🎯 Status: Ready for execution

Next Steps:
- Plan is now in 4_Approved/ folder
- You can execute it using /complete-task
- Dashboard has been updated

Would you like to execute this plan now?
```

## Usage Examples

**Approve specific plan:**
```
/request-approval Approve plan_security_audit_critical_2026-01-19
```

**Approve without specifying (interactive):**
```
/request-approval Approve
```
Then select from list.

**Bulk approve (if multiple plans mentioned):**
```
/request-approval Approve plan_1, plan_2, plan_3
```

## Edge Cases

1. **Plan already approved:** Check if file exists in `4_Approved/`, inform user it's already approved
2. **Empty Plans folder:** Inform user there are no plans pending approval
3. **Invalid filename:** Suggest closest match using fuzzy matching
4. **Permission issues:** Check write permissions before moving

## Integration with Other Skills

- **After approval:** Automatically update dashboard
- **Before execution:** `complete-task` should check `4_Approved/` folder
- **Rejection workflow:** If user says "Reject", move to a `Rejected/` folder instead

## Notes

- This implements the Silver Tier "Human-in-the-Loop" requirement
- Ensures AI doesn't execute plans without human oversight
- Maintains audit trail of all approvals
- Supports both interactive and command-line approval workflows
- Dashboard will show "Pending Approvals" count from `Plans/` folder
