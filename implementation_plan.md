# Spécifications & Architecture : Aegis-Swarm (Sovereign Swarm Defense)

Ce document décrit l'architecture technique, les flux de données et le plan de réalisation du projet **Aegis-Swarm**, situé dans `D:\Users\worke\Documents\portfolio\aegis-nim`.

---

## 1. Vue d'Ensemble & Proposition de Valeur Entreprise

Aegis-Swarm est un **système de défense distribué et souverain pour parcs d'entreprises (Fleet Security & Swarm Defense)** conçu pour être déployé sur infrastructure privée **HPE** avec accélération **NVIDIA**.

### La Problématique Réelle :
1. Les cyberattaques modernes ne ciblent pas une seule machine de façon isolée : elles pénètrent par un point faible (serveur DMZ ou phishing poste client) et effectuent des mouvements latéraux vers le cœur du système d'information (bases de données, Active Directory).
2. Les agents de sécurité classiques analysent chaque alerte en silo sans vue stratégique d'ensemble.
3. Les RSSI refusent catégoriquement de laisser un modèle d'IA autonome exécuter des contre-mesures destructrices sur des serveurs critiques de production (risque d'interruption d'activité).

### La Solution Aegis-Swarm :
1. **Flotte de nœuds monitorés (*Fleet Nodes*) :** Des sondes légères déployées sur les machines d'entreprise (`srv-web-dmz`, `srv-db-core`, `workstation-finances`).
2. **Cerveau Stratégique Central (*NVIDIA NIM Nemotron 70B*) :** Corrélation globale en temps réel des signaux remontés par la flotte pour anticiper le mouvement de l'attaquant et générer une stratégie de défense coordonnée.
3. **Pare-feu Décisionnel (*NVIDIA NeMo Guardrails*) :** 
   - *Input Rail* : Neutralisation des injections de prompt cachées dans les logs de télémétrie.
   - *Action Rail* : Blocage des ordres dangereux sur les machines de criticité élevée (Tier-0 / Crown Jewels) avec bascule en validation humaine (*Human-in-the-Loop*).

---

## 2. Structure du Dépôt (`D:\Users\worke\Documents\portfolio\aegis-nim`)

```
aegis-nim/
├── README.md                      # Présentation du projet, architecture et pitch entreprise
├── requirements.txt               # nemoguardrails, langchain-nvidia-ai-endpoints, pydantic, rich
├── .env.example                   # Configuration clés et endpoints NIM
├── config/
│   ├── settings.py                # Configuration Pydantic (modèles NIM, seuils)
│   └── guardrails/
│       ├── config.yml             # Configuration du moteur NeMo Guardrails + NIM
│       └── swarm_rails.co         # Règles Colang (politiques d'actions et sécurité)
├── aegis_swarm/
│   ├── __init__.py
│   ├── models.py                  # Schémas typés Pydantic (Node, Telemetry, Action, Strategy)
│   ├── fleet/
│   │   ├── __init__.py
│   │   ├── node.py                # Modèle de nœud d'entreprise (rôle, criticité, statut)
│   │   └── fleet_manager.py       # Gestionnaire de la flotte et application des actions
│   ├── brain/
│   │   ├── __init__.py
│   │   ├── nim_client.py          # Client unifié NVIDIA NIM (Nemotron 70B, Llama 3.1)
│   │   └── strategist.py          # Corrélation multi-nœuds et élaboration de stratégie
│   ├── guardrails/
│   │   ├── __init__.py
│   │   └── gatekeeper.py          # Interception NeMo Guardrails et validation d'actions
│   └── orchestrator.py            # Moteur central coordonnant Flotte -> Télémétrie -> IA -> Guardrails
├── simulate_fleet_attack.py       # Scénario de cyberattaque multi-nœuds en direct
└── main.py                        # Interface CLI / SOC Console interactive
```

---

## 3. Plan d'Implémentation Immédiat

1. **Création du répertoire et des configurations de base** (`requirements.txt`, `.env.example`, `config/settings.py`).
2. **Implémentation des modèles de données et de la flotte** (`models.py`, `node.py`, `fleet_manager.py`).
3. **Implémentation du client NVIDIA NIM** (`nim_client.py`, `strategist.py`).
4. **Mise en place de NeMo Guardrails** (`config/guardrails/config.yml`, `swarm_rails.co`, `gatekeeper.py`).
5. **Développement de l'orchestrateur et du script de simulation d'attaque**.
6. **Documentation complète (README.md)** prête pour publication sur GitHub / GitLab.
