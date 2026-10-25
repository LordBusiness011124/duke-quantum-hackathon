# Resources

This page separates references that directly informed the project from optional
learning material. The papers and BlueQubit documentation influenced simulator
selection, interpretation, or method exploration. The videos are included as
beginner background and were not used to generate the submitted values.

## Challenge and platform

- [Duke Quantum Hackathon](https://app.bluequbit.io/hackathons/2GMaAenu3iSsIC6Z) — challenge statement, circuit descriptions, scoring, and submission format.
- [BlueQubit OTOC tutorial](https://app.bluequbit.io/tutorial/otoc-tutorial) — echo circuits, OTOC(1)/OTOC(2), scrambling, and comparisons among exact, MPS, and Pauli-path simulation.
- [BlueQubit simulator-selection tutorial](https://app.bluequbit.io/tutorials) — entry point for the OTOC tutorial and the guide to choosing statevector, MPS, or Pauli-path simulation.
- [BlueQubit documentation](https://app.bluequbit.io/docs) and [SDK API reference](https://app.bluequbit.io/sdk-docs/bluequbit.sdk.html) — device limits, expectation-value requests, MPS bond dimension, Pauli-path cutoff, and transpilation-level options.

## Papers that informed the work

- Google Quantum AI and Collaborators, [“Observation of constructive interference at the edge of quantum ergodicity”](https://www.nature.com/articles/s41586-025-09526-6), *Nature* 646, 825–830 (2025). This is the Quantum Echoes experiment behind the challenge. It explains repeated time reversal, OTOCs, scrambling, and constructive interference among Pauli paths.
- Mazumder et al., [“Benchmarking Zero-Setup Quantum Circuit Simulators”](https://arxiv.org/abs/2607.09882) (2026). We used its comparison of statevector, MPS, and Pauli-path methods to reason about backend choice, GPU scaling, bond dimensions, and truncation thresholds. It also warns that Pauli-path error can be non-monotonic as the cutoff changes.
- Bermejo et al., [“Tensor Networks with Belief Propagation Cannot Feasibly Simulate Google’s Quantum Echoes Experiment”](https://arxiv.org/abs/2604.15427) (2026). This helped explain why highly entangled two-dimensional echo circuits are difficult for compressed tensor-network methods.
- Kremer and Dupuis, [“Efficient Classical Simulation of Heuristic Peaked Quantum Circuits”](https://arxiv.org/abs/2604.21908) (2026), with [reference implementation](https://github.com/d-kremer/peaked-circuit-simulation). We examined its low-bond MPS distillation, tensor-network operator contraction, and MPO “unswapping” ideas as examples of creative classical attacks. Those methods target peaked circuits and require circuit structure, so they were inspiration rather than a direct G4 solver for hidden OTOC circuits.

## Beginner learning resources

- Qiskit, [“Qubits and Quantum States, Quantum Circuits, Measurements — Part 1”](https://www.youtube.com/watch?v=NZD9APb7ZtY). Covers qubits, amplitudes, gates, circuits, and measurement.
- Qiskit, [“Qubits and Quantum States, Quantum Circuits, Measurements — Part 2”](https://www.youtube.com/watch?v=SlZoTjkPy7o). Continues the circuit model and measurement foundations.
- [BlueQubit quantum tutorials](https://app.bluequbit.io/tutorials). The BQ 101 material is a practical introduction, while the OTOC and simulator-selection tutorials connect directly to this project.

## Suggested reading order

1. Watch the two Qiskit introductory lectures or read BlueQubit’s beginner material.
2. Work through the BlueQubit OTOC tutorial to connect gates and measurement to an echo experiment.
3. Read the Nature Quantum Echoes paper for the experiment that motivated the challenge.
4. Read the simulator benchmark for the tradeoffs among exact statevector, MPS, and Pauli-path simulation.
5. Use the tensor-network papers to understand both the limits of compression and examples of structure-aware classical methods.

## How these sources affected our decisions

- Small circuits: use exact statevector simulation because retaining every amplitude is feasible.
- Thirty-qubit circuits: use BlueQubit’s exact cloud statevector backend and request the expectation directly.
- Circuits beyond the exact backend’s qubit limit: test MPS and Pauli-path approximations.
- Highly entangled grid echoes: expect low-bond MPS to lose important correlations.
- Pauli-path runs: reduce the truncation cutoff when memory permits, validate on an exact sample, and avoid treating a smaller cutoff as automatic proof of convergence.

