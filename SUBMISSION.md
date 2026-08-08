# Portal submission - Self-Consistency Checker

## Title

Self-Consistency Checker

## Notes

Standalone GenLayer Intelligent Contract that takes one document plus fixed axes
and finds contradictions inside the document, not between two inputs.

Consensus boundary: Stage A is deterministic - the stored document is rehashed
before any LLM call, so validators cannot judge different bytes. Stage B asks
one yes/no question per axis and compares only `{ok, doc, bits, reason}`; quote
pairs are recorded for audit but excluded from consensus. Stage C folds bits
into a mask deterministically.

`UNDETERMINED` is terminal, not an error. Axes are frozen and hashed before
document submission; whitespace-only and duplicate axes revert before hashing;
document submission is one-shot; `evaluate` is permissionless and terminal.

Repo includes README, TEST_PLAN and `sim/check.py`; local harness 7/7 pass.
Verified in hosted Studio on 2026-08-08: schema loaded and deployed/finalized at
`0xE10A9D1066280F639684171f17E374F81185fCf6`. Full live LLM adjudication was
not simulated.

## Evidence

- https://github.com/Zhekinmaksim/genlayer-self-consistency-checker
- https://explorer-studio.genlayer.com/address/0xE10A9D1066280F639684171f17E374F81185fCf6
- https://explorer-studio.genlayer.com/tx/0x92041494f8ebb23e312938690a5b0c8711f88c187432c0730a27489397fb9647
