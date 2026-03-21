# Tiger Style Notes

This document captures the parts of Tiger Style that are most useful as general engineering guidance for agent-driven work.

Official source:

- <https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md>
- <https://tigerstyle.dev/>

## What to Carry Forward

### 1. Safety first

Safety comes before performance, and performance comes before convenience.

For agent work, this means:

- do not accept silent failure
- do not hide bad states behind defaults
- do not trade away correctness for short-term speed
- be explicit about assumptions and limits

### 2. Performance is a design concern

Performance is not just a final optimization pass. Important cost and throughput questions should shape the design early.

Useful habits:

- do napkin math early
- think about network, disk, memory, and CPU costs in that order when relevant
- batch expensive operations when possible
- prefer predictable execution over overly clever logic

### 3. Bounded and predictable systems are easier to trust

Tiger Style strongly values predictable control flow and explicit limits.

For a general agent context, the portable version is:

- prefer straightforward control flow
- avoid hidden or unbounded behavior
- use explicit limits on retries, loops, queues, and payload sizes
- keep system behavior comprehensible under failure

### 4. Good names and good organization are not cosmetic

Clear naming and logical organization improve correctness because people can reason about the system more reliably.

Carry forward:

- use descriptive names
- avoid unnecessary abbreviations
- organize code so high-level intent is visible
- keep interfaces simple where possible

### 5. Comments should explain why

Tiger Style's strongest documentation lesson is that comments should justify intent, tradeoffs, and warnings.

The code already shows what it does. Comments should explain:

- why the design is this way
- what invariant must hold
- what edge case or constraint matters
- what future maintainers must not accidentally break

## What Not to Import Literally

Some Tiger Style rules are powerful in systems programming but should not be treated as universal law in a cross-agent canonical file.

Examples:

- exact function length thresholds
- no recursion as an absolute rule
- explicit integer-size rules in languages where that does not map cleanly
- static allocation as a blanket rule
- language-specific formatting doctrine

Those can still inform taste, but they should not be copied into a general-purpose `AGENTS.md` unless a project specifically needs them.

## Practical Takeaway

The distilled Tiger Style contribution to the canonical file is:

- safety over speed
- predictable, bounded behavior
- performance considered early
- clear naming and organization
- comments explain why
- explicit limits and strong invariants
