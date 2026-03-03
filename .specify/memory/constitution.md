<!--
Sync Impact Report:
Version: 1.0.0 → 2.0.0
Change Type: MAJOR (Initial constitution establishment for Gold Tier architecture)
Modified Principles: N/A (initial creation)
Added Sections: All core principles, Development Standards, Governance
Removed Sections: None
Templates Status:
  ✅ plan-template.md - Constitution Check section aligns with principles
  ✅ spec-template.md - Requirements structure supports principle validation
  ✅ tasks-template.md - Task categorization reflects principle-driven workflow
  ⚠️ Command files - Generic guidance maintained (no agent-specific references)
Follow-up TODOs: None
-->

# Sana AI Employee Constitution

## Core Principles

### I. Autonomous Reasoning (Ralph Wiggum Loop)

The system MUST implement multi-step autonomous reasoning before completing any task. Before finishing, the agent MUST check: "Is there a next step?" and "Did I achieve the final outcome?" This prevents premature task completion and ensures thorough execution.

**Rationale**: Single-pass execution often misses follow-up actions. The 2D reasoning loop (next step + outcome verification) ensures complete task fulfillment and reduces human intervention needs.

### II. Error Recovery & Graceful Degradation

The system MUST NEVER stop on error. When an MCP server (Odoo, Gmail, LinkedIn, X/Twitter, Facebook, Instagram) fails, the agent MUST:
- Log the error with full context to audit trail
- Notify via summary in Dashboard.md
- Attempt alternative execution paths when available
- Continue with remaining tasks rather than blocking the entire workflow

**Rationale**: Production systems require resilience. External service failures should not cascade into complete system failure. Graceful degradation maintains business continuity.

### III. Comprehensive Audit Trail

The system MUST maintain detailed audit logging for every autonomous action in `Logs/Audit_Trail/`. Each log entry MUST include:
- Timestamp (ISO 8601 format)
- Action type and parameters
- Decision rationale
- Execution result (success/failure)
- Business impact assessment

**Rationale**: Autonomous systems require transparency for debugging, compliance, and trust-building. Complete audit trails enable post-hoc analysis and continuous improvement.

### IV. Human-in-the-Loop Approval (Silver Tier)

For Silver Tier operations, the system MUST:
- Generate execution plans in `/Plans` folder
- Wait for explicit human approval before execution
- Move approved plans to `/4_Approved` folder
- Execute only approved actions
- Maintain approval audit log with timestamps

**Rationale**: During transition to full autonomy, human oversight ensures safety and builds confidence. Approval workflow provides learning data for future autonomous decision-making.

### V. Multi-Source Intelligence Integration

The system MUST integrate data from multiple sources through MCP servers:
- **Local Files**: Filesystem watcher for `/Inbox` folder
- **Email**: Gmail MCP for inbox monitoring and sending
- **Social Media**: LinkedIn, Facebook, Instagram, Twitter/X for posting and monitoring
- **Business Systems**: Odoo MCP for accounting, invoices, expenses

All sources MUST feed into unified processing pipeline: Inbox → Needs_Action → Plans → Execution.

**Rationale**: Business intelligence requires aggregating signals from multiple channels. Unified processing ensures consistent prioritization and prevents information silos.

### VI. Priority-Driven Execution (4-Tier Matrix)

The system MUST classify all tasks using the 4-Tier Priority Matrix:
- **P0 (Critical/Revenue)**: Immediate action + alert (bank issues, overdue invoices)
- **P1 (Client Retention)**: Same-day processing (client queries, feedback)
- **P2 (Operational)**: Next 24 hours (internal reports, documentation)
- **P3 (General/Growth)**: Weekly batching (LinkedIn ideas, learning material)

Priority MUST be determined by sentiment analysis, financial impact, and deadline proximity.

**Rationale**: Not all tasks are equal. Intelligent prioritization maximizes business value and prevents revenue loss from delayed critical actions.

### VII. Zero-Loss Data Policy

The system MUST treat all original data as "Gold Source" and NEVER modify it. Processing workflow MUST:
- Preserve original files in `/Inbox` or source location
- Create processed copies in `/Needs_Action`
- Maintain complete lineage from source to output
- Enable rollback to any previous state

**Rationale**: Data integrity is non-negotiable. Immutable source data enables debugging, compliance audits, and recovery from processing errors.

### VIII. Financial Intelligence & Auditing

For all financial operations (invoices, expenses, payments), the system MUST:
- Validate calculations and tax amounts
- Cross-reference against approved vendor/client lists
- Flag transactions exceeding $500 for review
- Maintain double-entry audit trail
- Generate weekly CEO briefing with financial summary

**Rationale**: Financial errors have direct business impact. Automated validation catches mistakes before they become costly problems.

### IX. Observability & Monitoring

The system MUST provide real-time visibility through:
- **Dashboard.md**: Executive summary with business metrics, pending tasks, completion rates
- **Structured Logging**: JSON-formatted logs for all operations
- **Performance Metrics**: Processing time, completion rate, error rate
- **Alert System**: Proactive notifications for P0/P1 tasks and system failures

**Rationale**: Autonomous systems require continuous monitoring. Real-time visibility enables rapid response to issues and performance optimization.

### X. Test-First Development (NON-NEGOTIABLE)

For all new features and integrations, the system MUST follow TDD:
- Tests written FIRST and approved by user
- Tests MUST fail before implementation
- Red-Green-Refactor cycle strictly enforced
- Contract tests for all MCP server integrations
- Integration tests for cross-module workflows

**Rationale**: Autonomous systems have high reliability requirements. Test-first development catches bugs early and provides regression safety for continuous evolution.

## Development Standards

### Code Quality
- All code MUST be self-documenting with clear variable/function names
- Complex logic MUST include inline comments explaining "why" not "what"
- All functions MUST have single responsibility
- Error messages MUST be actionable and include context

### Security Requirements
- Secrets MUST be stored in `.env` files (never committed)
- All external API calls MUST use authentication
- User data MUST be encrypted at rest
- Audit logs MUST be tamper-evident

### Performance Standards
- Task processing MUST complete within 5 minutes for P0/P1 tasks
- Dashboard updates MUST complete within 1 second
- System MUST handle 100+ concurrent tasks without degradation
- Memory usage MUST stay below 500MB for standard operations

### Integration Standards
- All MCP servers MUST implement graceful degradation
- API calls MUST include timeout and retry logic
- Failed integrations MUST NOT block other operations
- Integration health MUST be monitored and reported

## Workflow Architecture

### Folder-Based State Machine
The system operates through a structured folder workflow:

1. **`/Inbox`**: Raw perception layer - all incoming data lands here
2. **`/Needs_Action`**: Classified tasks with metadata and priority
3. **`/Plans`**: AI-generated execution strategies awaiting approval
4. **`/4_Approved`**: Human-approved plans ready for execution
5. **`/Done`**: Completed tasks with execution logs and outputs
6. **`/Memory`**: Long-term preferences and learned behaviors
7. **`/Knowledge_Base`**: Business documents and domain knowledge
8. **`/Logs/Audit_Trail`**: Comprehensive action and decision logs

### Processing Pipeline
Each task MUST flow through:
1. **Perception**: Detect and ingest from source
2. **Classification**: Apply priority matrix and sentiment analysis
3. **Planning**: Generate execution strategy with business impact
4. **Approval**: Human review (Silver Tier) or autonomous decision (Gold Tier)
5. **Execution**: Perform actions with error recovery
6. **Verification**: Confirm outcome and update dashboard
7. **Archival**: Move to Done with complete audit trail

## Governance

### Amendment Process
1. Proposed changes MUST be documented with rationale
2. Impact analysis MUST be performed on dependent templates
3. Version MUST be incremented per semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes
   - **MINOR**: New principles or material expansions
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements
4. All dependent artifacts MUST be updated before amendment is ratified
5. Amendment MUST be approved by project owner

### Compliance Review
- All PRs MUST verify compliance with constitution principles
- Complexity violations MUST be explicitly justified
- Constitution supersedes all other practices and documentation
- Quarterly review MUST assess principle effectiveness and identify needed updates

### Version Control
- Constitution changes MUST be tracked in git with detailed commit messages
- Each version MUST include Sync Impact Report documenting changes
- Breaking changes MUST include migration guide for existing implementations

### Runtime Guidance
For day-to-day development guidance and agent-specific instructions, refer to `CLAUDE.md` in the repository root. The constitution defines "what" and "why"; runtime guidance defines "how" for specific contexts.

**Version**: 2.0.0 | **Ratified**: 2026-02-20 | **Last Amended**: 2026-02-20
