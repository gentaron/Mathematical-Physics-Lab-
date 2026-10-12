# Mathematical Physics Lab design

Implement the user's supplied Genesis Vault research design as an independent,
public repository. The intended outcome is reproducible mathematical exploration,
not automatic claims of discovery. All required software is free and open source;
no API key, paid service, GPU, Mathematica, Aristotle or Clef is required.

## Architecture and conventions

Python 3.12+, SymPy 1.14.0, standard library; pytest for validation. There is no
existing TypeScript application to extend, so director, decision, hypothesis and
evaluator are Python modules with a JSON interface for future Genesis Vault use.

The core enumerates non-crossing dissections and recursively nested polygon
partitions. Each internal Matryoshka includes the outer polygon as a bookkeeping
root; the singleton root represents the whole polytope. Codimension counts
non-minimal polygons. Reverse set inclusion gives face containment, with an
explicit empty face. Enumerate only 3–7 polygon vertices; emit the full Hasse
diagram only through 6 vertices to bound memory and runtime.

Validate enumerated codimension vectors against arXiv:2603.03425v3 Table 1:
3: [1], 4: [1,2], 5: [1,10,10], 6: [1,44,114,72],
7: [1,196,952,1400,644]. Also compute face counts by the independent
subdivision/product recurrence (Equation 11), without enumerating Matryoshkas.

Construct planar cubic tree amplitudes from triangulations. Verify every simple
channel residue against independently constructed subpolygon amplitudes; check
crossing-channel double residues vanish. These are scalar amplitudes, not an
amplituhedron realization or a canonical differential form.

## Research loop

Director proposes small rational polynomial models of observed count sequences.
Decision enforces bounded schema and separates fitting from held-out inputs.
Evaluator uses exact arithmetic to find counterexamples; passing finite tests
remains an unproved conjecture. SymPy rational identities have their own exact
verification record. The append-only ledger uses unique files, provenance,
content hashes, environment, source references, timestamps and explicit statuses:
reproduced, counterexample, conjecture, symbolic_verified, formally_proved.
Formal status requires an external Lean kernel check; current Python execution
never awards it. No candidate text is evaluated as Python or unrestricted SymPy.

Optional AI uses a user-selected existing Ollama model on localhost over its JSON
API. No automatic model downloads or paid fallback. Failure leaves a recorded
error and the deterministic proposal mode remains available. AI output is data
in the same restricted polynomial schema, never executable code.

## Physics and proof boundaries

Implement a finite flat-space scalar tree wavefunction recursion and two-site
residue / symmetry / homogeneity tests as the first bootstrap seed. Explicitly
label this as not a de Sitter correlator or a port of Kinematic-Flow. Provide
source-backed setup guidance for optional CosmoFlow, SageMath, polymake and Lean;
do not pretend those integrations were executed. Include an optional pinned
Lean/mathlib project proving one rational algebraic identity; kernel verification
is a separate manual workflow, not evidence manufactured by Python.

## Execution and acceptance

CLI exports JSON plus a Markdown journal; run directories never overwrite an
existing ledger entry. Commit a reproducible reference run for polygon sizes
3–6. Run all tests and the complete CLI before pushing to the named repository.
Public standard Ubuntu Actions runners only, no secrets, no cache, no uploaded
artifacts, no schedule. Read-only token, checkout without credential persistence,
bounded choices and timeout. Print the journal to the Actions job summary; users
can reproduce durable JSON locally. Existing Genesis Vault is untouched.
