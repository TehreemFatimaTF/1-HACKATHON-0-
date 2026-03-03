# Implementation Plan: Gold Tier Autonomous Employee

**Branch**: `001-gold-tier-autonomous` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-gold-tier-autonomous/spec.md`

## Summary

Evolve the Silver Tier AI Employee into a fully autonomous Gold Tier system by implementing the Ralph Wiggum Loop (multi-step autonomous reasoning), integrating Odoo 19+ for accounting operations, expanding social media capabilities to X (Twitter), Facebook, and Instagram, and establishing comprehensive audit trails with graceful error recovery. The system will autonomously execute routine business operations (invoice creation, social media posting, expense logging) without human approval while maintaining complete transparency through Gold_Audit logging and real-time Dashboard.md updates.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Existing: watchdog, requests, python-dotenv, anthropic
- New: odoorpc (Odoo JSON-RPC client), tweepy (X/Twitter API), facebook-sdk (Meta Graph API), instagrapi (Instagram), textblob (sentiment analysis), tenacity (retry logic)

**Storage**: File-based (existing folder structure: Inbox, Needs_Action, Plans, 4_Approved, Done, Memory, Knowledge_Base, Logs/Audit_Trail) + External Odoo 19+ database (localhost:8069)

**Testing**: pytest with contract tests for MCP servers, integration tests for multi-step workflows, unit tests for core logic

**Target Platform**: Windows 10+ / Linux (cross-platform Python), localhost development with production deployment capability

**Project Type**: Single project (extending existing Silver Tier architecture)

**Performance Goals**:
- Task processing: <5 minutes for P0/P1 tasks
- Dashboard updates: <1 second
- Concurrent tasks: 100+ without degradation
- Memory usage: <500MB for standard operations

**Constraints**:
- Must maintain backward compatibility with Silver Tier folder structure
- Must preserve existing skills and watcher functionality
- Must handle MCP server failures gracefully (no cascading failures)
- Must maintain 100% financial accuracy for Odoo operations

**Scale/Scope**:
- Small business operations: 10-100 tasks/day
- 5-10 autonomous workflows active simultaneously
- 3-5 MCP server integrations (Odoo, X, Facebook, Instagram, existing Gmail/LinkedIn)
- Audit log retention: 12 months (estimated 1.2GB)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance Assessment

✅ **I. Autonomous Reasoning (Ralph Wiggum Loop)** - CORE FEATURE
- Implementation: `src/engine_gold.py` with 2D reasoning loop
- Compliance: Multi-step task execution with "next step?" and "outcome achieved?" checks

✅ **II. Error Recovery & Graceful Degradation** - REQUIRED
- Implementation: Try-except blocks with fallback paths for each MCP server
- Compliance: System continues on failure, logs errors, notifies via Dashboard.md

✅ **III. Comprehensive Audit Trail** - REQUIRED
- Implementation: `Logs/Audit_Trail/gold_audit_YYYY-MM-DD.jsonl` with structured logging
- Compliance: Every autonomous action logged with timestamp, rationale, result, impact

✅ **IV. Human-in-the-Loop Approval (Silver Tier)** - TRANSITIONING
- Implementation: Configurable autonomous action whitelist in `.env`
- Compliance: Maintains Silver Tier approval workflow for non-whitelisted actions

✅ **V. Multi-Source Intelligence Integration** - EXPANDING
- Implementation: New MCP servers for Odoo, X, Facebook, Instagram
- Compliance: All sources feed into unified Inbox → Needs_Action → Execution pipeline

✅ **VI. Priority-Driven Execution (4-Tier Matrix)** - MAINTAINED
- Implementation: Existing Company_Handbook.md priority matrix preserved
- Compliance: P0-P3 classification with sentiment analysis and financial impact

✅ **VII. Zero-Loss Data Policy** - MAINTAINED
- Implementation: Existing folder workflow preserves original data in Inbox
- Compliance: All processing creates copies, maintains lineage

✅ **VIII. Financial Intelligence & Auditing** - ENHANCED
- Implementation: Odoo integration with validation, $500+ flagging, double-entry audit
- Compliance: Tax validation, vendor cross-reference, weekly CEO briefing

✅ **IX. Observability & Monitoring** - ENHANCED
- Implementation: Real-time Dashboard.md updates, structured JSON logging
- Compliance: <1 second dashboard updates, performance metrics tracking

✅ **X. Test-First Development (NON-NEGOTIABLE)** - REQUIRED
- Implementation: Contract tests for MCP servers, integration tests for workflows
- Compliance: TDD with Red-Green-Refactor cycle for all new features

**GATE STATUS**: ✅ PASSED - All 10 principles compliant, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/001-gold-tier-autonomous/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - MCP integration patterns
├── data-model.md        # Phase 1 output - Entity schemas
├── quickstart.md        # Phase 1 output - Setup and testing guide
├── contracts/           # Phase 1 output - MCP server contracts
│   ├── odoo-mcp.yaml
│   ├── twitter-mcp.yaml
│   ├── facebook-mcp.yaml
│   └── instagram-mcp.yaml
└── checklists/
    └── requirements.md  # Quality validation (already created)
```

### Source Code (repository root)

```text
src/
├── engine_gold.py           # NEW: Ralph Wiggum Loop autonomous executor
├── watcher.py               # MODIFIED: Add autonomous mode flag
├── action_executor.py       # MODIFIED: Integrate engine_gold for autonomous tasks
├── mcp/                     # NEW: MCP server integrations
│   ├── __init__.py
│   ├── odoo_client.py       # Odoo JSON-RPC client
│   ├── twitter_client.py    # X (Twitter) API client
│   ├── facebook_client.py   # Facebook Graph API client
│   ├── instagram_client.py  # Instagram API client
│   └── base_mcp.py          # Base class with retry/fallback logic
├── skills/                  # NEW: Gold Tier skills
│   ├── odoo_sync_contacts.py
│   ├── odoo_create_invoice.py
│   ├── odoo_fetch_ledger.py
│   ├── broadcast_marketing.py
│   ├── fetch_engagement.py
│   └── generate_ceo_briefing.py
├── audit/                   # NEW: Gold Audit logging
│   ├── __init__.py
│   ├── gold_logger.py       # Structured audit logging
│   └── audit_schema.py      # Gold_Audit entry schema
└── utils/
    ├── sentiment.py         # NEW: Sentiment analysis utilities
    └── retry.py             # NEW: Retry/fallback decorators

.claude/skills/              # EXISTING: Silver Tier skills (preserved)
├── process-needs-action.md
├── request-approval.md
├── execute-approved-task.md
└── ...

tests/
├── contract/                # NEW: MCP server contract tests
│   ├── test_odoo_mcp.py
│   ├── test_twitter_mcp.py
│   ├── test_facebook_mcp.py
│   └── test_instagram_mcp.py
├── integration/             # NEW: Multi-step workflow tests
│   ├── test_autonomous_loop.py
│   ├── test_social_broadcast.py
│   └── test_accounting_flow.py
└── unit/                    # NEW: Core logic tests
    ├── test_engine_gold.py
    ├── test_sentiment.py
    └── test_retry.py

Logs/Audit_Trail/            # NEW: Gold Audit logs
└── gold_audit_YYYY-MM-DD.jsonl

.env                         # MODIFIED: Add Odoo, X, Facebook, Instagram credentials
```

**Structure Decision**: Single project structure maintained to preserve Silver Tier compatibility. New Gold Tier components added as extensions rather than replacements. MCP clients isolated in `src/mcp/` module for clean separation. Skills follow existing `.claude/skills/` pattern but Python implementations in `src/skills/` for autonomous execution.

## Complexity Tracking

> **No violations detected - this section intentionally left empty per constitution compliance**

## Phase 0: Research & Technical Discovery

### Research Objectives

1. **Odoo JSON-RPC Integration Patterns**
   - Authentication mechanisms (session-based vs API key)
   - Best practices for invoice creation and expense logging
   - Error handling for connection failures
   - Transaction rollback strategies

2. **Social Media API Integration**
   - X (Twitter) API v2 authentication and rate limits
   - Meta Graph API for Facebook/Instagram unified posting
   - Platform-specific content formatting requirements
   - Engagement metrics collection methods

3. **Multi-Step Workflow State Management**
   - State persistence patterns for long-running workflows
   - Context preservation across task steps
   - Rollback and recovery strategies
   - Outcome verification techniques

4. **Sentiment Analysis Approaches**
   - Library comparison (TextBlob vs VADER vs transformers)
   - Accuracy vs performance tradeoffs
   - Multi-language support requirements
   - Integration with priority escalation logic

5. **Graceful Degradation Patterns**
   - Circuit breaker implementation
   - Retry with exponential backoff
   - Fallback path selection
   - Health monitoring and alerting

### Research Deliverable

Output: `specs/001-gold-tier-autonomous/research.md` with decisions, rationale, and alternatives for each research area.

## Phase 1: Design & Contracts

### Data Model Design

**Entities to model** (from spec.md Key Entities):

1. **AutonomousTask**
   - Fields: task_id, workflow_steps, current_step, completed_steps, pending_steps, context_data, outcome_status, created_at, updated_at
   - State transitions: PENDING → IN_PROGRESS → COMPLETED/FAILED/PAUSED
   - Relationships: Links to Gold_Audit entries

2. **OdooInvoice**
   - Fields: invoice_id, client_reference, line_items, subtotal, tax_amount, total, due_date, payment_status, odoo_id
   - Validation rules: Tax calculation verification, $500+ flagging
   - Relationships: Links to client in Odoo, audit entries

3. **OdooExpense**
   - Fields: expense_id, category, amount, date, description, approval_status, odoo_id
   - Validation rules: Category must be in approved list
   - Relationships: Links to accounting categories, audit entries

4. **SocialMediaPost**
   - Fields: post_id, content, platform_variants (X/FB/IG), publication_timestamps, engagement_metrics, sentiment_scores
   - Platform-specific fields: character_count (X), image_urls (IG), hashtags
   - Relationships: Links to engagement data, audit entries

5. **GoldAuditEntry**
   - Fields: entry_id, timestamp (ISO 8601), action_type, parameters, decision_rationale, execution_result, business_impact, error_details
   - Validation rules: Tamper-evident (hash chain)
   - Relationships: Links to all entity types

6. **MCPServerConnection**
   - Fields: server_name, health_status, auth_state, retry_config, fallback_options, last_success, last_failure
   - Health states: HEALTHY, DEGRADED, FAILED, RECOVERING
   - Relationships: Links to audit entries for connection events

Output: `specs/001-gold-tier-autonomous/data-model.md`

### API Contracts

**MCP Server Contracts** (OpenAPI/JSON Schema format):

1. **Odoo MCP** (`contracts/odoo-mcp.yaml`)
   - `POST /odoo/invoice/create` - Create invoice with validation
   - `GET /odoo/expenses/list` - List expenses with filters
   - `GET /odoo/accounting/summary` - Get financial summary
   - `POST /odoo/contacts/sync` - Sync client/vendor contacts

2. **X (Twitter) MCP** (`contracts/twitter-mcp.yaml`)
   - `POST /twitter/post/create` - Create tweet with media
   - `GET /twitter/engagement/metrics` - Get tweet analytics
   - `GET /twitter/health` - Check API rate limits

3. **Facebook MCP** (`contracts/facebook-mcp.yaml`)
   - `POST /facebook/post/create` - Create Facebook post
   - `GET /facebook/engagement/metrics` - Get post insights
   - `GET /facebook/health` - Check API status

4. **Instagram MCP** (`contracts/instagram-mcp.yaml`)
   - `POST /instagram/post/create` - Create Instagram post with image
   - `GET /instagram/engagement/metrics` - Get post analytics
   - `GET /instagram/health` - Check API status

Output: `specs/001-gold-tier-autonomous/contracts/*.yaml`

### Quickstart Guide

**Setup and Testing Instructions**:

1. Prerequisites (Odoo installation, API credentials)
2. Environment configuration (.env setup)
3. MCP server health checks
4. Running autonomous mode for first time
5. Monitoring audit logs and dashboard
6. Troubleshooting common issues

Output: `specs/001-gold-tier-autonomous/quickstart.md`

### Agent Context Update

Run: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

This will update `CLAUDE.md` with new Gold Tier technologies and patterns.

## Phase 2: Implementation Milestones (User-Specified)

### Milestone 1: The Core Brain (Ralph Wiggum Loop)

**Objective**: Implement autonomous multi-step reasoning engine

**Components**:
- `src/engine_gold.py` - Main autonomous executor with 2D reasoning loop
- `src/watcher.py` modifications - Add autonomous mode flag and engine_gold integration
- `src/action_executor.py` modifications - Route autonomous tasks to engine_gold

**Key Features**:
- Multi-step task decomposition
- "Is there a next step?" check before completion
- "Did I achieve the final outcome?" verification
- Context preservation across steps
- Configurable autonomous action whitelist

**Testing**:
- Contract tests: N/A (internal logic)
- Integration tests: Multi-step workflow execution
- Unit tests: Step decomposition, outcome verification

**Success Criteria**: System can autonomously execute 3-step workflow (detect trend → create post → log expense) without human approval

---

### Milestone 2: Financial Foundation (Odoo 19+)

**Objective**: Integrate Odoo accounting system with error recovery

**Components**:
- `src/mcp/odoo_client.py` - JSON-RPC client with retry logic
- `src/skills/odoo_sync_contacts.py` - Sync client/vendor data
- `src/skills/odoo_create_invoice.py` - Create invoices with validation
- `src/skills/odoo_fetch_ledger.py` - Retrieve accounting summaries

**Key Features**:
- JSON-RPC connection to localhost:8069
- Invoice creation with tax validation
- Expense logging with categorization
- $500+ transaction flagging
- Local queueing on connection failure
- Exponential backoff retry

**Testing**:
- Contract tests: Odoo MCP endpoints
- Integration tests: Invoice creation → Odoo verification
- Unit tests: Tax calculation, validation logic

**Success Criteria**: System creates invoice in Odoo, validates data, and recovers gracefully from connection failure

---

### Milestone 3: Social Media Empire (X, FB, IG)

**Objective**: Unified multi-platform social media broadcasting

**Components**:
- `src/mcp/twitter_client.py` - X (Twitter) API v2 client
- `src/mcp/facebook_client.py` - Facebook Graph API client
- `src/mcp/instagram_client.py` - Instagram API client
- `src/skills/broadcast_marketing.py` - Unified posting skill
- `src/skills/fetch_engagement.py` - Engagement metrics collection
- `src/utils/sentiment.py` - Sentiment analysis utilities

**Key Features**:
- Simultaneous posting to X, Facebook, Instagram
- Platform-specific content optimization
- Rate limit handling per platform
- Graceful degradation (continue if one platform fails)
- Engagement metrics collection
- Sentiment analysis (positive/neutral/negative)

**Testing**:
- Contract tests: X, Facebook, Instagram MCP endpoints
- Integration tests: Broadcast to all platforms
- Unit tests: Content formatting, sentiment analysis

**Success Criteria**: System posts to all 3 platforms simultaneously, handles X failure gracefully, collects engagement metrics

---

### Milestone 4: The Executive Suite (Audits & Briefing)

**Objective**: Comprehensive audit logging and CEO briefing generation

**Components**:
- `src/audit/gold_logger.py` - Structured audit logging
- `src/audit/audit_schema.py` - Gold_Audit entry schema
- `src/skills/generate_ceo_briefing.py` - Weekly business intelligence report
- `Logs/Audit_Trail/` - Audit log storage

**Key Features**:
- Gold_Audit format (timestamp, action, rationale, result, impact)
- Tamper-evident log chain
- Real-time Dashboard.md updates
- Weekly CEO briefing (Sundays 6 PM)
- Financial summary from Odoo
- Social media engagement summary
- Error recovery report

**Testing**:
- Contract tests: N/A (internal logging)
- Integration tests: End-to-end audit trail verification
- Unit tests: Log formatting, tamper detection

**Success Criteria**: Every autonomous action logged, CEO briefing generates automatically with accurate data

---

### Milestone 5: Integration & Hardening

**Objective**: End-to-end testing, performance optimization, production readiness

**Components**:
- Full system integration tests
- Performance benchmarking
- Error recovery stress testing
- Documentation finalization
- Deployment guide

**Key Features**:
- 100+ concurrent task handling
- <5 minute P0/P1 task processing
- <1 second dashboard updates
- 90% autonomous completion rate
- 95% workflow success rate
- 100% financial accuracy

**Testing**:
- Contract tests: All MCP servers
- Integration tests: All user stories from spec.md
- Unit tests: All core modules
- Performance tests: Load testing, memory profiling
- Chaos tests: MCP server failure scenarios

**Success Criteria**: All 10 success criteria from spec.md met, system ready for production deployment

## Re-evaluation: Constitution Check Post-Design

*Re-check after Phase 1 design completion*

**Status**: ✅ ALL PRINCIPLES MAINTAINED

- Design preserves existing Silver Tier architecture (backward compatible)
- New components follow constitution principles (error recovery, audit trail, test-first)
- No new complexity violations introduced
- MCP server isolation enables graceful degradation
- Autonomous action whitelist maintains human oversight option

**GATE STATUS**: ✅ PASSED - Ready for `/sp.tasks` command to generate implementation tasks

## Next Steps

1. **Complete Phase 0**: Generate `research.md` with technical decisions
2. **Complete Phase 1**: Generate `data-model.md`, `contracts/*.yaml`, `quickstart.md`
3. **Update Agent Context**: Run update-agent-context.ps1
4. **Generate Tasks**: Run `/sp.tasks` to create detailed implementation task list
5. **Begin Implementation**: Start with Milestone 1 (Ralph Wiggum Loop)

**Command Completion**: Planning phase complete. Branch `001-gold-tier-autonomous` ready for task generation.
