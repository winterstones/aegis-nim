# AI Operating Guidelines

How this team drives AI coding assistants on this project.

## House rules

- **Règle d'or de sécurité (NeMo Guardrails):** Interdiction absolue d'isoler ou d'altérer un nœud de criticité Tier-0 / Crown Jewels (ex: bases de données critiques `srv-db-core`, contrôleurs de domaine) sans validation explicite d'un analyste humain (*Human-in-the-Loop*).
- **Inférence Souveraine & NIM:** Tous les appels LLM passent par le client NVIDIA NIM unifié (`https://integrate.api.nvidia.com/v1` ou endpoint privé HPE), jamais par des endpoints SaaS tiers non autorisés.
- **Typage & Schémas stricts:** Tous les messages inter-nœuds, payloads de télémétrie, actions et stratégies sont strictement modélisés avec Pydantic v2.
- **Protection Anti-Injection:** Les logs et charges utiles de télémétrie sont systématiquement soumis aux Input Rails de NeMo Guardrails pour neutraliser les attaques par injection de prompt indirecte.
- **Découplage Stratégie / Exécution:** Le cerveau Nemotron 70B propose des stratégies; seul le composant Gatekeeper (NeMo Guardrails déterministe) autorise ou bloque leur exécution sur la flotte.
- **Séparation stricte AIDD vs NeMo Guardrails:** AIDD opère exclusivement au *dev-time* (workflow IDE, compétences de dev, revue). NeMo Guardrails opère exclusivement au *runtime* Python (`nemoguardrails`, Colang). Aucun code AIDD n'est importé en production ni n'altère le comportement de NeMo. L'apprentissage de NeMo Guardrails reste pur et direct.

## Validation depth

- Tout ajout ou modification d'actions de flotte nécessite un test unitaire validant le comportement du Gatekeeper.
- Tout refactoring de code doit passer le test de simulation `python simulate_fleet_attack.py` sans régression de sécurité.

## When the AI drifts

- Vérifier immédiatement les règles Colang (`config/guardrails/swarm_rails.co`) et les schémas de `aegis_swarm/models.py`.
- Recadrer l'objectif autour du scénario de démonstration du hackathon HPE & NVIDIA.
