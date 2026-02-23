# Architecture Reference: Real-World LangGraph Agent

> This is a production agent system built with LangGraph and LangChain. Use it as a reference for how real-world agent architectures are structured. You don't need to build anything this complex in the workshop — but the patterns are the same.

---

## System Overview

This platform is a multi-tenant SaaS that deploys custom AI agents for businesses. Each agent:
- Has its own knowledge base (indexed from the business website)
- Handles customer conversations via a chat widget
- Detects intent and triggers business actions (CTAs)
- Evaluates its own responses and falls back gracefully when it doesn't know something

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Business   │  │   End User   │  │    Admin     │          │
│  │   Website    │  │   (Chat)     │  │  Dashboard   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         └──────────────────┼──────────────────┘                  │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                        │
└────────────────────────────┼────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
   Onboarding Agent    Generic Agent     Analytics
   (setup flow)        (runtime)         (tracking)
            │                │                │
            └────────────────┼────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│     MongoDB          Vector DB          Redis                    │
│    (metadata)       (embeddings)      (cache + queue)            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Patterns to Notice

### 1. State Machine for Onboarding

The onboarding agent uses a state machine (same concept as LangGraph state):

```
INIT → COLLECTING_BUSINESS_INFO → COLLECTING_PERSONALITY → COLLECTING_CTAS → REVIEW → COMPLETE
```

Each state has:
- **Required data** (what must be collected before moving on)
- **Validation rules** (what counts as valid input)
- **Transitions** (what triggers the move to the next state)

This is the same idea as your LangGraph graph: nodes do work, edges define flow, conditions determine routing.

### 2. Parallel Operations for Performance

The runtime agent runs 6 operations in parallel using `asyncio.gather`:
- Intent classification
- CTA detection
- Knowledge retrieval
- Sentiment analysis
- Similarity detection
- Page context resolution

This reduced response time from ~10-17s to ~2.5-3s. In your workshop agent, you probably run things sequentially — but this shows how the same architecture scales.

### 3. Evaluate-and-Fallback (Same as Your Loop)

The agent evaluates every response before sending it:

```
generate response → check uncertainty → [confident?]
                                          ├── YES → send response
                                          └── NO  → fallback handler → suggest CTA
```

This is the exact same pattern as the evaluate-and-retry loop in your workshop agent. The production version just has more sophisticated evaluation (sentiment detection, knowledge gap logging, CTA injection).

### 4. Tools in Production

Production tools include:
- **Knowledge retriever** — searches the business knowledge graph
- **CTA detector** — identifies when to trigger business actions
- **Page context resolver** — understands what page the user is browsing
- **Sentiment detector** — identifies user frustration

Your workshop agent has 1-3 tools. The pattern is identical — `@tool` decorator, clear docstring, single responsibility.

### 5. State Design

Production state includes:
- Conversation history
- User profile (returning visitor detection)
- Knowledge retrieval results
- Sentiment analysis
- CTA opportunities
- Page context

Your workshop state is simpler, but the principle is the same: state is the shared memory that every node reads from and writes to.

## What Makes This "Production" vs "Workshop"

| Aspect | Workshop Agent | Production Agent |
|--------|---------------|-----------------|
| **Tools** | 1-3, possibly mocked | 6+, connected to real services |
| **State** | 4-6 fields | 15+ fields with nested structures |
| **Error handling** | Basic try/catch | Circuit breakers, retry logic, fallbacks |
| **Loop** | Simple pass/fail evaluation | Multi-signal evaluation with confidence scores |
| **Data** | Mock or local files | MongoDB, vector DB, Redis, knowledge graphs |
| **Performance** | Sequential | Parallel async operations |
| **Multi-tenancy** | Single user | Isolated per-business with auth |

The architecture and thinking are the same. The difference is tools, error handling, and scale.
