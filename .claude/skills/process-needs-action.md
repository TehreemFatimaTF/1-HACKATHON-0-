---
name: process-needs-action
description: Processes files from Needs_Action and creates plans
---

# Process Needs Action

## Description
This skill processes all files in the Needs_Action folder, analyzes them, updates the Dashboard.md with current status, and creates detailed execution plans in the Plans folder.

## Instructions

When this skill is invoked, follow these steps:

### 1. Scan Needs_Action Folder
- List all files in the `Needs_Action/` folder
- If the folder is empty, inform the user and exit
- Read each file completely to understand the tasks/actions required

### 2. Analyze Tasks
For each file in Needs_Action:
- Extract the main task or action items
- Identify priority level (if mentioned)
- Note any dependencies or prerequisites
- Determine the complexity and scope

### 3. Update Dashboard.md
Create or update `Dashboard.md` in the root directory with:
- **Current Date and Time**: Add timestamp of when this was processed
- **Pending Actions Summary**: List all tasks from Needs_Action folder
  - File name
  - Brief description
  - Priority (High/Medium/Low)
  - Status (New/In Progress/Blocked)
- **Statistics**:
  - Total tasks pending
  - Tasks by priority
  - Tasks by category (if applicable)
- **Recent Updates**: What changed since last run

### 4. Create Execution Plans
For each task in Needs_Action, create a detailed plan file in `Plans/` folder:
- File naming: `plan_[original-filename]_[date].md`
- Include:
  - **Task Overview**: What needs to be done
  - **Prerequisites**: What's needed before starting
  - **Step-by-Step Plan**: Detailed execution steps
  - **Expected Outcomes**: What success looks like
  - **Potential Risks**: What could go wrong
  - **Estimated Effort**: Complexity assessment
  - **Dependencies**: Links to other tasks if any

### 5. Summary Report
After processing, provide the user with:
- Number of files processed
- Number of plans created
- Dashboard update confirmation
- Any issues or blockers identified
- Recommended next steps

## Output Format

Always structure your response as:
1. Files found in Needs_Action
2. Analysis summary
3. Dashboard updated (with link)
4. Plans created (with links)
5. Recommendations

## Notes
- If Dashboard.md doesn't exist, create it
- If Plans folder doesn't exist, create it
- Archive processed files by moving them to appropriate folders (Done/Logs) only if user confirms
- Use clear, actionable language in plans
- Include timestamps for tracking
