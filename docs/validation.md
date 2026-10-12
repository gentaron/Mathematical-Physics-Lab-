# Validation and delivery notes

Verified on 2026-10-12 with Python 3.12.14 and SymPy 1.14.0.

- Full test suite: **56 passed**, including CLI end-to-end runs, all 3–7 vertex
  reference vectors, amplitude factorization, crossing double residue, exact
  hypothesis counterexamples, bootstrap constraints, ledger preservation and
  local HTTP adapter behavior.
- Complete CLI experiment: 7-vertex maximum passed. The checked-in reference run
  uses the final implementation and a 6-vertex maximum.
- Wheel build and installed-package `python -m research doctor` passed.
- Both workflow files parse as YAML and use pinned actions, public-only standard
  runners, bounded timeouts and read-only repository permission.
- A separate read-only reviewer recomputed the reference vectors and checked
  Eulerian interval relations in all exported lattices through six vertices.

## Review fixes

Each issue was reproduced by a failing regression test before correction:

1. Validate polygon size before allocating a count vector.
2. Require a regular candidate file and enforce the bound on bytes actually read,
   using nonblocking open to reject FIFOs without waiting.
3. Translate malformed HTTP status responses into an optional-AI error.
4. Reject incompatible three-vertex/AI runs before creating partial output.

The latter two reliability issues were fixed because the documented contract is
that optional service failures do not terminate the core experiment and invalid
requests do not begin expensive work. The full suite passed after all fixes.

## Implementation decisions

- The user supplied the project goal, architecture and commit destination; work
  proceeded within that authorization without another design-approval exchange.
- The destination was empty, so Python modules implement the proposed research
  roles directly instead of adding TypeScript scaffolding with no application.
  JSON and Markdown are the integration boundary to Genesis Vault.
- The free core does not depend on Mathematica, Aristotle, Clef or a hosted LLM.
  CosmoFlow, SageMath and polymake have source-backed extension guidance only.
- An isolated local git repository was used because the supplied remote was
  empty. GitHub delivery initializes main and adds an atomic verified snapshot,
  without a force update or modifying another repository.

## Explicitly unverified or outside scope

- Lean is not installed in this execution environment. Its pinned project and
  manual workflow are delivered, but no Lean kernel success is claimed here.
- No actual neural model was installed or run; the optional Ollama adapter was
  tested against a local HTTP service, including failure cases.
- The pinned Lean action's internal implementation and optional external-tool
  models were not independently audited. The workflow configuration was checked
  against the action's advertised inputs.
- JSON ledger hashes are reproducibility aids, not authentication. Trusted Python
  callers can construct their own descriptive records; the untrusted candidate
  interface cannot request formal proof status or execute code.
- No novel theorem, coordinate realization, full amplituhedron calculation,
  de Sitter correlator or Kinematic-Flow reproduction is claimed.
- GitHub-hosted execution is separate evidence from local tests. The final
  delivery message reports the observed remote status, if available.
