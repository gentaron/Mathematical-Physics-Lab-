# Mathematical conventions and evidence

## Polygon combinatorics

Vertex labels are distinct positive integers in counterclockwise increasing order.
Boundary edges are not propagators. Two chords cross only when their endpoints
strictly interlace; shared endpoints are allowed. A triangulation is a maximal
non-crossing diagonal set. The empty set is the unique triangulation of a triangle.

The implementation recursively partitions polygons, combining the independent
nested structures of each cell and deduplicating identical polygon families.
The outer polygon is always included as a bookkeeping root. Its singleton family
denotes the whole face. Codimension is the number of subdivided (non-minimal)
polygons in this rooted representation. This is not the total number of polygons.
This convention differs from representations that omit the outer polygon.

For an N-gon the polytope dimension is N-3. A family of codimension r corresponds
to a face of dimension N-3-r. Superset inclusion of families corresponds to
subface containment. The artificial top element is exported as the empty face
of dimension -1. The JSON covers point from a lower face to an upper face.

The implementation compares two algorithms: explicit family enumeration and
polynomial multiplication over polygon subdivisions. Both are checked against
the small values in Table 1 of [arXiv:2603.03425v3](https://arxiv.org/html/2603.03425v3).
The 6-gon also passes the Euler boundary check 72-114+44=2.
Matching these cases is a software reproduction, not a new proof of the paper.

## Scalar amplitudes

Each triangulation contributes the reciprocal of the product of its channel
variables. Variables `X1_3`, etc., are algebraically independent. No ABHY
embedding, momentum conservation or four-dimensional constraints are imposed.
For every channel the code compares the coefficient of its simple pole with the
product of amplitudes constructed independently on the two subpolygons.
Crossing-channel double residues are checked in the test suite.

These are planar cubic scalar tree amplitudes. A rational function alone is not
a canonical differential form. This module does not realize the amplituhedron.

## Bootstrap seed

`wavefunction` repeatedly removes a tree edge, adds its energy to the incident
vertices of the two resulting components, multiplies their recursively computed
coefficients, sums over removed edges and divides by the total external energy.
The single-site coefficient is the inverse external energy. Trees are restricted
to 1–4 sites. Coupling and overall phase conventions are suppressed.

The two-site experiment chooses the denominator
`(x1+x2)(x1+y)(x2+y)` and a numerator linear in the independent energies.
Homogeneity of degree -3, exchange symmetry and normalization at the total-energy
pole determine the coefficients. Uniqueness is relative to this supplied ansatz.
This is a flat-space scalar tree seed, not an inflationary bispectrum or a
reimplementation of the differential system in Kinematic-Flow.

## Research statuses

| Status | Evidence |
| --- | --- |
| reproduced | Explicitly stated finite reference results agree |
| counterexample | Exact predicted and observed values disagree at a recorded input |
| conjecture | Listed finite cases agree; general claim remains unproved |
| symbolic_verified | SymPy establishes an identity under the recorded formal assumptions |
| inconclusive | An optional computation or proposal could not be completed |
| formally_proved | Reserved for a separate successful Lean kernel verification; unavailable to the JSON append API |

Neither local LLM text nor numerical agreement can certify a theorem. Record
hashes capture input and implementation bytes; they are not signatures, novelty
certificates or proof. Independent experts should review physical assumptions
before interpreting a seed calculation as a statement about the early universe.
