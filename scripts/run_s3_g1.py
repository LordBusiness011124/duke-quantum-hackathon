import bluequbit,csv,json,math,time
from pathlib import Path
b=bluequbit.init(execution_mode='cloud')
out=Path('submissions');out.mkdir(exist_ok=True)
cache=out/'S3_G1_progress.json'
records=json.loads(cache.read_text()) if cache.exists() else {}
for circuit in ['S3','G1']:
 rows=[]
 for q in range(30):
  cid=f'Duke_{circuit}_{q}'
  if cid not in records:
   info=b.get_circuit_info(cid);assert info.num_qubits==30
   est=b.estimate(cid,device='cpu')
   assert est.error_message is None and est.estimated_cost==0.0, f'STOP: nonzero or unknown cost: {cid}: {est}'
   print('START',cid,str(est),flush=True)
   z='I'*(29-q)+'Z'+'I'*q
   job=b.run(cid,device='cpu',pauli_sum=[(z,1.0)],job_name=f'exact_{cid}',timeout=900)
   val=float(job.expectation_value)
   assert math.isfinite(val) and abs(val)<=1+1e-9
   records[cid]={'value':val,'job_id':str(job.job_id),'estimated_cost':est.estimated_cost,'method':'exact CPU; Z on matching qubit'}
   tmp=cache.with_suffix('.tmp');tmp.write_text(json.dumps(records,indent=2));tmp.replace(cache)
   print('DONE',cid,val,'job',job.job_id,flush=True)
  rows.append((cid,records[cid]['value']))
 with (out/(circuit+'.partial.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['circuit_id','value']);w.writerows(rows)
 assert len(rows)==30 and len(set(x[0] for x in rows))==30
 (out/(circuit+'.partial.csv')).replace(out/(circuit+'.csv'))
 print('COMPLETE',circuit,'30 validated finite values',flush=True)
print('COMPLETE ALL',flush=True)
