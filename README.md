# Self-Consistency Checker

A GenLayer Intelligent Contract that takes **one** document and a fixed set of
axes, and answers one question: does this document contradict itself along any
of these axes.

Most judgment contracts compare two things - a deliverable against a rubric, a
text against another text. This one takes a single input and looks for conflict
*inside* it. There is nothing to compare it against, which changes the whole
consensus problem: the output cannot be a similarity score, it has to be a
decision about the document's own internal structure.

## The problem

Long agreements, specs and policies accumulate internal contradictions. Clause 4
forbids what clause 12 requires. A spec demands two incompatible latencies. A
policy grants a right in one section and revokes it in another.

A diff cannot find these, because both clauses are individually valid and
individually well formed. It takes reading to see that they cannot both hold.
Today that reading happens by hand, late, usually after the contradiction has
already caused a dispute.

## Consensus design

This is the part that matters, so it goes first.

**Non-determinism is confined to the smallest possible surface.** Setup,
aggregation and the final state change are deterministic. Only the judgment
itself runs an LLM, and its result is reduced to a fixed-length discrete output
before anything is compared.

**Stage A - deterministic.** The document lives in contract storage and was
hashed at submission time. Before any judgment runs, the stored text is
re-hashed and compared to the committed hash. No LLM call, no web fetch, so
there is no way for two validators to silently judge different bytes. If the pin
does not hold, the case settles as `UNDETERMINED` with reason
`INTEGRITY_FAILURE` and nothing is judged.

**Stage B - non deterministic.** One prompt asks a bounded yes or no question
per axis: is there a contradiction on this axis. The object returned to
consensus is:

```json
{"ok": true, "doc": "0x...", "bits": "1001", "reason": "", "pairs": ["..."]}
```

The equivalence principle names the compared fields explicitly - `ok`, `doc`,
`bits`, `reason` - and instructs validators to ignore everything else. So `bits`
must match character by character across validators, and the fragment quotes in
`pairs`, which no two models will ever phrase identically, are reported without
ever entering consensus.

**Stage C - deterministic.** The bit string is folded into a `u32` mask, the
verdict is derived (`any bit set -> INCONSISTENT`, `none -> CONSISTENT`), and
the case becomes terminal.

**`UNDETERMINED` is a first-class verdict, not an error.** It means the contract
could not establish the facts and therefore decides nothing. Collapsing "could
not decide" into "no contradiction" would be an attack surface: it would let an
author manufacture a clean bill of health by making the judgment hard.
Reasons stored on chain: `INTEGRITY_FAILURE`, `JUDGMENT_UNAVAILABLE`,
`MALFORMED_JUDGMENT`, `INPUT_SWAPPED`.

## Adversarial analysis

There is one author and one document here, so there is no second party to
countersign. The adversarial fix is **ordering** instead.

- **The axes are fixed and hashed before the document is accepted.** An author
  who could add or edit axes after seeing the document could tune the question
  until the answer suited. `open_check` freezes the terms; only then does
  `submit_document` accept the input.
- **An empty or whitespace-only axis set is rejected before hashing.** An empty
  set would hash to a stable value and then pass vacuously - a free clean
  verdict for anyone who wants one. Duplicate axes are rejected for the same
  reason: they would let an author pad the mask.
- **The document is one shot and immutable.** Once pinned it cannot be replaced,
  so nobody can swap the input after seeing an early result.
- **`evaluate` is permissionless.** Once both the terms and the input are
  frozen, there is nothing left to choose, so anyone may trigger the verdict.
  The author cannot bury a result by never calling.
- **The verdict is terminal, `UNDETERMINED` included.** Allowing a retry would
  let a party re-roll the judgment until it came out convenient. To try again,
  open a new check, which means a new commitment to new terms.
- **The document is treated as untrusted data.** It is fenced with a marker
  derived from the axes hash, labelled as material under examination, and the
  model is told to ignore instructions found inside it. The discrete output plus
  consensus design means a successful injection would have to flip the *same
  bits* across independent validators, or it fails consensus instead of winning.
- **The verdict carries the document hash.** A swap after judging is detectable,
  and a returned hash that does not match the commitment settles as
  `INPUT_SWAPPED`.

## Why it converges

"Is there a contradiction on this axis" is a bounded binary question, so the
output is a bit vector rather than a prose critique. Validators that phrase the
conflicting fragments differently still settle, because only the bit vector and
the document hash are compared. That is the whole trick: a similarity score or a
free-text critique never converges across validators, a bit string either
matches or does not.

## Interface

| Method | Who | Effect |
| --- | --- | --- |
| `open_check(check_id, axes_text)` | anyone | Fixes the axes, one per line, 1 to 12. Returns the axes hash. |
| `submit_document(check_id, document, content_hash)` | author | Pins the document. One shot. Reverts on hash mismatch. |
| `evaluate(check_id)` | anyone | Runs the three stages and settles the verdict. Terminal. |
| `status_of`, `verdict_of`, `reason_of` | view | Lifecycle and outcome. |
| `axes_of`, `axes_hash_of`, `document_hash_of` | view | The frozen terms and the pin. |
| `conflict_mask`, `conflicting_axes` | view | Which axes carry a contradiction. |
| `conflicts` | view | Readable fragment pairs. Reported, never consensus. |
| `case_ids` | view | Enumerates cases. |

### Hash convention

Every hash in this contract is `keccak256` over the **canonical** form of the
text: line endings normalised to `\n`, trailing whitespace stripped per line,
ends stripped. Reproduce it off-chain before calling `submit_document` and the
contract will accept it. The axes hash is taken over the parsed axes joined by
`\n`, after empty lines are dropped and each line is collapsed to single spaces.

## Cost

One LLM call per `evaluate`, replicated per validator. No web fetch at all,
which is deliberate: the judged artifact lives in storage, so the fragile part
of GenLayer is not on the path. Document is capped at 20000 characters and axes
at 12, which bounds the prompt.

## Testing

`sim/` holds a small offline stand-in for the SDK and a seven-case check that
exercises every deterministic path: input guards, canonical hashing, bit folding,
verdict routing, one-shot inputs and terminality.

```
python3 sim/check.py
```

All seven pass. This does **not** test consensus - cross-validator agreement is
what hosted Studio exercises, and `TEST_PLAN.md` lists what was run there and
what was not. Full live LLM adjudication is not simulated offline.

## Hosted Studio verification

Checked in hosted GenLayer Studio on 2026-08-20 after the comparative callback
was inlined directly inside `evaluate()` in commit `799c985`.

- Deployment finalized:
  `0xAa0E282Be73f13BB1A388bB4E4F38Fe2165B9368`
- Explorer:
  `https://explorer-studio.genlayer.com/address/0xAa0E282Be73f13BB1A388bB4E4F38Fe2165B9368`
- Deploy transaction:
  `0x502e10a3bc5402985a856a19e8143ba7c634826401d5d1e2071d1d8db6868512`
- Studio schema loaded with the hosted runner header:
  `# v0.2.16` and
  `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.

The Explorer transaction source contains `def judge() -> dict` inside
`evaluate()`, calls `gl.eq_principle.prompt_comparative(judge, PRINCIPLE)`
directly, and contains no `_judgment_fn` callback factory. The hosted Studio
runner accepted this header at schema/deploy time. The current SDK docs describe
the newer `v0.3.0-rc7` runner, so a future migration should be mechanical:
update the dependency header and re-check event/schema generation. The
deployment verification is ABI/schema and deployment finality only; full live
LLM adjudication was not simulated.

## Layout

```
contract.py     the Intelligent Contract
README.md       this file
TEST_PLAN.md    seven cases, expected results, Studio notes
sim/            offline stand-in for the SDK plus the seven-case check
```

Solo project. MIT licensed.
