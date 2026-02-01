# 🏙️ OpenTruth for Gastown
> **Status:** Alpha | **Target:** Gastown Swarms & Polyrepos

This repository contains the infrastructure tools required to integrate the **OpenTruth Framework** into a Gastown orchestrated environment. It enables specialized agents (**Gaugers** and **Spotters**) to verify the state of multiple repositories ("Rigs") against their local `.truth` definitions.

---

## 🏗 Architecture

In a Gastown Polyrepo, OpenTruth operates as a centralized service:

```text
Town-Root/
├── tools/
│   └── opentruth/           # <--- This Repo installed here
├── data/
│   └── truth_ledger/        # <--- Centralized Proofs (JSONL)
├── Rig-A/
│   ├── .truth/              # <--- Local Specs (Logic/Assets)
│   └── src/
└── Rig-B/
    ├── .truth/
    └── src/
```

---

## 🛠 Usage

### 1. Installation
Clone this repository into your Town's `tools/` directory:
```bash
mkdir -p tools
git clone https://github.com/OpenTruth-Framework/OpenTruth-Gastown tools/opentruth
```

### 2. Orchestration
Add the specialized roles to your `Formula.toml` (see `gastown-orchestration/` for templates).

### 3. Verification
Agents running as **Gaugers** (Logic) or **Spotters** (Visual) will use the CLI to verify Rigs:

```bash
# Gauger: Checks unit tests & logic
python tools/opentruth/scripts/verify_rig.py --target ./Rig-A --role gauger

# Spotter: Checks visual assets (.png)
python tools/opentruth/scripts/verify_rig.py --target ./Rig-A --role spotter
```

---

## 📂 Contents

*   **`scripts/verify_rig.py`**: The "Target-Aware" verification CLI.
*   **`gastown-orchestration/`**: Templates for `Formula.toml` and Agent Prompts.
*   **`bin/`**: Additional utility scripts.
