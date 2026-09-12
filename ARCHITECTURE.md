# Dossier de Synthèse : Hackathon HPE & NVIDIA & Projet Aegis-Swarm

> **Document de cadrage et de transfert pour projet Antigravity**  
> **Événement :** HPE & NVIDIA Agentic AI Hackathon for Enterprises @ HPE Geneva CIC  
> **Date :** Lundi 14 septembre 2026 (Hands-on) & Jeudi 24 septembre 2026 (Awards)  
> **Projet :** Aegis-Swarm (Sovereign Enterprise Swarm Defense)

---

## 1. Contexte du Hackathon HPE & NVIDIA (Genève)

### A. Format et Calendrier
- **Lundi 14 septembre (09:00 - 21:00) :** Journée technique et prototypage au **HPE Customer Innovation Center (CIC)** à Meyrin (Genève).
- **Jeudi 24 septembre :** Présentation des projets, pitch devant jury et remise des prix à l'**Hôtel Hilton Geneva**.
- **Organisateurs :** Swiss {ai} Weeks & HPE AI Services, en partenariat avec NVIDIA.

### B. Les Attentes du Jury (Critères Clés)
1. **Focus « Enterprise » & ROI concret :** Résoudre un vrai problème d'entreprise (finance, industrie, santé, télécoms) avec un modèle de coûts et de valeur crédible.
2. **IA Agentique Réelle :** Ne pas se limiter à un simple chatbot RAG. Le jury attend de l'autonomie, du multi-agents, du raisonnement multi-étapes et du *tool-calling*.
3. **Exploitation de la stack HPE & NVIDIA :** 
   - Déploiement souverain sur infrastructure privée (on-premise / private cloud HPE).
   - Inférence accélérée via **NVIDIA NIM**.
   - Modèles de raisonnement **NVIDIA Nemotron**.
   - Sécurité et contrôle via **NVIDIA NeMo Guardrails**.
4. **Gouvernance & Sécurité :** Traçabilité des actions, prévention des dérives, absence de fuites de données.

---

## 2. Piliers Technologiques & Fiche Mémo

### A. NVIDIA NIM (NVIDIA Inference Microservices)
- **Définition :** Microservices conteneurisés ultra-optimisés (TensorRT-LLM + Triton Inference Server) exposant des API compatibles OpenAI (`/v1/chat/completions`).
- **Accès Sandbox :** [build.nvidia.com](https://build.nvidia.com) (crédits gratuits via clé `nvapi-...`).
- **Modèle de référence :** `nvidia/llama-3.1-nemotron-70b-instruct` (taillé pour l'alignement entreprise et le raisonnement agentique).

```python
# Exemple d'appel standard NIM
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="nvapi-VOTRE_CLE"
)
response = client.chat.completions.create(
    model="nvidia/llama-3.1-nemotron-70b-instruct",
    messages=[{"role": "user", "content": "Analyse ce log d'incident..."}],
    temperature=0.1
)
```

### B. NVIDIA NeMo Guardrails
- **Définition :** Couche open-source de gouvernance et de sécurité programmable au-dessus des LLMs.
- **Les 4 Rails d'Entreprise :**
  1. **Input Rail :** Bloque les injections de prompt (jailbreaks, prompts malveillants cachés dans les logs).
  2. **Topical Rail :** Maintient l'agent strictement dans son périmètre métier.
  3. **Execution/Action Rail :** Intercepte et valide les ordres/outils avant exécution sur le système.
  4. **Output Rail :** Vérifie la véracité des faits et anonymise les données sensibles (PII).
- **Langage Colang (`.co`) & Configuration (`config.yml`) :** Permet de définir les règles de manière déclarative.

---

## 3. Analyse Critique du Projet Initial (`aegis-local`)

- **Ce qui fonctionnait bien :**
  - Principe d'un *Anti-Hallucination Gate* déterministe en Python.
  - Utilisation de LangGraph pour structurer un pipeline séquentiel.
  - Conscience des contraintes locales (VRAM, exécution privée).
- **Pourquoi le projet était "invendable" en l'état :**
  - Fichiers de logs mockés en dur, sans lien avec les outils réels d'entreprise (SIEM/EDR).
  - Triage passif et règles trop simplistes (fenêtres temporelles rigides).
  - Absence de protection contre l'injection de prompt indirecte (un pirate insérant une fausse instruction dans les logs bernait l'agent).
  - Aucune vision de flotte globale.

---

## 4. Spécifications du Nouveau Projet : Aegis-Swarm

### A. La Thématique : "Sovereign Swarm Defense"
Un système distribué où un cerveau central stratégique (HPE + NVIDIA NIM) coordonne la sécurité d'une flotte de serveurs d'entreprise hétérogènes, sous le contrôle strict de NeMo Guardrails.

```
                    ┌──────────────────────────────────────────────┐
                    │   HPE GreenLake / Private AI Data Center     │
                    │                                              │
                    │   ┌──────────────────────────────────────┐   │
                    │   │   NVIDIA NIM (Nemotron 70B)          │   │
                    │   │   "Swarm Strategic Brain"            │   │
                    │   └──────────────────┬───────────────────┘   │
                    │                      │                       │
                    │   ┌──────────────────┴───────────────────┐   │
                    │   │   NVIDIA NeMo Guardrails             │   │
                    │   │   (Validation & Action Governance)   │   │
                    │   └──────────────────┬───────────────────┘   │
                    └──────────────────────┼───────────────────────┘
                                           │ mTLS / gRPC / WebSocket
               ┌───────────────────────────┼───────────────────────────┐
               ▼                           ▼                           ▼
    ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
    │ Serveur Web (DMZ)   │     │ Base de Données     │     │ Contrôleur Domaine  │
    │ [Worker Node 1]     │     │ [Worker Node 2]     │     │ [Worker Node 3]     │
    │ Télémétrie + Acteur │     │ Télémétrie + Acteur │     │ Télémétrie + Acteur │
    └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### B. Composants Clés

1. **La Flotte de Nœuds (Fleet Workers) :**
   - Sondes légères déployées sur les serveurs (`srv-web-dmz`, `srv-db-core`, `workstation-finances`).
   - Remontent la télémétrie locale et appliquent les contre-mesures validées (isolation réseau, blocage d'IP, kill de processus).

2. **Le Cerveau Central (NVIDIA Nemotron 70B via NIM) :**
   - Corrélation transversale des alertes pour détecter les mouvements latéraux et les attaques coordonnées.
   - Élaboration d'une stratégie de défense proactive (ex: durcir la base de données avant que l'attaquant n'y parvienne depuis la DMZ).

3. **Le Pare-Feu Décisionnel (NeMo Guardrails) :**
   - **Protection Anti-Injection :** Analyse les charges utiles et les logs pour neutraliser toute tentative d'empoisonnement d'instructions.
   - **Action Rails (Sécurité Métier) :** Règle d'or : *Interdiction d'isoler un serveur critique (Tier-0 / Crown Jewels) sans validation explicite d'un analyste humain (Human-in-the-Loop).*

### C. Scénario de Démonstration (Le "Pitch" Hackathon)
1. **Étape 1 (Infiltration) :** Tentative de compromission détectée sur `srv-web-dmz`.
2. **Étape 2 (Anticipation Swarm) :** Nemotron corrèle l'activité et comprend que la cible finale est la base de données financière `srv-db-core`.
3. **Étape 3 (Garde-fous) :** L'agent veut couper le serveur DB. NeMo Guardrails bloque l'action automatique car le nœud est classé "Critique / Crown Jewel".
4. **Étape 4 (Résolution) :** L'alerte est remontée au dashboard SOC, l'analyste valide la mise sous quarantaine ciblée du port suspect, le service reste actif et la menace est neutralisée.

---

## 5. Comment exploiter ce document dans Antigravity

Pour démarrer ce projet dans un nouvel espace de travail Antigravity :
1. Créez un nouveau dossier de projet (ex: `D:\Users\worke\Documents\portfolio\aegis-nim`).
2. Copiez ce fichier sous le nom `README.md` ou `ARCHITECTURE.md` à la racine de votre nouveau projet.
3. Ouvrez le dossier dans Antigravity : l'assistant lira automatiquement ce fichier et saura exactement quel code générer et quelle stratégie suivre sans que vous ayez besoin de tout réexpliquer.
