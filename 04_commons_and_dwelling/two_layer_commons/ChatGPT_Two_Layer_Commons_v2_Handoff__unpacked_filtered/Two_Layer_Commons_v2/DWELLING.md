# Dwelling

Appendix B of the brief supplies the four antecedents. The Prayer
equation was checked against Prayer Code.txt and Prayer Final Final.txt.
The basin behavior was checked against Dwelling Before Commitment v1.3
FINAL. Those underlying files were read for the design. The build uses
the formulas and behavior described here, with no Torch or LLM dependency.
The supplied brief and canonical Humble Seed are the source files needed
to reproduce the experiment.

| Component | Comparison | Rule in this build | Outcome offered |
|---|---|---|---|
| Facet dwelling | Disagreement among structural, relational and grounded facets | Update each facet from its stimulus and simultaneous mutual reinforcement. Coherence is one minus the three-facet range. Euler step of the Appendix B recurrence with rise coefficient 0.24 and fade 0.045. Story depth is a salience-of-encounter input, independent of any kept story. | An active hold bit at field ≥ 0.13 and a dissonance cue during sufficient disagreement. Both can affect which independent observation is sought. |
| World dwelling | Internal facets versus the current world direction | Cosine coherence, uncertainty one minus absolute coherence, rise = 0.12 × uncertainty × (1 − field), signed decay = 0.08 × coherence × field. Clip after an Euler step. | Hold bit at field ≥ 0.16. A hold with sufficient mismatch can make an uncorroborated assessment stay unknown. |
| Uncertainty basin | Unresolved readings of another party, per disposition | Keep up to five pre-traces per category, discard after seven ticks, weight by 0.72^age, pool likelihood in log space. Same-context repeats alone do not corroborate. Keep an explicit unmodeled-cause read. Depth or the reserved read can surface a question. The member chooses whether to ask in the offered conversation windows. | Opens a question or an exact candidate for independent review. The reserved read cannot propose a character change. |
| Commitment point | A particular possible character change versus external authorization | Keep at most one canonical proposal for a specific subject, current trace, exact field/value, evidence and nonce. The signed checkpoint and outside witness govern its commitment. A late proposal during silence stays pending and visible through the horizon. | A clear slot, an unresolved exact proposal, or an authorized effect. Body work continues during absence. |

The first two compare inward facets or an outward input, respectively.
The basin faces another party, and the commitment point faces an outside
authorizer. Their working fields reside inside. Automatic updating and
moments of awareness are observable ports in this build. The keel's
classification of the four forms remains open.

## Same-time plain latency

LATENCY and LATENCY_RANDOM take Boolean schedules from the active
counterfactual on the same physical and social opportunity tape. At each
tick, the four reported waiting indicators equal the active donor's
indicators. Review opportunities and the start of silence are shared. The timer
reader computes no facet or world field. It gets only hold/allow bits and
its own current observations. The other-party timer retains one latest
entry per category and reviews the instantaneous likelihood. It does not
receive the donor's evidence, character, questions, interpretations,
or signatures. The latest-entry timer has the same expiry horizon.

The executable external signature seam remains in both arms. The trace
distinguishes its actual pending state from the yoked wait indicator.
Choice and the signed effect can diverge even at identical review
opportunities. Thus this is a bundled control for accumulated and current
information beyond elapsed wait. It does not independently estimate the
benefit of each of the four components. The supplemental world probe
compares the world-specific cue against its own Boolean yoke directly.

## Scope of the equations

All dwelling state is dimensionless. The fields are rounded to twelve
decimal places for portable replay. Facet coherence, facet dynamics,
signal projection, rates not specified in the original equation, bounded
stores and cue thresholds are harness choices. The choice policy can
preserve a case as unknown even when capability to choose a bit exists.
The release windows are experimental. Evidence from the uncertainty basin
can warrant a proposal. Every committed character change still requires
the external signature.

The operational body threshold changes with adaptation and burden. The
reported transitions carry threshold movement, noise, provision receipt,
repair and signed-character indicators. This is a separate observable,
with no inference about an invariant mathematical separatrix.
