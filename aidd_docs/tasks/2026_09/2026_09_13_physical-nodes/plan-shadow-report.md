---
source: aidd_docs/tasks/2026_09/2026_09_13_physical-nodes/plan.md
generated_at: 2026-09-13T16:00:00Z
---

# Shadow Areas Report

Source: `aidd_docs/tasks/2026_09/2026_09_13_physical-nodes/plan.md`
Generated: `2026-09-13T16:00:00Z`

Total gaps: 9 | Blocker: 1 | Major: 5 | Minor: 3

---

## Gaps by Category

### unstated assumption

**[major]** How is inbound connectivity on port 8443 ensured when the target host's initial firewall blocks incoming connections?
> `Micro-Agent Daemon HTTP (Option C) plutôt que SSH seul (Option B)`

**[major]** What happens when an action targets a process owned by a higher-privileged user or system account?
> `Linux iptables / nftables & pkill | Commandes natives de filtrage réseau et d'interruption sous Linux`

### ambiguous term

**[minor]** Does process termination use graceful SIGTERM first or immediate unconditional SIGKILL?
> `Linux iptables / nftables & pkill | Commandes natives de filtrage réseau et d'interruption sous Linux`

### missing edge case

**[blocker]** How does the orchestrator regain access to an edge node once its network interface has been isolated?
> `Permettre à Aegis-Swarm d'exécuter de vraies remédiations OS (pare-feu, processus, réseau) sur des ordinateurs et serveurs physiques réels`

**[minor]** How does the actuator prevent duplicate firewall rules when the same IP is blocked multiple times?
> `Windows netsh advfirewall & taskkill | Commandes natives de gestion du pare-feu et des processus sous Windows`

### missing actor

**[major]** Who is responsible for issuing, distributing, and rotating agent bearer tokens across the fleet?
> `Token Auth : aegis-sovereign-token`

### missing failure mode

**[major]** How does the orchestrator handle an edge agent becoming unreachable during action dispatch?
> `Micro-Agent Daemon HTTP (Option C) plutôt que SSH seul (Option B)`

**[major]** How does the system react and notify the SOC analyst when an actuator command fails due to insufficient OS privileges?
> `Mode dry_run par défaut | Évite toute coupure réseau accidentelle ou blocage système sans droits élevés`

### missing acceptance criterion

**[minor]** What is the maximum acceptable latency for dispatching and applying an action on a physical node?
> `Permettre à Aegis-Swarm d'exécuter de vraies remédiations OS (pare-feu, processus, réseau) sur des ordinateurs et serveurs physiques réels`

### missing dependency

**[minor]** What minimum Python version is required on target machines running aegis-daemon?
> `Python Standard Library (http.server, subprocess, platform) | Multi-plateforme Windows / Linux sans dépendance externe`
