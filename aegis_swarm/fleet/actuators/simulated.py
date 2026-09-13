"""Simulated in-memory actuator for tests and offline hackathon demos."""

from aegis_swarm.models import Node, NodeStatus, ProposedAction, ActionType
from aegis_swarm.fleet.actuators.base import BaseActuator, ExecutionResult


class SimulatedActuator(BaseActuator):
    """Actionneur simulé en mémoire, sans impact sur le système d'exploitation réel."""

    def apply_action(self, action: ProposedAction, node: Node) -> ExecutionResult:
        act_type = action.action_type

        if act_type == ActionType.ISOLATE_NODE:
            node.status = NodeStatus.ISOLATED
            return ExecutionResult(
                success=True,
                action_type=act_type,
                command_executed="[MOCK] iptables -F && iptables -P INPUT DROP",
                output="Node isolation simulated successfully in memory",
            )
        elif act_type == ActionType.UN_ISOLATE_NODE:
            node.status = NodeStatus.HEALTHY
            return ExecutionResult(
                success=True,
                action_type=act_type,
                command_executed="[MOCK] iptables -D INPUT -j DROP && iptables -P INPUT ACCEPT",
                output="Node un-isolation simulated successfully in memory",
            )
        elif act_type == ActionType.QUARANTINE_PORT:
            port = action.parameters.get("port", 3306)
            node.status = NodeStatus.QUARANTINED
            return ExecutionResult(
                success=True,
                action_type=act_type,
                command_executed=f"[MOCK] iptables -I INPUT -p tcp --dport {port} -j DROP",
                output=f"Port {port} quarantine simulated successfully",
                metadata={"port": port},
            )
        elif act_type == ActionType.BLOCK_IP:
            ip = action.parameters.get("ip", "198.51.100.42")
            return ExecutionResult(
                success=True,
                action_type=act_type,
                command_executed=f"[MOCK] iptables -I INPUT -s {ip} -j DROP",
                output=f"IP {ip} block simulated successfully",
                metadata={"ip": ip},
            )
        elif act_type == ActionType.KILL_PROCESS:
            process = action.parameters.get("process_name", "malware.exe")
            return ExecutionResult(
                success=True,
                action_type=act_type,
                command_executed=f"[MOCK] pkill -9 {process}",
                output=f"Process {process} termination simulated successfully",
                metadata={"process_name": process},
            )

        return ExecutionResult(
            success=False,
            action_type=act_type,
            error=f"Action type {act_type} not supported by SimulatedActuator",
        )
