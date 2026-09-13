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


from aegis_swarm.fleet.actuators.base import BaseActuator, ExecutionResult
from aegis_swarm.fleet.actuators.simulated import SimulatedActuator


class NodeInstance:
    def __init__(self, node: Node, actuator: Optional[BaseActuator] = None):
        self.node = node
        self.actuator = actuator or SimulatedActuator()
        self.events: List[TelemetryEvent] = []
        self.blocked_ips: List[str] = []
        self.quarantined_ports: List[int] = []
        self.active_processes: List[str] = ["systemd", "sshd"]
        self.last_result: Optional[ExecutionResult] = None

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
        """Applique une action défensive sur le nœud via son actionneur dédié."""
        # Suivi local des paramètres
        if action.action_type == ActionType.BLOCK_IP:
            ip = action.parameters.get("ip")
            if ip and ip not in self.blocked_ips:
                self.blocked_ips.append(ip)
        elif action.action_type == ActionType.QUARANTINE_PORT:
            port = action.parameters.get("port")
            if port and port not in self.quarantined_ports:
                self.quarantined_ports.append(port)
        elif action.action_type == ActionType.KILL_PROCESS:
            proc = action.parameters.get("process_name")
            if proc and proc in self.active_processes:
                self.active_processes.remove(proc)

        # Délégation à l'actionneur (Simulé, OS Local, ou Micro-Agent distant)
        res = self.actuator.apply_action(action, self.node)
        self.last_result = res
        if res.success and action.action_type == ActionType.UN_ISOLATE_NODE:
            self.node.status = NodeStatus.HEALTHY
        return res.success

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
