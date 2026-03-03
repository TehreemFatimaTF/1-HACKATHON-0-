# Data Model: Gold Tier Autonomous Employee

**Feature**: 001-gold-tier-autonomous
**Date**: 2026-02-20
**Purpose**: Entity schemas and relationships for Gold Tier implementation

## Entity Schemas

### 1. AutonomousTask

**Purpose**: Represents a multi-step workflow with state tracking for autonomous execution

**Fields**:
- `task_id` (string, UUID): Unique identifier for the task
- `workflow_name` (string): Name of the workflow template (e.g., "trend_to_post_to_expense")
- `original_intent` (string): Natural language description of what the task should achieve
- `current_step` (integer): Index of the currently executing step (0-based)
- `total_steps` (integer): Total number of steps in the workflow
- `completed_steps` (array of Step): Steps that have been executed
- `pending_steps` (array of Step): Steps remaining to be executed
- `context` (object): Workflow-specific data preserved across steps
- `outcome_status` (enum): PENDING | IN_PROGRESS | COMPLETED | FAILED | PAUSED
- `priority` (enum): P0 | P1 | P2 | P3 (from 4-Tier Matrix)
- `created_at` (datetime, ISO 8601): Task creation timestamp
- `updated_at` (datetime, ISO 8601): Last modification timestamp
- `completed_at` (datetime, ISO 8601, nullable): Task completion timestamp

**Step Schema** (nested):
- `step_number` (integer): Sequential step index
- `action` (string): Action name (e.g., "detect_trend", "create_post", "log_expense")
- `status` (enum): PENDING | IN_PROGRESS | SUCCESS | FAILED | SKIPPED
- `input` (object): Input parameters for this step
- `output` (object): Result data from this step
- `error` (string, nullable): Error message if step failed
- `started_at` (datetime, ISO 8601): Step start timestamp
- `completed_at` (datetime, ISO 8601, nullable): Step completion timestamp
- `retry_count` (integer): Number of retry attempts

**Validation Rules**:
- `task_id` must be unique
- `current_step` must be < `total_steps`
- `completed_steps.length + pending_steps.length` must equal `total_steps`
- `outcome_status` transitions: PENDING → IN_PROGRESS → (COMPLETED | FAILED | PAUSED)

**State Transitions**:
```
PENDING → IN_PROGRESS (when first step starts)
IN_PROGRESS → COMPLETED (when all steps succeed and outcome verified)
IN_PROGRESS → FAILED (when step fails and no recovery possible)
IN_PROGRESS → PAUSED (when human input required)
PAUSED → IN_PROGRESS (when human provides input)
```

**Relationships**:
- Links to multiple GoldAuditEntry records (one per step)
- May link to OdooInvoice, OdooExpense, SocialMediaPost depending on workflow

**Storage**: `Needs_Action/state_<task_id>.json`

---

### 2. OdooInvoice

**Purpose**: Financial document for client billing with Odoo integration

**Fields**:
- `invoice_id` (string, UUID): Internal unique identifier
- `odoo_id` (integer, nullable): Odoo database record ID (null until synced)
- `client_reference` (string): Client identifier (name or Odoo partner_id)
- `invoice_number` (string): Human-readable invoice number (e.g., "INV-2026-001")
- `line_items` (array of LineItem): Invoice line items
- `subtotal` (decimal): Sum of line items before tax
- `tax_rate` (decimal): Tax percentage (e.g., 0.10 for 10%)
- `tax_amount` (decimal): Calculated tax amount
- `total` (decimal): Final amount (subtotal + tax_amount)
- `currency` (string): Currency code (e.g., "USD", "EUR")
- `due_date` (date, ISO 8601): Payment due date
- `payment_status` (enum): DRAFT | SENT | PAID | OVERDUE | CANCELLED
- `created_at` (datetime, ISO 8601): Invoice creation timestamp
- `synced_at` (datetime, ISO 8601, nullable): Last Odoo sync timestamp

**LineItem Schema** (nested):
- `description` (string): Item description
- `quantity` (decimal): Quantity of items
- `unit_price` (decimal): Price per unit
- `line_total` (decimal): quantity × unit_price
- `product_id` (integer, nullable): Odoo product ID if applicable

**Validation Rules**:
- `subtotal` must equal sum of `line_items[].line_total`
- `tax_amount` must equal `subtotal × tax_rate`
- `total` must equal `subtotal + tax_amount`
- `total >= 500` triggers audit flag (FR-011)
- `due_date` must be >= `created_at`
- All monetary values must have exactly 2 decimal places

**Relationships**:
- Links to Odoo partner (client) via `client_reference`
- Links to GoldAuditEntry for creation and sync events
- May link to AutonomousTask if created by workflow

**Storage**: `Done/invoice_<invoice_id>.json` (after completion)

---

### 3. OdooExpense

**Purpose**: Financial transaction for business expenses with Odoo integration

**Fields**:
- `expense_id` (string, UUID): Internal unique identifier
- `odoo_id` (integer, nullable): Odoo database record ID (null until synced)
- `category` (enum): MARKETING | OPERATIONS | TRAVEL | SUPPLIES | SOFTWARE | OTHER
- `subcategory` (string): Detailed categorization (e.g., "LinkedIn Ads", "Office Supplies")
- `amount` (decimal): Expense amount
- `currency` (string): Currency code (e.g., "USD")
- `date` (date, ISO 8601): Expense date
- `description` (string): Detailed description of expense
- `vendor` (string): Vendor/supplier name
- `receipt_url` (string, nullable): URL or path to receipt image
- `approval_status` (enum): PENDING | APPROVED | REJECTED
- `approved_by` (string, nullable): User who approved (for manual approvals)
- `created_at` (datetime, ISO 8601): Expense creation timestamp
- `synced_at` (datetime, ISO 8601, nullable): Last Odoo sync timestamp

**Validation Rules**:
- `amount > 0`
- `amount >= 500` triggers audit flag (FR-011)
- `category` must be in approved list
- `date` must be <= current date (no future expenses)
- All monetary values must have exactly 2 decimal places

**Relationships**:
- Links to Odoo expense category via `category`
- Links to GoldAuditEntry for creation and sync events
- May link to AutonomousTask if created by workflow
- May link to SocialMediaPost if marketing expense

**Storage**: `Done/expense_<expense_id>.json` (after completion)

---

### 4. SocialMediaPost

**Purpose**: Content published across multiple social media platforms with engagement tracking

**Fields**:
- `post_id` (string, UUID): Internal unique identifier
- `content` (string): Base content (platform-agnostic)
- `platform_variants` (object): Platform-specific formatted content
  - `twitter` (object): X-specific version
  - `facebook` (object): Facebook-specific version
  - `instagram` (object): Instagram-specific version
- `media_urls` (array of string): URLs to attached images/videos
- `hashtags` (array of string): Hashtags used (max 30 for Instagram)
- `publication_timestamps` (object): When posted to each platform
  - `twitter` (datetime, ISO 8601, nullable)
  - `facebook` (datetime, ISO 8601, nullable)
  - `instagram` (datetime, ISO 8601, nullable)
- `platform_post_ids` (object): Platform-specific post IDs
  - `twitter` (string, nullable)
  - `facebook` (string, nullable)
  - `instagram` (string, nullable)
- `engagement_metrics` (object): Aggregated engagement data
- `sentiment_scores` (object): Sentiment analysis results
- `status` (enum): DRAFT | PUBLISHING | PUBLISHED | FAILED | PARTIAL
- `created_at` (datetime, ISO 8601): Post creation timestamp
- `last_updated` (datetime, ISO 8601): Last engagement data update

**PlatformVariant Schema** (nested):
- `content` (string): Platform-formatted content
- `character_count` (integer): Content length
- `media_count` (integer): Number of attached media
- `hashtag_count` (integer): Number of hashtags

**EngagementMetrics Schema** (nested):
- `platform` (string): Platform name
- `likes` (integer): Like/favorite count
- `comments` (integer): Comment count
- `shares` (integer): Share/retweet count
- `reach` (integer): Total impressions
- `engagement_rate` (decimal): (likes + comments + shares) / reach
- `collected_at` (datetime, ISO 8601): When metrics were collected

**SentimentScores Schema** (nested):
- `overall_polarity` (decimal): -1.0 (negative) to +1.0 (positive)
- `overall_classification` (enum): POSITIVE | NEUTRAL | NEGATIVE
- `comment_sentiments` (array): Individual comment sentiment scores
- `analyzed_at` (datetime, ISO 8601): When analysis was performed

**Validation Rules**:
- `content` length <= 2200 characters (Instagram limit)
- `platform_variants.twitter.character_count` <= 280 (or 4000 for premium)
- `hashtags.length` <= 30 (Instagram limit)
- `status` = PARTIAL if published to some but not all platforms
- `engagement_rate` must be between 0.0 and 1.0

**State Transitions**:
```
DRAFT → PUBLISHING (when broadcast starts)
PUBLISHING → PUBLISHED (when all platforms succeed)
PUBLISHING → PARTIAL (when some platforms fail)
PUBLISHING → FAILED (when all platforms fail)
```

**Relationships**:
- Links to GoldAuditEntry for publication events
- May link to AutonomousTask if created by workflow
- May link to OdooExpense if marketing expense logged

**Storage**: `Done/post_<post_id>.json` (after publication)

---

### 5. GoldAuditEntry

**Purpose**: Tamper-evident log record for all autonomous actions

**Fields**:
- `entry_id` (string, UUID): Unique identifier for this log entry
- `timestamp` (datetime, ISO 8601): When action occurred (microsecond precision)
- `action_type` (enum): TASK_START | TASK_COMPLETE | STEP_EXECUTE | MCP_CALL | ERROR | DECISION
- `action_name` (string): Human-readable action name (e.g., "create_invoice", "post_to_twitter")
- `parameters` (object): Input parameters for the action
- `decision_rationale` (string): Why this action was taken (Ralph Wiggum Loop reasoning)
- `execution_result` (enum): SUCCESS | FAILURE | PARTIAL | SKIPPED
- `result_data` (object): Output data from the action
- `business_impact` (string): Assessment of business value (e.g., "$500 invoice created", "3 platforms reached")
- `error_details` (object, nullable): Error information if action failed
  - `error_type` (string): Exception class name
  - `error_message` (string): Error description
  - `stack_trace` (string): Full stack trace
  - `recovery_attempted` (boolean): Whether recovery was tried
  - `recovery_result` (string): Outcome of recovery attempt
- `related_entity_type` (string, nullable): Type of entity affected (e.g., "OdooInvoice", "SocialMediaPost")
- `related_entity_id` (string, nullable): ID of affected entity
- `task_id` (string, nullable): AutonomousTask ID if part of workflow
- `previous_entry_hash` (string): SHA-256 hash of previous log entry (tamper detection)
- `entry_hash` (string): SHA-256 hash of this entry's content

**Validation Rules**:
- `entry_id` must be unique
- `timestamp` must be >= previous entry's timestamp
- `entry_hash` must match computed hash of entry content
- `previous_entry_hash` must match previous entry's `entry_hash`
- Hash chain must be unbroken for tamper-evidence

**Hash Calculation**:
```python
import hashlib
import json

def calculate_entry_hash(entry: dict) -> str:
    # Exclude entry_hash itself from calculation
    hashable_content = {k: v for k, v in entry.items() if k != 'entry_hash'}
    content_json = json.dumps(hashable_content, sort_keys=True)
    return hashlib.sha256(content_json.encode()).hexdigest()
```

**Relationships**:
- Links to AutonomousTask via `task_id`
- Links to any entity via `related_entity_type` and `related_entity_id`
- Forms chain with previous GoldAuditEntry via `previous_entry_hash`

**Storage**: `Logs/Audit_Trail/gold_audit_YYYY-MM-DD.jsonl` (one entry per line, append-only)

---

### 6. MCPServerConnection

**Purpose**: Health and configuration tracking for MCP server integrations

**Fields**:
- `server_name` (enum): ODOO | GMAIL | LINKEDIN | TWITTER | FACEBOOK | INSTAGRAM
- `endpoint_url` (string): Base URL for the MCP server
- `health_status` (enum): HEALTHY | DEGRADED | FAILED | RECOVERING | UNKNOWN
- `auth_state` (enum): AUTHENTICATED | UNAUTHENTICATED | EXPIRED | INVALID
- `last_success` (datetime, ISO 8601, nullable): Last successful API call
- `last_failure` (datetime, ISO 8601, nullable): Last failed API call
- `consecutive_failures` (integer): Count of consecutive failures (for circuit breaker)
- `total_calls` (integer): Total API calls made
- `successful_calls` (integer): Count of successful calls
- `failed_calls` (integer): Count of failed calls
- `success_rate` (decimal): successful_calls / total_calls
- `average_response_time` (decimal): Average response time in milliseconds
- `retry_config` (object): Retry configuration
  - `max_attempts` (integer): Maximum retry attempts
  - `backoff_multiplier` (decimal): Exponential backoff multiplier
  - `max_wait` (integer): Maximum wait time in seconds
- `circuit_breaker_state` (enum): CLOSED | OPEN | HALF_OPEN
- `circuit_breaker_opened_at` (datetime, ISO 8601, nullable): When circuit breaker opened
- `fallback_options` (array of string): Alternative actions when server unavailable
- `rate_limit_info` (object, nullable): Platform-specific rate limit data
  - `limit` (integer): Requests allowed per window
  - `remaining` (integer): Requests remaining
  - `reset_at` (datetime, ISO 8601): When limit resets

**Validation Rules**:
- `consecutive_failures >= 3` triggers circuit breaker OPEN
- `success_rate < 0.5` triggers DEGRADED health status
- `consecutive_failures == 0` and `circuit_breaker_state == HALF_OPEN` → CLOSED
- `auth_state == EXPIRED` triggers re-authentication attempt

**State Transitions**:
```
HEALTHY → DEGRADED (success_rate drops below 0.5)
DEGRADED → FAILED (consecutive_failures >= 3)
FAILED → RECOVERING (circuit breaker enters HALF_OPEN)
RECOVERING → HEALTHY (successful call in HALF_OPEN state)
RECOVERING → FAILED (failed call in HALF_OPEN state)
```

**Relationships**:
- Links to GoldAuditEntry for all connection events
- Referenced by all MCP client operations

**Storage**: `Memory/mcp_connections.json` (updated in real-time)

---

## Entity Relationships Diagram

```
AutonomousTask
    ├─> GoldAuditEntry (many) - logs each step
    ├─> OdooInvoice (optional) - if workflow creates invoice
    ├─> OdooExpense (optional) - if workflow logs expense
    └─> SocialMediaPost (optional) - if workflow creates post

OdooInvoice
    ├─> GoldAuditEntry (many) - creation, sync, validation events
    └─> AutonomousTask (optional) - if created by workflow

OdooExpense
    ├─> GoldAuditEntry (many) - creation, sync events
    ├─> AutonomousTask (optional) - if created by workflow
    └─> SocialMediaPost (optional) - if marketing expense

SocialMediaPost
    ├─> GoldAuditEntry (many) - publication, engagement events
    ├─> AutonomousTask (optional) - if created by workflow
    └─> OdooExpense (optional) - if expense logged

GoldAuditEntry
    ├─> GoldAuditEntry (previous) - hash chain for tamper-evidence
    ├─> AutonomousTask (optional) - if part of workflow
    └─> Any Entity - via related_entity_type/id

MCPServerConnection
    └─> GoldAuditEntry (many) - connection events
```

## Data Flow Example: Trend to Post to Expense Workflow

1. **AutonomousTask** created with workflow "trend_to_post_to_expense"
2. **Step 1**: Detect LinkedIn trend
   - **GoldAuditEntry** logged: "STEP_EXECUTE: detect_trend"
3. **Step 2**: Create social media post
   - **SocialMediaPost** entity created
   - **MCPServerConnection** checked for Twitter, Facebook, Instagram
   - **GoldAuditEntry** logged: "MCP_CALL: post_to_twitter" (3x for each platform)
4. **Step 3**: Log marketing expense
   - **OdooExpense** entity created
   - **MCPServerConnection** checked for Odoo
   - **GoldAuditEntry** logged: "MCP_CALL: create_expense"
5. **Step 4**: Verify outcome
   - **GoldAuditEntry** logged: "DECISION: outcome_verified"
6. **AutonomousTask** marked COMPLETED
   - **GoldAuditEntry** logged: "TASK_COMPLETE"

## Storage Strategy

- **Active workflows**: `Needs_Action/state_<task_id>.json`
- **Completed tasks**: `Done/task_<task_id>.json`
- **Invoices**: `Done/invoice_<invoice_id>.json`
- **Expenses**: `Done/expense_<expense_id>.json`
- **Posts**: `Done/post_<post_id>.json`
- **Audit logs**: `Logs/Audit_Trail/gold_audit_YYYY-MM-DD.jsonl` (append-only, one entry per line)
- **MCP connections**: `Memory/mcp_connections.json` (real-time updates)

## Next Steps

1. Create MCP server contracts (contracts/*.yaml)
2. Write quickstart.md for setup and testing
3. Update agent context with new entities
4. Generate implementation tasks with /sp.tasks
