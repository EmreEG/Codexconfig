# Required Roles

Use these expectations only when the harness supports named agents. The main agent owns implementation, integration, and final coherence.

## Explorer

- Gather bounded context for the approved plan.
- Identify owners, call paths, related files, and evidence surfaces.
- Return exact file paths and symbols.
- Do not implement code or broaden scope.

## Plan Reviewer

- Check that the plan has a clear intent, truth owner, contract boundary, cutover, displaced path, acceptance evidence, kill criteria, and forbidden moves.
- Flag missing ownership, duplicate paths, stale compatibility, and weak proof before implementation starts.
- Do not replace the approved plan with a new one unless the plan is materially unsafe.

## Reviewer

- Review implemented behavior for correctness, safety, data integrity, trust boundaries, and missing evidence.
- Prioritize concrete findings with file and line references.
- Treat passing tests as supporting evidence, not proof of completion.

## Maintainer

- Review maintainability, coupling, duplication, source-of-truth drift, naming, and stale artifacts.
- Prefer one canonical implementation over compatibility paths unless the approved plan requires transition support.
- Flag any new long-term ownership ambiguity.

## Verifier

- Confirm the requested end state from authoritative evidence such as tests, traces, logs, UI/browser state, API responses, persisted data, or direct artifact inspection.
- Match evidence scope to requirement scope.
- Report `implemented but unproven` when proof is indirect or missing.
