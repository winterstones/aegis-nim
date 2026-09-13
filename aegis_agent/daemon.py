"""Standalone Edge Node Daemon for physical and virtual machines.
Zero external dependencies: uses Python standard library only.
Compatible with Windows, Linux, and macOS.
"""

import sys
import os
import json
import socket
import platform
import subprocess
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

DEFAULT_TOKEN = "aegis-sovereign-token"


def compute_subnet_24(ip: str) -> str:
    """Calcule le sous-réseau /24 d'une adresse IPv4 ou renvoie 127.0.0.1 pour le loopback."""
    if not ip or ip in ("127.0.0.1", "localhost", "::1"):
        return "127.0.0.1"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    return ip


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class NodeState:
    """État local du nœud physique et historique des actions."""
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.os_type = platform.system().lower()
        self.hostname = socket.gethostname()
        self.ip_address = self._get_local_ip()
        self.status = "healthy"
        self.is_isolated: bool = False
        self.isolated_interface: Optional[str] = None
        self.release_timer: Optional[threading.Timer] = None
        self.isolation_rules: List[str] = []
        self.blocked_ips: List[str] = []
        self.quarantined_ports: List[int] = []
        self.applied_rules: List[str] = []
        self.action_history: List[Dict[str, Any]] = []

    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def execute_action(self, action_type: str, parameters: Dict[str, Any], caller_ip: Optional[str] = None) -> Dict[str, Any]:
        """Applique une action défensive sur le système local."""
        cmd = ""
        success = False
        output = ""
        error = None

        if action_type == "block_ip":
            ip = parameters.get("ip", "198.51.100.42")
            if self.os_type == "windows":
                rule_name = f"Aegis_Block_{ip.replace('.', '_')}"
                cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
            else:
                rule_name = f"Aegis_Block_{ip}"
                cmd = f"iptables -I INPUT -s {ip} -j DROP"

            res = self._run_command(cmd)
            success = res["success"]
            output = res["output"]
            error = res["error"]
            if success:
                self.blocked_ips.append(ip)
                self.applied_rules.append(rule_name)

        elif action_type == "quarantine_port":
            port = parameters.get("port", 3306)
            if self.os_type == "windows":
                rule_name = f"Aegis_Quarantine_Port_{port}"
                cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block protocol=TCP localport={port}'
            else:
                rule_name = f"Aegis_Quarantine_Port_{port}"
                cmd = f"iptables -I INPUT -p tcp --dport {port} -j DROP"

            res = self._run_command(cmd)
            success = res["success"]
            output = res["output"]
            error = res["error"]
            if success:
                self.quarantined_ports.append(port)
                self.applied_rules.append(rule_name)
                self.status = "quarantined"

        elif action_type == "kill_process":
            proc = parameters.get("process_name", "malware.exe")
            if self.os_type == "windows":
                proc_arg = proc if "." in proc else f"{proc}.exe"
                cmd = f'taskkill /F /IM "{proc_arg}"'
            else:
                cmd = f"pkill -9 -f {proc}"

            res = self._run_command(cmd)
            success = res["success"]
            output = res["output"]
            error = res["error"]

        elif action_type == "isolate_node":
            soc_subnet = parameters.get("soc_subnet")
            soc_ip = parameters.get("soc_ip") or caller_ip
            if not soc_subnet:
                soc_subnet = compute_subnet_24(soc_ip or self.ip_address)

            mgmt_interface = parameters.get("mgmt_interface")
            prod_interface = parameters.get("prod_interface", "Ethernet" if self.os_type == "windows" else "eth0")
            auto_release_timeout = parameters.get("auto_release_timeout")

            if mgmt_interface:
                # Multi-NIC : Désactivation ciblée de la carte de production
                self.isolated_interface = prod_interface
                if self.os_type == "windows":
                    cmd = f'netsh interface set interface name="{prod_interface}" admin=disable'
                else:
                    cmd = f"ip link set {prod_interface} down"

                res = self._run_command(cmd)
                success = res["success"]
                output = res["output"]
                error = res["error"]
                if success:
                    self.status = "isolated"
                    self.is_isolated = True
            else:
                # Monocarte : Pare-feu sélectif avec whitelist du sous-réseau SOC sur port 8443
                allow_rule = f"Aegis_Isolate_Allow_SOC_{self.hostname}"
                block_rule = f"Aegis_Isolate_BlockAll_{self.hostname}"
                if self.os_type == "windows":
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

                res = self._run_command(cmd)
                success = res["success"]
                output = res["output"]
                error = res["error"]
                if success:
                    self.applied_rules.extend([allow_rule, block_rule])
                    self.isolation_rules.extend([allow_rule, block_rule])
                    self.status = "isolated"
                    self.is_isolated = True

            # Dead Man's Switch / Auto-release timer pour sécurité des tests temporaires
            if success and auto_release_timeout:
                try:
                    timeout_val = float(auto_release_timeout)
                    if self.release_timer:
                        self.release_timer.cancel()
                    self.release_timer = threading.Timer(timeout_val, self.un_isolate)
                    self.release_timer.daemon = True
                    self.release_timer.start()
                    output = (output + f" | [DEAD-MAN-SWITCH] Auto-release programmé dans {timeout_val}s").strip()
                except Exception as te:
                    error = f"Erreur timer auto-release : {te}"

        elif action_type == "un_isolate":
            res_un = self.un_isolate()
            cmd = res_un["command"]
            success = res_un["success"]
            output = res_un["output"]
            error = res_un["error"]

        else:
            return {
                "success": False,
                "command": None,
                "error": f"Type d'action inconnu : {action_type}",
            }

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "parameters": parameters,
            "command": cmd,
            "success": success,
            "output": output,
            "error": error,
            "dry_run": self.dry_run,
        }
        self.action_history.append(record)
        return record

    def un_isolate(self) -> Dict[str, Any]:
        """Lève l'isolement du nœud, rétablit les interfaces réseau et supprime les règles de confinement."""
        if self.release_timer:
            self.release_timer.cancel()
            self.release_timer = None

        cmds = []
        # 1. Rétablir interface Multi-NIC si désactivée
        if self.isolated_interface:
            if self.os_type == "windows":
                cmds.append(f'netsh interface set interface name="{self.isolated_interface}" admin=enable')
            else:
                cmds.append(f"ip link set {self.isolated_interface} up")
            self.isolated_interface = None

        # 2. Supprimer les règles pare-feu d'isolation
        to_remove = list(self.isolation_rules)
        for rule in to_remove:
            if self.os_type == "windows":
                cmds.append(f'netsh advfirewall firewall delete rule name="{rule}"')
            else:
                cmds.append(f"iptables -D INPUT -m comment --comment '{rule}' -j DROP")
            if rule in self.applied_rules:
                self.applied_rules.remove(rule)
            self.isolation_rules.remove(rule)

        if not cmds:
            if self.os_type == "windows":
                allow_rule = f"Aegis_Isolate_Allow_SOC_{self.hostname}"
                block_rule = f"Aegis_Isolate_BlockAll_{self.hostname}"
                cmds.append(f'netsh advfirewall firewall delete rule name="{allow_rule}" & netsh advfirewall firewall delete rule name="{block_rule}"')
            else:
                cmds.append("iptables -F")

        full_cmd = " && ".join(cmds)
        res = self._run_command(full_cmd)
        self.is_isolated = False
        self.status = "healthy"
        return {
            "success": res["success"],
            "command": full_cmd,
            "output": res["output"] or "Isolement levé avec succès, connectivité réseau rétablie.",
            "error": res["error"],
        }

    def flush_aegis_rules(self) -> List[str]:
        """Supprime toutes les règles pare-feu créées par Aegis pour réinitialiser la machine."""
        if self.release_timer:
            self.release_timer.cancel()
            self.release_timer = None

        if self.isolated_interface:
            if self.os_type == "windows":
                cmd = f'netsh interface set interface name="{self.isolated_interface}" admin=enable'
            else:
                cmd = f"ip link set {self.isolated_interface} up"
            if not self.dry_run:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
            self.isolated_interface = None

        removed = []
        for rule in list(self.applied_rules):
            if self.os_type == "windows":
                cmd = f'netsh advfirewall firewall delete rule name="{rule}"'
            else:
                cmd = f"iptables -D INPUT -m comment --comment '{rule}' -j DROP"

            if not self.dry_run:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
            removed.append(rule)

        self.applied_rules.clear()
        self.isolation_rules.clear()
        self.blocked_ips.clear()
        self.quarantined_ports.clear()
        self.is_isolated = False
        self.status = "healthy"
        return removed

    def _run_command(self, cmd: str) -> Dict[str, Any]:
        if self.dry_run:
            return {
                "success": True,
                "output": f"[DRY-RUN] Commande simulée : {cmd}",
                "error": None,
            }

        try:
            res = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "success": res.returncode == 0,
                "output": res.stdout.strip(),
                "error": res.stderr.strip() if res.returncode != 0 else None,
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
            }


class AgentHTTPHandler(BaseHTTPRequestHandler):
    state: NodeState = None
    expected_token: str = DEFAULT_TOKEN

    def _send_json(self, status_code: int, data: Dict[str, Any]):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def _check_auth(self) -> bool:
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:].strip()
        return token == self.expected_token

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ["/health", "/status", "/"]:
            data = {
                "hostname": self.state.hostname,
                "ip": self.state.ip_address,
                "os": self.state.os_type,
                "status": self.state.status,
                "dry_run": self.state.dry_run,
                "blocked_ips": self.state.blocked_ips,
                "quarantined_ports": self.state.quarantined_ports,
                "active_rules_count": len(self.state.applied_rules),
            }
            self._send_json(200, data)

        elif path == "/telemetry":
            data = {
                "hostname": self.state.hostname,
                "status": self.state.status,
                "history": self.state.action_history[-10:],
            }
            self._send_json(200, data)

        else:
            self._send_json(404, {"error": "Endpoint non trouvé"})

    def do_POST(self):
        if not self._check_auth():
            self._send_json(401, {"error": "Non autorisé : Token Bearer invalide"})
            return

        path = self.path.split("?")[0]

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"

        try:
            payload = json.loads(post_body)
        except Exception:
            payload = {}

        if path == "/action":
            action_type = payload.get("action_type")
            parameters = payload.get("parameters", {})
            if not action_type:
                self._send_json(400, {"error": "Paramètre 'action_type' manquant"})
                return

            caller_ip = self.client_address[0] if hasattr(self, "client_address") and self.client_address else "127.0.0.1"
            result = self.state.execute_action(action_type, parameters, caller_ip=caller_ip)
            status_code = 200 if result.get("success") else 500
            self._send_json(status_code, result)

        elif path == "/reset":
            flushed = self.state.flush_aegis_rules()
            self._send_json(200, {
                "message": "Toutes les règles de confinement Aegis ont été supprimées.",
                "flushed_rules": flushed,
                "status": self.state.status,
            })

        else:
            self._send_json(404, {"error": "Endpoint non trouvé"})

    def log_message(self, format, *args):
        # Désactive les logs HTTP intempestifs en console
        pass


def run_daemon(host: str = "0.0.0.0", port: int = 8443, token: str = DEFAULT_TOKEN, dry_run: bool = False):
    state = NodeState(dry_run=dry_run)
    AgentHTTPHandler.state = state
    AgentHTTPHandler.expected_token = token

    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, AgentHTTPHandler)

    mode_str = "[DRY-RUN]" if dry_run else "[LIVE REAL SYSTEM]"
    print(f"============================================================")
    print(f"  AEGIS-SWARM EDGE NODE DAEMON {mode_str}")
    print(f"============================================================")
    print(f"Hostname   : {state.hostname}")
    print(f"OS Natif   : {state.os_type.upper()}")
    print(f"IP Locale  : {state.ip_address}")
    print(f"Écoute sur : http://{host}:{port}")
    print(f"Token Auth : {token}")
    print(f"Endpoints  : GET /health | GET /telemetry | POST /action | POST /reset")
    print(f"Appuyez sur Ctrl+C pour arrêter.")
    print(f"============================================================\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du daemon. Restauration de l'état système...")
        state.flush_aegis_rules()
        httpd.server_close()
        print("Daemon arrêté proprement.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aegis-Swarm Standalone Edge Node Daemon")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute")
    parser.add_argument("--port", type=int, default=8443, help="Port d'écoute (défaut: 8443)")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Jeton Bearer secret d'authentification")
    parser.add_argument("--dry-run", action="store_true", help="Simule les commandes OS sans toucher au système")
    args = parser.parse_args()

    run_daemon(host=args.host, port=args.port, token=args.token, dry_run=args.dry_run)
