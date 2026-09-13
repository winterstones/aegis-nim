"""Data models for Aegis-Swarm (Nodes, Telemetry, Actions, Strategies)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeRole(str, Enum):
    DMZ_WEB = "dmz_web"
    DB_CORE = "db_core"
    WORKSTATION = "workstation"


class NodeTier(str, Enum):
    TIER_0 = "tier_0"  # Crown Jewels (DBs, Active Directory) - Aucune coupure sans HITL
    TIER_1 = "tier_1"  # Serveurs d'applications / DMZ
    TIER_2 = "tier_2"  # Postes de travail / machines non-critiques


class NodeStatus(str, Enum):
    HEALTHY = "healthy"
    SUSPICIOUS = "suspicious"
    COMPROMISED = "compromised"
    ISOLATED = "isolated"
    QUARANTINED = "quarantined"


class ActionType(str, Enum):
    ISOLATE_NODE = "isolate_node"          # Destructif / arrêt total
    BLOCK_IP = "block_ip"                  # Dégradation gracieuse / filtrage
    QUARANTINE_PORT = "quarantine_port"    # Dégradation gracieuse / restriction
    KILL_PROCESS = "kill_process"          # Ciblé


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    DEGRADED = "degraded"
    EXECUTED = "executed"
    PENDING_HITL = "pending_hitl"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Node(BaseModel):
    id: str
    name: str
    ip: str
    role: NodeRole
    tier: NodeTier
    status: NodeStatus = NodeStatus.HEALTHY
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_crown_jewel(self) -> bool:
        """Retourne True si le nœud appartient au Tier-0 (Crown Jewel), False sinon."""
        return self.tier == NodeTier.TIER_0

class TelemetryEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_node_id: str
    event_type: str
    payload: str
    flagged_injection: bool = False


class SecurityAlert(BaseModel):
    alert_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    node_id: str
    severity: Severity
    description: str
    raw_event: Optional[TelemetryEvent] = None


class ProposedAction(BaseModel):
    action_type: ActionType
    target_node_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    justification: str
    status: ActionStatus = ActionStatus.PROPOSED

    def is_destructive(self) -> bool:
        """Retourne True si l'action est considérée comme destructive (ex: ISOLATE_NODE)."""
        return self.action_type == ActionType.ISOLATE_NODE



class SwarmStrategy(BaseModel):
    strategy_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlated_threat: str
    anticipated_target_id: Optional[str] = None
    actions: List[ProposedAction] = Field(default_factory=list)

    def has_critical_actions(self) -> bool:
        """Retourne True si au moins une des actions proposées est destructive."""
        for action in self.actions:
            if action.is_destructive():
                return True
        return False
