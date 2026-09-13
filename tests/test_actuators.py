"""Unit tests for Fleet Actuators and Edge Node Daemon."""

import pytest
from aegis_swarm.models import (
    Node,
    NodeRole,
    NodeTier,
    NodeStatus,
    ProposedAction,
    ActionType,
    ActionStatus,
)
from aegis_swarm.fleet.node import NodeInstance
from aegis_swarm.fleet.actuators.simulated import SimulatedActuator
from aegis_swarm.fleet.actuators.local_os import LocalOSActuator
from aegis_swarm.fleet.actuators.agent_actuator import AgentActuator
from aegis_agent.daemon import NodeState


def test_simulated_actuator_actions():
    node = Node(id="n1", name="srv1", ip="10.0.0.1", role=NodeRole.DMZ_WEB, tier=NodeTier.TIER_1)
    actuator = SimulatedActuator()

    act_block = ProposedAction(
        action_type=ActionType.BLOCK_IP,
        target_node_id="n1",
        parameters={"ip": "1.2.3.4"},
        justification="test",
        status=ActionStatus.ALLOWED,
    )
    res = actuator.apply_action(act_block, node)
    assert res.success is True
    assert "[MOCK]" in res.command_executed

    act_isolate = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="n1",
        parameters={},
        justification="test",
        status=ActionStatus.ALLOWED,
    )
    res2 = actuator.apply_action(act_isolate, node)
    assert res2.success is True
    assert node.status == NodeStatus.ISOLATED


def test_local_os_actuator_dry_run():
    node = Node(id="n-local", name="localhost", ip="127.0.0.1", role=NodeRole.WORKSTATION, tier=NodeTier.TIER_2)
    actuator = LocalOSActuator(dry_run=True)

    # Test Block IP command generation
    act_block = ProposedAction(
        action_type=ActionType.BLOCK_IP,
        target_node_id="n-local",
        parameters={"ip": "198.51.100.99"},
        justification="block test",
        status=ActionStatus.ALLOWED,
    )
    res = actuator.apply_action(act_block, node)
    assert res.success is True
    assert res.dry_run is True
    assert "198.51.100.99" in res.command_executed

    # Test Kill Process command generation
    act_kill = ProposedAction(
        action_type=ActionType.KILL_PROCESS,
        target_node_id="n-local",
        parameters={"process_name": "malware.exe"},
        justification="kill test",
        status=ActionStatus.ALLOWED,
    )
    res_kill = actuator.apply_action(act_kill, node)
    assert res_kill.success is True
    assert "malware.exe" in res_kill.command_executed


def test_agent_daemon_state_dry_run():
    state = NodeState(dry_run=True)
    assert state.status == "healthy"

    # Action block_ip
    res = state.execute_action("block_ip", {"ip": "203.0.113.10"})
    assert res["success"] is True
    assert "203.0.113.10" in state.blocked_ips
    assert "203.0.113.10" in res["command"]

    # Action quarantine_port
    res_port = state.execute_action("quarantine_port", {"port": 8080})
    assert res_port["success"] is True
    assert 8080 in state.quarantined_ports
    assert state.status == "quarantined"

    # Flush rules
    flushed = state.flush_aegis_rules()
    assert len(flushed) >= 1
    assert state.status == "healthy"
    assert len(state.blocked_ips) == 0


def test_un_isolate_simulated():
    node = Node(id="n-sim", name="srv-sim", ip="10.0.0.5", role=NodeRole.WORKSTATION, tier=NodeTier.TIER_2)
    actuator = SimulatedActuator()
    instance = NodeInstance(node=node, actuator=actuator)

    # Isolate
    act_iso = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="n-sim",
        parameters={},
        justification="test",
        status=ActionStatus.ALLOWED,
    )
    instance.apply_action(act_iso)
    assert instance.status == NodeStatus.ISOLATED

    # Un-isolate
    act_un = ProposedAction(
        action_type=ActionType.UN_ISOLATE_NODE,
        target_node_id="n-sim",
        parameters={},
        justification="test un_isolate",
        status=ActionStatus.ALLOWED,
    )
    instance.apply_action(act_un)
    assert instance.status == NodeStatus.HEALTHY


def test_local_os_actuator_selective_isolation():
    node = Node(id="n-loc", name="localhost", ip="127.0.0.1", role=NodeRole.WORKSTATION, tier=NodeTier.TIER_2)
    actuator = LocalOSActuator(dry_run=True)

    # Test Isolate with subnet calculation
    act_iso = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="n-loc",
        parameters={"soc_ip": "192.168.1.50"},
        justification="selective isolate",
        status=ActionStatus.ALLOWED,
    )
    res = actuator.apply_action(act_iso, node)
    assert res.success is True
    assert node.status == NodeStatus.ISOLATED
    assert "192.168.1.0/24" in res.command_executed
    assert "8443" in res.command_executed

    # Test Un-isolate
    act_un = ProposedAction(
        action_type=ActionType.UN_ISOLATE_NODE,
        target_node_id="n-loc",
        parameters={},
        justification="release",
        status=ActionStatus.ALLOWED,
    )
    res_un = actuator.apply_action(act_un, node)
    assert res_un.success is True
    assert node.status == NodeStatus.HEALTHY


def test_local_os_actuator_multi_nic():
    node = Node(id="n-server", name="hpe-srv", ip="10.10.10.5", role=NodeRole.DMZ_WEB, tier=NodeTier.TIER_1)
    actuator = LocalOSActuator(dry_run=True)

    act_iso = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="n-server",
        parameters={"mgmt_interface": "eno2", "prod_interface": "eno1"},
        justification="multi-nic isolate",
        status=ActionStatus.ALLOWED,
    )
    res = actuator.apply_action(act_iso, node)
    assert res.success is True
    assert node.status == NodeStatus.ISOLATED
    assert "eno1" in res.command_executed
    assert "eno2" not in res.command_executed  # Mgmt NIC must NOT be touched

    act_un = ProposedAction(
        action_type=ActionType.UN_ISOLATE_NODE,
        target_node_id="n-server",
        parameters={"mgmt_interface": "eno2", "prod_interface": "eno1"},
        justification="multi-nic restore",
        status=ActionStatus.ALLOWED,
    )
    res_un = actuator.apply_action(act_un, node)
    assert res_un.success is True
    assert node.status == NodeStatus.HEALTHY
    assert "eno1" in res_un.command_executed


def test_agent_daemon_selective_isolation_subnet_24():
    state = NodeState(dry_run=True)

    # Calling from 192.168.1.75 -> Should whitelist 192.168.1.0/24
    res = state.execute_action("isolate_node", {}, caller_ip="192.168.1.75")
    assert res["success"] is True
    assert state.status == "isolated"
    assert state.is_isolated is True
    assert "192.168.1.0/24" in res["command"]
    assert "8443" in res["command"]

    # Un-isolate
    res_un = state.execute_action("un_isolate", {})
    assert res_un["success"] is True
    assert state.status == "healthy"
    assert state.is_isolated is False


def test_agent_daemon_dead_man_switch():
    import time
    state = NodeState(dry_run=True)

    # Auto-release in 0.1s
    res = state.execute_action("isolate_node", {"auto_release_timeout": 0.1}, caller_ip="10.0.0.15")
    assert res["success"] is True
    assert state.status == "isolated"
    assert state.is_isolated is True

    # Wait for timer to expire
    time.sleep(0.2)
    assert state.status == "healthy"
    assert state.is_isolated is False


@pytest.fixture
def running_daemon():
    import threading
    from aegis_agent.daemon import ThreadedHTTPServer, AgentHTTPHandler

    state = NodeState(dry_run=True)
    token = "test-secret-token"
    AgentHTTPHandler.state = state
    AgentHTTPHandler.expected_token = token

    httpd = ThreadedHTTPServer(("127.0.0.1", 0), AgentHTTPHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    yield base_url, token, state

    httpd.shutdown()
    httpd.server_close()


def test_daemon_http_auth_and_validation(running_daemon):
    import urllib.request
    import urllib.error
    import json

    base_url, token, state = running_daemon

    # 1. Missing Auth Header -> 401
    req_no_auth = urllib.request.Request(
        f"{base_url}/action",
        data=json.dumps({"action_type": "block_ip"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req_no_auth)
    assert exc_info.value.code == 401

    # 2. Invalid Token -> 401
    req_bad_token = urllib.request.Request(
        f"{base_url}/action",
        data=json.dumps({"action_type": "block_ip"}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer wrong-token"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as exc_info_token:
        urllib.request.urlopen(req_bad_token)
    assert exc_info_token.value.code == 401

    # 3. Valid Token but Missing action_type -> 400
    req_missing_type = urllib.request.Request(
        f"{base_url}/action",
        data=json.dumps({"parameters": {}}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as exc_info_missing:
        urllib.request.urlopen(req_missing_type)
    assert exc_info_missing.value.code == 400


def test_daemon_http_reset_and_public_endpoints(running_daemon):
    import urllib.request
    import json

    base_url, token, state = running_daemon

    # 1. GET /health without auth -> 200
    with urllib.request.urlopen(f"{base_url}/health") as resp:
        assert resp.status == 200
        health_data = json.loads(resp.read().decode("utf-8"))
        assert health_data["status"] == "healthy"
        assert "hostname" in health_data
        assert health_data["dry_run"] is True

    # 2. GET /telemetry without auth -> 200
    with urllib.request.urlopen(f"{base_url}/telemetry") as resp:
        assert resp.status == 200
        telemetry_data = json.loads(resp.read().decode("utf-8"))
        assert telemetry_data["status"] == "healthy"
        assert "history" in telemetry_data

    # 3. Trigger action block_ip
    req_action = urllib.request.Request(
        f"{base_url}/action",
        data=json.dumps({"action_type": "block_ip", "parameters": {"ip": "198.51.100.77"}}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req_action) as resp:
        assert resp.status == 200
        assert "198.51.100.77" in state.blocked_ips

    # 4. POST /reset -> cleans rules and restores healthy status
    req_reset = urllib.request.Request(
        f"{base_url}/reset",
        headers={"Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req_reset) as resp:
        assert resp.status == 200
        reset_data = json.loads(resp.read().decode("utf-8"))
        assert reset_data["status"] == "healthy"
        assert len(state.blocked_ips) == 0


def test_agent_actuator_end_to_end_http(running_daemon):
    base_url, token, state = running_daemon
    actuator = AgentActuator(agent_url=base_url, token=token)

    # 1. Check health
    health = actuator.check_health()
    assert health is not None
    assert health["status"] == "healthy"

    node = Node(id="n-phys-test", name="server-edge-01", ip="192.168.1.80", role=NodeRole.WORKSTATION, tier=NodeTier.TIER_2)

    # 2. Apply ISOLATE_NODE
    act_iso = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="n-phys-test",
        parameters={},
        justification="isolate edge",
        status=ActionStatus.ALLOWED,
    )
    res_iso = actuator.apply_action(act_iso, node)
    assert res_iso.success is True
    assert node.status == NodeStatus.ISOLATED
    assert state.status == "isolated"
    assert state.is_isolated is True

    # 3. Apply UN_ISOLATE_NODE
    res_un = actuator.un_isolate_node(node)
    assert res_un.success is True
    assert node.status == NodeStatus.HEALTHY
    assert state.status == "healthy"
    assert state.is_isolated is False

    # 4. Dedicated reset_node()
    assert actuator.reset_node() is True


def test_agent_actuator_resilience():
    # Use an unallocated port to simulate network failure / daemon down
    actuator = AgentActuator(agent_url="http://127.0.0.1:59999", token="dummy-token", timeout=0.5)

    assert actuator.check_health() is None
    assert actuator.reset_node() is False

    node = Node(id="n-offline", name="server-down", ip="192.168.1.99", role=NodeRole.WORKSTATION, tier=NodeTier.TIER_2)
    act = ProposedAction(
        action_type=ActionType.BLOCK_IP,
        target_node_id="n-offline",
        parameters={"ip": "1.2.3.4"},
        justification="test offline resilience",
        status=ActionStatus.ALLOWED,
    )
    res = actuator.apply_action(act, node)
    assert res.success is False
    assert "Impossible de joindre l'agent distant" in res.error


