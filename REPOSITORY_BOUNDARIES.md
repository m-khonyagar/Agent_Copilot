# Repository Boundaries

## Canonical product
`taskflow/` is the main product in this repository.

## Supporting directories
- `design-md/`: design and planning material
- `messenger_platform/`: separate exploratory work that should not be treated as part of the core TaskFlow runtime unless explicitly integrated

## Structural rules
- New product runtime code should go under `taskflow/`.
- Cross-cutting docs should live at the repository root or under a future `docs/` directory.
- Large generated artifacts, recordings, and exports should not be committed to git.

## When to split
If `messenger_platform/` or another exploratory area becomes independently deployable and evolves on its own cadence, it should be moved into its own repository rather than expanding this root further.
