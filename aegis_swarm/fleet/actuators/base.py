"""Abstract Base Actuator for physical and virtual nodes."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from aegis_swarm.models import Node, ProposedAction, ActionType


class ExecutionResult(BaseModel):
    """Résultat technique détaillé de l'exécution d'une action défensive."""
    success: bool
    action_type: ActionType
    command_executed: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    dry_run: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseActuator(ABC):
    """Interface unifiée pour tous les actionneurs (Simulation, OS Local, Daemon Edge HTTP)."""

    @abstractmethod
    def apply_action(self, action: ProposedAction, node: Node) -> ExecutionResult:
        """Exécute l'action défensive sur le nœud et retourne le résultat technique."""
        pass
