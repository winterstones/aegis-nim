# Aegis-Swarm 🛡️⚡
> **Sovereign Swarm Cyberdefense with HPE & NVIDIA NIM**  
> *Système souverain de cyberdéfense agentique distribuée pour flottes de serveurs d'entreprise.*

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20Nemotron--70B-76B900.svg)](https://build.nvidia.com/)
[![NeMo Guardrails](https://img.shields.io/badge/Security-NeMo%20Guardrails-green.svg)](https://github.com/NVIDIA/NeMo-Guardrails)
[![Tests](https://img.shields.io/badge/Tests-29%2F29%20Passing-brightgreen.svg)](tests/)
[![HPE](https://img.shields.io/badge/Infrastructure-HPE%20Sovereign%20AI-01A982.svg)](https://www.hpe.com/)

---

## 🎯 Vision & Problématique

Dans les infrastructures d'entreprise modernes, les cyberattaques ne sont plus confinées à un serveur isolé : elles exploitent un maillon faible (DMZ Web, phishing poste de travail) pour **pivoter latéralement** vers les serveurs critiques (*Crown Jewels / Tier-0* : bases de données financières, Active Directory).

Les approches de défense traditionnelles souffrent de deux limites majeures :
1. **Défenses en silos** : Absence de corrélation transverse à l'échelle de la flotte en temps réel.
2. **Refus du "Shadow AI" destructeur par les RSSI** : Une IA autonome ne doit jamais pouvoir couper ou isoler brutalement un cœur de production sans garde-fous stricts et supervision humaine (*Human-in-the-Loop*).

**Aegis-Swarm** résout ce dilemme en associant :
- Un **Cerveau Stratégique centralisé** propulsé par **NVIDIA NIM** (Nemotron 70B) pour anticiper les mouvements d'attaque.
- Un **Pare-feu Décisionnel rigoureux** propulsé par **NVIDIA NeMo Guardrails** qui garantit la continuité d'activité par dégradation gracieuse.
- Un **Micro-Agent Edge autonome (`aegis-daemon`)** sans dépendance externe, déployable sur tout serveur physique Windows/Linux avec **isolation réseau sélective d'entreprise**.

---

## 🏗️ Architecture Globale

```mermaid
flowchart TD
    subgraph Fleet ["Flotte d'Entreprise & Edge Nodes"]
        Node1["srv-web-dmz (Tier-1 DMZ)"]
        Node2["srv-db-core (Tier-0 Crown Jewel)"]
        Node3["workstation-finances (Tier-2 LAN)"]
        NodePhysical["Serveur Physique / Edge Daemon (:8443)"]
    end

    subgraph Core ["Aegis Core Orchestrator"]
        FM["Fleet Manager (Inventaire & Dispatch)"]
        InputRail["NeMo Input Rail (Neutralisation Prompt Injection)"]
        Brain["NIM Strategic Brain (Nemotron 70B Correlation)"]
        ActionRail["NeMo Action Rail (Colang Policies & Tier-0 Safety)"]
    end

    subgraph Decision ["Gouvernance & Exécution"]
        AutoExec["Actionneur Automatique (Local / Agent / Simulation)"]
        HITL["Escalade Human-in-the-Loop (SOC Analyst Approval)"]
    end

    Node1 -->|Logs / Télémétrie| FM
    Node2 -->|Logs / Télémétrie| FM
    Node3 -->|Logs / Télémétrie| FM
    NodePhysical -->|Télémétrie HTTP| FM

    FM --> InputRail
    InputRail -->|Télémétrie Assainie| Brain
    Brain -->|Stratégie de Défense Proposée| ActionRail
    
    ActionRail -->|Nœud Non-Critique (Tier-1 / Tier-2)| AutoExec
    ActionRail -->|Nœud Critique Tier-0 (Blocage & Dégradation)| HITL
    HITL -->|Validation Humaine ou Timeout Fail-Secure| AutoExec

    AutoExec -->|Contre-Mesure Ciblée| Node1
    AutoExec -->|Confinement Passif / Dégradation| Node2
    AutoExec -->|Isolation Sélective Whitelist SOC /24| NodePhysical
```

---

## 🔑 Composants Clés

### 1. Cerveau Stratégique NIM (`aegis_swarm/brain/`)
- Client unifié compatible OpenAI (`NIMClient`) interrogeable sur le cloud NVIDIA ou des appliances privées **HPE**.
- Mode mock automatique avec bascule transparente en cas d'absence de clé API ou de coupure réseau.
- Extraction de stratégies défensives JSON structurées : corrélation multi-alertes et prédiction de cible.

### 2. NeMo Guardrails Gatekeeper (`aegis_swarm/guardrails/`)
- **Input Rail** : Analyse les payloads et logs ingérés pour neutraliser les tentatives d'injections de prompt indirectes (`SYSTEM: ignore previous rules...`).
- **Action Rail** : Règles déclaratives Colang (`config/guardrails/swarm_rails.co`) interdisant toute interruption destructive d'un *Tier-0* sans accord explicite.
- **Dégradation Gracieuse** : Transforme un ordre destructeur (`isolate_node`) en confinement passif non bloquant (`quarantine_port 3306`).

### 3. Actionneurs de Flotte Pluggables (`aegis_swarm/fleet/actuators/`)
- `SimulatedActuator` : Émulation en mémoire pour les tests et la validation de scénarios.
- `LocalOSActuator` : Commandes natives OS sur la machine hôte (`netsh advfirewall` sous Windows, `iptables` sous Linux). Supporte le mode `--dry-run`.
- `AgentActuator` : Pilotage à distance de machines et VM via HTTP sécurisé (Bearer token).

### 4. Micro-Agent Edge Autonome (`aegis_agent/daemon.py`)
- **Zéro dépendance externe** (uniquement la bibliothèque standard Python 3).
- **Isolation Sélective d'Entreprise** :
  - Calcule automatiquement le sous-réseau `/24` de la console SOC depuis le socket TCP appelant (`self.client_address[0]`).
  - Bloque tout le trafic entrant/sortant **SAUF** le flux d'administration sur le port 8443 depuis le sous-réseau SOC.
  - **Support Multi-NIC** : Coupe l'interface de production (`prod_interface`) tout en préservant la carte de gestion (`mgmt_interface`).
  - **Dead Man's Switch** : Minuteur d'auto-rétablissement (`auto_release_timeout`) pour sécuriser les tests en labo sans risquer de couper l'accès machine.
  - Commande de déblocage `un_isolate` pour restaurer l'état sain après remédiation.

---

## 🚀 Installation & Démarrage Rapide

### Prérequis
- Python 3.11 ou supérieur
- Clé API NVIDIA NIM (optionnelle, mode mock autonome inclus)

### Installation
```bash
# Cloner le dépôt
git clone https://github.com/winterstones/aegis-nim.git
cd aegis-nim

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sous Linux/macOS
# ou : .venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration (Optionnel)
Créez un fichier `.env` à la racine pour activer l'inférence NIM en direct :
```env
NVIDIA_API_KEY="nvapi-your-key-here"
NIM_MODEL="deepseek-ai/deepseek-v4-flash-0731"
```

---

## 💻 Utilisation

### 1. Console de Supervision SOC Interactive
Lancez la console enrichie pour piloter la flotte en direct :
```bash
python main.py
```
Options disponibles dans la console :
- `[1]` Lancer la simulation d'attaque en 5 actes (Démo Hackathon).
- `[2]` Lancer la simulation en mode pas-à-pas (`--step`).
- `[3]` **Sandbox IA en direct** : Injecter des attaques personnalisées (Ransomware, SSH brute-force, SQL injection, Prompt injection) et observer la réponse de l'IA.
- `[4]` **Connecter des nœuds physiques réels** (poste local ou serveur distant Asus PN40 / VM VirtualBox).
- `[5]` **Centre de remédiation SOC** : Isoler sélectivement ou débloquer (`un_isolate`) un serveur.
- `[6]` Réinitialiser la flotte au statut sain.

### 2. Démonstration Scriptée en 5 Actes
Pour une démonstration complète et automatisée de la chaîne de cyberdéfense :
```bash
# Mode rapide pour tests automatiques
python simulate_fleet_attack.py --fast

# Mode interactif pas-à-pas avec explications
python simulate_fleet_attack.py --step
```

### 3. Démarrage du Micro-Agent Daemon sur un Serveur Distant
Sur un ordinateur ou une machine virtuelle que vous souhaitez protéger :
```bash
# Démarrage en mode réel (exécuter en Administrateur / root pour le pare-feu)
python -m aegis_agent.daemon --host 0.0.0.0 --port 8443 --token "aegis-sovereign-token"

# Ou en mode sécurisé / simulation :
python -m aegis_agent.daemon --dry-run
```

---

## 🧪 Validation & Tests

La suite de tests unitaires et d'intégration hermétiques couvre l'ensemble des modules (modèles, prompt injection, action rails, isolation sélective, minuteur de sécurité, authentification HTTP de l'agent) :

```bash
# Exécuter l'ensemble des 29 tests
python -m pytest tests/ -v
```

```text
tests/test_actuators.py::test_simulated_actuator_actions PASSED
tests/test_actuators.py::test_local_os_actuator_dry_run PASSED
tests/test_actuators.py::test_agent_daemon_state_dry_run PASSED
tests/test_actuators.py::test_un_isolate_simulated PASSED
tests/test_actuators.py::test_local_os_actuator_selective_isolation PASSED
tests/test_actuators.py::test_local_os_actuator_multi_nic PASSED
tests/test_actuators.py::test_agent_daemon_selective_isolation_subnet_24 PASSED
tests/test_actuators.py::test_agent_daemon_dead_man_switch PASSED
tests/test_actuators.py::test_daemon_http_auth_and_validation PASSED
tests/test_actuators.py::test_daemon_http_reset_and_public_endpoints PASSED
tests/test_actuators.py::test_agent_actuator_end_to_end_http PASSED
tests/test_actuators.py::test_agent_actuator_resilience PASSED
tests/test_fleet.py::test_fleet_manager_register_physical_node PASSED
tests/test_fleet.py::test_fleet_manager_get_node_by_name PASSED
tests/test_guardrails.py::test_input_rail_detects_prompt_injection PASSED
tests/test_guardrails.py::test_action_rail_blocks_and_degrades_on_tier_0_crown_jewel PASSED
...
============================= 29 passed in 4.79s ==============================
```

---

## 📂 Structure du Projet

```text
aegis-nim/
├── aegis_agent/                  # Micro-agent autonome multi-OS (Edge Nodes)
│   └── daemon.py                 # Serveur HTTP natif avec isolation sélective & dead man's switch
├── aegis_swarm/                  # Cœur du framework agentique
│   ├── brain/                    # Client NVIDIA NIM & Stratégiste de corrélation
│   ├── fleet/                    # Inventaire de flotte & Actionneurs (Simulated, Local, Agent)
│   ├── guardrails/               # Passerelle NeMo Guardrails (Input & Action rails)
│   ├── models.py                 # Schémas typés Pydantic v2
│   └── orchestrator.py           # Pipeline unifié de détection et remédiation
├── config/                       # Configuration applicative & Politiques Colang (.co)
├── tests/                        # Suite complète de tests unitaires et intégration
├── main.py                       # Console SOC interactive Rich
├── simulate_fleet_attack.py      # Scénario de cyberattaque de démonstration en 5 actes
└── aidd_docs/                    # Mémoire pérenne et documentation du framework AIDD
```

---

## 🏆 Hackathon HPE & NVIDIA 2026

Projet conçu et développé dans le cadre du **Hackathon HPE & NVIDIA Agentic AI (Genève, 2026)** pour illustrer la puissance des modèles NVIDIA NIM orchestrés par des agents souverains, sous la gouvernance infranchissable de NeMo Guardrails.
