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
