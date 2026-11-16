# Two-layer Commons v0.1 results

Frozen predictions SHA-256
6b4a0d139899dc52ea75905917d551b086211b8bd4fd28d8d15608023a41d4d3
at 2026-11-14 14:55:00 UTC. Python 3.12.14, NumPy 2.3.5.

Eight predecessor runs and 1,536 matched reader trajectories. The primary
table uses eight ACTIVE readers in each condition with ASK_ONLY, REMOVE,
SILENCE and OPEN. Each condition has 96 ticks. The result files retain
each individual member's actions and outcomes.

| Condition | Independent access | Independent checks | Correct | Wrong | Unresolved | Deferred |
|---|---:|---:|---:|---:|---:|---:|
| Original | 36 | 14 | 36 | 23 | 0 | 37 |
| Changed ground | 84 | 36 | 56 | 27 | 0 | 13 |
| Story | 36 | 33 | 31 | 2 | 26 | 37 |
| Changed ground and story | 84 | 83 | 76 | 7 | 0 | 13 |

- **Ground, outside body.** The median paired gain was six independent
  access opportunities in each choice mode. Ground widens an authored
  evidence channel and lowers friction. BODY_ONLY received the access
  without choosing evidence. FROZEN used the repeated-source default.
- **Story, outside choice to inside choice.** ACTIVE searched once per
  trial, with 256 successful requests. FROZEN and BODY_ONLY retrieved
  zero. The median gain from story on original ground was two independent
  checks. Both pathways together gained a median 4.5 correct judgments
  versus original, with an increase on every tape.
- **Restoration.** Each ACTIVE release arm signed and completed 256
  releases. Burden cleared at tick 4 after asking and tick 3 after turning
  and approaching. The timing difference follows the scripted schedule.
  Other modes completed zero repairs.
- **Harvest.** FEED deposited two units in 672 trials. Each arm had 96
  harvest failures. REMOVE produced zero deposits.
- **Silence.** The kernel denied 256 requests in SILENCE. STEWARD_ARM
  applied and witnessed 256 exact fixture mutations. The new curiosity
  value is disconnected from the toy reader policy.
- **Hand.** ACTIVE OPEN forwarded 17,888 circulation units versus 11,552
  in ACTIVE CLENCH. Re-offers are included. Provision reached the unready
  in every mode. A pulse-only comparison kept internal terrain, evidence
  and settled state equal.
- **Body.** All 18,432 reader body ticks ran. Reader faults logged were
  2,880 intake, 1,536 regulation, 2,496 circulation and 2,496 ground faults.
  All 1,536 operational crossings followed some receipt, and 24 occurred
  on ticks with no receipt. The separately frozen zero-pulse diagnostic
  recorded 16 operational crossings, eight on each ground, with zero
  received grace, signed repair or protected mutation.

The JSON files and manifests give every reader trajectory and digest.

Local replay matched all ten main JSON digests byte for byte. The
supplemental JSON also matched byte for byte. Verification checked bounded
occupancies, equal tapes and reader identities across arms, story access
only after a request, choice-mode behavior, and exact signed repair fields.
The compatibility adapter passed the fixed RFC 8032 empty-message vector
and rejected the signature for altered content.
