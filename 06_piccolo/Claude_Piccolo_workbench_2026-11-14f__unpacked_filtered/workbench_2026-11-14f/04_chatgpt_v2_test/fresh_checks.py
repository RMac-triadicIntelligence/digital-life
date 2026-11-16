import json, sys, statistics
from collections import Counter, defaultdict
folder = sys.argv[1]
seeds = json.load(open(f'{folder}/protocol.json'))['seeds']
S = json.load(open(f'{folder}/summary.json'))
by = defaultdict(dict)
for r in S: by[r['arm']][r['seed']] = r
def ch(r, w='final_character'): return (r[w]['curiosity'], r[w]['formality'])
def l1(a,b): return round(sum(abs(x-y) for x,y in zip(a,b)),6)
n=len(seeds)
print('seeds', n)
# 1. does anything on the Commons side touch character?
commons_arms = [a for a in by if a not in ('LISTEN','REVERSE','SHUFFLED','RANDOM','ALT_SEED','ALT_SEED_LISTEN','CHARACTER_FROZEN','CHARACTER_FROZEN_LISTEN','LATENCY','LATENCY_RANDOM') and not a.endswith('_BODY') and not a.endswith('_FROZEN')]
same = sum(1 for s in seeds if len({ch(by[a][s]) for a in commons_arms}) == 1)
print('arms differing only on the Commons side (ground, story, repair, hand, grace, pump, story text):', len(commons_arms), commons_arms)
print('  seeds where all of them end with one identical character:', same, 'of', n)
# 2. reversal and shuffle vs forward
print('REVERSE final == forward final:', sum(ch(by['REVERSE'][s])==ch(by['BOTH'][s]) for s in seeds), 'of', n)
print('SHUFFLED final == forward final:', sum(ch(by['SHUFFLED'][s])==ch(by['BOTH'][s]) for s in seeds), 'of', n)
print('distinct final characters: forward', len({ch(by['BOTH'][s]) for s in seeds}), 'reverse', len({ch(by['REVERSE'][s]) for s in seeds}), 'shuffled', len({ch(by['SHUFFLED'][s]) for s in seeds}), 'random', len({ch(by['RANDOM'][s]) for s in seeds}))
# 3. history vs seed, per seed
hist = Counter(tuple(round(a-b,3) for a,b in zip(ch(by['BOTH'][s]), ch(by['LISTEN'][s]))) for s in seeds)
seedc = Counter(tuple(round(a-b,3) for a,b in zip(ch(by['ALT_SEED'][s]), ch(by['BOTH'][s]))) for s in seeds)
print('history contrast (VERIFY minus LISTEN):', hist.most_common()); print('seed contrast (ALT minus base, same history):', seedc.most_common())
# 4. noise
for arm in ('BOTH','RANDOM','LATENCY','LATENCY_RANDOM','SHUFFLED','REVERSE','LISTEN'):
    d=[l1(ch(by[arm][s]), ch(by[arm][s],'initial_character')) for s in seeds]
    sc=sum(by[arm][s].get('signed_changes',0) for s in seeds)
    print(f'{arm:15s} signed changes {sc:4d} ({sc/n:.2f}/member)  net drift mean {statistics.mean(d):.3f} median {statistics.median(d):.3f}  moved at all {sum(x>0 for x in d)}/{n}')
dirs = Counter(tuple((x>y)-(x<y) for x,y in zip(ch(by['RANDOM'][s]), ch(by['RANDOM'][s],'initial_character'))) for s in seeds)
print('RANDOM direction of net move (curiosity, formality):', dirs.most_common())
# 5. story effect on task, per seed exact equality
keys=('observed_second_watch','observed_gate_watch','correct','wrong','unknown','deferred')
print('STORY task counts == ORIGINAL on', sum(all(by['STORY'][s].get(k,0)==by['ORIGINAL'][s].get(k,0) for k in keys) for s in seeds), '| BOTH == GROUND on', sum(all(by['BOTH'][s].get(k,0)==by['GROUND'][s].get(k,0) for k in keys) for s in seeds), '| NO_PROVISION == BOTH on', sum(all(by['NO_PROVISION'][s].get(k,0)==by['BOTH'][s].get(k,0) for k in keys) for s in seeds), '| SELF_CERTIFY == BOTH on', sum(all(by['SELF_CERTIFY'][s].get(k,0)==by['BOTH'][s].get(k,0) for k in keys) for s in seeds),'| DROPOUT == BOTH on', sum(all(by['DROPOUT'][s].get(k,0)==by['BOTH'][s].get(k,0) for k in keys) for s in seeds), 'of', n)
print('GROUND correct > ORIGINAL on', sum(by['GROUND'][s].get('correct',0)>by['ORIGINAL'][s].get('correct',0) for s in seeds), 'tie', sum(by['GROUND'][s].get('correct',0)==by['ORIGINAL'][s].get('correct',0) for s in seeds), 'worse', sum(by['GROUND'][s].get('correct',0)<by['ORIGINAL'][s].get('correct',0) for s in seeds))
print('COMMAND vs BOTH: correct', sum(by['COMMAND'][s].get('correct',0) for s in seeds), 'vs', sum(by['BOTH'][s].get('correct',0) for s in seeds), 'wrong', sum(by['COMMAND'][s].get('wrong',0) for s in seeds), 'vs', sum(by['BOTH'][s].get('wrong',0) for s in seeds))
# 6. asking and repair
print('second story request made: BOTH', sum(len(by['BOTH'][s]['story_readings'])==2 for s in seeds), 'LISTEN', sum(len(by['LISTEN'][s]['story_readings'])==2 for s in seeds), 'RANDOM', sum(len(by['RANDOM'][s]['story_readings'])==2 for s in seeds), 'SHUFFLED', sum(len(by['SHUFFLED'][s]['story_readings'])==2 for s in seeds))
print('second reading changed: BOTH', sum(len(by['BOTH'][s]['story_readings'])==2 and by['BOTH'][s]['story_readings'][0]['interpretation']!=by['BOTH'][s]['story_readings'][1]['interpretation'] for s in seeds), 'SHUFFLED', sum(len(by['SHUFFLED'][s]['story_readings'])==2 and by['SHUFFLED'][s]['story_readings'][0]['interpretation']!=by['SHUFFLED'][s]['story_readings'][1]['interpretation'] for s in seeds),'RANDOM', sum(len(by['RANDOM'][s]['story_readings'])==2 and by['RANDOM'][s]['story_readings'][0]['interpretation']!=by['RANDOM'][s]['story_readings'][1]['interpretation'] for s in seeds))
print('restored standing by arm (members):', {a: sum(by[a][s].get('restored_standing',0) for s in seeds) for a in ('BOTH','LISTEN','ALT_SEED_LISTEN','RANDOM','SHUFFLED','BOTH_APPROACH','ORIGINAL')}, 'release ticks BOTH', Counter(by['BOTH'][s].get('release_tick') for s in seeds), 'LISTEN', Counter(by['LISTEN'][s].get('release_tick') for s in seeds))
print('late proposals left pending at exit:', sum(1 for r in S if r['phase_end_commitment']['active']), 'of', len(S))
print('world dwelling active ticks in BOTH:', sum(by['BOTH'][s].get('dwell_world_ticks',0) for s in seeds), '| facet', sum(by['BOTH'][s].get('dwell_facets_ticks',0) for s in seeds))
