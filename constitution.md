# Agentic IDE Constitution: ColdOutreachPythonNoDB
*Version 1.0 - Rules binding LLM assistants to Project Canon*

## Core Authority

### Canon as Truth Source
- **Treat `canon.yaml` as the single, versioned source of truth**
- Canon wins all conflicts; update canon first, then implement
- Never invent configurations outside canon structure
- All API settings, prompts, schemas live in canon.yaml exclusively

### Validated Boundaries
- **Every flow class constructor takes explicit dependencies via DI**
- All external inputs validated via Pydantic schemas before processing  
- Standard error envelope: `{ok: false, code, message, details?}`
- Success envelope: `{ok: true, data}`
- No implicit globals; inject SheetsClient, ApifyClient, etc. explicitly

### Deterministic Operations
- **All commands must be reproducible with same inputs**
- Phase-based implementation: complete Phase N before starting Phase N+1
- Rich progress bars for all long operations (>2s expected duration)
- Structured CLI feedback: start panel → progress → end panel (green/red)

### Definition of Done
- **Code conforms to canon + all acceptance criteria pass**
- Phase acceptance criteria must be met before proceeding
- All test commands execute successfully
- CLI help displays correctly with typer

## Essential NEVER Rules

### No Canon Violations
- **Never add surfaces, behaviors, or configs outside canon.yaml**
- No hardcoded API keys, endpoints, or prompts in source code
- No configuration scattered across multiple files
- No magic strings; reference canon for all external integrations

### No Parallel Patterns  
- **One client class per external service (SheetsClient, ApifyClient, etc.)**
- No duplicate HTTP libraries; use requests consistently
- No alternative CLI frameworks; typer only for command structure
- No mixed progress indicators; rich.progress exclusively

### No Hidden State
- **No global variables or implicit singletons**
- Flow classes are stateless; dependencies injected via constructor
- No background processes or async magic without explicit handling
- All state changes visible in Google Sheets or CLI output

### No Contract Changes Without Canon
- **Update canon.yaml schema first, then implement changes**
- No breaking changes to Pydantic models without canon update
- Google Sheets column structure defined in canon, not code
- API client interfaces match canon specifications exactly

## Project-Specific Rules

### Python Architecture
- **Modular monolith: src/app_logic/ for flows, src/clients/ for integrations**
- Class-based flow controllers with dependency injection pattern
- Standard Python layout: src/ directory with proper __init__.py files
- Python 3.10+ required; pin versions in requirements.txt

### CLI Design System  
- **Verb-noun command structure only: `python main.py run discovery`**
- Typer framework exclusively for CLI structure
- Rich library for all UI elements: panels, progress, tables
- No alternative command parsing or output formatting

### Google Sheets Integration
- **Single SheetsClient handles all worksheet operations**
- Authenticate once, reuse connection for all operations
- Worksheet names and structure defined in canon.yaml
- Upsert pattern for all data writes (find existing, then update/insert)

### External API Clients
- **One adapter class per service: ApifyClient, TavilyClient, GeminiClient, SalesHandyClient**
- Hide authentication and error handling in client classes
- Pass API tokens and settings from canon.yaml to client constructors
- Standard retry and rate limiting patterns per service requirements

### Data Flow Validation
- **ApifyProspect, other Pydantic models validate all external data**
- Skip invalid records with rich warning, continue processing
- Phase progression: discovered → researched → drafted → synced/failed  
- DNC compliance checking before SalesHandy import

### Testing Requirements
- **Each phase has explicit acceptance criteria**
- Test commands (test-sheets, etc.) prove integration works
- Manual verification steps documented for each phase
- No proceeding to next phase until current phase fully passes

## Compliance Checkpoints

### Before Any Implementation
- [ ] Canon.yaml contains all required configurations
- [ ] Phase acceptance criteria clearly defined
- [ ] All external API credentials configured via env/canon
- [ ] Google Sheets structure matches canon specification

### During Development  
- [ ] Rich feedback implemented per UX flow specification
- [ ] All external data validated via Pydantic before processing
- [ ] Error handling follows standard envelope pattern
- [ ] Progress bars for operations >2s duration

### Before Phase Completion
- [ ] Acceptance criteria demonstrably met
- [ ] Test commands execute without errors  
- [ ] Google Sheets updated with expected data
- [ ] CLI output matches structured feedback requirements

## Emergency Overrides

**No emergency overrides permitted.** This constitution enforces the deterministic, traceable approach required for LLM-driven development. Canon updates and proper phase completion are non-negotiable for system integrity.
