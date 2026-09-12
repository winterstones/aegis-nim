# Coding Assertions

The checks that must pass for code to count as done. Minimal, run after every change.

## Before commit

The fast gate.

| Order | Command | Checks |
| ----- | ------- | ------ |
| 1 | `python -m py_compile aegis_swarm/**/*.py main.py simulate_fleet_attack.py` | Syntaxe Python valide |
| 2 | `python -c "import pydantic; from aegis_swarm.models import Node, SwarmStrategy"` | Schémas Pydantic valides |

## Before push

The heavier gate.

| Order | Command | Checks |
| ----- | ------- | ------ |
| 1 | `pytest tests/` | Tests unitaires flotte & guardrails |
| 2 | `python simulate_fleet_attack.py --dry-run` | Validation sans échec du scénario de démonstration |

## Behavior

If a security rule or schema validation is broken, stop and fix immediately before adding any feature.
