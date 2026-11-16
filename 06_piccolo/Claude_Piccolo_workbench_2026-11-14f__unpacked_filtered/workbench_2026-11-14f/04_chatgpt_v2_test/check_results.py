import json, sys, statistics
from collections import Counter, defaultdict
folder = sys.argv[1]
S = json.load(open(f'{folder}/summary.json'))
by = defaultdict(dict)
for r in S: by[r['arm']][r['seed']] = r
seeds = sorted(by['BOTH'])
def tot(arm, key): return sum(by[arm][s].get(key, 0) for s in seeds)
print('arms', len(by), 'seeds', seeds)
print('--- ground/story')
for arm in ('ORIGINAL','GROUND','STORY','BOTH'):
    print(arm, {k: tot(arm,k) for k in ('independent_available','observed_second_watch','observed_gate_watch','correct','wrong','unknown','deferred','story_reads','story_requests')})
print('per-seed correct ORIGINAL vs GROUND:', [(by['ORIGINAL'][s].get('correct',0), by['GROUND'][s].get('correct',0)) for s in seeds])
print('per-seed indep avail O vs G:', [(by['ORIGINAL'][s]['independent_available'], by['GROUND'][s]['independent_available']) for s in seeds])
print('--- character')
def ch(r, w): c = r[w]; return (c['curiosity'], c['formality'], c['verbosity'])
for arm in ('BOTH','LISTEN','ALT_SEED','ALT_SEED_LISTEN','CHARACTER_FROZEN','REVERSE','SHUFFLED','RANDOM','LATENCY','LATENCY_RANDOM','COMMAND','NO_PROVISION','DROPOUT','SELF_CERTIFY','STORY_REDACTED'):
    print(arm, 'init', Counter(ch(by[arm][s],'initial_character') for s in seeds).most_common(), 'final', Counter(ch(by[arm][s],'final_character') for s in seeds).most_common())
def l1(a,b): return round(sum(abs(x-y) for x,y in zip(a,b)),6)
for arm in ('BOTH','REVERSE','SHUFFLED','RANDOM','LATENCY','LATENCY_RANDOM'):
    d=[l1(ch(by[arm][s],'final_character'), ch(by[arm][s],'initial_character')) for s in seeds]
    print(arm,'drift from seed',d,'median',statistics.median(d))
print('SHUFFLED vs BOTH final L1', [l1(ch(by['SHUFFLED'][s],'final_character'), ch(by['BOTH'][s],'final_character')) for s in seeds])
print('REVERSE vs BOTH final L1', [l1(ch(by['REVERSE'][s],'final_character'), ch(by['BOTH'][s],'final_character')) for s in seeds])
print('RANDOM final == BOTH final on', sum(ch(by['RANDOM'][s],'final_character')==ch(by['BOTH'][s],'final_character') for s in seeds))
print('--- story readings')
for arm in ('BOTH','STORY','LISTEN','ALT_SEED','ALT_SEED_LISTEN','CHARACTER_FROZEN','STORY_REDACTED','REVERSE','SHUFFLED','RANDOM','LATENCY','COMMAND'):
    print(arm, Counter(tuple((x['tick'],x['interpretation'],x['character']['curiosity'],x['character']['formality']) for x in by[arm][s]['story_readings']) for s in seeds).most_common())
print('--- dwelling/latency')
for arm in ('BOTH','LATENCY','RANDOM','LATENCY_RANDOM'):
    print(arm, {k: tot(arm,k) for k in ('dwell_facets_ticks','dwell_world_ticks','dwell_uncertainty_basin_ticks','dwell_commitment_point_ticks','signed_changes','observed_second_watch','questions','questions_unmodeled','proposals','correct','wrong','unknown')})
print('world dwell ticks by arm', {a: tot(a,'dwell_world_ticks') for a in by if tot(a,'dwell_world_ticks')})
print('--- grace')
for arm in ('BOTH','COMMAND','NO_PROVISION','BOTH_CLENCH','BOTH_APPROACH','DROPOUT','SELF_CERTIFY','BOTH_BODY','BOTH_FROZEN'):
    print(arm, {k: tot(arm,k) for k in ('observed_second_watch','correct','wrong','unknown','deferred','carried_when_short_ticks','provision_forwarded','restored_standing','pump_strokes','pump_delivered','pump_false_success_ticks','crossings','unready_receipts')}, 'release', Counter(by[arm][s].get('release_tick') for s in seeds))
print('late pending', sum(1 for r in S if r['phase_end_commitment']['active']), 'of', len(S))
print('review statuses', {k: sum(r.get(k,0) for r in S) for k in ('review_granted','review_owner_silent','review_character_frozen','review_outside_review_scope')})
