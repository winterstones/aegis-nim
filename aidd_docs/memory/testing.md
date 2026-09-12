# Testing

How the project is tested: the layers, the tools, and the conventions. Where tests live and how to run them.

## Strategy

- **Unit tests :** Validation des modèles Pydantic, transitions d'état des nœuds de flotte, et règles Colang NeMo Guardrails.
- **Mocked Integration :** Simulation de réponses NVIDIA NIM Nemotron pour valider l'orchestrateur hors ligne.
- **Scenario Testing :** Scénario complet d'attaque simulée (`simulate_fleet_attack.py`) démontrant la neutralisation de l'attaque et le blocage de l'action Tier-0.

## Tools

- **Runner :** Pytest (`pytest`)
- **Mocks :** `unittest.mock` (pour simuler les réponses de l'API NVIDIA NIM)

## Conventions

- Les tests résident dans `tests/`.
- Les noms de fichiers débutent par `test_*.py`.

## Run

- `pytest tests/ -v`
- `python simulate_fleet_attack.py`
