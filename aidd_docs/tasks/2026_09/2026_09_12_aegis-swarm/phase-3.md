---
status: done
---

# Instruction: Phase 3 - Client NVIDIA NIM & Stratège de Corrélation

## Architecture projection

> Tree of the final files. ✅ create · ✏️ modify · ❌ delete

```txt
.
├── aegis_swarm/
│   └── brain/
│       ├── __init__.py        ✅
│       ├── nim_client.py      ✅ Client NVIDIA NIM (OpenAI format + fallback mock)
│       └── strategist.py      ✅ Prompt de corrélation multi-nœuds et extraction de stratégie
└── tests/
    └── test_strategist.py     ✅ Tests de génération de stratégie défensive
```

## User Journey

```mermaid
flowchart TD
    Telemetry["Télémétrie de flotte suspecte"] --> Strat["Swarm Strategist"]
    Strat --> NIM["Appel NVIDIA NIM (Nemotron 70B)"]
    NIM --> Parse["Parsing de la réponse en SwarmStrategy typée"]
```

## Test Scope

```mermaid
---
title: Test scope Phase 3
---
journey
  section Setup
    Initialisation du client NIM avec clé ou mock => Client prêt: 5: api
  section Happy path
    Soumission d'une alerte DMZ => Stratégie anticipant l'attaque latérale: 5: api
  section Edge case - API indisponible
    Erreur réseau ou timeout API => Bascule automatique en mode heuristique/fallback: 1: api
  section Teardown
    Reset cache client => Prêt: 5: system
```

## Tasks to do

### `1)` Client unifié NVIDIA NIM (`aegis_swarm/brain/nim_client.py`)
> Implémenter l'appel à `https://integrate.api.nvidia.com/v1` avec support `--mock`.

### `2)` Stratège de corrélation (`aegis_swarm/brain/strategist.py`)
> Créer le prompt de corrélation d'attaques latérales pour Nemotron 70B et parser la réponse en `SwarmStrategy`.

### `3)` Tests unitaires (`tests/test_strategist.py`)

## Test acceptance criteria

| Task | Acceptance criteria |
| ---- | ------------------- |
| 1 | `nim_client.chat_completion(...)` retourne une réponse valide de Nemotron (ou mock structuré) |
| 2 | `strategist.analyze_fleet(...)` extrait une `SwarmStrategy` conforme au schéma Pydantic |
| 3 | `pytest tests/test_strategist.py` passe à 100% |
