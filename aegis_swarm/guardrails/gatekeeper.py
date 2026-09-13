"""Gatekeeper: NeMo Guardrails enforcement and action policy gate."""

import re
from typing import Optional, Tuple
from config.settings import settings
from aegis_swarm.models import (
    Node,
    NodeTier,
    ActionType,
    ActionStatus,
    ProposedAction,
    TelemetryEvent,
)


class NeMoGatekeeper:
    """Passerelle de sécurité NeMo Guardrails appliquant les rails d'entrée et d'action."""

    def __init__(self):
        self.hitl_timeout = settings.hitl_timeout_seconds
        # Patterns de prompt injection indirecte classiques dans les logs
        self.injection_patterns = [
            r"system\s*:\s*ignore",
            r"ignore\s+(all\s+)?previous\s+rules",
            r"classify\s+alert\s+as\s+benign",
            r"override\s+security",
            r"do\s+not\s+flag",
        ]

    def sanitize_telemetry(self, event: TelemetryEvent) -> TelemetryEvent:
        """
        Input Rail : Analyse le payload de télémétrie pour détecter les injections de prompt.
        Si une injection est détectée, flag l'événement et neutralise le payload.
        """
        payload_lower = event.payload.lower()
        for pattern in self.injection_patterns:
            if re.search(pattern, payload_lower):
                event.flagged_injection = True
                event.payload = f"[NEUTRALIZED_BY_NEMO_INPUT_RAIL] {event.payload}"
                break
        return event

    def evaluate_action(self, action: ProposedAction, target_node: Node) -> Tuple[ActionStatus, Optional[ProposedAction]]:
        """Évalue la dangerosité de l'action contre les règles NeMo et applique la dégradation gracieuse sur Tier-0."""
        if target_node.is_crown_jewel() and action.is_destructive():
            reaction = ProposedAction(
                action_type=ActionType.QUARANTINE_PORT,
                target_node_id=action.target_node_id,
                parameters={"port": action.parameters.get("port", 3306), "mitigation": "graceful_degradation"},
                justification="Action destructive bloquée par NeMo Guardrails (Tier-0). Confinement réseau passif appliqué.",
                status=ActionStatus.DEGRADED,
            )
            return (ActionStatus.PENDING_HITL, reaction)

        action.status =  ActionStatus.ALLOWED
        return (ActionStatus.ALLOWED, action)
