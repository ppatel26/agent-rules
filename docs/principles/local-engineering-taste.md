# Local Engineering Taste

This document distills implementation preferences observed in real production codebases. It is a taste profile, not a universal law book.

## High-Signal Principles

### Fail loud, never fail silent

- Missing required values should raise, not quietly degrade.
- Defaults are good when they model reality, not when they mask bugs.

### Push integrity to strong enforcement layers

- If a rule truly matters, put it in the database, schema, type system, or another hard boundary where possible.
- Application validations alone are often too soft for critical invariants.

### Think in the database when the database is the right engine

- For filtering, aggregation, uniqueness, and atomic state changes, consider whether SQL can express the rule more directly and safely than application code.
- Avoid hauling large datasets into application memory just to do work the database can do better.

### Prefer explicit data models over vague flexible ones

- If a structure has a known shape, model it directly.
- Use schemaless structures only where the data is genuinely dynamic.

### Comments explain rationale

- Comments should focus on why a choice was made, what invariant matters, or what danger future maintainers must understand.

### Hand-roll simple things, depend on libraries for genuinely complex things

- Avoid dependencies when they add more configuration, indirection, or conceptual load than the problem warrants.
- Use libraries for truly complex areas where they materially reduce risk or effort.

### Atomic transitions beat loose coordination

- Prefer state transitions that encode the expected current state in the operation itself.
- Avoid multi-step coordination patterns that invite races when a tighter atomic update is available.

### Soft-delete with timestamps when deletion history matters

- A timestamp often carries more operational value than a boolean flag because it records when the change happened.

## Context-Dependent Principles

These are useful ideas but should not be treated as universal instructions in the canonical agent file:

- `structure.sql` over `schema.rb`
- Rails-specific hot-path optimization patterns
- JSONB-backed DSLs for business rules
- monolith over microservices as a blanket law
- skipping tests in favor of only constraints and monitoring

The canonical file should preserve the general insight while avoiding framework-specific doctrine.

## Practical Takeaway

The strongest generally reusable guidance from this taste profile is:

- fail loud
- use hard guarantees for critical integrity
- think in SQL when appropriate
- model data explicitly
- comments explain why
- avoid needless dependency complexity
