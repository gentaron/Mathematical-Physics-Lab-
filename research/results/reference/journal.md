# Mathematical Physics Lab — research journal

Reproduction and exact finite experiments; no claim of new mathematics.

Run: `run-20261012T110033Z-c96d0dddb176`
Implementation SHA-256: `067155475fc00097cc4888c6b95e15cc2107bf63cbb4e807bf36d46191c3d12b`

## Cosmohedron reproduction

| Polygon vertices | Polytope dimension | Faces by codimension (whole → vertices) | Reference match |
| --- | --- | --- | --- |
| 3 | 0 | [1] | True |
| 4 | 1 | [1, 2] | True |
| 5 | 2 | [1, 10, 10] | True |
| 6 | 3 | [1, 44, 114, 72] | True |

[Reference: arXiv:2603.03425v3, Table 1](https://arxiv.org/html/2603.03425v3#S5)

Counts exclude the empty face. Exported face lattices include it explicitly.
The outer polygon is a bookkeeping root. Inclusion of polygon sets reverses face containment.

## Exact scalar amplitude checks

- 3-point: 1 triangulations; all 0 channel factorizations passed: True
- 4-point: 2 triangulations; all 2 channel factorizations passed: True
- 5-point: 5 triangulations; all 5 channel factorizations passed: True
- 6-point: 14 triangulations; all 9 channel factorizations passed: True

These rational scalar amplitudes are not amplituhedron canonical forms.

## Hypotheses and counterexamples

Fitting inputs and held-out inputs are disjoint. Polynomial fits are a deliberate
baseline to expose invalid extrapolation. Passing finitely many cases is a conjecture.

- `poly-vertices`: **counterexample**
  N=6: predicted 25, actual 72 (held_out).
- `poly-facets`: **counterexample**
  N=6: predicted 24, actual 44 (held_out).

## Bootstrap seed

Two-site reconstruction is unique within the supplied denominator and linear-numerator ansatz.
Scaling, exchange symmetry and the normalized total-energy pole are checked exactly.
The 2–4-site expressions are flat-space scalar tree wavefunction coefficients.
They are not inflationary correlators and are not a Kinematic-Flow reproduction.

## Evidence and proof boundary

- `run.json`: machine-readable results and provenance.
- `faces-N.json`: full Hasse diagram through six polygon vertices.
- `ledger/*.json`: individual records with payload and implementation hashes.
- Lean kernel proofs were not checked by this Python experiment.
- No novelty assessment or automated publication to Genesis Vault was performed.
