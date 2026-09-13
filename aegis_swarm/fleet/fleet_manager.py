"""Fleet Manager: registry of enterprise nodes and dispatch hub."""

from typing import Dict, List, Optional
from aegis_swarm.models import (
    Node,
    NodeRole,
    NodeTier,
    NodeStatus,
    ProposedAction,
    ActionStatus,
)
from aegis_swarm.fleet.node import NodeInstance


class FleetManager:
    def __init__(self):
        self.nodes: Dict[str, NodeInstance] = {}

    def register_node(self, node_instance: NodeInstance) -> None:
        """Enregistre un nœud dans l'inventaire de la flotte."""
        self.nodes[node_instance.id] = node_instance

    def get_node(self, node_id_or_name: str) -> Optional[NodeInstance]:
        """Récupère un nœud par son identifiant unique ou par son nom réseau."""
        if node_id_or_name in self.nodes:
            return self.nodes[node_id_or_name]
        for node in self.nodes.values():
            if node.name == node_id_or_name:
                return node
        return None

    def dispatch_action(self, action: ProposedAction) -> bool:
        """Achemine et exécute une action sur le nœud cible spécifié."""
        node = self.get_node(action.target_node_id)
        if node is None:
            return False
        success = node.apply_action(action)
        if success:
            action.status = ActionStatus.EXECUTED
        return success

    def get_fleet_summary(self) -> Dict[str, str]:
        """Retourne un résumé clé-valeur de l'état de chaque nœud."""
        return {node.name: node.status.value for node in self.nodes.values()}

    def register_physical_node(
        self,
        node_id: str,
        name: str,
        ip: str,
        role: NodeRole,
        tier: NodeTier,
        actuator_type: str = "agent",
        agent_url: Optional[str] = None,
        agent_token: str = "aegis-sovereign-token",
        dry_run: bool = False,
    ) -> NodeInstance:
        """Enregistre un ordinateur ou serveur physique réel dans la flotte."""
        node = Node(
            id=node_id,
            name=name,
            ip=ip,
            role=role,
            tier=tier,
            status=NodeStatus.HEALTHY,
            metadata={"actuator_type": actuator_type, "physical": True},
        )
        if actuator_type == "local":
            from aegis_swarm.fleet.actuators.local_os import LocalOSActuator
            actuator = LocalOSActuator(dry_run=dry_run)
        else:
            from aegis_swarm.fleet.actuators.agent_actuator import AgentActuator
            actuator = AgentActuator(agent_url=agent_url or f"http://{ip}:8443", token=agent_token)

        instance = NodeInstance(node, actuator=actuator)
        self.register_node(instance)
        return instance

    @classmethod
    def bootstrap_default_fleet(cls) -> "FleetManager":
        """Initialise la flotte par défaut pour le scénario du Hackathon HPE & NVIDIA."""
        manager = cls()

        # 1. Nœud exposé Web / DMZ
        dmz_node = Node(
            id="node-web-1",
            name="srv-web-dmz",
            ip="192.168.1.50",
            role=NodeRole.DMZ_WEB,
            tier=NodeTier.TIER_1,
            status=NodeStatus.HEALTHY,
        )
        manager.register_node(NodeInstance(dmz_node))

        # 2. Cœur de base de données critique / Crown Jewel (Tier-0)
        db_node = Node(
            id="node-db-1",
            name="srv-db-core",
            ip="10.0.5.20",
            role=NodeRole.DB_CORE,
            tier=NodeTier.TIER_0,
            status=NodeStatus.HEALTHY,
        )
        manager.register_node(NodeInstance(db_node))

        # 3. Poste de travail utilisateur (LAN interne)
        workstation_node = Node(
            id="node-workstation-1",
            name="workstation-finances",
            ip="10.0.10.15",
            role=NodeRole.WORKSTATION,
            tier=NodeTier.TIER_2,
            status=NodeStatus.HEALTHY,
        )
        manager.register_node(NodeInstance(workstation_node))

        return manager
