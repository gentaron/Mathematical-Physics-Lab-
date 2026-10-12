# Homepage validation

The HTML is generated from the existing verified reference report, with no new
scientific or novelty claims. Source values and recurrence agreement are checked
before publishing. Rendered data text is escaped, and the page uses no JavaScript,
external stylesheets, images, fonts, API calls or browser-side computation.

Validation covers the displayed six-vertex result (72 vertices, 114 edges,
44 two-dimensional faces), exact counterexample (25 predicted, 72 observed),
working internal link targets, viewport markup, native disclosure elements,
rejection of unverified figures, static snapshot export, and HTML generation
alongside CLI research runs. A complete test-suite rerun checks the integration.

The text-based design follows the requested plain-paper reference: white,
serif typography, thin rules and blue underlined links. CSS includes a one-column
mobile navigation layout and a bounded fluid reading width.

Browser screenshots and real-device interaction were not verified here. The
managed environment has neither the Browser control skill nor an installed
Chromium executable; its Sites instructions prohibit installing a browser or
starting an improvised preview server in that situation. The HTML/DOM and output
checks are the available verification evidence, not a substitute for device QA.

The complete suite passed: **60 tests**. A separate read-only review found no
blocking issues in the displayed claims, escaping, static dependencies, CLI
export path or responsive CSS. The CLI integration test uses the returned run
directories, so previously preserved research runs cannot contaminate its count.

GitHub repository metadata reported has_pages=false before delivery. The homepage
can be opened locally; public hosting requires the one-time main/docs setting
in Settings/Pages. The connected GitHub tools do not expose that administration
operation. No additional hosting provider or paid service was created.
