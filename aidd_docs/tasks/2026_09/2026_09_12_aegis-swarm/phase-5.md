---
status: done
---

# Instruction: Phase 5 - Orchestrateur Swarm, Simulateur & Console SOC

## Architecture projection

> Tree of the final files. ✅ create · ✏️ modify · ❌ delete

```txt
.
├── aegis_swarm/
│   └── orchestrator.py        ✅ Boucle centrale Swarm (Flotte -> NIM -> Guardrails -> Action)
├── simulate_fleet_attack.py   ✅ Script de démonstration de cyberattaque en 5 actes
└── main.py                    ✅ Console SOC interactive (Rich UI)
```

## User Journey

```mermaid
flowchart TD
    Run["Lancement simulate_fleet_attack.py"] --> Act1["Acte 1: Attaque DMZ + Injection log"]
    Act1 --> Act2["Acte 2: Neutralisation Input Rail"]
    Act2 --> Act3["Acte 3: Anticipation Nemotron"]
    Act3 --> Act4["Acte 4: Blocage Tier-0 & Confinement passif (30s timer)"]
    Act4 --> Act5["Acte 5: Timeout & Escalade Fail-Secure autonome"]
    Act5 --> Summary["Bilan de sécurité & Pitch Hackathon validé"]
```

## Test Scope

```mermaid
---
title: Test scope Phase 5
---
journey
  section Setup
    Flotte initialisée, simulateur prêt => Démo prête: 5: cli
  section Happy path
    Exécution du scénario en 5 actes => Menace neutralisée, DB protégée: 5: cli
  section Edge case - Interruption précoce
    Appui Ctrl+C => Quitter proprement sans corrompre l'état: 1: cli
  section Teardown
    Rapport final affiché => Succès: 5: cli
```

## Tasks to do

### `1)` Orchestrateur central (`aegis_swarm/orchestrator.py`)
> Lier les composants Flotte, Cerveau NIM et Gatekeeper NeMo dans un pipeline asynchrone.

### `2)` Simulateur d'attaque en direct (`simulate_fleet_attack.py`)
> Implémenter les 5 actes scénarisés avec affichage Rich (tableaux, compte à rebours de 30s).

### `3)` Console interactive SOC (`main.py`)
> Offrir une vue de bord en temps réel de la flotte et des alertes.

## Test acceptance criteria

| Task | Acceptance criteria |
| ---- | ------------------- |
| 1 | `python simulate_fleet_attack.py` déroule les 5 actes sans exception |
| 2 | Le compte à rebours de 30s s'affiche et l'escalade autonome s'exécute à l'expiration |
| 3 | `python main.py` démarre la console SOC interactive avec interface Rich propre |
