"""Swarm Strategist: cross-node correlation and defense strategy planning."""

import json
import re
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
    """Moteur d'analyse globale corrélant les alertes de flotte avec NVIDIA NIM."""

    def __init__(self, nim_client: Optional[NIMClient] = None):
        self.nim_client = nim_client or NIMClient()

    def build_prompt(self, fleet_status: Dict[str, str], alerts: List[SecurityAlert]) -> List[Dict[str, str]]:
        """Construit le prompt système et utilisateur pour l'IA NIM."""
        system_prompt = (
            "Tu es le Cerveau Stratégique d'Aegis-Swarm (Sovereign Swarm Defense) propulsé par NVIDIA NIM. "
            "Ton rôle est d'analyser la télémétrie de toute la flotte d'entreprise, d'anticiper les attaques latérales "
            "et de produire une stratégie de défense au format JSON strict.\n"
            "Format attendu (réponds UNIQUEMENT ce JSON valide sans texte additionnel) :\n"
            "{\n"
            '  "strategy_id": "strat-unique-id",\n'
            '  "correlated_threat": "Description synthétique de la menace globale",\n'
            '  "anticipated_target_id": "node-id-cible-potentielle",\n'
            '  "actions": [\n'
            '    {\n'
            '      "action_type": "isolate_node|quarantine_port|block_ip|kill_process",\n'
            '      "target_node_id": "id_du_noeud",\n'
            '      "parameters": {},\n'
            '      "justification": "Raison tactique",\n'
            '      "status": "proposed"\n'
            '    }\n'
            '  ]\n'
            "}"
        )
        
        alerts_summary = "\n".join(
            [f"- [{a.severity.value.upper()}] Node: {a.node_id} | Alerte: {a.description}" for a in alerts]
        )
        fleet_summary = "\n".join([f"- Nœud {name}: Statut {status}" for name, status in fleet_status.items()])
        
        user_content = (
            f"=== ÉTAT DE LA FLOTTE ===\n{fleet_summary}\n\n"
            f"=== ALERTES RÉCENTES ===\n{alerts_summary}\n\n"
            "Analyse la corrélation entre ces alertes, prédis la prochaine cible et fournis le plan de remédiation en JSON strict."
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def _extract_json(self, raw_text: str) -> dict:
        """Extrait proprement le JSON même si le modèle a produit du texte ou du markdown."""
        clean = raw_text.strip()
        # 1. Essai direct
        try:
            return json.loads(clean)
        except Exception:
            pass

        # 2. Bloc ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        # 3. Première accolade ouvrante jusqu'à la dernière accolade fermante
        start = clean.find('{')
        end = clean.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(clean[start:end+1])
            except Exception:
                pass

        # 4. Fallback si tronqué : tenter de fermer les accolades
        if start != -1:
            snippet = clean[start:]
            for closing in ['"} ] }', '" } ] }', ' } ] }', ' ] }', ' }']:
                try:
                    return json.loads(snippet + closing)
                except Exception:
                    continue

        raise ValueError(f"Impossible d'extraire un JSON valide : {clean[:200]}")

    def analyze_fleet(self, fleet_status: Dict[str, str], alerts: List[SecurityAlert]) -> SwarmStrategy:
        """Analyse l'état de la flotte et les alertes pour produire une stratégie défensive."""
        if not alerts:
            return SwarmStrategy(
                strategy_id="strat-idle",
                correlated_threat="Aucune menace active",
                actions=[]
            )
        prompt = self.build_prompt(fleet_status, alerts)
        res_text = self.nim_client.chat_completion(prompt)
        try:
            res_dict = self._extract_json(res_text)
            return SwarmStrategy(**res_dict)
        except Exception:
            # Sécurité supplémentaire : si le parsing échoue, construire une stratégie minimale
            return SwarmStrategy(
                strategy_id=f"strat-nim-{int(datetime.now(timezone.utc).timestamp())}",
                correlated_threat=f"Analyse IA heuristique : {alerts[0].description}",
                anticipated_target_id=alerts[0].node_id,
                actions=[
                    ProposedAction(
                        action_type=ActionType.QUARANTINE_PORT,
                        target_node_id=alerts[0].node_id,
                        parameters={"port": 80},
                        justification="Mesure conservatoire automatique suite à alerte.",
                        status=ActionStatus.PROPOSED
                    )
                ]
            )
