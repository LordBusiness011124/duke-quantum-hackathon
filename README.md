# Duke Quantum Hackathon: OTOC estimation

DRAFT repository package, prepared 2026-10-25. G4 research remains active; results here are a snapshot. Do not claim that all values are exact.

## Task
For each circuit ID Duke_<problem>_<q>, start in the all-zero state and calculate the Z expectation on qubit q: P(q=0) - P(q=1). Each ID names a distinct circuit.

## Methods and reasoning
- S1/S2: retain the complete statevector locally. Four and sixteen qubits are manageable. Compute expectations from squared amplitude magnitudes; cross-check Qiskit Statevector against Aer and check normalization.
- S3/G1: use exact cloud CPU statevector simulation for 30-qubit circuits, requesting expectations directly rather than downloading the statevector. Exact means no intentional truncation, not infinite arithmetic precision.
- G2: best saved submission is a structural heuristic, a sigmoid profile based on distance from the butterfly qubit, front position 16 and width 2. It is not an exact circuit simulation. Approximate simulator pilots were also attempted. The generator for this particular CSV has not yet been located in the curated scripts.
- G3: saved best submission has 795/800 points. Its precise producing configuration is not yet verified; do not attribute it to a specific method without provenance. Approximate Pauli simulation was explored in the project.
- G4: early structural guesses and low-bond MPS did poorly. GPU Pauli-path simulation with transpilation level 3 and decreasing coefficient cutoffs improved results. Cutoffs are increased when backend memory validation rejects them. Alternative transpilation levels test approximation dependence. No convergence claim is made.

## Validation and limitations
S3 exact results were used to check selected approximate runs; S3 is mostly Clifford plus Rz and does not guarantee transfer of accuracy to G4's Haar-random circuits. Correlation scores measure pattern agreement, not absolute numerical accuracy. Best verified G4 snapshot: 197/1000. Score-derived reconstruction of hidden answers is not used.

## Files
results/ contains answer CSV snapshots. scripts/ contains selected original workspace scripts as an implementation record, not yet a standalone runnable distribution: some depend on workspace circuit downloads, prior result caches and configuration files. Reproduction instructions and missing provenance must be completed before calling this repository fully reproducible.

See [RESOURCES.md](RESOURCES.md) for the challenge materials, papers that
informed our simulator choices, prior classical-simulation work, and a short
beginner learning path.

The `site/` directory contains a responsive long-form walkthrough and a small
Nginx container for deployment to Vultr. See `site/DEPLOYMENT.md` for the
recommended server, DNS, HTTPS, and update workflow.

## Credentials and publishing
BlueQubit access uses the BLUEQUBIT_API_TOKEN environment variable. Never commit tokens, environment files, account exports or raw terminal logs. This curated package excludes those records. No hidden graded QASM is included. Keep unpublished competition answers private unless organizer rules permit their release.
