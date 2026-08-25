# Strategic Intelligence Project — Provider Architecture

## 1. Purpose

This document defines how V1 connects to external AI and research services without coupling core business logic to any vendor.

Core principle:

> Business components depend on provider contracts, not vendor SDKs.

The architecture must remain:

- Local-first
- Cloud-ready
- Provider-independent
- Testable
- Replaceable
- Observable
- Safe under provider failure

## 2. Provider Boundaries

V1 defines these provider boundaries:

1. `LLMProvider`
2. `SearchProvider`
3. `EmbeddingProvider` — only if a confirmed V1 requirement needs embeddings

Core components must not directly import or instantiate vendor clients.

```text
Business Component
       ↓
Provider Contract
       ↓
Provider Adapter
       ↓
External / Local Service
```

## 3. LLMProvider

`LLMProvider` is the application-facing contract for language-model capabilities.

Possible V1 uses:

- Structured extraction
- Research-plan assistance
- Claim formulation
- Semantic verification assistance
- Strategic analysis
- Classification
- Meeting-question generation
- Brief generation

The provider must not own business rules.

## 4. LLMProvider Contract

The exact Python API may evolve during implementation, but the logical contract should support:

- Model invocation
- Structured output
- Timeout configuration
- Error normalization
- Model/provider metadata
- Optional usage metadata

Conceptually:

```python
class LLMProvider:
    def generate(...): ...
    def generate_structured(...): ...
```

Application code should not depend on vendor-specific response objects.

## 5. Structured Output

AI components should prefer structured outputs validated against application schemas.

```text
Component
   ↓
LLMProvider
   ↓
Provider Response
   ↓
Schema Validation
   ↓
Typed Domain Model
```

Invalid output must not silently enter Workflow State.

Possible handling:

- One bounded repair attempt
- Controlled retry
- Structured failure

## 6. Local LLM Adapter

V1 is local-first.

The primary local implementation may use Ollama.

```text
LLMProvider
    ↓
OllamaAdapter
    ↓
Local Ollama Runtime
```

Only the adapter should know Ollama-specific SDK/API details.

Core components should not contain Ollama imports or model-specific request formats.

## 7. Future Hosted LLM Adapters

The architecture should allow future adapters such as:

```text
LLMProvider
 ├── OllamaAdapter
 ├── OpenAIAdapter
 ├── AzureOpenAIAdapter
 ├── AnthropicAdapter
 └── OtherAdapter
```

Adding a provider should not require rewriting Strategic Analysis, Verification, Governance, or Brief generation logic.

## 8. Provider Capability Differences

Providers may differ in:

- Structured-output support
- Context limits
- Tool support
- Latency
- Cost
- Local/cloud execution
- Model capabilities

The application should depend only on capabilities it actually requires.

Avoid designing V1 around proprietary features that make provider replacement difficult.

## 9. SearchProvider

`SearchProvider` provides vendor-independent search and source discovery.

Used by:

- Company Research
- Executive Research
- Focused verification follow-up research

Conceptually:

```python
class SearchProvider:
    def search(...): ...
```

It should return normalized application-owned search-result models.

## 10. Search Result Model

Provider-specific results should be converted into a common structure such as:

```text
SearchResult
- title
- url
- snippet
- publisher
- published_at
- provider_metadata
```

Search results are discovery signals, not automatically verified Evidence.

## 11. Search Adapter Boundary

```text
Research Component
      ↓
SearchProvider
      ↓
Search Adapter
      ↓
Search Service
```

Research logic should not know the vendor-specific request or response format.

## 12. Source Access

Search discovery and source-content access are separate concerns.

A search result may point to:

- Accessible page
- Blocked page
- Paywalled page
- Missing page
- Restricted platform

The system must respect source-access rules defined in the Source and Research Policy.

Provider abstraction must never be used to bypass restrictions.

## 13. LinkedIn Boundary

V1 does not implement an automated LinkedIn scraping provider.

A public LinkedIn URL may be used as a research hint or permitted source reference.

The provider architecture must not introduce:

- LinkedIn crawler adapters
- Profile harvesting
- Session/cookie automation
- Access-control bypass

Other public sources remain valid alternatives.

## 14. EmbeddingProvider

Embeddings are optional in V1.

Do not add an embedding stack simply because the project is an AI application.

Introduce `EmbeddingProvider` only if a confirmed V1 requirement needs:

- Semantic retrieval
- Similarity search
- Evidence deduplication that materially benefits from embeddings
- Local document retrieval

If introduced:

```text
Core Component
      ↓
EmbeddingProvider
      ↓
Embedding Adapter
```

The same provider-independence rules apply.

## 15. No Premature Vector Database

V1 does not automatically require:

- Chroma
- Pinecone
- Weaviate
- Qdrant
- pgvector

The current Source → Evidence → Claim workflow should remain simple unless evaluation proves semantic retrieval is necessary.

## 16. Provider Factory

Provider construction should happen in one composition boundary.

Conceptually:

```text
Configuration
     ↓
Provider Factory
     ↓
Configured Providers
     ↓
Application / Workflow
```

Example responsibilities:

- Read configured provider type
- Instantiate correct adapter
- Validate required configuration
- Return provider interfaces to the application

Business components should receive providers through dependency injection.

## 17. Dependency Injection

Preferred:

```text
StrategicAnalysis(LLMProvider)
CompanyResearch(SearchProvider)
ExecutiveResearch(SearchProvider)
```

Avoid:

```text
StrategicAnalysis()
    ↓
creates Ollama client internally
```

This improves testing and provider replacement.

## 18. Configuration

Provider configuration should be centralized.

Possible settings:

```text
LLM_PROVIDER
LLM_MODEL
LLM_TIMEOUT
SEARCH_PROVIDER
SEARCH_TIMEOUT
MAX_PROVIDER_RETRIES
OLLAMA_BASE_URL
```

Exact names may be finalized during implementation.

Do not scatter environment-variable reads throughout business components.

## 19. Secrets

Secrets must:

- Never be hardcoded
- Never be committed
- Never be logged
- Remain outside domain models
- Be loaded through configuration/environment mechanisms

`.env` should be excluded from Git.

Local Ollama operation should not require a cloud API key.

## 20. Local-First Behavior

The preferred V1 path is:

```text
Application
   ↓
LLMProvider
   ↓
OllamaAdapter
   ↓
Local Model
```

Web research may still require an external search service.

The application must remain useful without requiring its LLM reasoning to run in the cloud.

## 21. Cloud-Ready Behavior

Future deployment may change configuration to:

```text
Application
   ↓
LLMProvider
   ↓
HostedLLMAdapter
```

without changing domain logic.

Likewise:

```text
Research
   ↓
SearchProvider
   ↓
Different Search Adapter
```

Provider switching should be primarily configuration/composition work.

## 22. Provider Errors

Adapters should normalize vendor-specific failures into application-level errors.

Examples:

- `PROVIDER_UNAVAILABLE`
- `PROVIDER_TIMEOUT`
- `AUTHENTICATION_FAILED`
- `RATE_LIMITED`
- `INVALID_PROVIDER_RESPONSE`
- `MODEL_NOT_AVAILABLE`
- `STRUCTURED_OUTPUT_INVALID`

Core workflow code should not need to understand every vendor exception type.

## 23. Retry Responsibility

Provider adapters may expose normalized failures, but workflow-level retry policy belongs to the application/orchestrator.

This avoids hidden uncontrolled retries.

```text
Provider Failure
     ↓
Normalized Error
     ↓
Workflow Retry Policy
```

Retries must remain bounded.

## 24. Timeout Responsibility

All external or local provider calls that may block should support bounded timeouts where technically possible.

A provider must not freeze the entire Case indefinitely.

Timeout configuration should remain centralized.

## 25. Rate Limits

Hosted providers may impose rate limits.

The architecture should support:

- Detecting rate-limit responses
- Controlled retry/backoff
- Recording the event
- Returning PARTIAL/FAILED when limits cannot be resolved

V1 does not need complex distributed rate-limit infrastructure.

## 26. Provider Health

V1 may implement lightweight provider readiness checks.

Examples:

- Ollama reachable
- Configured model available
- Search provider configuration present

Health checks should provide clear startup/runtime errors.

They should not become a large monitoring subsystem in V1.

## 27. Model Selection

Model selection belongs to configuration/composition.

Business components should not hardcode model names.

Example:

```text
LLM_MODEL=<configured model>
```

This allows testing different local models without modifying business logic.

## 28. Component-Specific Model Configuration

V1 should begin simply, preferably with one configured LLM unless evaluation shows a strong reason for multiple models.

Future versions may support different models for:

- Extraction
- Analysis
- Brief generation

Do not introduce model-routing complexity prematurely.

## 29. Provider Metadata

Where useful, provider calls should expose metadata for observability:

- Provider name
- Model
- Duration
- Token usage when available
- Cost when available
- Retry count

This metadata must not leak secrets.

## 30. Audit Boundary

Audit records may record which provider/model produced an AI output.

Example:

```text
analysis_id
provider = ollama
model = configured_model
workflow_run_id
timestamp
```

This helps reproducibility and debugging.

## 31. Testing Providers

Business components should be testable without real provider calls.

Use fake/stub implementations of provider contracts.

Example:

```text
FakeLLMProvider
FakeSearchProvider
```

This allows deterministic tests for:

- Workflow routing
- Governance
- Verification
- Failure handling
- Brief filtering

## 32. Integration Tests

Separate integration tests should verify real adapters.

Examples:

- Ollama adapter can reach configured local model
- Search adapter normalizes results correctly
- Provider timeout becomes expected application error
- Invalid structured output is handled safely

## 33. Provider Failure Tests

Minimum V1 scenarios:

1. Ollama unavailable
2. Configured model missing
3. LLM timeout
4. Invalid structured response
5. Search timeout
6. Search provider unavailable
7. Rate-limit-style failure where applicable
8. Retry limit reached

The system must fail visibly rather than fabricate output.

## 34. Governance Independence

Governance belongs to the application, not the provider.

Changing:

```text
Ollama → Hosted LLM
```

must not change:

- FACT evidence requirements
- BLOCK behavior
- RESTRICT behavior
- Privacy rules
- Traceability requirements
- Prompt-injection boundary

Provider output is always subject to application Governance.

## 35. Verification Independence

The Verification architecture must not blindly trust a provider because it is a stronger model.

LLM output remains reasoning assistance.

Evidence and Source relationships remain the trust foundation.

## 36. Prompt-Injection Boundary

Providers receive external source content as untrusted data.

Source content cannot:

- Change provider configuration
- Request secrets
- Change system instructions
- Expand tool permissions
- Override Governance
- Trigger unauthorized provider calls

Provider adapters should not interpret source content as application configuration.

## 37. Provider Permissions

Each provider should receive only required information.

Do not send unnecessary:

- User context
- Executive data
- Full raw source archives
- Secrets

Data minimization applies to provider calls.

## 38. Local Data and Hosted Providers

If a future hosted LLM is enabled, the application should make the provider boundary explicit.

The system should be able to distinguish:

```text
LOCAL processing
```

from:

```text
EXTERNAL provider processing
```

This supports future privacy and deployment controls.

## 39. No Silent Fallback

V1 should not silently switch from a local provider to an external cloud provider.

Example prohibited behavior:

```text
Ollama fails
→ secretly send data to cloud LLM
```

Provider changes must follow explicit configuration/policy.

If Ollama fails, return the appropriate failure unless an explicitly configured fallback policy exists in a future version.

## 40. Fallback Providers

Automatic cross-provider fallback is not required for V1.

It adds:

- Privacy complexity
- Testing complexity
- Cost unpredictability
- Behavioral differences

V1 should prefer clear failure and recovery.

Fallback can be designed later if justified.

## 41. Provider Versioning

Where practical, record enough information to understand which provider/model produced an important result.

This is especially useful for reruns and debugging.

Full model-registry infrastructure is unnecessary for V1.

## 42. Cloud Migration

Cloud migration may change:

- LLM adapter
- Search adapter
- Secret management
- Network configuration
- Observability

It should not change:

- Domain models
- Workflow responsibilities
- Governance invariants
- Research policy
- Brief contracts

## 43. V1 Provider Invariants

P1. Business logic never directly depends on vendor SDKs.

P2. Providers are injected through application-owned contracts.

P3. Ollama is isolated behind an adapter.

P4. Search vendors are isolated behind `SearchProvider`.

P5. Embeddings are added only when a real V1 requirement justifies them.

P6. Provider errors are normalized.

P7. Retries are bounded and controlled by workflow policy.

P8. Provider calls have bounded execution where possible.

P9. Secrets never enter source content, domain models, or logs.

P10. Governance cannot be overridden by a provider.

P11. External source content cannot change provider configuration.

P12. Local failure does not silently send data to a cloud provider.

## 44. Final V1 Provider Architecture

```text
                         APPLICATION
                              │
             ┌────────────────┴────────────────┐
             │                                 │
        LLMProvider                       SearchProvider
             │                                 │
       OllamaAdapter                      SearchAdapter
             │                                 │
       Local Ollama                       Search Service

             Optional only if justified:

                         EmbeddingProvider
                               │
                         EmbeddingAdapter
```

Composition:

```text
Configuration
     ↓
Provider Factory
     ↓
Provider Interfaces
     ↓
Workflow Components
```

Future:

```text
LLMProvider
 ├── OllamaAdapter
 ├── OpenAIAdapter
 ├── AzureOpenAIAdapter
 ├── AnthropicAdapter
 └── OtherAdapter
```

without rewriting the core application.

## 45. Final Principle

V1 is local-first but not local-locked.

The provider architecture ensures that models and external services remain replaceable infrastructure rather than becoming part of the business logic.

The design priority is:

**Stable Contracts → Provider Independence → Local Control → Safe Failure → Cloud Readiness → Simplicity**
