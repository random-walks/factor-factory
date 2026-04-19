---
description: Run the contract-auditor agent against the current git diff vs main. Reports contract touches + ceremony compliance.
---

Invoke the `contract-auditor` agent (via the Agent tool with `subagent_type: contract-auditor`) with this prompt:

> Audit the diff on the current branch vs `main` against the three factor-factory contract invariants (Panel / Engine Protocol / Tearsheet JSON). Use the procedure in your system prompt. Report findings.

Pass through the auditor's response verbatim. Do not add your own analysis.
