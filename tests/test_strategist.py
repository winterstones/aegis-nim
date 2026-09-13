"""Unit tests for aegis_swarm.brain."""

import pytest
from aegis_swarm.models import (
    SecurityAlert,
    Severity,
    SwarmStrategy,
    ActionType,
)
from aegis_swarm.brain.nim_client import NIMClient
from aegis_swarm.brain.strategist import SwarmStrategist


def test_nim_client_mock_response():
    client = NIMClient(api_key="mock-key")
    assert client.mock_mode is True

    messages = [
        {"role": "system", "content": "Test"},
        {"role": "user", "content": "Attaque détectée sur srv-web-dmz visant srv-db-core"},
    ]
    response = client.chat_completion(messages)
    assert "strat-nemotron-lateral-01" in response
    assert "isolate_node" in response


def test_swarm_strategist_empty_alerts():
    strategist = SwarmStrategist()
    strategy = strategist.analyze_fleet(fleet_status={}, alerts=[])
    assert isinstance(strategy, SwarmStrategy)
    assert len(strategy.actions) == 0


def test_swarm_strategist_analyze_fleet():
    strategist = SwarmStrategist()
    fleet_status = {
        "srv-web-dmz": "compromised",
        "srv-db-core": "healthy",
        "workstation-finances": "healthy",
    }
    alerts = [
        SecurityAlert(
            alert_id="alt-1",
            node_id="srv-web-dmz",
            severity=Severity.CRITICAL,
            description="Exfiltration attempt targeting srv-db-core",
        )
    ]
    strategy = strategist.analyze_fleet(fleet_status, alerts)
    assert isinstance(strategy, SwarmStrategy)
    assert strategy.anticipated_target_id == "node-db-1"
    assert len(strategy.actions) == 2
    assert strategy.has_critical_actions() is True
