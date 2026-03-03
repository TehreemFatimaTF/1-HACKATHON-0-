# Research: Gold Tier Autonomous Employee

**Feature**: 001-gold-tier-autonomous
**Date**: 2026-02-20
**Purpose**: Technical research and decision documentation for Gold Tier implementation

## 1. Odoo JSON-RPC Integration Patterns

### Decision: Use `odoorpc` library with session-based authentication

**Rationale**:
- `odoorpc` provides Pythonic interface to Odoo's JSON-RPC API
- Session-based auth simpler than API keys for localhost deployment
- Built-in connection pooling and error handling
- Active maintenance and Odoo 19+ compatibility

**Implementation Pattern**:
```python
import odoorpc

# Connection with retry logic
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('database_name', 'username', 'password')

# Invoice creation
invoice_id = odoo.env['account.move'].create({
    'partner_id': client_id,
    'move_type': 'out_invoice',
    'invoice_line_ids': [(0, 0, {
        'product_id': product_id,
        'quantity': 1,
        'price_unit': amount
    })]
})
```

**Error Handling Strategy**:
- Connection failures: Local queue with exponential backoff (1s, 2s, 4s, 8s, 16s max)
- Authentication failures: Alert user immediately (P0 escalation)
- Transaction failures: Rollback and log detailed error context
- Timeout: 30 seconds per operation, then fallback to queue

**Alternatives Considered**:
- Direct XML-RPC: More verbose, less Pythonic
- REST API: Requires Odoo REST module installation
- Direct database access: Violates Odoo architecture, breaks audit trail

**Best Practices**:
- Always use transactions for multi-record operations
- Validate data client-side before submission (tax calculations, required fields)
- Cache frequently accessed data (product IDs, client IDs) to reduce API calls
- Use Odoo's search_read for efficient bulk queries

---

## 2. Social Media API Integration

### Decision: Platform-specific clients with unified interface

**X (Twitter) API v2**:
- Library: `tweepy` v4.14+
- Authentication: OAuth 2.0 Bearer Token
- Rate Limits: 50 tweets per 24 hours (free tier), 300 per 15 minutes (read)
- Character Limit: 280 characters (4000 for premium)
- Media: Up to 4 images per tweet

**Facebook Graph API**:
- Library: `facebook-sdk` v3.1+
- Authentication: Long-lived Page Access Token
- Rate Limits: 200 calls per hour per user
- Content: No character limit, supports rich media
- Posting: Requires `pages_manage_posts` permission

**Instagram Graph API**:
- Library: `instagrapi` v4.0+ (unofficial but stable)
- Authentication: Instagram Business Account + Facebook Page Token
- Rate Limits: 25 posts per day, 200 API calls per hour
- Content: Image required, 2200 character caption limit
- Hashtags: Max 30 per post

**Unified Interface Pattern**:
```python
class SocialMediaClient(ABC):
    @abstractmethod
    def post(self, content: str, media: List[str]) -> PostResult:
        pass

    @abstractmethod
    def get_engagement(self, post_id: str) -> EngagementMetrics:
        pass

    @abstractmethod
    def health_check(self) -> HealthStatus:
        pass
```

**Graceful Degradation Strategy**:
- Each platform wrapped in try-except with specific error handling
- Failed platform logged but doesn't block others
- Retry queue for transient failures (rate limits, network issues)
- Success tracking: Partial success (2/3 platforms) still reported as success

**Rate Limit Handling**:
- Pre-flight check: Query rate limit status before posting
- Exponential backoff: Wait and retry if rate limited
- Queue management: Spread posts over time windows to avoid bursts
- Alert: Notify user if consistently hitting rate limits

**Alternatives Considered**:
- Zapier/IFTTT: External dependency, less control, cost
- Browser automation (Selenium): Fragile, violates ToS, slow
- Official SDKs only: Instagram lacks official Python SDK

---

## 3. Multi-Step Workflow State Management

### Decision: File-based state persistence with JSON serialization

**Rationale**:
- Aligns with existing folder-based architecture
- No additional database dependency
- Human-readable for debugging
- Atomic writes prevent corruption
- Easy rollback (copy previous state file)

**State Schema**:
```json
{
  "task_id": "uuid",
  "workflow_name": "trend_to_post_to_expense",
  "current_step": 2,
  "total_steps": 4,
  "completed_steps": [
    {
      "step_number": 1,
      "action": "detect_trend",
      "result": "success",
      "output": {"trend_topic": "AI automation"},
      "timestamp": "2026-02-20T10:30:00Z"
    }
  ],
  "pending_steps": [
    {"step_number": 3, "action": "post_to_social"},
    {"step_number": 4, "action": "log_expense"}
  ],
  "context": {
    "trend_data": {...},
    "post_content": "...",
    "platforms": ["twitter", "facebook", "instagram"]
  },
  "outcome_status": "in_progress",
  "created_at": "2026-02-20T10:25:00Z",
  "updated_at": "2026-02-20T10:30:00Z"
}
```

**Storage Location**: `Needs_Action/state_<task_id>.json`

**Outcome Verification Pattern**:
```python
def verify_outcome(task: AutonomousTask) -> bool:
    """Ralph Wiggum Loop: Did I achieve the final outcome?"""
    original_intent = task.context.get('original_intent')
    actual_results = [step.result for step in task.completed_steps]

    # Check 1: All steps completed successfully
    if any(r != 'success' for r in actual_results):
        return False

    # Check 2: Final output matches intent
    final_output = task.completed_steps[-1].output
    return matches_intent(final_output, original_intent)
```

**Rollback Strategy**:
- Before each step: Save state snapshot
- On failure: Restore previous state, mark step as failed
- Compensating actions: Undo side effects (delete created invoice, remove post)
- Manual intervention: Flag for human review if rollback fails

**Alternatives Considered**:
- In-memory state: Lost on crash, no persistence
- SQLite database: Overkill for small-scale operations, adds dependency
- Redis: External service dependency, complexity

---

## 4. Sentiment Analysis Approaches

### Decision: TextBlob for simplicity, with upgrade path to transformers

**TextBlob (Initial Implementation)**:
- Library: `textblob` v0.17+
- Accuracy: ~70% for English social media text
- Performance: <10ms per text analysis
- Simplicity: Single line of code: `TextBlob(text).sentiment.polarity`
- Output: Polarity (-1 to +1), Subjectivity (0 to 1)

**Classification Logic**:
```python
def classify_sentiment(text: str) -> str:
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"
```

**Upgrade Path (Future)**:
- For higher accuracy: `transformers` with `cardiffnlp/twitter-roberta-base-sentiment`
- Accuracy: ~85-90% for social media text
- Performance: ~100ms per text (acceptable for batch processing)
- Trade-off: 10x slower but 15-20% more accurate

**Integration with Priority Escalation**:
- Negative sentiment on client communication → P0 escalation
- Negative sentiment on social media post → Flag for review
- Positive sentiment → Standard priority
- Neutral sentiment → Standard priority

**Multi-Language Support** (Future):
- TextBlob supports English only
- For multi-language: Use `langdetect` + language-specific models
- Current scope: English only (assumption documented in spec)

**Alternatives Considered**:
- VADER: Good for social media but similar accuracy to TextBlob
- spaCy: Overkill for simple sentiment, requires model download
- Cloud APIs (Google, AWS): External dependency, cost, latency

---

## 5. Graceful Degradation Patterns

### Decision: Circuit Breaker + Retry with Exponential Backoff

**Circuit Breaker Pattern**:
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen("Service unavailable")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

**Retry with Exponential Backoff**:
- Library: `tenacity` v8.2+
- Pattern: Retry 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Jitter: Add random 0-1s to prevent thundering herd
- Stop conditions: Max attempts OR max wait time (60s total)

**Implementation**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    reraise=True
)
def call_mcp_server(endpoint, data):
    response = requests.post(endpoint, json=data, timeout=30)
    response.raise_for_status()
    return response.json()
```

**Fallback Path Selection**:
1. Primary path: Direct MCP server call
2. Fallback 1: Retry with exponential backoff
3. Fallback 2: Queue for later processing
4. Fallback 3: Log error, notify user, continue with other tasks

**Health Monitoring**:
- Periodic health checks (every 60 seconds)
- Track success/failure rates per MCP server
- Dashboard.md shows health status: 🟢 Healthy, 🟡 Degraded, 🔴 Failed
- Alert on sustained failures (3+ consecutive failures)

**Alerting Strategy**:
- P0 alert: Critical MCP server down (Odoo, Gmail)
- P1 alert: Non-critical MCP server down (social media)
- P2 alert: Degraded performance (slow responses)
- Dashboard.md: Real-time status updates

**Alternatives Considered**:
- No retry: Fails too easily on transient errors
- Infinite retry: Can block system indefinitely
- Fixed backoff: Can overwhelm recovering services
- No circuit breaker: Wastes resources on dead services

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Odoo Integration | odoorpc with session auth | Pythonic, maintained, localhost-optimized |
| X (Twitter) | tweepy v4.14+ | Official SDK, OAuth 2.0, rate limit handling |
| Facebook | facebook-sdk v3.1+ | Stable, Graph API support |
| Instagram | instagrapi v4.0+ | Best available Python client |
| State Management | File-based JSON | Aligns with folder architecture, debuggable |
| Sentiment Analysis | TextBlob (initial) | Simple, fast, good enough for MVP |
| Error Recovery | Circuit Breaker + Retry | Industry standard, prevents cascading failures |
| Retry Strategy | Exponential backoff (tenacity) | Proven pattern, configurable |

## Implementation Priority

1. **Phase 1**: Odoo integration + Circuit Breaker (Milestone 2)
2. **Phase 2**: Ralph Wiggum Loop + State Management (Milestone 1)
3. **Phase 3**: Social Media + Sentiment Analysis (Milestone 3)
4. **Phase 4**: Audit Logging + CEO Briefing (Milestone 4)
5. **Phase 5**: Integration + Hardening (Milestone 5)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Odoo connection failure | Local queue + exponential backoff + user alert |
| Social media rate limits | Pre-flight checks + queue spreading + retry |
| State corruption | Atomic writes + backup before each step |
| Sentiment analysis inaccuracy | Conservative thresholds + human review for edge cases |
| Circuit breaker stuck open | Timeout + half-open state for recovery testing |

## Next Steps

1. Proceed to Phase 1: Generate data-model.md
2. Create MCP server contracts (contracts/*.yaml)
3. Write quickstart.md for setup and testing
4. Update agent context with new technologies
5. Generate implementation tasks with /sp.tasks
