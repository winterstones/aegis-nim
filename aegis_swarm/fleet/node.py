"""Live node representation for telemetry and actuator execution."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from aegis_swarm.models import (
    Node,
    NodeRole,
    NodeTier,
    NodeStatus,
    ActionType,
    ActionStatus,
    ProposedAction,
    TelemetryEvent,
    SecurityAlert,
    Severity,
)


class NodeInstance:
    def __init__(self, node: Node):
        self.node = node
        self.events: List[TelemetryEvent] = []
        self.blocked_ips: List[str] = []
        self.quarantined_ports: List[int] = []
        self.active_processes: List[str] = ["systemd", "sshd"]

    @property
    def id(self) -> str:
        return self.node.id

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def tier(self) -> NodeTier:
        return self.node.tier

    @property
    def status(self) -> NodeStatus:
        return self.node.status

    def apply_action(self, action: ProposedAction) -> bool:
        """Applique une action défensive sur le nœud et met à jour son état."""
        if action.action_type == ActionType.ISOLATE_NODE:
            self.node.status = NodeStatus.ISOLATED
            return True
        elif action.action_type == ActionType.QUARANTINE_PORT:
            port = action.parameters.get("port")
            if port:
                self.quarantined_ports.append(port)
            self.node.status = NodeStatus.QUARANTINED
            return True
        elif action.action_type == ActionType.BLOCK_IP:
            ip = action.parameters.get("ip")
            if ip:
                self.blocked_ips.append(ip)
            return True
        elif action.action_type == ActionType.KILL_PROCESS:
            process = action.parameters.get("process_name")
            if process and process in self.active_processes:
                self.active_processes.remove(process)
            return True
        return False

    def simulate_compromise(self, attacker_ip: str, payload: str, description: str) -> SecurityAlert:
        """Simule une compromission ou anomalie sur le nœud et génère une alerte."""
        self.node.status = NodeStatus.COMPROMISED
        event = TelemetryEvent(
            source_node_id=self.id,
            event_type="UNAUTHORIZED_ACCESS",
            payload=payload,
        )
        self.events.append(event)
        return SecurityAlert(
            alert_id=f"alert-{self.id}-{int(datetime.now(timezone.utc).timestamp())}",
            node_id=self.id,
            severity=Severity.HIGH,
            description=description,
            raw_event=event,
        )
