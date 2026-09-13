"""Unified NVIDIA NIM client (OpenAI-compatible) with mock fallback."""

import json
from typing import Any, Dict, List, Optional
from openai import OpenAI
from config.settings import settings


class NIMClient:
    """Client for NVIDIA Inference Microservices (NIM)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.nvidia_api_key
        self.base_url = base_url or settings.nim_base_url
        self.model = model or settings.nim_model
        self.mock_mode = settings.mock_mode or (not self.api_key or self.api_key.startswith("mock") or self.api_key.startswith("nvapi-your"))

        if not self.mock_mode:
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        else:
            self.client = None

    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        """Envoie une requête d'inférence à NVIDIA NIM ou génère un mock structuré."""
        if not self.mock_mode and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                )
                return response.choices[0].message.content or "{}"
            except Exception as e:
                # Fallback gracieux en cas de panne réseau au Hackathon
                return self._generate_mock_response(messages)
        else:
            return self._generate_mock_response(messages)

    def _generate_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Réponse simulée réaliste de Nemotron 70B pour le scénario du Hackathon."""
        last_message = messages[-1]["content"] if messages else ""
        
        # Détection de pivot vers la base de données
        if "srv-web-dmz" in last_message and "srv-db-core" in last_message:
            mock_strategy = {
                "strategy_id": "strat-nemotron-lateral-01",
                "correlated_threat": "Tentative de pivot latéral détectée depuis la DMZ vers la base de données financière srv-db-core",
                "anticipated_target_id": "node-db-1",
                "actions": [
                    {
                        "action_type": "isolate_node",
                        "target_node_id": "node-db-1",
                        "parameters": {},
                        "justification": "Arrêt d'urgence préventif de la base de données financière pour empêcher l'exfiltration.",
                        "status": "proposed"
                    },
                    {
                        "action_type": "block_ip",
                        "target_node_id": "node-web-1",
                        "parameters": {"ip": "198.51.100.42"},
                        "justification": "Blocage de l'IP source sur le serveur web DMZ.",
                        "status": "proposed"
                    }
                ]
            }
            return json.dumps(mock_strategy)
        
        # Réponse générique par défaut
        return json.dumps({
            "strategy_id": "strat-generic-01",
            "correlated_threat": "Activité anormale détectée",
            "anticipated_target_id": None,
            "actions": []
        })
