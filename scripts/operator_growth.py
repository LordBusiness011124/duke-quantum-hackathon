import numpy as np,csv,json,itertools,time
from pathlib import Path
rng=np.random.default_rng(20261024);out=Path('submissions/graded');N=60000
def grow(n,butterfly,layers,schedule):
 a=np.zeros((N,n),dtype=np.bool_);a[:,butterfly]=1
 for t in range(layers):
  for i,j in schedule[t%len(schedule)]:
   active=a[:,i]|a[:,j];r=rng.integers(0,15,size=N)
   a[:,i]=active&(r>=3);a[:,j]=active&((r<3)|(r>=6))
 return 1-4*a.mean(axis=0)/3
report={}
for c,n,depth in [('S2',16,12),('G1',30,32)]:
 schedule=[[(i,i+1) for i in range(parity,n-1,2)] for parity in [0,1]]
 pred=grow(n,0,depth,schedule)
 p=Path('submissions/S2.csv') if c=='S2' else out/'G1_exact.csv'
 d={r['circuit_id']:float(r['value']) for r in csv.DictReader(p.open())};exact=np.array([d[f'Duke_{c}_{q}'] for q in range(n)])
 corr=float(np.corrcoef(pred,exact)[0,1]);report[c]={'correlation':corr,'corr_squared':max(corr,0)**2,'prediction':pred.tolist()}
 print('VALIDATION',c,report[c],flush=True)
# G4 graph: 6x6 plus sites 36,37 below 30,31. Assumed four matching order.
coords=[(q//6,q%6) for q in range(38)];index={xy:q for q,xy in enumerate(coords)};matches=[[],[],[],[]]
for q,(r,c) in enumerate(coords):
 if (r,c+1) in index:matches[c%2].append((q,index[r,c+1]))
 if (r+1,c) in index:matches[2+r%2].append((q,index[r+1,c]))
preds=[]
for order in itertools.permutations(range(4)):
 pred=grow(38,0,16,[matches[k] for k in order]);preds.append(pred);print('G4 schedule',order,'done',flush=True)
mean=np.mean(preds,axis=0);spread=np.std(preds,axis=0)
with (out/'G4_operator_growth.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['circuit_id','value']);w.writerows((f'Duke_G4_{q}',float(v)) for q,v in enumerate(mean))
report['G4']={'prediction':mean.tolist(),'schedule_std':spread.tolist(),'trajectories_per_schedule':N,'schedule_count':len(preds),'limitation':'Ensemble averaged model, not fixed circuit simulation. Four matching ordering assumed and averaged.'}
(out/'operator_growth_report.json').write_text(json.dumps(report,indent=2));print('COMPLETE G4 candidate saved',flush=True)
