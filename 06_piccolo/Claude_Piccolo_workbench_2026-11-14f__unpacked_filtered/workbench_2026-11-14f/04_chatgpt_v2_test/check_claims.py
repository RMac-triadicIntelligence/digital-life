import json, sys, statistics
from collections import Counter, defaultdict
folder, diag = sys.argv[1], sys.argv[2]
seeds = json.load(open(f'{folder}/protocol.json'))['seeds']
def seq(beta, topic):
    out = []
    for row in beta['ticks']:
        for e in row['events']:
            if e['process'] == 'decision' and e['topic'] == topic:
                out.append((row['tick'], e['selected']))
    return out
tot = Counter(); distinct = defaultdict(lambda: defaultdict(set)); chan=[]; wpeak=0; dev=0; finals=defaultdict(set)
pred_ok = pred_bad = 0
for s in seeds:
    P = json.load(open(f'{folder}/seed_{s}.json'))
    T = {t['arm']['name']: t['beta'] for t in P['trials']}
    chan.append(tuple(P['handoff']['legacy']['channel']) + tuple(P['handoff']['legacy']['silt']))
    def diff(a, b, topic='thought.seek', lo=0, hi=99):
        A, B = dict(seq(T[a], topic)), dict(seq(T[b], topic))
        return sum(1 for k in set(A)|set(B) if lo <= k <= hi and A.get(k) != B.get(k))
    tot['alt_vs_base_seek'] += diff('ALT_SEED', 'BOTH')
    tot['listen_vs_base_seek'] += diff('LISTEN', 'BOTH')
    tot['reverse_vs_base_seek'] += diff('REVERSE', 'BOTH')
    tot['shuffled_vs_base_seek'] += diff('SHUFFLED', 'BOTH')
    tot['story_vs_original_seek'] += diff('STORY', 'ORIGINAL')
    tot['both_vs_ground_seek'] += diff('BOTH', 'GROUND')
    tot['both_vs_ground_assess'] += diff('BOTH', 'GROUND', 'thought.assess')
    tot['redacted_vs_both_seek'] += diff('STORY_REDACTED', 'BOTH')
    tot['seek_points'] += len(seq(T['BOTH'], 'thought.seek'))
    for name, beta in T.items():
        finals[(name)].add((beta['final_character']['curiosity'], beta['final_character']['formality']))
        for row in beta['ticks']:
            w = row['dwelling']['world']['after']
            if w and name == 'BOTH': wpeak = max(wpeak, w['field'])
            if 'development_while_dwelling' in row and row['development_while_dwelling']['writes']:
                # count internal body change while dwelling
                if any(x.startswith('body.') for x in row['development_while_dwelling']['writes']): dev += 1
        # predictability of story interpretation from signed shape
        for row in beta['ticks']:
            for e in row['events']:
                if e['process']=='decision' and e['topic']=='history.interpret_story':
                    c, f = e['signed_character']['curiosity'], e['signed_character']['formality']
                    cues = e['basis']['text_cues']
                    full = cues['shared_origin'] and cues['another_watchman']
                    pred = 'check_source_independence' if full and (0.24+0.68*c > 0.64+0.05*f) else 'notice_watchman'
                    if pred == e['selected']: pred_ok += 1
                    else: pred_bad += 1
        for topic in ('history.story_request','history.interpret_story','relationship.repair','thought.propose_shape','history.surface_question','thought.seek','thought.assess'):
            distinct[name][topic].add(tuple(seq(beta, topic)))
print({k: v for k, v in tot.items()})
print('distinct handoff vectors', len(set(chan)), 'of', len(chan), chan)
print('world field peak in BOTH', wpeak, '| ticks with a body write while any dwelling active', dev)
print('story interpretation predicted from (curiosity, formality, cue presence):', pred_ok, 'right,', pred_bad, 'wrong')
print('distinct choice sequences among the 8 members of BOTH, by topic:', {t: len(v) for t, v in distinct['BOTH'].items()})
print('same for ORIGINAL:', {t: len(v) for t, v in distinct['ORIGINAL'].items()})
print('arms whose 8 members all end with one identical character:', sum(1 for a in finals if len(finals[a])==1), 'of', len(finals))
print('arms with more than one final character:', {a: len(v) for a, v in finals.items() if len(v) > 1})
vf = defaultdict(set)
for s in seeds:
    P = json.load(open(f'{folder}/seed_{s}.json'))
    for t in P['trials']:
        a = t['arm']
        if a['history']=='VERIFY' and a['profile']==[0,0] and a['dwelling']=='ACTIVE' and a['character']=='ACTIVE' and a['choice']=='ACTIVE':
            vf[(t['beta']['final_character']['curiosity'], t['beta']['final_character']['formality'])].add(a['name'])
print('final characters over every active base-seed VERIFY reader (any ground, story, grace, pump, hand, repair arm):', {k: len(v) for k, v in vf.items()})
# marginal probe
m = Counter(); late = 0; early = 0; tapes = 0
for s in seeds:
    D = json.load(open(f'{diag}/probe_{s}.json')); T = {t['arm']: t['beta'] for t in D['trials']}
    for a in ('MARGINAL_FULL','MARGINAL_REDACTED','MARGINAL_NO_STORY'):
        for k in ('observed_second_watch','correct','wrong','unknown','deferred'): m[(a,k)] += T[a]['metrics'].get(k,0)
    A, B = dict(seq(T['MARGINAL_FULL'],'thought.seek')), dict(seq(T['MARGINAL_REDACTED'],'thought.seek'))
    d = [k for k in A if A[k] != B.get(k)]
    tapes += bool(d); early += sum(1 for k in d if k < 17); late += sum(1 for k in d if k >= 17)
    m[('NO_PROVISION_BODY','crossings')] += T['NO_PROVISION_BODY']['metrics'].get('crossings',0)
print('marginal probe', dict(m)); print('tapes with a seek difference', tapes, 'early diffs', early, 'late diffs (tick>=17)', late)
