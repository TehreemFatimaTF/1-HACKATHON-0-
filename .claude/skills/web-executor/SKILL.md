---
description: Web development execution using ship-fast-iterate-faster methodology
tags: [web-development, frontend, backend, deployment, iteration]
---

# Web Executor Skill

> [!NOTE]
> This skill is applied universally across all AI providers (Bonsai, Gemini Router, Qwen Router, Kiro, Native Claude Code). The orchestrator automatically includes this skill in the expert prompt wrapper for relevant tasks.

## Core Philosophy
**Ship fast, iterate faster.** Perfect is the enemy of shipped. Build MVPs in days, gather real user feedback, and iterate based on data. Prioritize working software over comprehensive documentation.

## Operating Principles

### 1. Bias Toward Action
- **Ship within 48 hours**: First version live in 2 days max
- **Real users > perfect code**: Get feedback from actual usage
- **Iterate in public**: Let users see evolution
- **Kill features fast**: Remove what doesn't work

### 2. The MVP Mindset
- **Core value only**: What's the ONE thing this must do?
- **Manual before automated**: Prove demand before scaling
- **Ugly but functional**: UI polish comes after validation
- **Measure everything**: Instrument from day one

### 3. Technical Pragmatism
- **Boring technology**: Use proven stacks, not bleeding edge
- **Monolith first**: Microservices only when necessary
- **Database last**: Start with files/localStorage if possible
- **Deploy early**: CI/CD from commit one

## Development Workflow

### Day 1: Foundation (0-8 hours)
```yaml
hour_0_2:
  - Project setup (Vite/Next.js + FastAPI/Express)
  - Git repo + GitHub
  - Basic CI/CD pipeline (GitHub Actions)
  - Deploy to Vercel/Netlify + Railway/Render

hour_2_4:
  - Core data model (1-3 entities max)
  - Basic CRUD API endpoints
  - Simple authentication (if needed)
  - Database schema (SQLite/Postgres)

hour_4_6:
  - Minimal UI (one page)
  - Core user flow (happy path only)
  - Basic styling (Tailwind/vanilla CSS)
  - Form validation

hour_6_8:
  - Integration testing
  - Error handling (basic)
  - Analytics setup (PostHog/Mixpanel)
  - First deploy to production
```

### Day 2: Polish and Launch (8-16 hours)
```yaml
hour_8_10:
  - Edge case handling
  - Loading states
  - Error messages
  - Mobile responsiveness

hour_10_12:
  - SEO basics (meta tags, sitemap)
  - Performance optimization
  - Security hardening
  - Backup strategy

hour_12_14:
  - User testing (5 people)
  - Bug fixes
  - UX improvements
  - Documentation (README)

hour_14_16:
  - Marketing page
  - Social sharing
  - Launch on Product Hunt/HN
  - Monitor and respond
```

### Week 1: Iterate Based on Feedback
- **Daily deploys**: Ship improvements every day
- **User interviews**: Talk to 10+ users
- **Analytics review**: What are people actually doing?
- **Feature prioritization**: Build what users ask for most

## Technology Stack Decisions

### Frontend Framework Selection
```yaml
simple_landing_page:
  choice: HTML + Vanilla CSS + Vanilla JS
  reason: No build step, instant deploy
  
interactive_app:
  choice: Vite + React/Vue
  reason: Fast dev experience, modern tooling
  
full_web_app:
  choice: Next.js/Nuxt
  reason: SSR, routing, API routes built-in
  
real_time_app:
  choice: Next.js + WebSockets/SSE
  reason: Full-stack with real-time capabilities
```

### Backend Framework Selection
```yaml
api_only:
  choice: FastAPI (Python) or Express (Node)
  reason: Fast to build, great DX
  
full_stack:
  choice: Next.js API routes or Django
  reason: Integrated frontend + backend
  
real_time:
  choice: FastAPI + WebSockets or Socket.io
  reason: Built-in WebSocket support
  
background_jobs:
  choice: FastAPI + Celery or BullMQ
  reason: Async task processing
```

### Database Selection
```yaml
mvp_prototype:
  choice: SQLite or localStorage
  reason: Zero setup, file-based
  
production_app:
  choice: PostgreSQL
  reason: Reliable, feature-rich, free tier available
  
real_time_data:
  choice: PostgreSQL + Redis
  reason: Persistent storage + caching/pub-sub
  
document_heavy:
  choice: MongoDB or Supabase
  reason: Flexible schema, easy to start
```

## Code Quality Standards

### The "Good Enough" Bar
```python
# ✅ Good enough for MVP
def create_user(email: str, password: str):
    """Create a new user."""
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return user

# ❌ Over-engineered for MVP
class UserFactory:
    def __init__(self, validator: UserValidator, hasher: PasswordHasher):
        self.validator = validator
        self.hasher = hasher
    
    def create(self, dto: CreateUserDTO) -> UserEntity:
        # ... 50 more lines
```

### When to Refactor
- **When adding third feature**: Extract common patterns
- **When code is read 3+ times**: Make it clearer
- **When performance matters**: Optimize hot paths
- **When tests fail repeatedly**: Improve design

### When NOT to Refactor
- **Before any users**: Premature optimization
- **For aesthetic reasons**: Functionality > beauty
- **To use new tech**: Boring tech wins
- **Because "best practices"**: Pragmatism > dogma

## Deployment Strategy

### The Continuous Deployment Pipeline
```yaml
on_commit:
  - Run linters (ESLint, Ruff)
  - Run type checks (TypeScript, mypy)
  - Run unit tests
  - Build application
  
on_pr:
  - All commit checks
  - Integration tests
  - Preview deployment
  - Lighthouse audit
  
on_merge_to_main:
  - All PR checks
  - Deploy to production
  - Run smoke tests
  - Notify team
```

### Environment Strategy
```yaml
development:
  location: localhost
  database: SQLite/local Postgres
  purpose: Active development

preview:
  location: Vercel/Netlify preview
  database: Staging database
  purpose: PR review and testing

production:
  location: Vercel/Railway/Render
  database: Production database
  purpose: Real users
```

## Performance Optimization

### The 80/20 Rule
Focus on these high-impact optimizations:
1. **Image optimization**: WebP, lazy loading, CDN
2. **Code splitting**: Load only what's needed
3. **Caching**: Browser cache, CDN, Redis
4. **Database indexing**: Index foreign keys and query fields
5. **API response size**: Paginate, compress, minimize payload

### Performance Budget
```yaml
initial_load:
  target: < 3 seconds on 3G
  measure: Lighthouse Performance score > 90
  
time_to_interactive:
  target: < 5 seconds
  measure: Lighthouse TTI metric
  
api_response:
  target: < 200ms for p95
  measure: Server-side monitoring
```

## Error Handling and Monitoring

### The Three Levels of Errors
```yaml
user_errors:
  examples: [Invalid input, not found, unauthorized]
  handling: Show friendly message, log for analytics
  alerting: None (expected errors)

application_errors:
  examples: [API timeout, database connection lost]
  handling: Retry with exponential backoff, fallback
  alerting: Log to Sentry, notify on-call if persistent

system_errors:
  examples: [Server crash, out of memory, disk full]
  handling: Automatic restart, failover
  alerting: Immediate page to on-call engineer
```

### Monitoring Essentials
```yaml
must_have:
  - Error tracking (Sentry, Rollbar)
  - Uptime monitoring (UptimeRobot, Better Uptime)
  - Analytics (PostHog, Mixpanel, Plausible)
  - Logs (Structured logging to stdout)

nice_to_have:
  - APM (Application Performance Monitoring)
  - Real User Monitoring (RUM)
  - Session replay
  - A/B testing platform
```

## Feature Development Process

### The Feature Flag Approach
```javascript
// Ship incomplete features behind flags
const features = {
  newDashboard: process.env.FEATURE_NEW_DASHBOARD === 'true',
  aiAssistant: user.betaTester === true,
  payments: process.env.NODE_ENV === 'production'
};

// Gradually roll out
if (features.newDashboard) {
  return <NewDashboard />;
}
return <OldDashboard />;
```

### The Kill Switch Pattern
```python
# Every new feature has a kill switch
@feature_flag("ai_recommendations", default=False)
def get_recommendations(user_id: str):
    # New AI-powered recommendations
    return ai_service.recommend(user_id)

# If it breaks production, flip the flag
# Users see old behavior, no deploy needed
```

## User Feedback Loop

### The Weekly Cycle
```yaml
monday:
  - Review analytics from previous week
  - Identify top user pain points
  - Prioritize fixes and features

tuesday_thursday:
  - Build and ship improvements
  - Deploy daily
  - Monitor error rates and usage

friday:
  - User interviews (3-5 users)
  - Collect qualitative feedback
  - Plan next week's priorities

weekend:
  - Monitor production
  - Fix critical bugs only
  - Rest and recharge
```

### Metrics That Matter
```yaml
acquisition:
  - Signups per day
  - Conversion rate (visitor → signup)
  - Traffic sources

activation:
  - Time to first value
  - Completion rate of onboarding
  - Feature adoption rate

retention:
  - Daily/Weekly/Monthly Active Users
  - Churn rate
  - Session frequency and duration

revenue:
  - MRR (Monthly Recurring Revenue)
  - Customer Lifetime Value
  - Conversion to paid
```

## Security Essentials

### The Minimum Security Checklist
- [ ] **HTTPS everywhere**: Force SSL/TLS
- [ ] **Authentication**: Secure password hashing (bcrypt, Argon2)
- [ ] **Authorization**: Check permissions on every request
- [ ] **Input validation**: Sanitize all user input
- [ ] **SQL injection prevention**: Use parameterized queries
- [ ] **XSS prevention**: Escape output, use CSP headers
- [ ] **CSRF protection**: Use CSRF tokens
- [ ] **Rate limiting**: Prevent abuse
- [ ] **Secrets management**: Never commit secrets
- [ ] **Dependency updates**: Automated security patches

### The "Good Enough" Security Posture
```yaml
mvp_stage:
  - Basic auth (email + password)
  - HTTPS
  - Input validation
  - Secrets in environment variables

growth_stage:
  - OAuth/SSO
  - 2FA for admins
  - Rate limiting
  - Security headers
  - Automated dependency scanning

scale_stage:
  - SOC 2 compliance
  - Penetration testing
  - Bug bounty program
  - Advanced threat detection
```

---

*This skill embodies rapid iteration, pragmatic technical decisions, and user-driven development.*
