"""Unit tests for aegis_swarm.models."""

import pytest
from aegis_swarm.models import (
    Node,
    NodeRole,
    NodeTier,
    NodeStatus,
    ActionType,
    ActionStatus,
    ProposedAction,
    SwarmStrategy,
    SecurityAlert,
    Severity,
)


def test_node_is_crown_jewel():
    db_node = Node(
        id="node-db-1",
        name="srv-db-core",
        ip="10.0.2.10",
        role=NodeRole.DB_CORE,
        tier=NodeTier.TIER_0,
    )
    assert db_node.is_crown_jewel() is True

    web_node = Node(
        id="node-web-1",
        name="srv-web-dmz",
        ip="192.168.1.10",
        role=NodeRole.DMZ_WEB,
        tier=NodeTier.TIER_1,
    )
    assert web_node.is_crown_jewel() is False


def test_proposed_action_is_destructive():
    destructive_action = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="node-db-1",
        justification="Attack detected, isolate completely",
    )
    assert destructive_action.is_destructive() is True

    soft_action = ProposedAction(
        action_type=ActionType.BLOCK_IP,
        target_node_id="node-web-1",
        parameters={"ip": "198.51.100.23"},
        justification="Block attacker IP on firewall",
    )
    assert soft_action.is_destructive() is False


def test_swarm_strategy_has_critical_actions():
    action_soft = ProposedAction(
        action_type=ActionType.QUARANTINE_PORT,
        target_node_id="node-web-1",
        parameters={"port": 8080},
        justification="Isolate suspicious port",
    )
    strategy_safe = SwarmStrategy(
        strategy_id="strat-001",
        correlated_threat="Port scanning",
        actions=[action_soft],
    )
    assert strategy_safe.has_critical_actions() is False

    action_hard = ProposedAction(
        action_type=ActionType.ISOLATE_NODE,
        target_node_id="node-db-1",
        justification="Emergency shutdown",
    )
    strategy_critical = SwarmStrategy(
        strategy_id="strat-002",
        correlated_threat="Lateral exfiltration",
        actions=[action_soft, action_hard],
    )
    assert strategy_critical.has_critical_actions() is True
