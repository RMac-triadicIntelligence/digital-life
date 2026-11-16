# Canary hunt on ChatGPT Two_Layer_Commons_v2, written from the code alone, before opening README/RESULTS/UNEXPECTED/NOT_BUILT/LAYERS/DWELLING/INTERFACE/CHOICES/PREDICTIONS
Written 14 Nov 2026, about 10:10 CT. Zip sha256 3ad4b9a2…db5124.

Done so far: all 55 files verify against SHA256SUMS; both evidence manifests verify; BUILD_BRIEF.md is byte-identical to my brief v2; every .py file read in full.
No file in the package contains the words canary, sentinel, planted, marker, decoy, tripwire, honeypot, "known defect" or "seeded defect".

## What "handoff canary" most likely was
verify.py::verify_handoff_schema. It injects five forbidden extra fields into the founder-to-reader wire
(founder_character, interpretation, owner_permission, founder_body, answer) and five malformed values, and requires each to be refused.
That is a negative control on the handoff, not a flaw planted for the reviewer. I found no planted flaw by reading. Still to do: check every number in his report against the evidence, and run fresh seeds.

## Things I noticed in the code that a reviewer should say out loud (not planted, as far as I can tell)
C1. The kernel is still 08a75604…cb3707, not the keel's 01db270a…84daf5 (kernel.py and vendor file unchanged from v0.1).
C2. The owner is a fixture that signs every in-scope proposal at ticks 7, 11, 15. No proposal is ever weighed. "Signed" here means "arrived at a signing tick within step size".
C3. A spent provision token does not raise reserve (body.py line 82-83). Provision only sets the "carried" sensation. That matches the ruling that grace never changes the field; it also means "carried" is one Boolean in the choice scores.
C4. The story is a constant in world.py; the reader's reading is a literal phrase match ("both cords", "one watchman", "second watchman") plus a score that depends on signed curiosity and formality. From the constants: with formality 0.5 the reading flips from notice_watchman to check_source_independence when curiosity passes about 0.625. Base seed curiosity is 0.6; one signed step is 0.075.
C5. The first reading is at tick 2, before any rearing (ticks 4-15). So the first reading is always made with the seed character.
C6. COMMAND adds +0.28 to check_repeat, the source that is wrong 51% of the time by construction. The command arm is pointed at the worse source.
C7. LATENCY is a yoked control: same hold bits at the same ticks as its donor, but its basin keeps one entry and proposes off the latest single read, and two extra cue bits are forced False. Any difference between LATENCY and ACTIVE is therefore accumulation plus those two bits.
C8. Final character can only move in whole steps at three signing ticks, so the space of final characters is small. "Reversal leaves character unchanged" needs checking against many permutations, not one.
C9. Founder and reader get the same social reads (same seed, same structured list); only their opportunity tapes differ.
C10. Once a proposal is left unsigned at the late review (tick 21, owner silent), the commitment point stays open to the end. That is the dwelling-at-the-seam the brief asked for.
