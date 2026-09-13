"""Swarm Orchestrator: central loop connecting Fleet, NIM Brain, and NeMo Gatekeeper."""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from aegis_swarm.models import (
    Node,
    TelemetryEvent,
    SecurityAlert,
    ProposedAction,
    SwarmStrategy,
    ActionStatus,
    ActionType,
    Severity,
)
from aegis_swarm.fleet.fleet_manager import FleetManager
from aegis_swarm.brain.strategist import SwarmStrategist
from aegis_swarm.guardrails.gatekeeper import NeMoGatekeeper


class AegisSwarmOrchestrator:
    """Orchestrateur central coordonnant Flotte, Cerveau NIM et Garde-fous NeMo."""

    def __init__(
        self,
        fleet_manager: Optional[FleetManager] = None,
        strategist: Optional[SwarmStrategist] = None,
        gatekeeper: Optional[NeMoGatekeeper] = None,
    ):
        self.fleet_manager = fleet_manager or FleetManager.bootstrap_default_fleet()
        self.strategist = strategist or SwarmStrategist()
        self.gatekeeper = gatekeeper or NeMoGatekeeper()
        self.alerts_history: List[SecurityAlert] = []
        self.executed_actions: List[ProposedAction] = []
        self.blocked_actions: List[ProposedAction] = []

    def ingest_telemetry(self, event: TelemetryEvent) -> Tuple[TelemetryEvent, Optional[SecurityAlert]]:
        """
        Ingère et assainit un événement de télémétrie via l'Input Rail NeMo.
        Génère une alerte si une injection de prompt est interceptée.
        """
        sanitized_event = self.gatekeeper.sanitize_telemetry(event)
        target_node = self.fleet_manager.get_node(sanitized_event.source_node_id)
        if target_node:
            target_node.events.append(sanitized_event)

        alert = None
        if sanitized_event.flagged_injection:
            alert = SecurityAlert(
                alert_id=f"alert-inj-{int(datetime.now(timezone.utc).timestamp())}",
                node_id=sanitized_event.source_node_id,
                severity=Severity.HIGH,
                description="Tentative d'injection de prompt indirecte neutralisée par NeMo Input Rail dans les logs.",
                raw_event=sanitized_event,
            )
            self.alerts_history.append(alert)

        return sanitized_event, alert

    def process_cycle(self, active_alerts: List[SecurityAlert]) -> Dict[str, Any]:
        """
        Exécute un cycle de réponse défensive :
        1. Corrélation Nemotron 70B -> SwarmStrategy
        2. Évaluation NeMo Guardrails de chaque action
        3. Dispatch d'action ou bascule HITL
        """
        fleet_status = self.fleet_manager.get_fleet_summary()
        strategy = self.strategist.analyze_fleet(fleet_status, active_alerts)

        decisions = []
        for action in strategy.actions:
            target_node_instance = self.fleet_manager.get_node(action.target_node_id)
            if not target_node_instance:
                continue

            status, final_action = self.gatekeeper.evaluate_action(action, target_node_instance.node)

            if status == ActionStatus.ALLOWED and final_action:
                self.fleet_manager.dispatch_action(final_action)
                self.executed_actions.append(final_action)
                decisions.append({
                    "action": final_action,
                    "verdict": "ALLOWED",
                    "executed": True,
                })
            elif status == ActionStatus.PENDING_HITL and final_action:
                # Applique la dégradation gracieuse immédiate
                self.fleet_manager.dispatch_action(final_action)
                self.blocked_actions.append(action)
                decisions.append({
                    "action": action,
                    "mitigation": final_action,
                    "verdict": "BLOCKED_DEGRADED_HITL",
                    "executed": True,
                })

        return {
            "strategy": strategy,
            "decisions": decisions,
            "fleet_status": self.fleet_manager.get_fleet_summary(),
        }
