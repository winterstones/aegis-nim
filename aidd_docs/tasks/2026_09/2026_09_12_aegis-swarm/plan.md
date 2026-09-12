---
objective: "Implémenter le système de cyberdéfense distribué et souverain Aegis-Swarm avec NVIDIA NIM et NeMo Guardrails."
status: in-progress
---

# Plan: Aegis-Swarm Implementation

## Overview

| Field | Value |
| ----- | ----- |
| **Goal** | Implémenter le prototype complet Aegis-Swarm (Flotte + NIM Nemotron 70B + NeMo Guardrails + Simulateur d'attaque + Console SOC) |
| **Source** | `implementation_plan.md` |

## Phases

| # | Phase | File |
| - | ----- | ---- |
| 1 | Socle, Configuration & Modèles Typés | [`phase-1.md`](./phase-1.md) |
| 2 | Gestionnaire de Flotte & Télémétrie | [`phase-2.md`](./phase-2.md) |
| 3 | Client NVIDIA NIM & Stratège de Corrélation | [`phase-3.md`](./phase-3.md) |
| 4 | Moteur NeMo Guardrails & Gatekeeper Colang | [`phase-4.md`](./phase-4.md) |
| 5 | Orchestrateur Swarm, Simulateur & Console SOC | [`phase-5.md`](./phase-5.md) |

## Resources

| Source | Verified |
| ------ | -------- |
| `https://build.nvidia.com` | Endpoints NIM compatibles OpenAI et modèles Nemotron 70B |
| `https://docs.nvidia.com/nemo/guardrails` | Syntaxe Colang 2.x et configuration des Input/Action/Output Rails |

## Decisions

| Decision | Why |
| -------- | --- |
| Découplage strict Stratégie (Nemotron) vs Validation (NeMo) | Garantie absolue qu'aucune action destructive n'est exécutée sans validation de politique déterministe |
| Mode mock intégré pour NIM et NeMo | Permet le développement, les tests unitaires et la démonstration hors-ligne sans clé active |
| Binômage IA/Humain | L'IA pose les squelettes, schémas et tests ; l'humain code la logique métier et les règles Colang |
