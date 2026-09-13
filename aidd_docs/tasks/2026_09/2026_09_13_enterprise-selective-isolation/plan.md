---
objective: "Implémenter l'isolation sélective d'entreprise avec whitelist d'administration SOC (sous-réseau /24), support multi-interfaces et commande un_isolate."
status: implemented
---

# Plan: Enterprise Selective Isolation & Management Whitelist

## Overview

| Field | Value |
| ----- | ----- |
| **Goal** | Éviter le briquage réseau des machines physiques lors d'un `isolate_node` via une whitelist du management plane (sous-réseau SOC `/24`), le support des cartes multi-NIC, et une commande de déblocage `un_isolate` |
| **Source** | Requête utilisateur / Brainstorms `aidd-refine-01-brainstorm` |

## Phases

| #   | Phase | File |
| --- | ----- | ---- |
| 1   | Isolation Sélective, Whitelist Sous-Réseau SOC /24, Multi-NIC & Déblocage | [`phase-1.md`](./phase-1.md) |

## Resources

| Source | Verified |
| ------ | -------- |
| `https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/netsh-advfirewall-firewall` | Règles de pare-feu Windows `netsh advfirewall` avec `remoteip` et exclusions de gestion |
| `https://netfilter.org/documentation/` | Règles `iptables` de filtrage avec conservation d'un port/IP d'administration (`-p tcp --dport 8443 -s <SOC_SUBNET> -j ACCEPT`) |

## Decisions

| Decision | Why |
| -------- | --- |
| Whitelist SOC systématique lors de `isolate_node` | Comportement standard EDR (CrowdStrike/Defender) : isole la machine du pirate et du LAN tout en gardant le canal de contrôle SOC ouvert |
| Détection automatique du caller et whitelist `/24` | L'agent extrait l'IP appelante du socket TCP (`self.client_address[0]`) et applique le masque `/24` pour englober le sous-réseau d'administration SOC, résilient au DHCP |
| Support Multi-NIC si `mgmt_interface` déclaré | Sur serveurs d'entreprise avec cartes séparées (ex: `eno1` prod, `eno2` admin), coupure ciblée de la prod sans altérer l'interface d'administration |
| Ajout de l'action `UN_ISOLATE_NODE` | Permet au SOC de restaurer les flux réseau une fois la menace éradiquée |
| Dead Man's Switch optionnel (`auto_release_timeout`) | Filet de sécurité paramétrable pour le lab (VirtualBox, Asus PN40) restaurant le réseau si la liaison est perdue |
