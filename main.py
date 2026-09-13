"""Interactive SOC Console for Aegis-Swarm."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from aegis_swarm.orchestrator import AegisSwarmOrchestrator
from simulate_fleet_attack import display_fleet_table, run_simulation

console = Console()


def main():
    orchestrator = AegisSwarmOrchestrator()

    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]AEGIS-SWARM : SOC Supervision Console[/bold cyan]\n"
            "[dim]Sovereign Swarm Defense Management | HPE & NVIDIA NIM[/dim]",
            border_style="cyan"
        ))

        display_fleet_table(orchestrator, "État de la Flotte en Temps Réel")

        console.print("[bold yellow]Menu des Actions :[/bold yellow]")
        console.print("  [1] Lancer la simulation d'attaque en 5 actes (Démo Hackathon)")
        console.print("  [2] Lancer la simulation en mode pas-à-pas (--step)")
        console.print("  [3] Réinitialiser la flotte au statut sain")
        console.print("  [q] Quitter la console")
        console.print()

        choice = Prompt.ask("Sélectionnez une option", choices=["1", "2", "3", "q"], default="1")

        if choice == "1":
            run_simulation(step_mode=False)
            Prompt.ask("\nAppuyez sur [Entrée] pour revenir au menu principal")
        elif choice == "2":
            run_simulation(step_mode=True)
            Prompt.ask("\nAppuyez sur [Entrée] pour revenir au menu principal")
        elif choice == "3":
            orchestrator = AegisSwarmOrchestrator()
            console.print("[green]Flotte réinitialisée avec succès ![/green]")
            import time
            time.sleep(1.0)
        elif choice == "q":
            console.print("[bold cyan]Fermeture de la console Aegis-Swarm. Veille souveraine active.[/bold cyan]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]Interruption utilisateur. Fin de session.[/dim]")
        sys.exit(0)
