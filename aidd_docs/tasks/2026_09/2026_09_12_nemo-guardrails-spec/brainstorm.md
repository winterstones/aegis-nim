# Spécification & Cadrage : NVIDIA NeMo Guardrails (Aegis-Swarm)

Document issu du cycle `aidd-refine:01-brainstorm` du 12 septembre 2026.

## 1. Vue d'ensemble

Définit le rôle, les mécanismes et les politiques d'interception de **NVIDIA NeMo Guardrails** au sein de l'architecture Aegis-Swarm pour le Hackathon HPE & NVIDIA.

---

## 2. Rails Implémentés

### A. Input Rail (Anti-Injection LLM Guard)
- **Rôle :** Inspection de la télémétrie et des logs de serveurs entrants (notamment issus de nœuds exposés comme `srv-web-dmz`).
- **Mécanisme :** Appel guard via modèle NVIDIA NIM pour détecter les instructions adverses dissimulées (prompt injections indirectes).
- **Consigne :** Neutralisation du log et alerte précoce si une tentative d'évasion est détectée.

### B. Action Rail (Gouvernance d'actions & Dégradation gracieuse)
- **Nœuds standards (Tier-1, Tier-2, DMZ, Postes utilisateurs) :**
  - Exécution directe des contre-mesures décidées (`isolate_node`, `kill_process`, `block_ip`).
- **Nœuds critiques Tier-0 / Crown Jewels (`srv-db-core`, Contrôleurs de domaine) :**
  - **Règle absolue :** Interdiction de coupure ou d'arrêt direct par l'IA.
  - **Dégradation gracieuse :** Remplacement automatique de l'action destructive par une restriction réseau ciblée (blocage des flux sortants suspects).
  - **Bascule HITL :** Si l'attaque nécessite une intervention lourde, passage obligatoire en validation humaine (*Human-in-the-Loop*).

### C. Output Rail (Schémas typés Pydantic)
- **Rôle :** Garantie que la stratégie émise est strictement interprétable par le code Python.
- **Format :** Contrainte sous forme d'objet JSON strict `{action, target_node, parameters, justification}` validé par Pydantic v2.
- **Rendu opérateur :** Mise en forme visuelle et enrichissement console délégués à Rich dans `main.py`.

---

## 3. Politique de Timeout & Escalade Graduée (Tier-0 HITL)

- **Durée d'attente configurable (`config/settings.py`) :**
  - *Mode Simulation / Démo Hackathon :* **30 secondes**.
  - *Mode Entreprise / Prod :* **300 secondes (5 minutes)**.

- **Confinement graduel :**
  1. **Phase 1 (Immédiate pendant attente analyste - Confinement passif) :**
     - Blocage immédiat des flux sortants et ports cibles suspects.
     - Maintien en ligne des services métier locaux (transactions DB préservées).
  2. **Phase 2 (À expiration du timeout sans réponse - Escalade Fail-Secure) :**
     - Si l'attaque persiste et franchit le seuil d'urgence, isolement complet du serveur pour éviter la contamination de flotte.
     - Déclenchement d'une alerte d'urgence P1 dans la console SOC.

---

## 4. Prochaine étape

Passage au cycle d'implémentation de la Phase 1 :
- `requirements.txt`
- `.env.example`
- `config/settings.py`
- `aegis_swarm/models.py`
