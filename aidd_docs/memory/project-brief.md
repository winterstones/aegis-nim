# Project Brief

What this project is, the problem it solves, and its domain language. The non-derivable "why", not the "how".

## What it is

- Aegis-Swarm est un système souverain de cyberdéfense agentique distribuée pour flottes de serveurs d'entreprise (*Fleet Security & Swarm Defense*), développé pour le Hackathon HPE & NVIDIA Agentic AI (Genève, septembre 2026).
- Il associe un Cerveau Stratégique central alimenté par NVIDIA NIM (Nemotron 70B sur infrastructure HPE) et un Pare-feu Décisionnel rigoureux alimenté par NVIDIA NeMo Guardrails.

## Why it exists

- **Les cyberattaques d'entreprise sont transversales :** Elles pénètrent par un maillon faible (serveur DMZ, phishing) pour pivoter latéralement vers les bases de données financières et contrôleurs de domaine.
- **Les défenses en silo échouent :** Les sondes isolées manquent de corrélation globale de flotte.
- **Refus du "Shadow AI" destructeur par les RSSI :** Une IA autonome ne doit jamais pouvoir couper ou isoler un serveur de production critique sans validation humaine explicite. Aegis-Swarm résout ce dilemme avec des garde-fous déterministes et du Human-in-the-Loop.

## Domain language

The terms a contributor must know to read the code.

| Term | Meaning |
| ---- | ------- |
| Swarm Brain | Cerveau stratégique central corrélant les alertes de flotte via NVIDIA Nemotron 70B |
| Fleet Node | Nœud surveillé (`srv-web-dmz`, `srv-db-core`, etc.) remontant de la télémétrie et recevant des actions |
| Crown Jewels / Tier-0 | Nœud ou ressource hautement critique interdisant toute coupure automatique sans validation humaine |
| NeMo Gatekeeper | Pare-feu décisionnel interceptant les stratégies de l'IA pour appliquer des politiques de sécurité strictes |
| Action Rail | Règle déclarative Colang (`.co`) validant ou bloquant une contre-mesure selon la criticité |
| Input Rail | Garde-fou NeMo inspectant les logs pour neutraliser les injections de prompt indirectes |

## Key features

- Sondes de télémétrie locale légères pour flotte de serveurs d'entreprise.
- Corrélation d'incidents globale et anticipation de mouvements latéraux par Nemotron 70B.
- Filtrage pré-exécution par NeMo Guardrails avec bascule Human-in-the-Loop sur nœuds critiques.
- Console interactive SOC avec visualisation d'état de flotte et simulation en direct d'attaques multi-cibles.
