"""Local OS Actuator: executes real defense commands on the host operating system."""

import os
import platform
import subprocess
from typing import Optional
from aegis_swarm.models import Node, NodeStatus, ProposedAction, ActionType
from aegis_swarm.fleet.actuators.base import BaseActuator, ExecutionResult


class LocalOSActuator(BaseActuator):
    """Actionneur exécutant de vraies commandes système sur l'hôte local (Windows ou Linux)."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.system = platform.system().lower()  # 'windows' ou 'linux' ou 'darwin'

    def _execute_command(self, cmd: str) -> ExecutionResult:
        """Exécute une commande système ou simule son exécution si dry_run est activé."""
        if self.dry_run:
            return ExecutionResult(
                success=True,
                action_type=ActionType.BLOCK_IP,  # Remplacé par l'appelant
                command_executed=cmd,
                output="[DRY-RUN] Commande simulée sans altération du système d'exploitation",
                dry_run=True,
            )

        try:
            shell_needed = self.system == "windows"
            res = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            success = res.returncode == 0
            return ExecutionResult(
                success=success,
                action_type=ActionType.BLOCK_IP,  # Remplacé par l'appelant
                command_executed=cmd,
                output=res.stdout.strip(),
                error=res.stderr.strip() if not success else None,
                dry_run=False,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                action_type=ActionType.BLOCK_IP,
                command_executed=cmd,
                error=f"Exception système lors de l'exécution : {e}",
                dry_run=False,
            )

    def apply_action(self, action: ProposedAction, node: Node) -> ExecutionResult:
        act_type = action.action_type

        if act_type == ActionType.BLOCK_IP:
            ip = action.parameters.get("ip", "198.51.100.42")
            if self.system == "windows":
                rule_name = f"Aegis_Block_{ip.replace('.', '_')}"
                cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
            else:
                cmd = f"iptables -I INPUT -s {ip} -j DROP"

            res = self._execute_command(cmd)
            res.action_type = act_type
            res.metadata = {"ip": ip, "system": self.system}
            return res

        elif act_type == ActionType.QUARANTINE_PORT:
            port = action.parameters.get("port", 3306)
            if self.system == "windows":
                rule_name = f"Aegis_Quarantine_Port_{port}"
                cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block protocol=TCP localport={port}'
            else:
                cmd = f"iptables -I INPUT -p tcp --dport {port} -j DROP"

            node.status = NodeStatus.QUARANTINED
            res = self._execute_command(cmd)
            res.action_type = act_type
            res.metadata = {"port": port, "system": self.system}
            return res

        elif act_type == ActionType.KILL_PROCESS:
            process = action.parameters.get("process_name", "malware.exe")
            if self.system == "windows":
                # Si pas d'extension .exe, l'ajouter pour taskkill
                proc_arg = process if "." in process else f"{process}.exe"
                cmd = f'taskkill /F /IM "{proc_arg}"'
            else:
                cmd = f"pkill -9 -f {process}"

            res = self._execute_command(cmd)
            res.action_type = act_type
            res.metadata = {"process_name": process, "system": self.system}
            return res

        elif act_type == ActionType.ISOLATE_NODE:
            soc_subnet = action.parameters.get("soc_subnet")
            soc_ip = action.parameters.get("soc_ip", "127.0.0.1")
            if not soc_subnet:
                parts = soc_ip.split(".")
                soc_subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24" if len(parts) == 4 and soc_ip != "127.0.0.1" else "127.0.0.1"

            mgmt_interface = action.parameters.get("mgmt_interface")
            prod_interface = action.parameters.get("prod_interface", "Ethernet" if self.system == "windows" else "eth0")

            if mgmt_interface:
                if self.system == "windows":
                    cmd = f'netsh interface set interface name="{prod_interface}" admin=disable'
                else:
                    cmd = f"ip link set {prod_interface} down"
            else:
                if self.system == "windows":
                    allow_rule = "Aegis_Isolate_Allow_SOC"
                    block_rule = "Aegis_Isolate_BlockAll"
                    cmd = (
                        f'netsh advfirewall firewall add rule name="{allow_rule}" dir=in action=allow '
                        f'protocol=TCP localport=8443 remoteip={soc_subnet},127.0.0.1 && '
                        f'netsh advfirewall firewall add rule name="{block_rule}" dir=in action=block'
                    )
                else:
                    cmd = (
                        f"iptables -I INPUT -s {soc_subnet} -p tcp --dport 8443 -j ACCEPT && "
                        f"iptables -I INPUT -i lo -j ACCEPT && "
                        f"iptables -A INPUT -j DROP"
                    )

            node.status = NodeStatus.ISOLATED
            res = self._execute_command(cmd)
            res.action_type = act_type
            res.metadata = {"system": self.system, "soc_subnet": soc_subnet, "mgmt_interface": mgmt_interface}
            return res

        elif act_type == ActionType.UN_ISOLATE_NODE:
            mgmt_interface = action.parameters.get("mgmt_interface")
            prod_interface = action.parameters.get("prod_interface", "Ethernet" if self.system == "windows" else "eth0")

            if mgmt_interface:
                if self.system == "windows":
                    cmd = f'netsh interface set interface name="{prod_interface}" admin=enable'
                else:
                    cmd = f"ip link set {prod_interface} up"
            else:
                if self.system == "windows":
                    cmd = 'netsh advfirewall firewall delete rule name="Aegis_Isolate_Allow_SOC" & netsh advfirewall firewall delete rule name="Aegis_Isolate_BlockAll"'
                else:
                    cmd = "iptables -D INPUT -p tcp --dport 8443 -j ACCEPT; iptables -D INPUT -j DROP"

            node.status = NodeStatus.HEALTHY
            res = self._execute_command(cmd)
            res.action_type = act_type
            res.metadata = {"system": self.system}
            return res

        return ExecutionResult(
            success=False,
            action_type=act_type,
            error=f"Action type {act_type} non supporté par LocalOSActuator",
            dry_run=self.dry_run,
        )
