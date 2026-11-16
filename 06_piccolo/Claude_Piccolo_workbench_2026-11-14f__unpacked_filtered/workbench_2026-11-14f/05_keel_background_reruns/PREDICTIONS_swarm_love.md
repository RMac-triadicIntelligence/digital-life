# Conductor predictions, swarm + love term (Swarmoluslove.txt), written from reading the code, before any run. 14 Nov 2026.
S1. Run as received: crashes with NameError (`organism` undefined in GraceOperator.on_multiplicity_detected) within the first few steps.
S2. With only that one name fixed (pass the organism in): every organism's facet coherence falls to a fixed point below 0.01 within ~10 steps and stays there for all 10,000 steps, every seed. Reason: each facet is overwritten each step by a Hill of the other two; the root turning (0.0007) is erased next step.
S3. Dwelling sits at 1.0 nearly always (rule: rises whenever coherence < 0.98); mean dwelling over the run > 0.85; dips only to 0.3 on internal grace (3%/step) and recovers in ~6 steps.
S4. Love term on vs off: final collective coherence differs by < 0.001; mean dwelling differs by < 0.01. The love term acts on dwelling fields that are all pinned at the same ceiling, so it has nothing to pull.
S5. Grace never changes the facets (it only raises memory.coherence by 0.03 and resets dwelling). The choir's issue_grace_to builds a token and nothing applies it.
S6. memory.coherence: falls 0.003/step, +0.06 per grace (applied twice); at 3%/step grace that nets about -0.0012/step, so it sits at the floor 0.1 most of the time.
Would surprise me: any seed where organisms end with different coherences from each other; any effect of the love term.
