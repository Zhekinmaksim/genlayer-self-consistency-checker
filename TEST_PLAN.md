# Test plan - Self-Consistency Checker

Seven cases. Each one is runnable offline against `sim/check.py` and again in
hosted Studio against a live deployment. Where the two differ, it is stated.

## 1. Contradiction found

Axes: `payment timing`, `termination rights`, `liability cap`.
Document: clause 4 requires payment in 30 days, clause 12 requires payment
immediately on receipt.

Expected: `evaluate` returns `INCONSISTENT`, `conflict_mask` is `1`,
`conflicting_axes` returns `["payment timing"]`, `conflicts` returns one readable
fragment pair. The other two axes stay clear, which is the point: the mask is
per-axis, not a global verdict.

## 2. Clean document

Axes: `scope`, `budget`. A short coherent policy with no internal conflict.

Expected: `CONSISTENT`, `conflict_mask` is `0`, `conflicts` is empty.

## 3. Malformed judgment settles as UNDETERMINED

The model returns fewer entries than there are axes, or an entry whose
`conflict` field is neither `true` nor `false`.

Expected: `UNDETERMINED` with reason `MALFORMED_JUDGMENT`. Crucially **not**
`CONSISTENT`. A judgment that could not be read must decide nothing, otherwise
an author could manufacture a clean verdict by making the judgment hard to
parse.

## 4. Provider failure settles as UNDETERMINED

`exec_prompt` raises.

Expected: `UNDETERMINED` with reason `JUDGMENT_UNAVAILABLE`. The failure is
caught inside the non-deterministic block and returned as a structured result,
so the failure signal itself reaches consensus rather than tearing down the VM
with an unstructured error.

## 5. Input guards reject bad terms before hashing

- whitespace-only axis text -> `EMPTY_AXIS_SET`
- `scope` and `SCOPE` in one set -> `DUPLICATE_AXIS`
- thirteen axes -> `TOO_MANY_AXES`
- reusing an existing id -> `ID_ALREADY_USED`
- a `content_hash` that does not match the document -> `HASH_MISMATCH`
- unknown id -> `UNKNOWN_CHECK`

Each of these reverts. None of them reaches the LLM.

## 6. One shot input, terminal verdict

Pin a document, then try to pin a second one -> `DOCUMENT_ALREADY_PINNED`.
Evaluate, then evaluate again -> `NOT_PINNED_OR_ALREADY_EVALUATED`.

This is the anti-grinding property. Neither the input nor the verdict can be
re-rolled.

## 7. Author-only submission

A second address tries to `submit_document` on someone else's open check ->
`NOT_AUTHOR`. Note that `evaluate` deliberately has no such restriction.

---

## Studio verification

Verified in hosted Studio on 2026-08-08:

- deployment finalized at
  `0xE10A9D1066280F639684171f17E374F81185fCf6`
- deploy transaction:
  `0x92041494f8ebb23e312938690a5b0c8711f88c187432c0730a27489397fb9647`
- Explorer source:
  `https://explorer-studio.genlayer.com/address/0xE10A9D1066280F639684171f17E374F81185fCf6`
- Studio schema extracted and exposed all read/write methods listed in the
  README.
- Offline deterministic harness: `python3 sim/check.py` -> 7/7 pass.

Not run in Studio before submission: live `evaluate` with full LLM adjudication.
The submission should state this boundary plainly.
