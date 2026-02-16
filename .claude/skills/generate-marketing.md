---
skill: generate-marketing
description: Generate creative LinkedIn marketing posts based on trends and company context
tags: [marketing, linkedin, content-generation, automation, sales]
---

# Generate Marketing Skill

This skill analyzes LinkedIn trends from the Inbox folder and company information to create compelling marketing posts that drive business and sales.

## Workflow

1. **Analyze Trends:** Read LinkedIn trend files from `Inbox/` folder
2. **Read Company Context:** Parse `Company_Handbook.md` for company info
3. **Generate Posts:** Create 2 creative LinkedIn posts for business growth
4. **Save Plans:** Store posts in `Plans/` folder with naming: `MARKETING_POST_[date].md`
5. **Approval Flow:** Posts can be approved via `/request-approval` skill
6. **Execution:** Approved posts execute via `/execute-action` skill

## Instructions for Claude

When this skill is invoked:

### Step 1: Analyze LinkedIn Trends

```bash
# List all LinkedIn trend files in Inbox
ls -la Inbox/ | grep -i linkedin
ls -la Inbox/ | grep -i trend
```

Read each LinkedIn trend file and extract:
- **Trending Topics:** What's currently popular
- **Hashtags:** Relevant hashtags for reach
- **Industry Insights:** Key business trends
- **Engagement Patterns:** What type of content performs well

### Step 2: Read Company Context

Read `Company_Handbook.md` to understand:
- Company name and mission
- Products/services offered
- Target audience
- Unique value proposition
- Brand voice and tone
- Key differentiators

### Step 3: Generate Creative Marketing Posts

Create **2 LinkedIn posts** that:

**Post 1: Thought Leadership / Industry Insight**
- Share valuable industry insights
- Position company as expert
- Include relevant statistics or trends
- Add 3-5 strategic hashtags
- Call-to-action for engagement

**Post 2: Product/Service Promotion**
- Highlight company offerings
- Focus on customer benefits
- Include social proof or results
- Add 3-5 strategic hashtags
- Call-to-action for leads/sales

**Content Guidelines:**
- Length: 150-300 words per post
- Tone: Professional yet conversational
- Include emojis strategically (2-3 per post)
- Use line breaks for readability
- End with clear call-to-action
- Align with current trends
- Focus on business value

### Step 4: Create Plan Files

For each post, create a file in `Plans/` folder:

**Filename Format:**
```
Plans/MARKETING_POST_[YYYY-MM-DD]_[number].md
```

Example:
- `Plans/MARKETING_POST_2026-02-13_1.md`
- `Plans/MARKETING_POST_2026-02-13_2.md`

**File Template:**

```markdown
---
Action_Type: LinkedIn_Post
Status: Pending_Approval
Priority: Medium
Created_By: generate-marketing skill
Created_At: YYYY-MM-DD HH:MM:SS
Category: Marketing
Post_Type: Thought_Leadership | Product_Promotion
Target_Audience: [describe target audience]
Expected_Reach: Medium | High
---

# LinkedIn Marketing Post - [Brief Title]

**Action:** Post on LinkedIn

**Post Type:** Thought Leadership / Product Promotion

**Target Audience:** [Who this post is for]

**Content:**

[Post content here - 150-300 words]
[Use line breaks for readability]
[Include emojis strategically]
[End with call-to-action]

#Hashtag1 #Hashtag2 #Hashtag3 #Hashtag4 #Hashtag5

---

**Marketing Strategy:**
- **Goal:** [Increase brand awareness / Generate leads / Drive sales]
- **Key Message:** [Main takeaway]
- **Trending Topic:** [Related trend from Inbox]
- **Expected Engagement:** [Comments / Shares / Leads]

**Approval Notes:**
- Review content for brand alignment
- Verify hashtags are relevant
- Confirm call-to-action is clear
- Check for typos and formatting
```

### Step 5: Generate Summary

After creating posts, provide summary:

```
✅ Generated 2 LinkedIn Marketing Posts

📊 Post 1: [Title]
   - Type: Thought Leadership
   - Hashtags: #tag1 #tag2 #tag3
   - Goal: Brand awareness
   - File: Plans/MARKETING_POST_2026-02-13_1.md

📊 Post 2: [Title]
   - Type: Product Promotion
   - Hashtags: #tag1 #tag2 #tag3
   - Goal: Lead generation
   - File: Plans/MARKETING_POST_2026-02-13_2.md

📁 Next Steps:
   1. Review posts in Plans/ folder
   2. Use /request-approval to approve posts
   3. Approved posts will execute via /execute-action
```

## Content Creation Best Practices

### Thought Leadership Posts

**Structure:**
1. **Hook:** Start with compelling question or statistic
2. **Insight:** Share valuable industry knowledge
3. **Value:** Explain why it matters
4. **CTA:** Encourage discussion or sharing

**Example Topics:**
- Industry trends and predictions
- Lessons learned from experience
- Data-driven insights
- Problem-solving approaches
- Innovation and technology

### Product/Service Promotion Posts

**Structure:**
1. **Problem:** Identify customer pain point
2. **Solution:** Introduce your offering
3. **Benefits:** Highlight key advantages
4. **Proof:** Share results or testimonials
5. **CTA:** Drive action (demo, contact, learn more)

**Example Topics:**
- New feature announcements
- Customer success stories
- Product comparisons
- Special offers or promotions
- Use case demonstrations

## Hashtag Strategy

**Categories:**
1. **Industry Hashtags:** #AI #Automation #SaaS #Technology
2. **Audience Hashtags:** #Entrepreneurs #BusinessOwners #Startups
3. **Topic Hashtags:** #Productivity #Innovation #DigitalTransformation
4. **Branded Hashtags:** #YourCompanyName #YourProduct

**Best Practices:**
- Use 3-5 hashtags per post
- Mix popular and niche hashtags
- Research trending hashtags from Inbox trends
- Avoid overused generic hashtags
- Create branded hashtags for campaigns

## Trend Analysis Guidelines

When analyzing LinkedIn trends from Inbox:

1. **Identify Patterns:**
   - What topics appear multiple times?
   - Which hashtags are trending?
   - What content formats are popular?

2. **Extract Insights:**
   - Industry challenges mentioned
   - Solutions being discussed
   - Emerging technologies or practices
   - Common pain points

3. **Find Opportunities:**
   - Gaps in current conversations
   - Questions people are asking
   - Problems needing solutions
   - Underserved audiences

4. **Align with Company:**
   - How do trends relate to our offerings?
   - Can we provide unique perspective?
   - What value can we add to conversation?
   - How can we position as solution?

## Company Context Integration

Use Company_Handbook.md to ensure posts:

- **Reflect Brand Voice:** Match company tone and style
- **Highlight Strengths:** Emphasize unique capabilities
- **Target Right Audience:** Speak to ideal customers
- **Support Goals:** Align with business objectives
- **Maintain Consistency:** Stay true to brand identity

## Approval Flow Integration

Posts created by this skill follow the standard approval workflow:

```
generate-marketing → Plans/MARKETING_POST_*.md
                            ↓
                    /request-approval
                            ↓
                    4_Approved/
                            ↓
                    /execute-action
                            ↓
                    LinkedIn (simulated)
                            ↓
                    Done/ + Logs/
```

## Usage Examples

### Example 1: Generate Marketing Posts

```bash
# User invokes skill
/generate-marketing
```

Claude will:
1. Scan Inbox/ for LinkedIn trends
2. Read Company_Handbook.md
3. Create 2 marketing posts in Plans/
4. Provide summary with next steps

### Example 2: Complete Workflow

```bash
# Step 1: Generate posts
/generate-marketing

# Step 2: Review and approve
/request-approval

# Step 3: Execute approved posts
/execute-action
```

### Example 3: Scheduled Generation

```bash
# Run weekly via cron
0 9 * * 1 cd /path/to/project && /generate-marketing
```

## Quality Checklist

Before saving posts, verify:

- ✅ Content is 150-300 words
- ✅ Includes 3-5 relevant hashtags
- ✅ Has clear call-to-action
- ✅ Aligns with company brand
- ✅ References current trends
- ✅ Provides business value
- ✅ Uses proper formatting
- ✅ Includes strategic emojis
- ✅ Targets right audience
- ✅ Has compelling hook

## Error Handling

**If no trends found in Inbox:**
- Use general industry knowledge
- Focus on evergreen content
- Reference company strengths
- Create educational content

**If Company_Handbook.md missing:**
- Use generic business context
- Focus on universal value propositions
- Create industry-agnostic content
- Log warning for user

**If Plans/ folder doesn't exist:**
- Create the folder automatically
- Log creation for user
- Proceed with post generation

## Success Metrics

Track effectiveness of generated posts:

- **Engagement Rate:** Comments, likes, shares
- **Reach:** Impressions and views
- **Lead Generation:** Profile visits, connections
- **Conversion:** Website clicks, inquiries
- **Brand Awareness:** Follower growth, mentions

## Future Enhancements

1. **AI-Powered Optimization:**
   - A/B testing different post formats
   - Sentiment analysis on trends
   - Predictive engagement scoring

2. **Advanced Features:**
   - Multi-platform support (Twitter, Facebook)
   - Image/video content suggestions
   - Optimal posting time recommendations
   - Competitor analysis integration

3. **Analytics Integration:**
   - Track post performance
   - Identify top-performing content
   - Refine strategy based on data
   - ROI measurement

## Notes

- Posts are created in **Plans/** folder (not 4_Approved)
- Requires manual approval via `/request-approval` skill
- Approved posts execute via `/execute-action` skill
- LinkedIn posts are currently simulated (logged to Logs/linkedin_posts.log)
- For live posting, LinkedIn API integration needed

## Example Output

When skill completes successfully:

```
🎯 LinkedIn Marketing Posts Generated!

📝 Post 1: "The Future of AI Automation in Business"
   Type: Thought Leadership
   Goal: Brand Awareness
   Hashtags: #AI #Automation #FutureOfWork #Innovation #BusinessGrowth
   File: Plans/MARKETING_POST_2026-02-13_1.md

📝 Post 2: "Transform Your Workflow with AI Employee"
   Type: Product Promotion
   Goal: Lead Generation
   Hashtags: #AIEmployee #Productivity #Automation #BusinessTools #Efficiency
   File: Plans/MARKETING_POST_2026-02-13_2.md

✅ Posts saved to Plans/ folder
📋 Next: Use /request-approval to review and approve
🚀 Then: Use /execute-action to post on LinkedIn
```
