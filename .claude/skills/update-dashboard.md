# Update Dashboard (CEO-Level Insights)

## Description
This skill creates a powerful, executive-level dashboard that provides actionable insights, priority breakdowns, bottleneck alerts, time estimates, business goal alignment, and beautiful Obsidian formatting.

## Instructions

When this skill is invoked, follow these steps:

### 1. Collect Comprehensive Statistics
Count files and analyze metadata in the following folders:
- `Needs_Action/` - Total pending tasks
- `Plans/` - Active execution plans
- `Done/` - Completed tasks
- `Inbox/` - Incoming items (if exists)
- `Logs/` - System logs (if exists)

Use bash commands:
```bash
ls -1 Needs_Action/ 2>/dev/null | wc -l
ls -1 Plans/ 2>/dev/null | wc -l
ls -1 Done/ 2>/dev/null | wc -l
```

### 2. Analyze Task Priority & Metadata
For each file in `Needs_Action/`:
- Read the file content
- Look for priority indicators: "urgent", "high priority", "critical", "ASAP", "⚠️", "🔴"
- Look for task type: "invoice", "email", "report", "meeting", "review"
- Estimate complexity: Simple (< 5 min), Medium (5-15 min), Complex (15+ min)
- Calculate total estimated time for all pending tasks

### 3. Bottleneck Detection
- If `Needs_Action/` has >= 5 files: **ALERT MODE**
- If `Plans/` has >= 10 files: **PLANNING OVERLOAD**
- If ratio of Needs_Action to Done is > 2:1: **EXECUTION GAP**

### 4. Business Goals Analysis
Analyze completed tasks in `Done/` folder:
- Count by category: Invoices, Emails, Reports, Meetings, Reviews
- Calculate business value delivered today
- Identify patterns and trends

### 5. Create/Update Dashboard.md
Create or completely overwrite `Dashboard.md` with this enhanced structure:

```markdown
# 🎯 AI Employee Vault - Executive Dashboard

> [!summary] Quick Overview
> **Status:** [🟢 Healthy / 🟡 Attention Needed / 🔴 Action Required]
> **Pending Tasks:** [count] | **Completed Today:** [count] | **Efficiency:** [completion rate]%

---

## 📊 Performance Metrics

| Metric | Current | Status |
|--------|---------|--------|
| 📥 Tasks Pending | [count] | [🟢/🟡/🔴] |
| 📋 Active Plans | [count] | [🟢/🟡/🔴] |
| ✅ Completed Today | [count] | [🟢/🟡/🔴] |
| ⚡ Avg. Processing Time | [X] min | [trend ↗️/↘️/→] |
| 🎯 Completion Rate | [X]% | [trend] |

### Priority Breakdown

> [!danger] Urgent Tasks
> **[count]** tasks require immediate attention
> - [List urgent task names]

> [!warning] High Priority
> **[count]** tasks scheduled for today
> - [List high priority task names]

> [!info] Normal Priority
> **[count]** tasks in queue
> - [List normal priority task names]

---

## ⏱️ Time Estimates

**Total Pending Workload:** ~[X] hours [Y] minutes

```progress
[=====>    ] 45% Complete
```

| Priority | Tasks | Est. Time |
|----------|-------|-----------|
| 🔴 Urgent | [count] | [X] min |
| 🟡 High | [count] | [X] min |
| 🟢 Normal | [count] | [X] min |

---

## 🚨 Alerts & Bottlenecks

[If Needs_Action >= 5:]
> [!error] ⚠️ ACTION REQUIRED: Backlog Increasing
> You have **[count]** pending tasks. Consider prioritizing or delegating.
> **Recommended Action:** Process top 3 urgent items immediately.

[If Plans >= 10:]
> [!warning] Planning Overload Detected
> **[count]** active plans may indicate over-planning. Focus on execution.

[If no alerts:]
> [!success] ✅ All Systems Operating Smoothly
> No bottlenecks detected. Workflow is healthy.

---

## 🎯 Progress Towards Goals

### Today's Business Impact

| Goal Category | Completed | Business Value |
|---------------|-----------|----------------|
| 💰 Invoices Processed | [count] | Revenue secured |
| 📧 Emails Handled | [count] | Communication cleared |
| 📊 Reports Generated | [count] | Insights delivered |
| 🤝 Meetings Scheduled | [count] | Collaboration enabled |
| 🔍 Reviews Completed | [count] | Quality assured |

**Total Value Delivered:** [X] tasks completed = [Y] hours saved

### Weekly Trend
```
Mon ████████░░ 80%
Tue ██████████ 100%
Wed ██████░░░░ 60%
Thu ████████░░ 75%
Fri [Today]
```

---

## 🕒 Recent Activity

**Last 5 Completed Tasks:**

[List last 5 files from Done folder with timestamps and task type]
1. ✅ [filename] - [timestamp] - [task type]
2. ✅ [filename] - [timestamp] - [task type]
...

[If no recent activity:]
> [!note] No Recent Activity
> No tasks completed yet today. Time to get started!

---

## 🔧 System Status

> [!check] System Health
> - ✅ **Watcher:** Active & Monitoring
> - ✅ **Human-in-the-loop:** Enabled
> - ✅ **Auto-Processing:** [On/Off]
> - ✅ **Backup:** Last backup [timestamp]

### Resource Utilization
- **Storage:** [X] files managed
- **Processing Queue:** [X] items
- **Response Time:** < [X] seconds

---

## 💡 Recommendations

[Based on analysis, provide 2-3 actionable recommendations:]
1. **[Recommendation]** - [Reason]
2. **[Recommendation]** - [Reason]
3. **[Recommendation]** - [Reason]

---

> [!quote] Daily Insight
> "[Generate a motivational insight based on today's performance]"

---

**Last Updated:** [Current Date and Time in format: YYYY-MM-DD HH:MM:SS]
**Next Refresh:** Auto-refresh every [X] minutes
```

### 6. Formatting Guidelines
- Use Obsidian callouts: `> [!info]`, `> [!warning]`, `> [!error]`, `> [!success]`, `> [!check]`
- Use emojis strategically for visual hierarchy
- Create progress bars using text: `[=====>    ]`
- Use tables for structured data
- Color code status: 🟢 (0-3 tasks), 🟡 (4-7 tasks), 🔴 (8+ tasks)
- Keep sections collapsible-friendly in Obsidian

### 7. Intelligence Layer
- Calculate completion rate: (Done / (Done + Needs_Action)) * 100
- Detect trends: Compare with previous dashboard state if available
- Estimate time: Simple=5min, Medium=10min, Complex=20min
- Identify task types from filenames and content
- Generate contextual recommendations

### 8. Output to User
After updating, provide executive summary:
```
🎯 Dashboard Updated Successfully!

📊 Executive Summary:
- Status: [🟢/🟡/🔴]
- Pending: [X] tasks (~[Y] hours)
- Completed: [X] tasks
- Alerts: [count] active alerts
- Business Value: [X] tasks delivered

💡 Top Recommendation: [Most important action]

Dashboard location: Dashboard.md
```

## Notes
- Always overwrite the entire Dashboard.md file for consistency
- Parse file content to extract priority and task type
- Use intelligent estimates based on task complexity
- Generate actionable insights, not just numbers
- Make it visually stunning in Obsidian
- Include trend analysis when possible
- Provide CEO-level strategic view, not just operational data

## Priority Detection Keywords
- **Urgent:** "urgent", "ASAP", "critical", "emergency", "🔴", "⚠️", "immediate"
- **High:** "high priority", "important", "today", "deadline", "🟡"
- **Normal:** Everything else, "🟢", "routine", "standard"

## Task Type Detection Keywords
- **Invoice:** "invoice", "payment", "bill", "💰"
- **Email:** "email", "message", "reply", "📧"
- **Report:** "report", "analysis", "summary", "📊"
- **Meeting:** "meeting", "call", "schedule", "🤝"
- **Review:** "review", "check", "audit", "🔍"
