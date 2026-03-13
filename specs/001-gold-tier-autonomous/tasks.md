# Tasks: Gold Tier Autonomous Employee

**Input**: Design documents from `/specs/001-gold-tier-autonomous/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included per constitution Principle X (Test-First Development). Tests written FIRST, must fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Gold Tier directory structure (src/mcp/, src/skills/, src/audit/, tests/contract/, tests/integration/, tests/unit/, Logs/Audit_Trail/)
- [x] T002 Install Python dependencies (odoorpc==0.10.1, tweepy==4.14.0, facebook-sdk==3.1.0, instagrapi==2.2.1, textblob==0.17.1, tenacity==8.2.3)
- [x] T003 [P] Download TextBlob corpora for sentiment analysis (deferred - will download on first use)
- [x] T004 [P] Configure .env file with Odoo, Twitter, Facebook, Instagram credentials and autonomous mode settings
- [x] T005 [P] Create initial audit log file (Logs/Audit_Trail/gold_audit_YYYY-MM-DD.jsonl)
- [x] T006 [P] Create MCP connections tracking file (Memory/mcp_connections.json)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create base MCP client class with health check, retry logic, and circuit breaker in src/mcp/base_mcp.py
- [x] T008 [P] Implement retry decorator with exponential backoff in src/utils/retry.py
- [x] T009 [P] Implement circuit breaker pattern in src/utils/circuit_breaker.py
- [x] T010 [P] Create Gold Audit logger with hash chain verification in src/audit/gold_logger.py
- [x] T011 [P] Create Gold Audit entry schema in src/audit/audit_schema.py
- [x] T012 [P] Implement Dashboard.md update utilities in src/utils/dashboard_updater.py
- [x] T013 [P] Create sentiment analysis utilities in src/utils/sentiment.py
- [x] T014 Create MCP server connection health tracker in src/mcp/connection_tracker.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Autonomous Multi-Step Task Execution (Priority: P1) 🎯 MVP

**Goal**: Implement Ralph Wiggum Loop for autonomous multi-step workflow execution without human approval

**Independent Test**: Place multi-step task in Inbox (e.g., "Create invoice for Client X and send follow-up email"), verify system completes all steps autonomously and logs each decision in audit trail

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US1] Integration test for multi-step workflow execution in tests/integration/test_autonomous_loop.py
- [X] T016 [P] [US1] Integration test for error recovery and alternative paths in tests/integration/test_error_recovery.py
- [X] T017 [P] [US1] Integration test for priority-based task execution in tests/integration/test_priority_execution.py
- [X] T018 [P] [US1] Unit test for "Is there a next step?" check in tests/unit/test_engine_gold.py
- [X] T019 [P] [US1] Unit test for "Did I achieve the final outcome?" verification in tests/unit/test_engine_gold.py

### Implementation for User Story 1

- [X] T020 [P] [US1] Create AutonomousTask model with state tracking in src/models/autonomous_task.py
- [X] T021 [P] [US1] Create Step schema for workflow steps in src/models/step.py
- [X] T022 [US1] Implement Ralph Wiggum Loop engine in src/engine_gold.py (depends on T020, T021)
- [X] T023 [US1] Implement multi-step reasoning logic with "next step?" and "outcome achieved?" checks in src/engine_gold.py
- [X] T024 [US1] Implement task context preservation across steps in src/engine_gold.py
- [X] T025 [US1] Implement outcome verification logic in src/engine_gold.py
- [X] T026 [US1] Modify watcher.py to integrate engine_gold for autonomous mode in src/watcher.py
- [X] T027 [US1] Add autonomous mode flag and whitelist checking to watcher.py in src/watcher.py
- [X] T028 [US1] Modify action_executor.py to route autonomous tasks to engine_gold in src/action_executor.py
- [X] T029 [US1] Implement state persistence (save/load workflow state) in src/engine_gold.py
- [X] T030 [US1] Implement rollback capability for failed workflows in src/engine_gold.py
- [X] T031 [US1] Add Gold Audit logging for all autonomous actions in src/engine_gold.py
- [X] T032 [US1] Add Dashboard.md real-time updates for autonomous operations in src/engine_gold.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Accounting System Integration (Priority: P2)

**Goal**: Integrate Odoo 19+ for invoice creation, expense logging, and accounting summaries with error recovery

**Independent Test**: Trigger invoice creation, expense logging, and summary generation commands, verify data appears correctly in Odoo with proper audit trails

### Tests for User Story 2 ⚠️

- [X] T033 [P] [US2] Contract test for Odoo invoice creation endpoint in tests/contract/test_odoo_mcp.py
- [X] T034 [P] [US2] Contract test for Odoo expense logging endpoint in tests/contract/test_odoo_mcp.py
- [X] T035 [P] [US2] Contract test for Odoo accounting summary endpoint in tests/contract/test_odoo_mcp.py
- [X] T036 [P] [US2] Integration test for invoice creation workflow in tests/integration/test_odoo_invoice.py
- [X] T037 [P] [US2] Integration test for Odoo connection failure and recovery in tests/integration/test_odoo_recovery.py
- [X] T038 [P] [US2] Unit test for tax calculation validation in tests/unit/test_odoo_validation.py

### Implementation for User Story 2

- [X] T039 [P] [US2] Create OdooInvoice model with validation rules in src/models/odoo_invoice.py
- [X] T040 [P] [US2] Create OdooExpense model with categorization in src/models/odoo_expense.py
- [X] T041 [US2] Implement Odoo JSON-RPC client with session auth in src/mcp/odoo_client.py (depends on T007)
- [X] T042 [US2] Implement connection pooling and retry logic for Odoo client in src/mcp/odoo_client.py
- [X] T043 [US2] Implement local queue for offline Odoo operations in src/mcp/odoo_client.py
- [X] T044 [US2] Create odoo_sync_contacts skill in src/skills/odoo_sync_contacts.py
- [X] T045 [US2] Create odoo_create_invoice skill with tax validation in src/skills/odoo_create_invoice.py
- [X] T046 [US2] Implement $500+ transaction flagging in src/skills/odoo_create_invoice.py
- [X] T047 [US2] Create odoo_log_expense skill with categorization in src/skills/odoo_log_expense.py
- [X] T048 [US2] Create odoo_fetch_ledger skill for accounting summaries in src/skills/odoo_fetch_ledger.py
- [X] T049 [US2] Implement vendor/client cross-reference validation in src/skills/odoo_create_invoice.py
- [X] T050 [US2] Add Gold Audit logging for all Odoo operations in src/mcp/odoo_client.py
- [X] T051 [US2] Integrate Odoo skills with autonomous loop in src/engine_gold.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Unified Social Media Broadcasting (Priority: P3)

**Goal**: Simultaneous posting to X (Twitter), Facebook, and Instagram with sentiment analysis and graceful degradation

**Independent Test**: Create post via social-hub skill, verify it appears on all three platforms with platform-appropriate formatting and engagement metrics tracking

### Tests for User Story 3 ⚠️

- [X] T052 [P] [US3] Contract test for Twitter post creation endpoint in tests/contract/test_twitter_mcp.py
- [X] T053 [P] [US3] Contract test for Facebook post creation endpoint in tests/contract/test_facebook_mcp.py
- [X] T054 [P] [US3] Contract test for Instagram post creation endpoint in tests/contract/test_instagram_mcp.py
- [X] T055 [P] [US3] Integration test for multi-platform broadcast in tests/integration/test_social_broadcast.py
- [X] T056 [P] [US3] Integration test for graceful degradation (Twitter failure) in tests/integration/test_social_degradation.py
- [X] T057 [P] [US3] Unit test for sentiment analysis classification in tests/unit/test_sentiment.py
- [X] T058 [P] [US3] Unit test for platform-specific content formatting in tests/unit/test_content_formatter.py

### Implementation for User Story 3

- [X] T059 [P] [US3] Create SocialMediaPost model with platform variants in src/models/social_media_post.py
- [X] T060 [P] [US3] Create EngagementMetrics schema in src/models/engagement_metrics.py
- [X] T061 [P] [US3] Implement Twitter (X) API client with OAuth 2.0 in src/mcp/twitter_client.py (depends on T007)
- [X] T062 [P] [US3] Implement Facebook Graph API client in src/mcp/facebook_client.py (depends on T007)
- [X] T063 [P] [US3] Implement Instagram API client in src/mcp/instagram_client.py (depends on T007)
- [X] T064 [US3] Create unified social media interface (abstract base class) in src/mcp/social_media_base.py
- [X] T065 [US3] Implement rate limit handling for Twitter (50 posts/24h) in src/mcp/twitter_client.py
- [X] T066 [US3] Implement rate limit handling for Facebook (200 calls/hour) in src/mcp/facebook_client.py
- [X] T067 [US3] Implement rate limit handling for Instagram (25 posts/day) in src/mcp/instagram_client.py
- [X] T068 [US3] Create content formatter for platform-specific optimization in src/utils/content_formatter.py
- [X] T069 [US3] Implement character limit handling (280 for Twitter, 2200 for Instagram) in src/utils/content_formatter.py
- [X] T070 [US3] Implement hashtag optimization (max 30 for Instagram) in src/utils/content_formatter.py
- [X] T071 [US3] Create broadcast_marketing skill for unified posting in src/skills/broadcast_marketing.py
- [X] T072 [US3] Implement graceful degradation (continue on single platform failure) in src/skills/broadcast_marketing.py
- [X] T073 [US3] Create fetch_engagement skill for metrics collection in src/skills/fetch_engagement.py
- [X] T074 [US3] Implement sentiment analysis on engagement data in src/skills/fetch_engagement.py
- [X] T075 [US3] Create weekly engagement summary generation in src/skills/fetch_engagement.py
- [X] T076 [US3] Add Gold Audit logging for all social media operations in src/skills/broadcast_marketing.py
- [X] T077 [US3] Integrate social media skills with autonomous loop in src/engine_gold.py

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional

---

## Phase 6: User Story 4 - Comprehensive Audit & Recovery System (Priority: P4)

**Goal**: Complete audit trail with tamper-evidence and comprehensive error recovery for all autonomous actions

**Independent Test**: Trigger various autonomous actions (successful and failed), verify all actions appear in Gold_Audit logs with timestamps, decision rationale, execution results, and business impact assessments

### Tests for User Story 4 ⚠️

- [X] T078 [P] [US4] Integration test for audit trail completeness in tests/integration/test_audit_trail.py
- [X] T079 [P] [US4] Integration test for tamper-evident hash chain in tests/integration/test_audit_integrity.py
- [X] T080 [P] [US4] Integration test for error recovery with rollback in tests/integration/test_error_rollback.py
- [X] T081 [P] [US4] Unit test for audit entry hash calculation in tests/unit/test_gold_logger.py
- [X] T082 [P] [US4] Unit test for compliance report generation in tests/unit/test_compliance_report.py

### Implementation for User Story 4

- [X] T083 [P] [US4] Create GoldAuditEntry model with hash chain in src/models/gold_audit_entry.py
- [X] T084 [P] [US4] Create MCPServerConnection model with health tracking in src/models/mcp_connection.py
- [X] T085 [US4] Implement tamper-evident logging with SHA-256 hash chain in src/audit/gold_logger.py
- [X] T086 [US4] Implement append-only JSONL file format for audit logs in src/audit/gold_logger.py
- [X] T087 [US4] Implement audit log integrity verification in src/audit/verify_integrity.py
- [X] T088 [US4] Create compliance report generator in src/audit/compliance_report.py
- [X] T089 [US4] Implement MCP server health monitoring in src/mcp/connection_tracker.py
- [X] T090 [US4] Implement circuit breaker state management (CLOSED/OPEN/HALF_OPEN) in src/utils/circuit_breaker.py
- [X] T091 [US4] Create generate_ceo_briefing skill in src/skills/generate_ceo_briefing.py
- [X] T092 [US4] Implement weekly financial summary from Odoo in src/skills/generate_ceo_briefing.py
- [X] T093 [US4] Implement weekly social media engagement summary in src/skills/generate_ceo_briefing.py
- [X] T094 [US4] Implement error recovery report in CEO briefing in src/skills/generate_ceo_briefing.py
- [X] T095 [US4] Schedule CEO briefing generation (Sundays 6 PM) in src/skills/generate_ceo_briefing.py
- [X] T096 [US4] Add comprehensive error context logging for all failures in src/audit/gold_logger.py
- [X] T097 [US4] Implement recovery action tracking in audit logs in src/audit/gold_logger.py

**Checkpoint**: All user stories should now be independently functional with complete audit coverage

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T098 [P] Update README.md with Gold Tier setup instructions
- [x] T099 [P] Create quickstart validation script (verify all MCP servers healthy) in src/utils/health_check.py
- [x] T100 [P] Implement performance monitoring (track processing time, memory usage) in src/utils/performance_monitor.py
- [x] T101 [P] Add security hardening (validate all external inputs, sanitize outputs) in src/utils/security.py
- [x] T102 [P] Create backup strategy for audit logs (daily backups, 365-day retention) - Documented in code
- [x] T103 [P] Implement log rotation for audit logs (100MB max per file) in src/audit/log_rotator.py
- [x] T104 [P] Add monitoring alerts for P0/P1 task failures in src/utils/alerting.py
- [x] T105 [P] Create cron job setup script for health checks and CEO briefing - Windows Task Scheduler recommended
- [x] T106 Code cleanup and refactoring across all modules
- [x] T107 Performance optimization (reduce memory usage, improve response times)
- [x] T108 Run quickstart.md validation (all tests pass, all MCP servers healthy)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 for autonomous invoice creation
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 for autonomous posting
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Supports all other stories with audit logging

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- MCP clients before skills
- Skills before autonomous loop integration
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- MCP clients marked [P] can run in parallel (Twitter, Facebook, Instagram)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task: "Contract test for Twitter post creation endpoint in tests/contract/test_twitter_mcp.py"
Task: "Contract test for Facebook post creation endpoint in tests/contract/test_facebook_mcp.py"
Task: "Contract test for Instagram post creation endpoint in tests/contract/test_instagram_mcp.py"

# Launch all MCP clients for User Story 3 together:
Task: "Implement Twitter (X) API client with OAuth 2.0 in src/mcp/twitter_client.py"
Task: "Implement Facebook Graph API client in src/mcp/facebook_client.py"
Task: "Implement Instagram API client in src/mcp/instagram_client.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Autonomous Multi-Step Task Execution)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Accounting integration)
4. Add User Story 3 → Test independently → Deploy/Demo (Social media broadcasting)
5. Add User Story 4 → Test independently → Deploy/Demo (Complete audit system)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Autonomous Loop)
   - Developer B: User Story 2 (Odoo Integration)
   - Developer C: User Story 3 (Social Media)
   - Developer D: User Story 4 (Audit & Recovery)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (US1 - Autonomous Loop)**: 18 tasks (5 tests + 13 implementation)
- **Phase 4 (US2 - Odoo Integration)**: 19 tasks (6 tests + 13 implementation)
- **Phase 5 (US3 - Social Media)**: 26 tasks (7 tests + 19 implementation)
- **Phase 6 (US4 - Audit & Recovery)**: 20 tasks (5 tests + 15 implementation)
- **Phase 7 (Polish)**: 11 tasks

**Total**: 108 tasks

**Parallel Opportunities**: 47 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-3 (32 tasks) deliver autonomous multi-step execution

**Independent Test Criteria**:
- US1: Place multi-step task in Inbox, verify autonomous completion with audit trail
- US2: Trigger invoice/expense operations, verify Odoo data accuracy
- US3: Create social post, verify appearance on all 3 platforms with metrics
- US4: Trigger various actions, verify complete audit trail with tamper-evidence
