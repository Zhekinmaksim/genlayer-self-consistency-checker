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
Corrected source is pushed at commit `799c985`; `judge()` is now declared
directly inside `evaluate()` and passed directly to
`gl.eq_principle.prompt_comparative(judge, PRINCIPLE)`. There is no callback
factory. Studio 2026-08-20: schema/deploy accepted and finalized at
`0xAa0E282Be73f13BB1A388bB4E4F38Fe2165B9368`. Explorer transaction source
matches the lint-recognizable inline callback shape. Full live LLM adjudication
was not simulated.

## Evidence

- https://github.com/Zhekinmaksim/genlayer-self-consistency-checker/blob/799c985e407fcd0ac16b2f300263d443f4908c63/contract.py
- https://explorer-studio.genlayer.com/address/0xAa0E282Be73f13BB1A388bB4E4F38Fe2165B9368
- https://explorer-studio.genlayer.com/tx/0x502e10a3bc5402985a856a19e8143ba7c634826401d5d1e2071d1d8db6868512
