<!--
Sync Impact Report:
Version: 2.0.0 → 3.0.0
Change Type: MAJOR (Architectural elevation to PLATINUM-tier with expanded governance)
Modified Principles:
  - Principle I: Autonomous Reasoning → Enhanced with deterministic reasoning requirements
  - Principle V: Multi-Source Intelligence → Expanded with explicit interface contracts
  - Development Standards → Elevated to Architecture Principles with strict modularity rules
Added Sections:
  - Section 1: Core Mission (explicit FTE definition)
  - Section 2: Architecture Principles (module isolation, interface contracts, async patterns)
  - Section 4: Memory Governance (structured knowledge management)
  - Section 7: Modularity Standards (layer separation and boundaries)
  - Section 10: Evolution Policy (extensibility and future-proofing)
  - Expanded Security & Privacy Principles (local-first, permission boundaries)
Removed Sections: None (all existing principles preserved and enhanced)
Templates Status:
  ✅ plan-template.md - Aligns with enhanced architectural principles
  ✅ spec-template.md - Supports modular design requirements
  ✅ tasks-template.md - Reflects test-first and modularity standards
  ⚠️ Command files - May need updates to reference new modularity standards
Follow-up TODOs:
  - Review all MCP server implementations for interface contract compliance
  - Audit existing modules for architecture principle violations
  - Update developer onboarding docs to reference PLATINUM-tier standards
-->

# Personal AI Employee Constitution - PLATINUM Tier

## Section 1: Core Mission

**Purpose**: The Personal AI Employee system operates as a fully autonomous Digital Full-Time Equivalent (FTE) that manages personal and business operations through AI-driven reasoning, proactive monitoring, and tool-based execution.

**Role Definition**: This system functions as a digital worker capable of:
- Autonomous perception of inputs across multiple channels (email, files, social media, business systems)
- Intelligent reasoning about task priority, dependencies, and execution strategies
- Proactive action execution through MCP (Model Context Protocol) servers and local tools
- Continuous learning from outcomes to improve decision quality
- Escalation to human oversight when confidence thresholds are not met

**Success Criteria**: The system succeeds when it reduces human cognitive load, prevents revenue loss through timely action, maintains complete operational transparency, and operates reliably without constant supervision.

## Section 2: Architecture Principles

### 2.1 Module Isolation Mandate

Every feature MUST begin as an isolated module before integration. Modules are defined as:
- Self-contained units with explicit boundaries
- Single responsibility (one domain concern per module)
- No direct dependencies on other modules' internal implementation
- Testable in isolation without external system dependencies

**Enforcement**: Code reviews MUST reject PRs that violate module boundaries. Integration tests MUST verify module isolation.

### 2.2 Interface Contract Discipline

Modules communicate ONLY through explicit, versioned interfaces. All interfaces MUST:
- Define input/output schemas using typed data structures (Pydantic models, TypedDicts)
- Specify error conditions and exception types
- Document performance characteristics (expected latency, resource usage)
- Version using semantic versioning (breaking changes require MAJOR bump)
- Include contract tests validating interface behavior

**Rationale**: Explicit interfaces enable independent module evolution, prevent coupling, and provide clear integration points for testing and debugging.

### 2.3 Async Operation Standards

All asynchronous operations MUST use structured error handling with Result patterns:
- Return `Result[T, E]` types (success value or error) instead of raising exceptions
- Chain operations using monadic composition (map, flatMap, recover)
- Timeout all external calls with explicit duration limits
- Implement circuit breakers for external service calls
- Log all async operation lifecycle events (start, success, failure, timeout)

**Rationale**: Async operations are inherently unreliable. Structured error handling makes failure modes explicit and prevents silent failures.

### 2.4 Repository Layer Isolation

NO direct database or file system access outside the repository layer. All data access MUST:
- Flow through repository interfaces (e.g., `TaskRepository`, `AuditRepository`)
- Use dependency injection to provide repositories to business logic
- Abstract storage implementation details (SQL, NoSQL, filesystem, cloud)
- Support transaction boundaries and rollback semantics
- Implement optimistic locking for concurrent access

**Rationale**: Repository isolation enables storage migration, simplifies testing with mocks, and centralizes data access patterns.

### 2.5 Event-Driven Agent Architecture

Agents MUST operate event-driven using watchers. The architecture requires:
- **Watchers**: Detect events from sources (filesystem, email, API webhooks)
- **Event Bus**: Publish events to interested subscribers
- **Handlers**: Process events asynchronously with retry logic
- **State Machine**: Track task progression through workflow stages
- **Idempotency**: Handle duplicate events gracefully

**Rationale**: Event-driven architecture decouples producers from consumers, enables parallel processing, and supports system evolution without breaking existing integrations.

### 2.6 Deterministic AI Reasoning

All AI reasoning MUST remain deterministic and auditable:
- Log all LLM prompts with input context and parameters
- Record model responses with timestamps and token usage
- Store reasoning chains (chain-of-thought) for complex decisions
- Enable replay of decisions from logged context
- Version prompt templates with semantic versioning

**Rationale**: Non-deterministic AI systems are impossible to debug. Deterministic reasoning with complete audit trails enables root cause analysis and continuous improvement.

## Section 3: Autonomy Rules

### 3.1 Proactive Action Mandate

The AI agent MUST act proactively when watchers detect events. Reactive-only behavior is prohibited. The agent MUST:
- Monitor all configured input sources continuously
- Classify and prioritize detected events within 30 seconds
- Generate execution plans without human prompting
- Execute approved actions autonomously (Gold Tier) or queue for approval (Silver Tier)

### 3.2 Ralph Wiggum Loop (Multi-Step Reasoning)

The system MUST implement multi-step autonomous reasoning before completing any task. Before finishing, the agent MUST check:
1. "Is there a next step?" - Identify follow-up actions
2. "Did I achieve the final outcome?" - Verify goal completion
3. "Are there side effects to handle?" - Check for cascading tasks

This prevents premature task completion and ensures thorough execution.

**Rationale**: Single-pass execution often misses follow-up actions. The 2D reasoning loop ensures complete task fulfillment and reduces human intervention needs.

### 3.3 Confidence-Based Escalation

The agent MUST escalate to human-in-the-loop when confidence is low. Escalation triggers:
- Ambiguous task requirements (multiple valid interpretations)
- High-risk actions (financial transactions >$500, data deletion, external communications)
- Novel scenarios not covered by training data or memory
- Conflicting priorities requiring business judgment
- Error recovery requiring domain expertise

Escalation MUST include: context summary, confidence score, proposed options, and risk assessment.

### 3.4 Traceable Decision Logs

Every autonomous decision MUST generate a structured log entry containing:
- Decision point identifier (task ID, step number)
- Input context (data, constraints, priorities)
- Reasoning process (chain-of-thought, alternatives considered)
- Selected action with rationale
- Confidence score (0.0-1.0)
- Execution outcome (success/failure with details)

Logs MUST be queryable by task, date, decision type, and outcome for post-hoc analysis.

## Section 4: Memory Governance

### 4.1 Structured Knowledge Storage

All long-term knowledge MUST be stored in structured markdown inside the Obsidian vault. Memory structure:
- **`/Memory`**: Agent preferences, learned behaviors, user instructions
- **`/Knowledge_Base`**: Business documents, domain knowledge, reference material
- **`/Templates`**: Reusable document templates and workflows
- **`/Logs/Audit_Trail`**: Immutable action logs with hash chains

### 4.2 Human-Readable Requirement

Memory MUST be human-readable and version controlled:
- Use markdown with consistent formatting (headings, lists, tables)
- Avoid binary formats or proprietary encodings
- Include metadata headers (created, modified, tags, links)
- Link related documents using wiki-style links `[[Document Name]]`
- Commit all memory changes to git with descriptive messages

**Rationale**: Human-readable memory enables manual inspection, debugging, and knowledge transfer. Version control provides audit trail and rollback capability.

### 4.3 Knowledge-Referenced Decisions

AI decisions MUST reference stored knowledge when possible:
- Check `/Memory` for user preferences before making choices
- Consult `/Knowledge_Base` for domain-specific rules
- Reference past decisions in `/Logs/Audit_Trail` for consistency
- Update memory when new patterns or preferences are learned

**Rationale**: Knowledge-referenced decisions improve consistency, reduce hallucination, and enable continuous learning.

### 4.4 Memory Lifecycle Management

Memory MUST be actively managed to prevent staleness:
- Review memory quarterly for outdated information
- Archive obsolete knowledge to `/Archive` with timestamp
- Consolidate duplicate or conflicting entries
- Validate external references (URLs, file paths) remain valid

## Section 5: Security & Privacy Principles

### 5.1 Local-First Architecture

The system MUST be local-first with minimal external dependencies:
- All core processing runs on local machine
- Data stored locally in Obsidian vault and local databases
- External services used only for specific integrations (email, social media, accounting)
- System MUST function in offline mode with graceful degradation

**Rationale**: Local-first architecture maximizes privacy, reduces latency, eliminates cloud vendor lock-in, and ensures data sovereignty.

### 5.2 Sensitive Data Protection

Sensitive data MUST NEVER be sent to third-party services unnecessarily:
- PII (Personally Identifiable Information) stays local unless explicitly required for task
- Financial data transmitted only to authorized accounting systems (Odoo)
- Credentials stored in `.env` files with restrictive permissions (600)
- API keys rotated quarterly and never logged in plaintext

### 5.3 Explicit Permission Boundaries

All integrations MUST use explicit permission boundaries:
- OAuth scopes limited to minimum required permissions
- MCP servers declare required permissions in manifest
- User approval required for permission escalation
- Permission grants logged in audit trail with justification

### 5.4 Tamper-Evident Audit Logging

Audit logs MUST be tamper-evident using cryptographic hash chains:
- Each log entry includes hash of previous entry
- Root hash stored in secure location (git commit, external service)
- Tampering detection on every log read operation
- Alerts triggered on hash chain validation failure

**Rationale**: Tamper-evident logs provide non-repudiation for autonomous actions and enable forensic analysis.

## Section 6: Observability & Monitoring

### 6.1 Real-Time Visibility

The system MUST provide real-time visibility through:
- **Dashboard.md**: Executive summary with business metrics, pending tasks, completion rates
- **Structured Logging**: JSON-formatted logs for all operations (timestamp, level, module, message, context)
- **Performance Metrics**: Processing time, completion rate, error rate, resource usage
- **Alert System**: Proactive notifications for P0/P1 tasks and system failures

### 6.2 Debuggability Mandate

Every component MUST be debuggable:
- Log all inputs and outputs at module boundaries
- Include correlation IDs for tracing requests across modules
- Provide debug mode with verbose logging (disabled in production)
- Support log level configuration per module
- Enable log filtering by task, module, time range, severity

### 6.3 Explainable Outputs

All AI-generated outputs MUST be explainable:
- Include reasoning summary with key decision factors
- Reference source data used in decision
- Provide confidence scores for predictions
- Link to relevant memory or knowledge base entries
- Enable "explain this decision" queries on any output

**Rationale**: Explainability builds trust, enables debugging, and supports continuous improvement through feedback loops.

## Section 7: Modularity Standards

### 7.1 Layer Separation

The system MUST maintain strict separation between layers:

**Layer 1: Watchers (Input Layer)**
- Detect events from sources (filesystem, email, API)
- Normalize events to standard format
- Publish to event bus
- NO business logic or decision-making

**Layer 2: Reasoning Agents (Business Logic Layer)**
- Receive events from event bus
- Apply business rules and AI reasoning
- Generate execution plans
- Make prioritization decisions
- NO direct I/O or external service calls

**Layer 3: Tool Executors (Action Layer)**
- Execute actions through MCP servers
- Handle retries and error recovery
- Report execution results
- NO business logic or decision-making

**Layer 4: Memory Layer (Persistence Layer)**
- Store and retrieve structured knowledge
- Maintain audit logs
- Provide query interfaces
- NO business logic

**Layer 5: User Interface (Presentation Layer)**
- Display dashboard and reports
- Accept user input and approvals
- Render visualizations
- NO business logic

**Enforcement**: Dependencies MUST flow downward only (UI → Reasoning → Executors → Memory). Upward dependencies prohibited.

### 7.2 Interface Contracts

All inter-layer communication MUST use typed interfaces:
- Define schemas using Pydantic models or TypedDicts
- Version interfaces with semantic versioning
- Document breaking changes in CHANGELOG
- Maintain backward compatibility for MINOR/PATCH versions
- Provide migration guides for MAJOR version bumps

### 7.3 Dependency Injection

All dependencies MUST be injected, not instantiated:
- Use constructor injection for required dependencies
- Use setter injection for optional dependencies
- Provide dependency injection container for wiring
- Support mock injection for testing
- Avoid service locator pattern (anti-pattern)

**Rationale**: Dependency injection enables testing, reduces coupling, and makes dependencies explicit.

## Section 8: Reliability Rules

### 8.1 No Silent Failures

The system MUST NEVER fail silently. Every error MUST:
- Generate a log entry with full context
- Update dashboard with error status
- Trigger alert for P0/P1 task failures
- Provide actionable error message
- Include recovery suggestions

### 8.2 Structured Success/Failure Output

Every action MUST produce structured success or failure output:
- Use `Result[T, E]` types for all operations
- Include execution metadata (duration, resource usage)
- Provide detailed error information (type, message, stack trace, context)
- Enable error aggregation and analysis
- Support retry decision logic

### 8.3 Retry Logic for External Systems

All external system calls MUST implement retry logic:
- Exponential backoff with jitter (1s, 2s, 4s, 8s)
- Maximum retry attempts (3-5 depending on operation criticality)
- Circuit breaker to prevent cascade failures
- Fallback strategies for degraded operation
- Timeout enforcement (5s for API calls, 30s for batch operations)

### 8.4 Graceful Degradation

When an MCP server fails, the agent MUST:
- Log the error with full context to audit trail
- Notify via summary in Dashboard.md
- Attempt alternative execution paths when available
- Continue with remaining tasks rather than blocking entire workflow
- Mark affected tasks as "degraded" not "failed"

**Rationale**: Production systems require resilience. External service failures should not cascade into complete system failure.

## Section 9: Development Standards

### 9.1 Test-First Development (NON-NEGOTIABLE)

For all new features and integrations, the system MUST follow TDD:
- Tests written FIRST and approved by user
- Tests MUST fail before implementation (Red phase)
- Implementation MUST make tests pass (Green phase)
- Refactoring MUST maintain passing tests (Refactor phase)
- Contract tests for all MCP server integrations
- Integration tests for cross-module workflows
- Unit tests for business logic with >80% coverage

**Rationale**: Autonomous systems have high reliability requirements. Test-first development catches bugs early and provides regression safety.

### 9.2 Code Quality Standards

All code MUST meet quality standards:
- Self-documenting with clear variable/function names
- Single Responsibility Principle (one function = one purpose)
- Functions <50 lines, classes <300 lines
- Cyclomatic complexity <10 per function
- No code duplication (DRY principle)
- Type hints for all function signatures (Python)
- Linting passes with zero warnings (ruff, mypy)

### 9.3 Small, Composable Functions

Functions MUST be small and composable:
- Pure functions preferred (no side effects)
- Input/output clearly defined
- Composable using function composition or pipelines
- Testable in isolation
- Reusable across modules

### 9.4 No Hidden Side Effects

Functions MUST NOT have hidden side effects:
- All side effects (I/O, state mutation, logging) explicit in function signature
- Use dependency injection for side-effecting dependencies
- Separate pure logic from side effects
- Document side effects in docstrings

### 9.5 Documentation Requirements

All modules MUST include documentation:
- Module-level docstring explaining purpose and responsibilities
- Function docstrings with parameters, return values, exceptions
- Architecture Decision Records (ADRs) for significant design choices
- README for each major subsystem
- Inline comments for complex logic explaining "why" not "what"

## Section 10: Evolution Policy

### 10.1 Extensibility by Design

The architecture MUST support future expansion:
- Plugin architecture for new watchers (email, Slack, webhooks)
- MCP server registry for dynamic tool discovery
- Event schema versioning for backward compatibility
- Feature flags for gradual rollout
- A/B testing framework for decision algorithm improvements

### 10.2 Multiple AI Employees

The system MUST support multiple AI employees:
- Isolated memory spaces per employee
- Shared knowledge base with access control
- Task routing based on employee specialization
- Coordination protocol for multi-employee workflows
- Resource allocation and conflict resolution

### 10.3 Distributed Automation Workflows

The architecture MUST enable distributed workflows:
- Task delegation across multiple agents
- Workflow orchestration with dependency management
- Distributed state management
- Consensus protocols for multi-agent decisions
- Failure recovery with partial rollback

### 10.4 Backward Compatibility

All changes MUST maintain backward compatibility:
- Deprecation warnings for 2 MINOR versions before removal
- Migration scripts for breaking changes
- Version negotiation for inter-module communication
- Graceful handling of unknown event types
- Schema evolution with default values

### 10.5 Performance Scalability

The system MUST scale with increasing load:
- Horizontal scaling for parallel task processing
- Caching for frequently accessed data
- Lazy loading for large datasets
- Resource pooling for expensive operations (LLM calls, DB connections)
- Performance budgets enforced in CI/CD

## Section 11: Workflow Architecture

### 11.1 Folder-Based State Machine

The system operates through a structured folder workflow:

1. **`/Inbox`**: Raw perception layer - all incoming data lands here
2. **`/Needs_Action`**: Classified tasks with metadata and priority
3. **`/Plans`**: AI-generated execution strategies awaiting approval
4. **`/4_Approved`**: Human-approved plans ready for execution
5. **`/Done`**: Completed tasks with execution logs and outputs
6. **`/Memory`**: Long-term preferences and learned behaviors
7. **`/Knowledge_Base`**: Business documents and domain knowledge
8. **`/Logs/Audit_Trail`**: Comprehensive action and decision logs

### 11.2 Processing Pipeline

Each task MUST flow through:
1. **Perception**: Detect and ingest from source
2. **Classification**: Apply priority matrix and sentiment analysis
3. **Planning**: Generate execution strategy with business impact
4. **Approval**: Human review (Silver Tier) or autonomous decision (Gold Tier)
5. **Execution**: Perform actions with error recovery
6. **Verification**: Confirm outcome and update dashboard
7. **Archival**: Move to Done with complete audit trail

### 11.3 Priority-Driven Execution (4-Tier Matrix)

The system MUST classify all tasks using the 4-Tier Priority Matrix:
- **P0 (Critical/Revenue)**: Immediate action + alert (bank issues, overdue invoices)
- **P1 (Client Retention)**: Same-day processing (client queries, feedback)
- **P2 (Operational)**: Next 24 hours (internal reports, documentation)
- **P3 (General/Growth)**: Weekly batching (LinkedIn ideas, learning material)

Priority MUST be determined by sentiment analysis, financial impact, and deadline proximity.

### 11.4 Zero-Loss Data Policy

The system MUST treat all original data as "Gold Source" and NEVER modify it:
- Preserve original files in `/Inbox` or source location
- Create processed copies in `/Needs_Action`
- Maintain complete lineage from source to output
- Enable rollback to any previous state
- Implement copy-on-write semantics

## Section 12: Governance

### 12.1 Amendment Process

1. Proposed changes MUST be documented with rationale
2. Impact analysis MUST be performed on dependent templates
3. Version MUST be incremented per semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes
   - **MINOR**: New principles or material expansions
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements
4. All dependent artifacts MUST be updated before amendment is ratified
5. Amendment MUST be approved by project owner

### 12.2 Compliance Review

- All PRs MUST verify compliance with constitution principles
- Architecture violations MUST be explicitly justified with ADR
- Constitution supersedes all other practices and documentation
- Quarterly review MUST assess principle effectiveness and identify needed updates
- Compliance dashboard MUST track adherence metrics

### 12.3 Version Control

- Constitution changes MUST be tracked in git with detailed commit messages
- Each version MUST include Sync Impact Report documenting changes
- Breaking changes MUST include migration guide for existing implementations
- Version history MUST be preserved (no force-push to main)

### 12.4 Runtime Guidance

For day-to-day development guidance and agent-specific instructions, refer to `CLAUDE.md` in the repository root. The constitution defines "what" and "why"; runtime guidance defines "how" for specific contexts.

---

**Version**: 3.0.0 | **Ratified**: 2026-02-20 | **Last Amended**: 2026-03-10
