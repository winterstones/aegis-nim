"""Unit tests for aegis_swarm.fleet."""

import pytest
from aegis_swarm.models import (
    Node,
    NodeRole,
    NodeTier,
    NodeStatus,
    ActionType,
    ActionStatus,
    ProposedAction,
)
from aegis_swarm.fleet.node import NodeInstance
from aegis_swarm.fleet.fleet_manager import FleetManager


@pytest.fixture
def sample_node_instance():
    node = Node(
        id="node-test-1",
        name="test-server",
        ip="10.0.0.1",
        role=NodeRole.DMZ_WEB,
        tier=NodeTier.TIER_1,
        status=NodeStatus.HEALTHY,
    )
    return NodeInstance(node)


def test_node_apply_isolate(sample_node_instance):
    action = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="node-test-1",
        justification="Isolate compromise",
    )
    result = sample_node_instance.apply_action(action)
    assert result is True
    assert sample_node_instance.status == NodeStatus.ISOLATED


def test_node_apply_quarantine_port(sample_node_instance):
    action = ProposedAction(
        action_type=ActionType.QUARANTINE_PORT,
        target_node_id="node-test-1",
        parameters={"port": 8080},
        justification="Block suspicious port",
    )
    result = sample_node_instance.apply_action(action)
    assert result is True
    assert 8080 in sample_node_instance.quarantined_ports
    assert sample_node_instance.status == NodeStatus.QUARANTINED


def test_fleet_manager_bootstrap_and_dispatch():
    manager = FleetManager.bootstrap_default_fleet()
    assert len(manager.nodes) == 3
    assert "node-web-1" in manager.nodes
    assert "node-db-1" in manager.nodes

    action = ProposedAction(
        action_type=ActionType.BLOCK_IP,
        target_node_id="node-web-1",
        parameters={"ip": "198.51.100.23"},
        justification="Block scanner",
    )
    success = manager.dispatch_action(action)
    assert success is True
    assert action.status == ActionStatus.EXECUTED
    assert "198.51.100.23" in manager.get_node("node-web-1").blocked_ips

    # Test unknown node
    bad_action = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="unknown-node-404",
        justification="Fail test",
    )
    assert manager.dispatch_action(bad_action) is False


def test_fleet_manager_register_physical_node():
    from aegis_swarm.fleet.actuators.local_os import LocalOSActuator
    from aegis_swarm.fleet.actuators.agent_actuator import AgentActuator

    manager = FleetManager()

    # 1. Local OS actuator registration
    inst_local = manager.register_physical_node(
        node_id="node-local-host",
        name="my-laptop",
        ip="127.0.0.1",
        role=NodeRole.WORKSTATION,
        tier=NodeTier.TIER_2,
        actuator_type="local",
        dry_run=True,
    )
    assert inst_local.id == "node-local-host"
    assert inst_local.node.metadata["physical"] is True
    assert isinstance(inst_local.actuator, LocalOSActuator)
    assert inst_local.actuator.dry_run is True
    assert manager.get_node("node-local-host") is inst_local

    # 2. Agent actuator registration
    inst_agent = manager.register_physical_node(
        node_id="node-edge-linux",
        name="asus-pn40",
        ip="192.168.1.105",
        role=NodeRole.DMZ_WEB,
        tier=NodeTier.TIER_1,
        actuator_type="agent",
        agent_url="http://192.168.1.105:8443",
        agent_token="my-token",
    )
    assert inst_agent.id == "node-edge-linux"
    assert isinstance(inst_agent.actuator, AgentActuator)
    assert inst_agent.actuator.agent_url == "http://192.168.1.105:8443"
    assert inst_agent.actuator.token == "my-token"


def test_fleet_manager_get_node_by_name():
    manager = FleetManager()
    node = Node(
        id="id-srv-1",
        name="host-datacenter-01",
        ip="10.0.0.10",
        role=NodeRole.DB_CORE,
        tier=NodeTier.TIER_0,
    )
    manager.register_node(NodeInstance(node))

    # Lookup by ID
    assert manager.get_node("id-srv-1") is not None
    assert manager.get_node("id-srv-1").name == "host-datacenter-01"

    # Lookup by Name
    assert manager.get_node("host-datacenter-01") is not None
    assert manager.get_node("host-datacenter-01").id == "id-srv-1"

    # Non-existent
    assert manager.get_node("non-existent") is None

