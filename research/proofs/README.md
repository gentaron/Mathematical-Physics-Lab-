# Optional Lean kernel verification

This standalone project targets Lean 4.19.0 and the corresponding pinned mathlib
commit. It proves two rational algebraic identities: grouping the pole-carrying
terms of the five-point expression, and writing the pole coefficient over a
common denominator. It does not formalize a limit, the enumeration algorithm,
the cosmohedron theorem or a discovery. No AI proof service is required.

With a working free Lean/elan installation:

```bash
cd research/proofs
lake update
lake exe cache get
lake build
lake env lean MathPhysicsLab.lean
```

Alternatively use **Actions → Lean Algebra Proof → Run workflow**. This uses a
standard public Ubuntu runner, no GitHub cache upload, no stored artifacts and
no secrets. The optional download of precompiled mathlib files is from its
upstream cache; it does not consume this account's Actions cache storage.

Only a successful kernel build plus a checked axiom report justifies the formal
status for these exact declarations. Expected axioms are at most `propext`,
`Classical.choice`, and `Quot.sound`; no `sorryAx` or reduction oracle is allowed.
The Python experiment records `formal_proofs_checked: false` independently.
If this project has not been run in your environment, treat its files as a proof
project awaiting kernel verification, not completed formal evidence.
