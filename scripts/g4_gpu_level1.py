import bluequbit, json, time, math, csv, argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args()
import fcntl
lock=open(a.config+'.lock','w')
try: fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: raise SystemExit('This config is already running')
conf=json.loads(Path(a.config).read_text()); out=Path('submissions/g4_takeover');out.mkdir(exist_ok=True)
exact=dict(csv.reader(open('submissions/graded/S3.csv')))
def run(t):
 b=bluequbit.init(execution_mode='cloud'); c=t['circuit'];q=t['q'];n=30 if c=='S3' else 38
 key=f"{c}_q{q}_{t['device']}_L{t.get('level','na')}_T{t.get('threshold','na')}_B{t.get('bond','na')}"
 path=out/(key+'.json'); jp=out/(key+'_job.json')
 if path.exists():return json.loads(path.read_text())
 opts=({'mps_bond_dimension':t['bond']} if 'bond' in t else {'pauli_path_truncation_threshold':t['threshold'],'pauli_path_circuit_transpilation_level':t['level']})
 j=None; done=False;data=dict(t,key=key)
 try:
  if jp.exists():
   saved=json.loads(jp.read_text());j=b.get(saved['job_id']);data.update(saved)
  else:
   j=b.run(f'Duke_{c}_{q}',device=t['device'],pauli_sum=[('I'*(n-1-q)+'Z'+'I'*q,1.)],options=opts,asynchronous=True,job_name=key)
   data.update(job_id=str(j.job_id),estimated_cost=j.estimated_cost,submitted_at=time.time());jp.write_text(json.dumps(data,indent=2))
  print('JOB',key,j.job_id,'estimate',data.get('estimated_cost'),flush=True)
  if data.get('estimated_cost') is None:raise RuntimeError('Missing cost estimate')
  if 'gpu' in t['device'] and float(data['estimated_cost'])>conf.get('gpu_estimate_limit',1):raise RuntimeError('GPU estimate exceeds guard')
  start=time.monotonic()
  while time.monotonic()-start<conf.get('timeout',240):
   r=b.get(j.job_id);status=str(r.run_status).upper()
   if status not in ['PENDING','QUEUED','RUNNING','CREATED','VALIDATING']:
    data.update(status=status,cost=float(r.cost or 0),runtime_ms=r.run_time_ms)
    if status=='COMPLETED':
     v=float(r.expectation_value);assert math.isfinite(v) and abs(v)<=1.000001
     data['value']=v
     if c=='S3':data.update(exact=float(exact[f'Duke_{c}_{q}']),absolute_error=abs(v-float(exact[f'Duke_{c}_{q}'])))
    else:data['failure']=str(getattr(r,'error_message',None))
    done=True;path.write_text(json.dumps(data,indent=2));print('RESULT',json.dumps(data),flush=True);return data
   time.sleep(5)
  raise TimeoutError('Pilot timeout')
 except Exception as e:
  data['error']=str(e);path.write_text(json.dumps(data,indent=2));print('ERROR',key,str(e),flush=True)
 finally:
  if j is not None and not done:
   try:b.cancel(j.job_id);data['cancellation_requested']=True
   except Exception as e:data['cancel_error']=str(e)
   path.write_text(json.dumps(data,indent=2))
 return data
def run_locked(t):
 key=f"{t['circuit']}_q{t['q']}_{t['device']}_L{t.get('level','na')}_T{t.get('threshold','na')}_B{t.get('bond','na')}"
 with (out/(key+'.lock')).open('a') as point_lock:
  fcntl.flock(point_lock,fcntl.LOCK_EX)
  return run(t)

b=bluequbit.init(execution_mode='cloud')
active=[j for j in b.search(created_later_than='2026-10-25T00:00:00Z') if j.run_status in ['PENDING','QUEUED','RUNNING']]
if active:raise SystemExit('Wait for the active cloud queue to clear before GPU jobs')
def total_spent():
 return sum(json.loads(p.read_text()).get('cost',0) or 0 for p in out.glob('G4_*pauli-path.gpu_L1_*_Bna.json'))

def point_key(t):
 return f"{t['circuit']}_q{t['q']}_{t['device']}_L{t.get('level','na')}_T{t.get('threshold','na')}_B{t.get('bond','na')}"
def threshold_rejected(r):
 msg=str(r.get('error',''))+' '+str(r.get('failure',''))
 return (r.get('status')=='FAILED_VALIDATION' or 'FAILED_VALIDATION' in msg) and 'threshold' in msg.lower() and 'too small' in msg.lower()
choices=[]
for base in conf['tasks']:
 import datetime
 if datetime.datetime.now(datetime.timezone.utc) >= datetime.datetime(2026,10,25,15,10,tzinfo=datetime.timezone.utc): raise SystemExit('Stop for submission deadline')
 chosen=None
 for cutoff in [0.00002,0.00003,0.00005,0.0001]:
  t=dict(base,threshold=cutoff);key=point_key(t);path=out/(key+'.json')
  if path.exists():
   r=json.loads(path.read_text())
   if r.get('status')=='COMPLETED':
    chosen=(path,r);break
   if threshold_rejected(r):
    print('CACHED REJECTION; NEXT CUTOFF',key,flush=True);continue
   raise SystemExit('STOP review existing error: '+str(r))
  if total_spent()+0.25>conf.get('actual_budget',8):
   raise SystemExit('STOP actual G4 GPU budget guard: '+str(total_spent()))
  import subprocess,re
  balance_text=subprocess.check_output(['bq','balance'],text=True)
  balance=float(re.search(r'balance: \$(\d+(?:\.\d+)?)',balance_text).group(1))
  if balance < 6.5: raise SystemExit('STOP preserve $5 reserve plus job/session margin')
  r=run_locked(t)
  if r.get('status')=='COMPLETED':
   if r.get('cost',0)>0.25:raise SystemExit('STOP review increased charge: '+str(r))
   chosen=(path,r);break
  if threshold_rejected(r):
   print('VALIDATION FALLBACK',key,flush=True);continue
  raise SystemExit('STOP review new failure: '+str(r))
 if chosen is None:
  raise SystemExit('No accepted level-1 cutoff; review before proceeding')
  path=out/f"G4_q{base['q']}_pauli-path_L3_T0.0001_Bna.json"
  r=json.loads(path.read_text());assert r['status']=='COMPLETED'
  chosen=(path,r)
 path,r=chosen
 choices.append({'q':base['q'],'source':str(path),'threshold':r['threshold'],'device':r['device'],'job_id':r['job_id'],'value':r['value']})
 (out/'gpu_level1_choices.json').write_text(json.dumps(choices,indent=2))
 print('SELECTED',base['q'],r['threshold'],r['device'],r['value'],'completed',len(choices),flush=True)
print('TOTAL_ACTUAL_G4_GPU_L3_COST',total_spent(),flush=True)
