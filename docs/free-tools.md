# Free tool policy

The required stack is Python, SymPy and (for tests) pytest. There are no paid
providers or automatic paid fallbacks. A free tier with uncertain limits is not
a required dependency. No billing account or credit card is needed by this code.

| Tool | Role here | Required? | Licence / operating condition |
| --- | --- | --- | --- |
| Python | Orchestration and exact combinatorics | Yes | PSF |
| SymPy | Symbolic factorization, residues, bounded ansatz reconstruction | Yes | BSD |
| pytest | Reproduction and regression tests | Development | MIT |
| Ollama | Local structured candidate generation | Optional | MIT software; choose a locally downloaded model with acceptable separate licence |
| Lean 4 / mathlib | Separate formal algebraic identity project | Optional | Apache-2.0; no theorem-proving API service |
| SageMath | Future larger exact algebra experiments | Optional, not integrated | GPL; see https://www.sagemath.org/ |
| polymake | Future coordinate realizations and polyhedral checks | Optional, not integrated | GPL; see https://polymake.org/ |
| CosmoFlow | Future model-specific inflationary correlator reproduction | Optional, not integrated | MIT; official repository linked below |

## CosmoFlow

Use the authors' [deniswerth/CosmoFlow](https://github.com/deniswerth/CosmoFlow).
Its README identifies NumPy, SciPy, tqdm and matplotlib, tutorial notebooks, and
model-specific Parameters/Theory/Solver modules. It is not treated here as a
generic `pip install cosmoflow` package: similarly named packages can be unrelated.
Begin with an upstream notebook in a separate environment, record its commit,
the model tensors and numerical tolerances, then reproduce a published figure.
No CosmoFlow run is claimed by this repository's reference ledger.

## Excluded from the required/free stack

- Kinematic-Flow and amplituhedronBoundaries: their Mathematica dependencies are
  not used. This project does not claim that Python reproduces those full tools.
- Aristotle: no assumption of permanent free access; no account or API integration.
- Open d1 / Clef: the decision router is transparent deterministic validation here.
- Hosted proprietary LLMs: no keys, calls or fallback chains.

## GitHub Actions

The repository is public. Workflows explicitly skip private repositories and
use standard Ubuntu runners. There are no uploaded artifacts, Actions caches,
scheduled loops or larger runners. Job summaries and logs are the CI outputs;
full durable research records are generated locally and may be committed by the
user. Official policy: https://docs.github.com/en/billing/concepts/product-billing/github-actions

Local optional AI needs an Ollama server with `OLLAMA_NO_CLOUD=1` and an existing
local model. The adapter does not pull models and refuses cloud metadata, names,
non-loopback URLs, redirects and proxies. Server configuration and model licences
remain under the operator's control. Local hardware, electricity and network
costs are outside the software/service-fee claim.
