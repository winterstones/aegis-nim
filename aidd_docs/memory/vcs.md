# VCS

The version-control conventions this project follows: branches, commits, and the platform.

## Setup

- Main branch: `main`
- Platform: GitHub / GitLab
- GitHub: `https://github.com/winterstones/aegis-nim.git`
- GitLab: `https://gitlab.com/winterstones/aegis-nim.git`
- Remotes: `origin` (dual push to GitHub + GitLab), `github` (GitHub direct), `gitlab` (GitLab direct)

## Branches

- Format: `feat/nom-fonctionnalite` ou `fix/nom-correctif`

## Commits

- Convention: Conventional Commits
- Format: `type(scope): description`
- Examples: `feat(brain): add nemotron correlation prompt`, `fix(guardrails): block crown jewel reboot`
- **Traçabilité IA / Humain (Git Trailers) :**
  - Code généré ou commité par l'assistant : inclut le trailer `Generated-by: Antigravity AI` et `Co-authored-by: Antigravity <ai@antigravity>`.
  - Code implémenté directement par l'humain : signé uniquement par l'auteur `winterstone` (sans mention IA).

## Commit Strategy

AI should auto commit: `after phase`
