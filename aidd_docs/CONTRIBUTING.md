# Contributing to this project's AI context

How to add or change the context the AI relies on here.

## Changing project memory

Add or edit a file under `aidd_docs/memory/`. See [`memory/README.md`](memory/README.md) for what belongs there and how it loads.

## Adding AI content (skills, rules, agents, commands, hooks)

- Use the generator skills (`aidd-context-04-skill-generate` through `08-hook-generate`, and `10-learn` for memory or rules). They scaffold the right shape and write to the right place for each tool you use.
- Open a pull request for anything that changes how the AI behaves on this project. The team reviews it like any code change.

## Adding recipes

Create or edit project recipes under `aidd_docs/recipes/`. Use the cook skill when available so new recipes follow the shared contract and do not overwrite bundled framework recipes.

## House conventions

- Architecture et invariants de sécurité sont décrits dans `aidd_docs/memory/architecture.md` et `aidd_docs/GUIDELINES.md`.
- Les modifications de règles de garde-fous doivent être répercutées dans `aidd_docs/memory/coding-assertions.md`.
