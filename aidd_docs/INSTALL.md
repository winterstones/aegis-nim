# INSTALL.md - Aegis-Swarm Tech Stack & Setup

> **Sovereign Enterprise Swarm Defense**  
> Hackathon HPE & NVIDIA Agentic AI for Enterprises (Geneva)

---

## 1. Vision & Architecture Pattern

- **Project:** Aegis-Swarm (`aegis-nim`)
- **Pattern:** Central Strategic Brain (NVIDIA NIM Nemotron 70B) + Policy Enforcement Gatekeeper (NVIDIA NeMo Guardrails) + Distributed Fleet Probe/Actuator Swarm.
- **Target Infra:** Sovereign on-premise / private cloud HPE GreenLake & NVIDIA accelerated computing.

---

## 2. Tech Stack

| Layer | Component | Version / Target |
|---|---|---|
| Runtime | Python | 3.11+ |
| Strategic LLM | NVIDIA NIM (`nvidia/llama-3.1-nemotron-70b-instruct`) | OpenAI API format |
| Guardrails & Safety | NVIDIA NeMo Guardrails | Colang (`.co`) + YAML |
| Data Schemas | Pydantic | v2 |
| Terminal UI | Rich | Latest |
| Testing | Pytest | Latest |

---

## 3. Prerequisites

1. **Python 3.11+** installed and available in `PATH`.
2. **NVIDIA API Key** (`NVAPI_KEY` or `NVIDIA_API_KEY`) from [build.nvidia.com](https://build.nvidia.com).
3. Git for version control.

---

## 4. Installation Steps

```bash
# 1. Create and activate virtual environment
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and enter your NVIDIA_API_KEY
```

---

## 5. Entry Points

- **Interactive SOC Console:** `python main.py`
- **Attack & Defense Swarm Simulation:** `python simulate_fleet_attack.py`
