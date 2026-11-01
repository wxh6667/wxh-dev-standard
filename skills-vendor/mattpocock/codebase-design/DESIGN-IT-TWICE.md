# Design It Twice

Use when the user asks to compare module APIs or interface designs, or says "design it twice".

First confirm from existing context the problem, the callers, the key operations, compatibility and performance constraints, and the complexity the interface must hide. Ask only about missing decisions that would change the design. Use the project's domain language and this skill's architecture vocabulary.

Propose candidates that differ in substance, for example a minimal common-case interface, an extensible interface, and one shaped around the main caller. Do not pad to a fixed number of designs or methods. Delegate independent designs to parallel agents only when it is worth it and the host supports it, giving each a different constraint; otherwise compare directly.

For each candidate give the interface signature, a usage example, the complexity hidden inside, its dependency strategy, and its error and ordering constraints. For a deepening candidate read `DEEPENING.md` to classify dependencies first. Compare simplicity, difficulty of correct use, compatibility, implementation efficiency, depth, locality and seam placement, in a table or short paragraphs.

Give a recommendation with reasons, combining candidates when that is better. When the authorization is design only, deliver the design; implement only within the user's task scope.
