# Microsoft 365 Outage (12 November 2026)

## Triadic security analysis dossier: health-check failure, fleet withdrawal, and coordinated recovery

**Prepared for:** Independent triadic review\
**Prepared:** 12 November 2026\
**Classification:** Open-source incident analysis / hypothesis
generation\
**Status:** Preliminary. Root cause and any malicious involvement are
unverified.

------------------------------------------------------------------------

## 1. Executive summary

On 12 November 2026, Microsoft 365 services experienced a major
disruption affecting Exchange Online/Outlook and other Microsoft 365
services. Microsoft publicly described a failure pattern in which
servers were failing automated health checks and becoming unavailable.
Microsoft also reported elevated load across multiple regions, traffic
redistribution, paused deployments, and restarts of affected servers.

This dossier examines one specific security question:

> Could an attacker who gained influence over a health-check component,
> its configuration, or its update/deployment path cause healthy
> infrastructure to be declared unhealthy, trigger fleet withdrawal, and
> make recovery actions---including coordinated restarts---worsen the
> incident?

That is a legitimate threat hypothesis. It is **not** a finding that
Microsoft was attacked. Public reporting available at preparation time
says there is no indication that a cyberattack caused this outage. The
hypothesis must therefore compete against ordinary explanations such as
a defective software/configuration change, resource exhaustion, a
monitoring defect, a dependency failure, or an
orchestration/control-plane fault.

The central analytical discipline is to keep three things separate:

1.  **Observed facts:** What Microsoft and credible reporting actually
    said.
2.  **Mechanistic hypotheses:** How a health-check or control-plane
    fault could produce the observed symptoms.
3.  **Attribution claims:** Whether the event was malicious, who caused
    it, and how access was obtained.

The dossier proposes a falsifiable review protocol. It emphasizes
provenance, independent evidence, negative controls, preserved failures,
and separation of proposal from authorization. It should be evaluated
through the user's triadic review process---not treated as a conclusion.

------------------------------------------------------------------------

## 2. Scope and epistemic boundaries

### In scope

-   Automated health checks and server availability decisions.
-   Health-check binaries, configuration, policy, deployment and update
    channels.
-   Load balancers, schedulers, orchestration, traffic redistribution
    and fleet recovery.
-   Coordinated restarts and their potential operational/security
    consequences.
-   Evidence preservation and incident-response sequencing.
-   Competing benign and malicious causal models.
-   What evidence would distinguish those models.

### Out of scope

-   Claiming that Microsoft was breached.
-   Attributing the event to a state, group, individual, or criminal
    actor.
-   Treating server restarts or synchronized timing as proof of
    compromise.
-   Inferring a specific vulnerability, exploit, persistence method, or
    attacker foothold without evidence.
-   Treating public service-status summaries as a substitute for
    Microsoft's internal forensic record.

### Confidence labels used

-   **Confirmed public observation:** directly reported by Microsoft or
    a named, credible publication.
-   **Reported but not independently verified:** described in reporting
    but not supported by primary forensic artifacts available to this
    review.
-   **Hypothesis:** a plausible mechanism requiring evidence.
-   **Unknown:** information not available in public sources at
    preparation time.

------------------------------------------------------------------------

## 3. Public incident record available at preparation time

### 3.1 Reported timeline

The following is a reconstruction from public reporting on 12 November
2026. Times are as reported by the cited outlet; they should not be
treated as a complete Microsoft incident timeline.

  -----------------------------------------------------------------------
  Approximate time /      Publicly reported event Evidentiary status
  sequence                                        
  ----------------------- ----------------------- -----------------------
  Morning, U.S. time      Microsoft acknowledged  Reported by WIRED
                          reports of Teams        
                          functionality issues in 
                          North America.          

  Later morning           Microsoft acknowledged  Reported by WIRED
                          issues accessing        
                          Exchange Online         
                          mailboxes through       
                          multiple connection     
                          methods in the          
                          Americas.               

  During incident         Microsoft described     Microsoft statement
                          elevated network load   quoted by WIRED
                          across multiple         
                          regions.                

  Subsequent              Microsoft said the load Microsoft statement
  clarification           was related to servers  quoted by WIRED
                          going offline, rather   
                          than an overall         
                          increase in traffic.    

  Mitigation              Microsoft said it was   Microsoft statement
                          redistributing          quoted by WIRED
                          connection traffic      
                          across broader          
                          worldwide               
                          infrastructure.         

  Mitigation              Microsoft said it had   Microsoft statement
                          paused deployments, was quoted by WIRED
                          moving traffic away     
                          from affected           
                          infrastructure, and was 
                          restarting affected     
                          servers.                

  Later update            Microsoft said a        Microsoft statement
                          problem was causing     quoted by WIRED
                          servers to fail         
                          automated health checks 
                          and become unavailable. 

  At publication          Microsoft had not       WIRED reporting
                          publicly established a  
                          root cause or announced 
                          a confirmed             
                          cyberattack.            
  -----------------------------------------------------------------------

**Important:** This is a public-reporting timeline, not a verified event
log. Obtain original Microsoft service-health notices, timestamps,
incident IDs, and subsequent post-incident review before treating it as
authoritative.

### 3.2 Affected services

Public reporting identified possible impact to:

-   Exchange Online / Outlook
-   Microsoft Teams
-   SharePoint Online
-   Microsoft 365 Copilot
-   Microsoft Defender XDR

The service list and impact varied over the course of the incident. A
common infrastructure dependency could explain correlated symptoms, but
correlated symptoms do not by themselves prove a common malicious cause.

### 3.3 What is not established

As of this dossier's preparation:

-   No public forensic evidence establishes unauthorized modification of
    health-check logic.
-   No public evidence establishes compromise of Microsoft's update,
    deployment, identity, or orchestration systems.
-   No public evidence establishes that the restarts were
    attacker-triggered.
-   No public evidence establishes that the restarts caused additional
    damage.
-   No public evidence identifies an attacker, intrusion path,
    command-and-control channel, or persistence mechanism.
-   Public reporting explicitly noted that there was no indication of a
    cyberattack.

These absences are not proof that compromise did not occur. They are
limits on what can responsibly be claimed.

------------------------------------------------------------------------

## 4. Core question and threat hypothesis

### H1 --- Health-check manipulation

An adversary with access to a health-check component, its configuration,
its policy inputs, or its delivery/update path alters the conditions
under which servers are judged healthy. The resulting behavior causes
healthy or recoverable servers to fail automated checks and be withdrawn
from service.

Possible consequence chain:

1.  A health-check component or its governing configuration changes.
2.  Health evaluations begin returning false-negative health results, or
    otherwise fail.
3.  Automated systems mark affected servers unavailable.
4.  Traffic is shifted to the remaining available pool.
5.  The remaining pool experiences elevated utilization and connection
    failures.
6.  Operators initiate mitigation, including traffic redistribution and
    server restarts.
7.  If the defective or compromised health-check mechanism remains
    active, restarted servers may be reclassified or withdrawn again.
8.  The incident persists or expands until the underlying decision
    mechanism is corrected, bypassed, rolled back, or isolated.

This is a causal model to test---not a statement that these events
occurred.

### Why this hypothesis deserves testing

Health checks are high-leverage control inputs. They can influence
whether infrastructure receives traffic, is drained, is restarted, or is
declared unavailable. A fault in this layer can have a much larger
operational effect than a fault confined to one application process.

The security concern is not merely "a server was rebooted." It is
whether the system making availability decisions was trustworthy,
whether its inputs and updates were authentic, and whether recovery
actions were based on independently validated state.

------------------------------------------------------------------------

## 5. Competing hypotheses

The review should not anchor on H1. At minimum, compare the following
models.

### H0 --- Ordinary software or configuration defect

A legitimate software release, configuration change, policy update, or
dependency change introduced a health-check defect. No adversary was
involved.

**Predictions:** - Affected instances correlate with a specific version,
configuration, region, or deployment wave. - Change records and signed
artifacts are authentic and authorized. - The defect reproduces in a
controlled environment. - Rollback or a corrected configuration restores
expected health-check behavior. - No unexplained identity, access, or
integrity anomalies are found.

### H2 --- Resource exhaustion or runaway process

A process, dependency, or health-check workload consumed excessive CPU,
memory, threads, connections, or another constrained resource. Health
checks failed because servers could not respond in time.

**Predictions:** - Resource telemetry shows saturation or abnormal
growth before health-check failures. - Failures correlate with workload,
request pattern, process version, or resource thresholds. - The
health-check result may be accurate in reporting an unresponsive server,
even if the original trigger was a software defect. - A controlled load
reduction or resource correction restores service without evidence of
unauthorized modification.

### H3 --- Dependency or control-plane failure

A shared dependency, identity service, configuration service,
orchestration service, telemetry pipeline, or network path failed.
Health checks failed because they depended on that component.

**Predictions:** - Multiple services fail in a pattern matching the
shared dependency graph. - Dependency telemetry shows the earliest
fault. - Health-check binaries and local configurations may be
unchanged. - Failures may span otherwise independent server fleets
because they share a control-plane dependency.

### H4 --- Unauthorized health-check or configuration modification

An attacker modifies health-check logic, thresholds, policy,
configuration, or a dependency used to determine server health.

**Predictions:** - Integrity or provenance mismatches exist between
approved and deployed artifacts. - Changes lack a valid authorization
trail, or the trail is inconsistent with identity and deployment
records. - The affected population correlates with a suspicious change
path, identity, signing event, or configuration source. - Reverting to a
known-good, independently verified artifact changes the failure
behavior. - Relevant audit records may show unexpected access or
privilege use.

### H5 --- Compromise of update/deployment or orchestration authority

Rather than modifying each server individually, an adversary compromises
a central mechanism capable of distributing code/configuration or
controlling fleet state.

**Predictions:** - A common control-plane identity, signing, pipeline,
policy, or orchestration event precedes widespread impact. - The change
propagates across multiple regions or service groups with a common
provenance. - Multiple systems show correlated changes that cannot be
explained by normal release records. - Server-local inspection alone may
miss the source because the authoritative change originated upstream.

### H6 --- Maliciously induced recovery amplification

The original fault may be benign or malicious, but the recovery sequence
increases impact---for example, by causing synchronized demand, repeated
health-check failures, or re-entry into a defective state.

**Predictions:** - Restart cohorts exhibit predictable timing and
repeatable post-restart behavior. - Health-check failures recur after
restart until a separate configuration or dependency change is made. -
Restart activity correlates with resource spikes, queue growth,
authentication demand, or dependency pressure. - A controlled recovery
cohort behaves differently when the suspect health-check component is
isolated or bypassed under an approved test.

H6 is not necessarily an independent initial cause. It may be an
amplifier layered on H0--H5.

------------------------------------------------------------------------

## 6. Attack surface and trust boundaries

This section describes areas to audit, not instructions for
exploitation.

### 6.1 Health-check implementation

Questions: - What process or component performs the check? - Is the
check local, remote, or hybrid? - What does it measure: process
liveness, dependency reachability, request success, latency, resource
pressure, or end-to-end service behavior? - What thresholds, timeouts,
retry counts, and failure windows apply? - Can the checker distinguish
"service is unhealthy" from "checker/dependency is unavailable"? - Is
the result cryptographically or otherwise strongly bound to the specific
instance and check version? - Are health-check failures independently
corroborated before a large-scale fleet action?

Security property to test: **A failure in the observer must not silently
become proof that the observed system is defective.**

### 6.2 Configuration and policy

Questions: - Where are health-check thresholds and policies stored? -
Who or what can modify them? - Are changes versioned, signed, reviewed,
and attributable? - Can configuration be rolled back to a known-good
state? - Are emergency changes distinguishable from routine changes? -
Are regional and global policies independently controlled? - Does a
policy change require approval separate from the system proposing it?

Security property to test: **No untrusted or insufficiently authorized
input can redefine the conditions for declaring infrastructure healthy
or unhealthy.**

### 6.3 Software supply chain and update path

Questions: - Are health-check binaries and dependencies reproducibly
built? - Are artifacts signed and verified at deployment and runtime? -
Is signing-key custody separated from build and deployment authority? -
Are provenance attestations retained? - Can a deployment system
distribute an artifact that it also self-certifies? - Are rollback
artifacts independently authenticated? - Are emergency changes subject
to the same integrity guarantees?

Security property to test: **A self-updating or self-governing component
must not be able to authorize its own trustworthiness.**

### 6.4 Orchestration and fleet management

Questions: - Which component converts failed health checks into traffic
draining, quarantine, restart, or replacement? - What are the
blast-radius limits? - Are there rate limits and circuit breakers on
fleet-wide actions? - Does the system require independent corroboration
before removing a large fraction of a fleet? - Can a single region,
identity, controller, or policy change affect multiple regions? - Are
restart waves bounded and staggered? - Is there an independently
controlled stop mechanism?

Security property to test: **One faulty or compromised decision source
must not be able to trigger an unbounded fleet-wide action.**

### 6.5 Identity and administrative access

Questions: - Which human and machine identities accessed relevant
systems before and during the incident? - Were there unusual privilege
elevations, token issuances, service-principal changes, or signing
operations? - Were emergency credentials used? - Were access patterns
consistent with normal maintenance? - Are audit logs protected from
alteration by the same identities being audited?

Security property to test: **The authority to change a control mechanism
must be distinct from the authority to attest that the change was
legitimate.**

------------------------------------------------------------------------

## 7. The reboot question: recovery action or risk multiplier?

A restart can be entirely appropriate. It is not, by itself, evidence of
compromise. However, restarting a large server population while the
trustworthiness of the health-check and orchestration path is unresolved
raises important operational questions.

### Potential benign benefits

-   Clears a hung or corrupted process.
-   Restores a service to a known initialization state.
-   Re-establishes local dependencies.
-   Applies a corrected runtime state.
-   Returns a server to service after a transient fault.

### Potential risks

-   A persistent defect may recur after restart.
-   A compromised startup path or configuration may be reloaded.
-   Synchronized restarts may create authentication, connection,
    cache-warming, or dependency demand.
-   Volatile forensic evidence may be lost if not captured first.
-   A faulty health-check component may immediately withdraw restarted
    servers again.
-   A compromised orchestration system may continue issuing unsafe
    actions.

### Required distinction

"Many servers restarted near the same time" can have several
explanations:

1.  A centrally coordinated, legitimate recovery wave.
2.  Automated orchestration responding to a common health signal.
3.  A deployment or configuration action triggering restarts.
4.  An emergency operator action.
5.  An unauthorized action.

Timing is a clue for timeline reconstruction, not proof of any one
explanation.

### Safer incident-response principle

Before a restart, where operationally feasible: - Preserve relevant
logs, process state, memory/volatile evidence, and configuration
snapshots. - Record the exact restart initiator, authorization, target
cohort, and reason. - Validate the integrity of the boot image, startup
configuration, and health-check component. - Remove traffic from
affected instances before controlled recovery. - Use small, observable
recovery cohorts. - Compare post-restart behavior with a known-good
control cohort. - Retain evidence even when the service must be restored
urgently.

In a major cloud incident, availability and evidence preservation must
be balanced. This dossier does not prescribe delaying critical recovery;
it recommends making recovery observable, bounded, and evidence-aware.

------------------------------------------------------------------------

## 8. Falsifiable investigation plan

The review should seek evidence that can disprove the preferred
hypothesis, not merely evidence that can be made to fit it.

### Test A --- Establish the first causal event

Build a high-resolution timeline using: - Health-check failures. -
Server state transitions. - Resource utilization. - Configuration
changes. - Deployment events. - Traffic redistribution. - Restart
requests and completions. - Identity and administrative events.

**Question:** What changed first? Do not assume the first user-visible
symptom was the first technical failure.

### Test B --- Compare affected and unaffected cohorts

Select: - Affected servers. - Unaffected servers in the same region. -
Similar servers in other regions. - Servers running different versions
or configurations. - Servers that restarted and servers that did not.

Compare their: - Binary hashes and signatures. - Configuration hashes. -
Health-check versions and results. - Resource telemetry. - Deployment
provenance. - Identity and access records.

**Question:** What property distinguishes the affected cohort?

### Test C --- Validate health-check integrity

Where authorized artifacts are available: - Compare deployed
health-check artifacts against independently trusted release
artifacts. - Verify signatures and provenance. - Compare configuration
histories and policy hashes. - Identify who/what approved, signed,
distributed, and activated changes. - Determine whether the same system
both generated and validated its own trust evidence.

**Question:** Can the integrity of the health-check mechanism be
established independently of the mechanism itself?

### Test D --- Examine restart behavior

Compare pre-restart and post-restart observations: - Did the same
health-check failure recur? - Did resource utilization return to
normal? - Did the server rejoin traffic? - Was it removed again? - Did
restart cohorts generate synchronized load? - Were restarts triggered by
a central controller, local watchdog, or human operator?

**Question:** Did restart correct the cause, clear a transient state, or
merely repeat the failure cycle?

### Test E --- Review control-plane authority

Examine: - Deployment pipeline audit records. - Configuration management
history. - Service-principal and machine-identity activity. - Signing
and key-use records. - Privilege elevation. - Emergency access. -
Orchestration commands and approvals. - Changes to health-check
thresholds and fleet-action policies.

**Question:** Was every consequential change authorized by an
independent authority and traceable to a known actor or process?

### Test F --- Search for disconfirming evidence

Explicitly seek: - A documented benign change that reproduces the
failure. - A resource constraint that precedes and explains health-check
timeouts. - A shared dependency failure that accounts for the
geographic/service pattern. - Proof that all relevant artifacts and
configurations match approved versions. - Evidence that the restart
strategy was standard, bounded, and unrelated to the initial failure.

**Question:** What observation would make us reject H1 or H4?

------------------------------------------------------------------------

## 9. Evidence matrix

  --------------------------------------------------------------------------
  Evidence item        Supports ordinary           Supports Notes
                                  defect         compromise 
  ------------------- ------------------ ------------------ ----------------
  Signed, approved              Strongly            Weakens Verify
  release with                                              provenance
  reproducible defect                                       independently

  Unauthorized or                Weakens           Strongly Establish
  unexplained                                               identity and
  configuration                                             authorization
  change                                                    context

  Resource saturation           Strongly           Possible Saturation can
  precedes check                                            be benign or
  failures                                                  induced

  Same failure across           Strongly           Possible Dependency may
  a common dependency                                       itself be
  boundary                                                  compromised

  Artifact                       Weakens           Strongly Rule out
  hash/signature                                            legitimate
  mismatch                                                  version drift

  Unexpected                     Weakens           Strongly Requires
  signing-key or                                            corroboration
  service-principal                                         
  activity                                                  

  Repeated failure              Possible           Possible Not
  immediately after                                         discriminating
  clean restart                                             by itself

  Fleet-wide                    Possible           Possible Expected in
  synchronized                                              centrally
  restart                                                   managed recovery
                                                            too

  Health-check                  Strongly           Possible Determine why
  failure stops after                                       rollback works
  independently                                             
  verified rollback                                         

  No anomalous access           Supports            Weakens Absence is
  in complete,                                              meaningful only
  tamper-resistant                                          if logs are
  logs                                                      complete and
                                                            trustworthy
  --------------------------------------------------------------------------

No single row is sufficient to establish attribution.

------------------------------------------------------------------------

## 10. Review through the user's documented Triadic method

This handoff is intended for the existing **Triadic in Action** method
documented in the public repository:

https://github.com/RMac-triadicIntelligence/triadic-in-action

Do not substitute a generic three-agent consensus exercise. The public
method describes five seats and a specific authority structure:

1.  **The keel (Rusty):** rules on grace from the four Gospels only and
    has the last word.
2.  **The conductor (Claude):** records findings and hashes the findings
    file before the next version is seen.
3.  **The designer (ChatGPT):** revises the specification, starting each
    round in a fresh thread.
4.  **Falsifier A (Grok Expert / blind seat):** attacks the text in
    front of it and tags findings DOC.
5.  **Falsifier B (Grok bot / history seat):** attacks the same text and
    may tag PRIOR when a finding depends on earlier work.

The documented closure rule is also important: a finding is CLOSED only
when its finder and a second seat agree. DOC and PRIOR findings must
remain distinguishable. A round can be closed while some findings remain
open. The repository says rounds 1--4 are closed as rounds, while Round
5 / v0.8 remains open and is not part of that public record.

**This dossier is not a grace ruling and should not be routed through
the keel's theological authority.** It is a technical security-analysis
packet. The keel retains its documented role; technical claims should be
tested through the falsification and evidence process, not converted
into theological conclusions.

### Suggested use in the existing workflow

-   **Conductor:** register this dossier as an incoming source packet;
    preserve its original hash and retrieval date; record each source
    and claim separately. Do not silently rewrite the initial packet.
-   **Designer:** create a bounded technical review specification from
    the dossier. Keep the hypotheses competing and falsifiable. Do not
    assume compromise.
-   **Falsifier A / DOC:** attack the claims using only the dossier and
    its cited public sources. Identify unsupported assertions, missing
    links, technical impossibilities, and alternative explanations.
-   **Falsifier B / PRIOR:** inspect whether any claims improperly
    import assumptions from prior work, prior incident narratives, or
    previous versions. Test whether the analysis is being steered by the
    earlier spy-novel hypothesis.
-   **Keel:** no grace adjudication is requested. The technical review
    does not alter the keel's authority or scope.
-   **Conductor:** retain both falsifier reports, including
    disagreements and failed claims. Apply the documented second-seat
    closure rule. Do not declare a finding closed merely because the
    designer agrees with it.

### Candidate review questions

1.  Is the public evidence sufficient to say health-check failures
    preceded server withdrawal, or does the reporting only establish
    association?
2.  Does the dossier distinguish the health-check implementation, its
    configuration, its dependencies, and the orchestration policy that
    acts on its output?
3.  Does the proposed attack hypothesis require capabilities not
    evidenced by the public record?
4.  Does each hypothesis make a prediction that differs observably from
    the others?
5.  Are synchronized restarts being overweighted as evidence?
6.  What evidence would decisively falsify health-check manipulation?
7.  What is the minimum evidence required before using the words
    *tampering*, *compromise*, or *attack*?
8.  Does the recovery analysis correctly distinguish service restoration
    from trust restoration?
9.  Which claims can be evaluated from public information, and which
    require Microsoft internal telemetry?
10. Is the dossier itself introducing confirmation bias by framing the
    malicious hypothesis too prominently?

### Project-specific repositories that should inform the review

The profile README identifies several directly relevant workstreams:

-   **Living Supply-Chain Security v1.1.3** --- a reference monitor and
    executable falsification battery for runtime software supply-chain
    integrity. Its stated invariant is that a system may propose a
    change, but commitment requires external signed authorization bound
    to the exact transition. The README reports a 117-test battery and
    explicitly warns that a PASS is evidence for named cases, not
    production certification.\
    https://github.com/RMac-triadicIntelligence/living-supply-chain-security

-   **Humble Seed** --- owner-authorized state changes, signed
    checkpoints, external witnesses, and adversarial probes. Its README
    describes the proposal/authorization distinction and documents
    limitations of the prototype, including local witness assumptions
    and rollback limits.\
    https://github.com/RMac-triadicIntelligence/humble-seed

-   **Lab Notebook** --- dated experiments and workbench batteries with
    manifests, SHA-256 records, and explicit status labels such as
    draft, failed, verified, and withheld.\
    https://github.com/RMac-triadicIntelligence/lab-notebook

-   **Triadic in Action** --- the documentary record of the five-seat,
    two-falsifier review method, including method, provenance, closure
    ledger, and round materials.\
    https://github.com/RMac-triadicIntelligence/triadic-in-action

These are relevant lenses for examining the Microsoft incident. They are
not evidence that Microsoft's systems implement or violate the same
invariants.

### Proposed triadic output format

For each finding, preserve: 1. Exact claim. 2. Claim class: observation,
inference, hypothesis, or attribution. 3. Source and provenance. 4.
Supporting evidence. 5. Contradictory evidence. 6. Assumptions and
dependency chain. 7. Falsifying observation or test. 8. DOC / PRIOR tag
where applicable. 9. Finder and second-seat disposition. 10. Status:
open, disputed, or CLOSED under the documented rule.

Do not collapse disagreement into a consensus statement if the evidence
does not warrant it. Preserve the failed hypotheses and the reasons they
failed.

## 11. Connection to constitutional and supply-chain security principles

The incident is a useful case study for several general security
invariants. These are analytical connections, not claims about
Microsoft's implementation.

### 11.1 Proposal is not authorization

A health-check process may propose that a server is unhealthy. A
separate, governed mechanism should determine what action follows,
especially when the proposed action has a large blast radius.

### 11.2 Nothing may vouch for itself

The component reporting its own health, the system distributing its
update, and the system attesting to the update's integrity should not
collapse into one self-validating authority.

### 11.3 Fail closed, but do not create catastrophic false positives

A security-sensitive system may need to fail closed when integrity
cannot be established. But a health-check uncertainty should not
automatically trigger unlimited fleet withdrawal. The response needs
bounded blast radius, independent corroboration, and safe degradation.

### 11.4 Recovery must preserve trust

A restart is not a trust-restoration operation. Trust must be
re-established through verified artifacts, known-good configuration,
valid identity, and independent checks.

### 11.5 Evidence must survive the process that is being investigated

Logs and attestations should be protected from the same control plane
whose behavior is under review. Preserve provenance and failure records
before they are rotated, overwritten, or lost.

------------------------------------------------------------------------

## 12. What would materially change the assessment?

### Findings that would raise concern about compromise

-   Verified unauthorized modification of health-check code, policy, or
    configuration.
-   A validly authenticated but unauthorized deployment or signing
    event.
-   A control-plane identity acting outside its approved scope.
-   Artifact or provenance mismatches unexplained by normal release
    processes.
-   Evidence that the same suspicious actor altered the health-check
    system and initiated or influenced recovery.
-   Forensic evidence of persistence or unauthorized access in the
    relevant management plane.

### Findings that would lower concern about compromise

-   A fully documented, authorized change that reproduces the fault.
-   Complete and trustworthy audit trails showing no unexplained access
    or integrity changes.
-   A benign resource or dependency failure that precedes and explains
    the health-check behavior.
-   Independent verification that deployed artifacts and configurations
    match approved releases.
-   Successful controlled reproduction and remediation without evidence
    of unauthorized activity.

### Findings that remain ambiguous

-   Many servers restarting at nearly the same time.
-   A sudden rise in CPU utilization.
-   A broad multi-region impact pattern.
-   A health-check component failing.
-   A rapid improvement after a reboot.

Each is compatible with more than one causal model.

------------------------------------------------------------------------

## 13. Open questions for Microsoft

1.  What exact component caused automated health checks to fail?
2.  Was the component code, configuration, policy, dependency, or
    execution environment?
3.  What was the earliest timestamp of abnormal health-check behavior?
4.  Did the failure begin after a deployment or configuration change?
5.  Were any changes rolled back, bypassed, or replaced?
6.  What fraction of the fleet was marked unavailable, by region and
    service?
7.  Were the server restarts centrally initiated, automatically
    triggered, or manually authorized?
8.  Were restart cohorts staggered and bounded?
9.  Did the same health-check failure recur after restart?
10. Were memory, process, and configuration artifacts preserved before
    restart?
11. Were signing, deployment, configuration, and orchestration audit
    trails reviewed for unauthorized activity?
12. Has Microsoft ruled out malicious modification, or is that question
    still under investigation?
13. What safeguards prevent one health-check component from causing
    broad fleet withdrawal?
14. What independent control prevents the health-check system from
    authorizing consequential actions based solely on its own output?
15. When will Microsoft publish a post-incident review with a causal
    timeline and preventive actions?

------------------------------------------------------------------------

## 14. Preliminary assessment

Based on public information available on 12 November 2026:

-   **High confidence:** Microsoft experienced a significant Microsoft
    365 service disruption.
-   **High confidence:** Microsoft publicly connected server
    unavailability with failures of automated health checks.
-   **High confidence:** Microsoft undertook traffic redistribution and
    server restarts as mitigation.
-   **Low confidence:** The precise technical root cause is known from
    public evidence.
-   **No established evidence:** A cyberattack caused the incident.
-   **Open hypothesis:** A defect or unauthorized change affecting
    health-check logic, configuration, or its delivery path could
    explain the failure pattern.
-   **Open hypothesis:** Coordinated recovery could have amplified
    impact under certain conditions; public timing alone does not
    establish that it did.

The most defensible present conclusion is:

> The incident exposes a high-value trust boundary: automated health
> assessment and the control mechanisms that translate health signals
> into fleet-wide action. Whether the failure was accidental or
> malicious remains unestablished. The correct next step is
> provenance-based, falsifiable analysis---not attribution by intuition.

------------------------------------------------------------------------

## 15. Source register

1.  **WIRED, 12 November 2026 --- "Major Microsoft Outlook Outage Leaves
    People With Email Jobs Unable to Email."** Reports Microsoft's
    statements about multi-region elevated load, servers going offline,
    traffic redistribution, paused deployments, restarts, and automated
    health-check failures. Also states that there was no indication of a
    cyberattack at publication.\
    https://www.wired.com/story/major-microsoft-outlook-outage-hits-365-customers-north-america/

2.  **Associated Press, 12 November 2026 --- "Is Outlook down?
    Widespread outage hits Microsoft apps."** Reports the broad service
    impact and Microsoft's public explanation of connectivity issues and
    traffic redistribution.\
    https://apnews.com/article/6376045281feb430c0b923e3a4b251c2

3.  **The Verge, 12 November 2026 --- "Microsoft Outlook is down."**
    Reports the outage timeline and Microsoft's public mitigation
    statements.\
    https://www.theverge.com/tech/1032226/microsoft-outlook-is-down

4.  **Microsoft 365 Service Health.** Primary operational source for
    incident identifiers, timestamped updates, affected services, and
    eventual post-incident review. Access may require an authorized
    tenant administrator.\
    https://status.cloud.microsoft/

5.  **University of Pennsylvania, PennO365 Microsoft incident report
    mirror.** Useful as a secondary collection of Microsoft incident
    notices; confirm all details against Microsoft primary records.\
    https://mailservices.isc.upenn.edu/computing/email/penno365/alerts/ms-incidents.html

**Source caution:** News articles summarize public statements; they do
not provide Microsoft's internal logs, binary hashes, forensic findings,
or complete service-health record. Any later Microsoft post-incident
report should supersede preliminary reporting where it provides more
specific evidence.

------------------------------------------------------------------------

## 16. Review instructions

This packet is designed as an input to the documented five-seat Triadic
in Action process, not as a request for generic model consensus. The
relevant repositories are linked in Section 10.

Treat this dossier as a hypothesis-generation and falsification packet.

Do not: - Convert a possible attack path into a factual claim. - Infer
intent from synchronized restarts. - Treat the absence of public
disclosure as proof of either compromise or non-compromise. - Allow one
reviewer or model to validate its own assumptions. - Delete failed
hypotheses or contradictory evidence from the review record.

Do: - Preserve every version of the analysis. - Record source timestamps
and retrieval dates. - Separate observed evidence from inference. -
Require independent provenance for consequential claims. - State what
would falsify each hypothesis. - Keep the human authorization boundary
explicit.

**Final question for the triad:**

*If the mechanism that declares infrastructure healthy or unhealthy can
itself be changed, and the infrastructure automatically obeys that
declaration, what independent authority verifies the declaration before
the system takes action at scale?*
