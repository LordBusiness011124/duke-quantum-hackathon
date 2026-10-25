import bluequbit,json,csv,math,time,concurrent.futures
from pathlib import Path
out=Path('submissions/graded');out.mkdir(exist_ok=True)
def run_one(c,q,device,options,label):
 p=out/f'{c}_{q}_{label}.json'
 if p.exists():return json.loads(p.read_text())
 b=bluequbit.init(execution_mode='cloud');cid=f'Duke_{c}_{q}';n=b.get_circuit_info(cid).num_qubits
 if device=='cpu':
  e=b.estimate(cid,device=device);assert e.error_message is None and e.estimated_cost==0
 assert device in ['cpu','mps.cpu','pauli-path']
 z='I'*(n-1-q)+'Z'+'I'*q
 j=b.run(cid,device=device,pauli_sum=[(z,1.0)],options=options,asynchronous=True,job_name=f'{c}_{q}_{label}')
 pending=out/f'{c}_{q}_{label}_job.json';pending.write_text(json.dumps({'job_id':str(j.job_id),'circuit_id':cid}))
 print('START',cid,label,j.job_id,flush=True)
 r=b.wait(j.job_id);v=float(r.expectation_value)
 assert math.isfinite(v) and abs(v)<=1+1e-7
 row=dict(circuit_id=cid,value=v,job_id=str(j.job_id),device=device,options=options)
 p.write_text(json.dumps(row,indent=2));print('DONE',cid,label,v,flush=True);return row
def exact_g1():
 # Pilot owns 0,1,2. Do not duplicate its jobs.
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  fs=[pool.submit(run_one,'G1',q,'cpu',{},'exact') for q in range(3,30)]
  for f in concurrent.futures.as_completed(fs):
   try:f.result()
   except Exception as e:print('ERROR G1',repr(e),flush=True)
 pilot=Path('submissions/G1_pilot_results.json')
 for _ in range(120):
  if pilot.exists() and len(json.loads(pilot.read_text()))==3:break
  time.sleep(5)
 rows=json.loads(pilot.read_text()) if pilot.exists() else []
 rows += [json.loads(p.read_text()) for p in out.glob('G1_*_exact.json')]
 if len(rows)==30:write_csv('G1',rows,'exact')
def write_csv(c,rows,label):
 rows=sorted(rows,key=lambda r:int(r['circuit_id'].rsplit('_',1)[1]))
 assert len(set(r['circuit_id'] for r in rows))==len(rows)
 with (out/f'{c}_{label}.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['circuit_id','value']);w.writerows((r['circuit_id'],r['value']) for r in rows)
 print('CSV COMPLETE',c,label,len(rows),flush=True)
def approximate(c,n,device,coarse,fine):
 rows=[];checks=[]
 for q in range(n):
  try:
   a=run_one(c,q,device,coarse,'coarse');b=run_one(c,q,device,fine,'fine')
   delta=abs(a['value']-b['value']);checks.append({'q':q,'difference':delta});rows.append(b)
   (out/f'{c}_convergence.json').write_text(json.dumps(checks,indent=2))
  except Exception as e:print('ERROR',c,q,repr(e),flush=True)
 if len(rows)==n:write_csv(c,rows,'approx_unreviewed')
if __name__=='__main__':
 import sys
 if sys.argv[1]=='G1':exact_g1()
 elif sys.argv[1]=='G3':approximate('G3',36,'pauli-path',{'pauli_path_truncation_threshold':0.001},{'pauli_path_truncation_threshold':0.0001})
 else:
  c=sys.argv[1];approximate(c,36 if c=='G2' else 38,'mps.cpu',{'mps_bond_dimension':64},{'mps_bond_dimension':128})
