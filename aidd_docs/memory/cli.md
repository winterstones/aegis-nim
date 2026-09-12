# CLI

The command-line tool: its commands, inputs, and distribution.

## Commands

- `python main.py` : Lance la console de supervision SOC interactive.
- `python simulate_fleet_attack.py` : Lance la simulation d'attaque multi-machines avec démonstration des garde-fous.

## Interface

- Sortie stylisée en console via **Rich** (tableaux de bord, statuts des nœuds, alertes critiques).
- Variables d'environnement configurées dans `.env` (`NVIDIA_API_KEY`, `NIM_BASE_URL`, `NEMO_CONFIG_PATH`).

## Distribution

- Exécution directe en Python 3.11+ via environnement virtuel (`.venv`).
