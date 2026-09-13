"""Agent Actuator: communicates with a remote physical machine running aegis-daemon."""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from aegis_swarm.models import Node, NodeStatus, ProposedAction, ActionType, ActionStatus
from aegis_swarm.fleet.actuators.base import BaseActuator, ExecutionResult


class AgentActuator(BaseActuator):
    """Actionneur pilotant un nœud physique ou virtuel distant via son micro-agent HTTP."""

    def __init__(self, agent_url: str, token: str = "aegis-sovereign-token", timeout: float = 10.0):
        self.agent_url = agent_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def check_health(self) -> Optional[Dict[str, Any]]:
        """Interroge le endpoint /health de l'agent distant pour valider la connectivité."""
        url = f"{self.agent_url}/health"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None
        return None

    def apply_action(self, action: ProposedAction, node: Node) -> ExecutionResult:
        """Envoie l'ordre d'action défensive au micro-agent distant sur le serveur physique."""
        if action.action_type == ActionType.ISOLATE_NODE:
            if "soc_ip" not in action.parameters and "soc_subnet" not in action.parameters:
                try:
                    import socket
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    action.parameters["soc_ip"] = s.getsockname()[0]
                    s.close()
                except Exception:
                    action.parameters["soc_ip"] = "127.0.0.1"

        url = f"{self.agent_url}/action"
        payload = {
            "action_type": action.action_type.value,
            "parameters": action.parameters,
        }
        data_bytes = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                success = body.get("success", False)
                cmd = body.get("command")
                out = body.get("output")
                err = body.get("error")
                dry = body.get("dry_run", False)

                # Mettre à jour le statut du nœud
                if success:
                    if action.action_type == ActionType.ISOLATE_NODE:
                        node.status = NodeStatus.ISOLATED
                    elif action.action_type == ActionType.UN_ISOLATE_NODE:
                        node.status = NodeStatus.HEALTHY
                    elif action.action_type == ActionType.QUARANTINE_PORT:
                        node.status = NodeStatus.QUARANTINED

                return ExecutionResult(
                    success=success,
                    action_type=action.action_type,
                    command_executed=cmd,
                    output=out,
                    error=err,
                    dry_run=dry,
                    metadata=body,
                )
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8")
            return ExecutionResult(
                success=False,
                action_type=action.action_type,
                error=f"Erreur HTTP {he.code} de l'agent distant : {err_body}",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                action_type=action.action_type,
                error=f"Impossible de joindre l'agent distant sur {self.agent_url} : {e}",
            )

    def reset_node(self) -> bool:
        """Demande au micro-agent de supprimer les règles pare-feu temporaires."""
        url = f"{self.agent_url}/reset"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status == 200
        except Exception:
            return False

    def un_isolate_node(self, node: Node) -> ExecutionResult:
        """Envoie l'ordre de levée d'isolement au micro-agent distant pour restaurer le réseau."""
        action = ProposedAction(
            action_type=ActionType.UN_ISOLATE_NODE,
            target_node_id=node.id,
            parameters={},
            justification="Levée d'isolement ordonnée par le SOC",
            status=ActionStatus.ALLOWED,
        )
        return self.apply_action(action, node)

