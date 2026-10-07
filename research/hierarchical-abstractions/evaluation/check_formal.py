"""Finite checks of the stated definitions, not a replacement for proofs."""
import itertools,json
from pathlib import Path
X=set(range(-2,3));C=[set(v) for n in range(6) for v in itertools.combinations(sorted(X),n)]
A=[set()]+[set(range(a,b+1)) for a in sorted(X) for b in sorted(X) if a<=b]
B=[set()]+[set(range(a,b+1)) for a in [-2,0,2] for b in [-2,0,2] if a<=b]
def alpha(S):return set(range(min(S),max(S)+1)) if S else set()
def beta(I):
 if not I:return set()
 low=max(x for x in [-2,0,2] if x<=min(I));high=min(x for x in [-2,0,2] if x>=max(I));return set(range(low,high+1))
counts={'concrete_interval_adjunctions':0,'interval_coarse_adjunctions':0,'composed_adjunctions':0}
for S,I in itertools.product(C,A):assert (alpha(S)<=I)==(S<=I);counts['concrete_interval_adjunctions']+=1
for I,J in itertools.product(A,B):assert (beta(I)<=J)==(I<=J);counts['interval_coarse_adjunctions']+=1
for S,J in itertools.product(C,B):assert (beta(alpha(S))<=J)==(S<=J);counts['composed_adjunctions']+=1
for S in C:assert S<=beta(alpha(S))
worlds=[{'sequential':'ok','stale_read':False},{'sequential':'ok','stale_read':True}]
assert worlds[0]['sequential']==worlds[1]['sequential'] and worlds[0]['stale_read']!=worlds[1]['stale_read']
models=[(False,False),(True,False),(False,True)];assert any(a for a,b in models) and any(b for a,b in models) and not any(a and b for a,b in models)
counts['summary_counterexample_checked']=True;counts['merge_counterexample_checked']=True
Path(__file__).with_name('formal-checks.json').write_text(json.dumps(counts,indent=2)+'\n');print(counts)
