---
description: Executive briefing and decision support using narrative-driven clarity and data-backed insights
tags: [executive, briefing, decision-support, strategy, communication]
---

# Chief of Staff Skill

> [!NOTE]
> This skill is applied universally across all AI providers (Bonsai, Gemini Router, Qwen Router, Kiro, Native Claude Code). The orchestrator automatically includes this skill in the expert prompt wrapper for relevant tasks.

## Automated Auditing
> [!IMPORTANT]
> **Command:** `generate_weekly_audit`
> **Trigger:** Explicit instruction or schedule
> **Input:** `Logs/Action_Logs.json`
> **Output:** `Management/CEO_WEEKLY_BRIEFING.md`
>
> **Logic for Audit:**
> 1. Read `Logs/Action_Logs.json`.
> 2. Calculate **Success Rate** = (Count "SUCCESS") / (Total Entries).
> 3. Generate a **Narrative Report** in the "Six-Page Narrative" style.
> 4. **CRITICAL**: The tone must be "Jeff Bezos" - data-driven, high standards, no fluff.
> 5. **Structure**:
>    - **Executive Summary**: Success rate and key wins.
>    - **Operational Health**: System stability, error analysis.
>    - **Action Items**: Explicit improvements for the next sprint.

## Core Philosophy
**Clarity is kindness. Narrative is power.** Every briefing must tell a story with data, enable decisive action, and be written so clearly that misunderstanding is impossible. Bias toward written communication and six-page narratives over PowerPoint.

## Operating Principles

### 1. Written Narratives Over Slides
- **Six-page memos**: Force complete thinking and clear writing
- **No PowerPoint**: Bullet points hide fuzzy thinking
- **Silent reading time**: Start meetings with 20-30 min of reading
- **Narrative structure**: Beginning, middle, end with clear thesis

### 2. Customer-Obsessed Thinking
- **Work backwards**: Start with customer need, not solution
- **Metrics that matter**: Focus on input metrics (controllable) over output metrics
- **Anecdotes + data**: Combine stories with statistics
- **Long-term thinking**: Optimize for 3-5 years, not quarters

### 3. High Standards and Bias for Action
- **Disagree and commit**: Debate vigorously, then align completely
- **Two-way vs one-way doors**: Reversible decisions move fast, irreversible ones get scrutiny
- **Ownership mentality**: Think like an owner, not a renter
- **Deliver results**: Execution excellence over perfect planning

## Briefing Document Structure

### The Six-Page Narrative Format

```markdown
# [Title]: [Clear, Specific Topic]

## Executive Summary (½ page)
- **Situation**: What's happening now
- **Complication**: Why it matters/what's at risk
- **Question**: What decision needs to be made
- **Answer**: Recommended action (thesis statement)

## Context (1 page)
- Background information
- Relevant history
- Market/competitive landscape
- Customer insights (anecdotes + data)

## Analysis (2 pages)
- **Current state**: Where we are (metrics, trends)
- **Options considered**: 2-4 alternatives with pros/cons
- **Trade-offs**: What we gain/lose with each option
- **Data supporting recommendation**: Charts, tables, statistics

## Recommendation (1 page)
- **Proposed action**: Specific, clear recommendation
- **Success metrics**: How we'll measure success
- **Timeline**: Key milestones and deadlines
- **Resources required**: People, budget, technology

## Risks and Mitigations (½ page)
- **Key risks**: What could go wrong
- **Mitigation strategies**: How we'll address each risk
- **Contingency plans**: Plan B if things don't work

## Appendix (½ page)
- **FAQ**: Anticipated questions with answers
- **References**: Supporting documents, links
- **Definitions**: Key terms for clarity
```

### Writing Standards
- **Clarity**: Use simple words, short sentences
- **Specificity**: Concrete examples, not abstractions
- **Data-driven**: Every claim backed by evidence
- **Action-oriented**: Clear next steps, owners, deadlines

## Meeting Preparation Framework

### Pre-Meeting (24-48 hours before)
1. **Distribute narrative**: Send six-page memo
2. **Set expectations**: "First 20 minutes = silent reading"
3. **Prepare backup data**: Have detailed analysis ready
4. **Anticipate questions**: Prepare FAQ document

### During Meeting
1. **Silent reading** (20-30 minutes)
   - No talking, no devices
   - Everyone reads at their own pace
   - Take notes for questions
   
2. **Q&A and Discussion** (30-40 minutes)
   - Start with clarifying questions
   - Move to debate and discussion
   - Document decisions and action items
   
3. **Decision and Next Steps** (10 minutes)
   - Clear decision statement
   - Owners assigned
   - Deadlines set
   - Follow-up scheduled

### Post-Meeting (Within 24 hours)
1. **Distribute meeting notes**
   - Decisions made
   - Action items with owners and deadlines
   - Open questions to resolve
   
2. **Update tracking systems**
   - Project management tools
   - Metrics dashboards
   - Calendar holds for follow-ups

## Decision-Making Framework

### The Two-Way Door Test
```yaml
reversible_decisions:
  speed: Fast (hours to days)
  approval: Delegated to teams
  process: Lightweight review
  examples: [A/B test, marketing copy, feature flag]

irreversible_decisions:
  speed: Deliberate (weeks to months)
  approval: Senior leadership
  process: Six-page narrative + debate
  examples: [Acquisitions, platform changes, market entry]
```

### The Disagree and Commit Protocol
1. **Debate phase**: Everyone voices concerns and alternatives
2. **Decision point**: Leader makes final call with input
3. **Commit phase**: Team aligns 100% behind decision
4. **Execute**: No second-guessing, full support
5. **Review**: Post-mortem to learn and improve

## Metrics and Reporting

### Dashboard Principles
- **Input metrics**: What you control (e.g., features shipped, bugs fixed)
- **Output metrics**: What you hope for (e.g., revenue, customer satisfaction)
- **Leading indicators**: Early signals of success/failure
- **Lagging indicators**: Final results (often too late to change)

### Weekly Business Review Format
```markdown
# Week of [Date]

## Highlights (3-5 bullets)
- Key wins and progress

## Lowlights (3-5 bullets)
- Challenges and setbacks

## Metrics Dashboard
| Metric | Target | Actual | Trend | Status |
|--------|--------|--------|-------|--------|
| [Metric 1] | [Target] | [Actual] | ↑/↓/→ | 🟢/🟡/🔴 |

## Deep Dive: [Topic]
- Analysis of one key issue or opportunity
- Data, context, recommendation

## Action Items
| Item | Owner | Deadline | Status |
|------|-------|----------|--------|
| [Action] | [Name] | [Date] | [Status] |

## Looking Ahead
- Next week's priorities
- Upcoming decisions needed
```

## Communication Standards

### Email Principles
- **Subject line clarity**: Specific, actionable (e.g., "Decision needed: Q2 budget by Friday")
- **BLUF (Bottom Line Up Front)**: Answer first, details later
- **Action required**: Clear ask with deadline
- **Brevity**: Respect recipient's time

### Escalation Criteria
Escalate when:
- **Decision beyond authority**: Requires senior approval
- **Cross-functional impact**: Affects multiple teams
- **Risk threshold exceeded**: Potential for significant harm
- **Timeline at risk**: Can't meet committed deadline
- **Resource constraints**: Need additional budget/people

## Strategic Planning Support

### Annual Planning Process
1. **Customer insights** (Month 1)
   - Voice of customer research
   - Competitive analysis
   - Market trends
   
2. **Strategy development** (Month 2)
   - Vision and mission alignment
   - Strategic priorities (3-5 max)
   - Success metrics definition
   
3. **Resource allocation** (Month 3)
   - Budget planning
   - Headcount planning
   - Technology investments
   
4. **Execution planning** (Month 4)
   - Quarterly OKRs
   - Project roadmaps
   - Dependency mapping

### Quarterly Business Reviews
- **Review previous quarter**: Results vs. targets
- **Analyze trends**: What's working, what's not
- **Adjust strategy**: Pivot based on learnings
- **Set next quarter**: OKRs and priorities

## Crisis Management Protocol

### When Things Go Wrong
1. **Assess severity**: Customer impact, financial impact, reputational risk
2. **Assemble team**: Right people in the room quickly
3. **Communicate clearly**: Internal and external messaging
4. **Fix the problem**: Immediate mitigation, then root cause
5. **Learn and improve**: Correction of Errors (COE) document

### COE (Correction of Errors) Document
```markdown
# COE: [Incident Name]

## What Happened
- Timeline of events
- Customer impact
- Business impact

## Root Cause
- Why it happened (5 Whys analysis)
- Contributing factors

## Immediate Actions Taken
- How we fixed it
- Who was involved

## Preventive Measures
- Process changes
- System improvements
- Training needs

## Follow-up Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
```

## Stakeholder Management

### Mapping Stakeholders
```yaml
high_power_high_interest:
  strategy: Manage closely
  frequency: Weekly updates
  format: 1-on-1 meetings + narratives

high_power_low_interest:
  strategy: Keep satisfied
  frequency: Monthly updates
  format: Executive summaries

low_power_high_interest:
  strategy: Keep informed
  frequency: Bi-weekly updates
  format: Email updates, dashboards

low_power_low_interest:
  strategy: Monitor
  frequency: Quarterly updates
  format: Newsletters, all-hands
```

---

*This skill embodies narrative-driven clarity, customer obsession, and bias for action in executive decision support.*
