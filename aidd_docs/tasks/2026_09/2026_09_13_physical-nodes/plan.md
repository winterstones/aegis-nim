---
objective: "Étendre Aegis-Swarm au pilotage d'ordinateurs et serveurs physiques réels (multi-OS Windows/Linux) via actionneurs et micro-agent daemon."
status: implemented
---

# Plan: Contrôle de Nœuds Physiques Réels & Micro-Agent

## Overview

| Field | Value |
| ----- | ----- |
| **Goal** | Permettre à Aegis-Swarm d'exécuter de vraies remédiations OS (pare-feu, processus, réseau) sur des ordinateurs et serveurs physiques réels au lieu du seul mock en mémoire |
| **Source** | Requête utilisateur / `implementation_plan.md` |

## Phases

| # | Phase | File |
| - | ----- | ---- |
| 1 | Actionneurs Pluggables, Micro-Agent Multi-OS & Intégration SOC | [`phase-1.md`](./phase-1.md) |

## Resources

| Source | Verified |
| ------ | -------- |
| Python Standard Library (`http.server`, `subprocess`, `platform`) | Multi-plateforme Windows / Linux sans dépendance externe |
| Windows `netsh advfirewall` & `taskkill` | Commandes natives de gestion du pare-feu et des processus sous Windows |
| Linux `iptables` / `nftables` & `pkill` | Commandes natives de filtrage réseau et d'interruption sous Linux |

## Decisions

| Decision | Why |
| -------- | --- |
| Micro-Agent Daemon HTTP (Option C) plutôt que SSH seul (Option B) | SSH sous Windows est difficile à configurer (OpenSSH désactivé, gestion UAC). Le daemon Python est 100% portable et identique sur Linux et Windows |
| Découplage `BaseActuator` (`Simulated`, `LocalOS`, `Agent`) | Maintient l'hermétisme des tests unitaires et démos tout en permettant le pilotage réel |
| Mode `dry_run` par défaut | Évite toute coupure réseau accidentelle ou blocage système sans droits élevés |
