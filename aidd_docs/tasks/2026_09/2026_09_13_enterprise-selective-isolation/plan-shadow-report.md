---
source: aidd_docs/tasks/2026_09/2026_09_13_enterprise-selective-isolation/plan.md
generated_at: 2026-09-13T16:56:00+02:00
---

# Shadow Areas Report

Source: `aidd_docs/tasks/2026_09/2026_09_13_enterprise-selective-isolation/plan.md`
Generated: `2026-09-13T16:56:00+02:00`

Total gaps: 5 | Blocker: 0 | Major: 3 | Minor: 2

---

## Gaps by Category

### unstated assumption

**[major]** What happens when the orchestrator connects through an HTTP reverse proxy or NAT where the TCP socket IP reflects the gateway rather than the actual SOC subnet?
> L'agent extrait l'IP appelante du socket TCP (self.client_address[0]) et applique le masque /24 pour englober le sous-réseau d'administration SOC, résilient au DHCP

**[minor]** How does the system determine the default production interface when prod_interface is not explicitly provided in a multi-NIC configuration?
> Sur serveurs d'entreprise avec cartes séparées (ex: eno1 prod, eno2 admin), coupure ciblée de la prod sans altérer l'interface d'administration

### missing edge case

**[major]** What occurs if the host machine or daemon reboots while an auto-release dead man's switch timer is still running?
> Dead Man's Switch optionnel (auto_release_timeout) : Filet de sécurité paramétrable pour le lab (VirtualBox, Asus PN40) restaurant le réseau si la liaison est perdue

**[minor]** How is isolation traffic handled when the edge node connects over an IPv6 address rather than standard IPv4 dotted-quad?
> L'agent extrait l'IP appelante du socket TCP (self.client_address[0]) et applique le masque /24 pour englober le sous-réseau d'administration SOC

### missing failure mode

**[major]** How does the orchestrator recover if an isolate_node command applies firewall rules successfully on the host but drops the socket connection before the HTTP 200 response can be delivered?
> Whitelist SOC systématique lors de isolate_node : isole la machine du pirate et du LAN tout en gardant le canal de contrôle SOC ouvert
