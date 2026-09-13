"""Swarm Strategist: cross-node correlation and defense strategy planning."""

import json
from typing import Dict, List, Optional
from datetime import datetime, timezone
from aegis_swarm.models import (
    Node,
    SecurityAlert,
    ProposedAction,
    SwarmStrategy,
    ActionType,
    ActionStatus,
)
from aegis_swarm.brain.nim_client import NIMClient


class SwarmStrategist:
    """Moteur d'analyse globale corrélant les alertes de flotte avec NVIDIA Nemotron 70B."""

    def __init__(self, nim_client: Optional[NIMClient] = None):
        self.nim_client = nim_client or NIMClient()

    def build_prompt(self, fleet_status: Dict[str, str], alerts: List[SecurityAlert]) -> List[Dict[str, str]]:
        """Construit le prompt système et utilisateur pour Nemotron 70B."""
        system_prompt = (
            "Tu es le Cerveau Stratégique d'Aegis-Swarm (Sovereign Swarm Defense) propulsé par NVIDIA Nemotron 70B. "
            "Ton rôle est d'analyser la télémétrie de toute la flotte d'entreprise, d'anticiper les attaques latérales "
            "et de produire une stratégie de défense au format JSON strict."
        )
        
        alerts_summary = "\n".join(
            [f"- [{a.severity.value.upper()}] Node: {a.node_id} | Alerte: {a.description}" for a in alerts]
        )
        fleet_summary = "\n".join([f"- Nœud {name}: Statut {status}" for name, status in fleet_status.items()])
        
        user_content = (
            f"=== ÉTAT DE LA FLOTTE ===\n{fleet_summary}\n\n"
            f"=== ALERTES RÉCENTES ===\n{alerts_summary}\n\n"
            "Analyse la corrélation entre ces alertes, prédis la prochaine cible et fournis le plan de remédiation en JSON."
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def analyze_fleet(self, fleet_status: Dict[str, str], alerts: List[SecurityAlert]) -> SwarmStrategy:
        """Analyse l'état de la flotte et les alertes pour produire une stratégie défensive."""
        if not alerts:
            return SwarmStrategy(
                strategy_id="strat-idle",
                correlated_threat="Aucune menace active",
                actions=[]
            )
        prompt = self.build_prompt(fleet_status, alerts)
        res_json = self.nim_client.chat_completion(prompt)
        res = json.loads(res_json)
        return SwarmStrategy(**res)
