import csv,json,hashlib,time
from pathlib import Path
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
start=time.time()
out=Path('submissions');out.mkdir(exist_ok=True)
report=[]
for sample,n in [('S1',4),('S2',16)]:
 rows=[]
 for q in range(n):
  cid=f'Duke_{sample}_{q}'
  paths=list(Path('circuits').rglob(cid+'.qasm'))
  assert len(paths)==1,(cid,paths)
  p=paths[0];qc=QuantumCircuit.from_qasm_file(str(p))
  assert qc.num_qubits==n and not qc.num_clbits
  state=Statevector.from_instruction(qc)
  probs=np.abs(state.data)**2
  signs=1-2*((np.arange(2**n)>>q)&1)
  value=float(probs@signs)
  check=qc.copy();check.save_statevector()
  sim=AerSimulator(method='statevector',device='CPU',precision='double',max_parallel_threads=2)
  result=sim.run(check).result();assert result.success
  other=np.asarray(result.get_statevector())
  value2=float((np.abs(other)**2)@signs)
  norm=float(probs.sum());err=abs(value-value2)
  assert abs(norm-1)<1e-10 and err<1e-10 and np.isfinite(value) and abs(value)<=1+1e-10
  rows.append((cid,value))
  report.append(dict(circuit_id=cid,value=value,aer_value=value2,error=err,norm=norm,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  print(cid,format(value,'.16g'),'error',err,flush=True)
 assert len(rows)==n and len(set(r[0] for r in rows))==n
 with (out/(sample+'.csv')).open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['circuit_id','value']);writer.writerows(rows)
 with (out/(sample+'.csv')).open() as f:
  loaded=list(csv.DictReader(f));assert [r['circuit_id'] for r in loaded]==[f'Duke_{sample}_{q}' for q in range(n)]
 (out/(sample+'_method.txt')).write_text('Exact double precision CPU statevector simulation of each supplied QASM from the all zero state. Computed P(q=0)-P(q=1) for the matching qubit q. Independently checked Qiskit Statevector against Aer CPU statevector, with normalization and CSV completeness checks. No sampling or paid simulator jobs.\n')
(out/'validation.json').write_text(json.dumps(report,indent=2))
print('PASS: all 20 circuits validated. Seconds:',time.time()-start,flush=True)
