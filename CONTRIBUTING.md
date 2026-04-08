# Contributing

## Scope
This repository currently contains the `taskflow` product plus supporting design and messenger-platform exploration material. Keep production-impacting changes focused on `taskflow/` unless a change explicitly targets another subproject.

## Workflow
1. Open an issue or document the intent in the pull request.
2. Create a focused branch from `main`.
3. Keep changes scoped to one concern.
4. Update documentation when repository boundaries or setup steps change.
5. Run the relevant local checks before opening a PR.

## Expected checks
- Backend: install dependencies and validate the FastAPI app starts cleanly.
- Frontend: install dependencies and run a production build for `taskflow/frontend`.
- Docker: keep `taskflow/docker-compose.yml` valid when changing local stack behavior.

## Repository boundaries
- `taskflow/` is the canonical product directory.
- `design-md/` is documentation and design material.
- `messenger_platform/` is auxiliary exploratory work and should not silently change product assumptions.

## Pull requests
Please include:
- what changed
- why it changed
- how it was validated
- any follow-up work still needed
