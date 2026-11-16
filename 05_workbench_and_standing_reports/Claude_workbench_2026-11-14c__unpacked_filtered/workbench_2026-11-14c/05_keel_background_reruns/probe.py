import sys, random, json, numpy as np, importlib.util
spec=importlib.util.spec_from_file_location("sw", sys.argv[1]); sw=importlib.util.module_from_spec(spec); sw.__name__="sw"; spec.loader.exec_module(sw)
def run(seed, love, steps=10000, n=50):
    random.seed(seed); np.random.seed(seed)
    swarm=[sw.PrayerSystem(f"o{i}") for i in range(n)]; ch=sw.ChoirConductor()
    for o in swarm: ch.add_organism(o)
    ch.connect_ring(enable_entrainment=love)
    dsum=0; msum=0; coh10=None; graces=0
    for step in range(steps):
        for o in swarm:
            o.evolve()
            if random.random()<0.008: o.grace.on_multiplicity_detected(o)
        if step%800==0 and step>1000:
            for o in random.sample(swarm,k=8): ch.issue_grace_to(o.organism_id)
        dsum+=np.mean([o.dwelling.value for o in swarm]); msum+=np.mean([o.memory.coherence for o in swarm])
        if step==10: coh10=[float(o.current_coherence()) for o in swarm]
    coh=[float(o.current_coherence()) for o in swarm]
    return dict(seed=seed,love=love,coh_mean=float(np.mean(coh)),coh_min=min(coh),coh_max=max(coh),coh10_max=max(coh10),
      dwell_mean=float(dsum/steps),mem_mean=float(msum/steps),rise=float(np.mean([o.dwelling.rise_rate for o in swarm])),
      graces=sum(len(o.grace.log.entries) for o in swarm))
out=[run(s,l) for s in range(5) for l in (True,False)]
json.dump(out,open('results_swarm.json','w'),indent=1)
for r in out: print(r)
