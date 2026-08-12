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
Corrected source is pushed at commit `8e7f1a9`; the nondeterministic prompt call
is now directly inside the `prompt_comparative` callback so GenVM lint can see
the consensus path. Verified in hosted Studio on 2026-08-12: schema loaded and
deployed/finalized at `0x08FEF3c1b43B1e973d9E57d6e7E207ce86359c74`. Full live
LLM adjudication was not simulated.

## Evidence

- https://github.com/Zhekinmaksim/genlayer-self-consistency-checker
- https://explorer-studio.genlayer.com/address/0x08FEF3c1b43B1e973d9E57d6e7E207ce86359c74
- https://explorer-studio.genlayer.com/tx/0xef2760febd2672827aa448827884a14ac355a4d7b26180adb9e4dafc811c0133
