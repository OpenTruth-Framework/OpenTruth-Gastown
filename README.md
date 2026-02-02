# 🏙️ OpenTruth for Gastown
> **Status:** Alpha | **Target:** Gastown Swarms & Polyrepos

This repository contains the infrastructure tools required to integrate the **OpenTruth Framework** into a Gastown orchestrated environment. It enables specialized agents (ex: **Gaugers** and **Spotters**) to verify the state of multiple repositories ("Rigs") against their local `.truth` definitions.

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
│   │   ├── verify_logic.sh  # <--- Implementation (e.g., Godot CLI)
│   │   └── verify_visual.py # <--- Implementation (e.g., Screenshot Compare)
│   └── src/
└── Rig-B/
    ├── .truth/
    └── src/
```

---

## 🛠 Usage

OpenTruth follows an **Inversion of Control** model. This means that the OpenTruth-Framework provides the *Protocol*, but each Rig in a town provides the *Implementation*.

### 1. Verification Hooks (The Contract)
Each Rig must provide executable scripts in its `.truth/` directory:

*   **Logic Verification (Gauger):** `.truth/verify_logic` (or `.sh`, `.py`)
    *   *Example:* Runs `godot --run-tests` or `npm test`.
*   **Visual Verification (Spotter):** `.truth/verify_visual`
    *   *Example:* Runs a screenshot comparison script.

### 2. Execution
Agents run the standard CLI, which finds and executes the Rig's specific hook:

```bash
# Gauger finds and runs .truth/verify_logic
python tools/opentruth/scripts/verify_rig.py --target ./Rig-A --role gauger
```

The CLI captures the hook's `Exit Code`, `Stdout`, and `Stderr` and logs it to the central ledger.

---

## 📂 Contents

*   **`scripts/verify_rig.py`**: The "Target-Aware" verification CLI (Delegator).
*   **`gastown-orchestration/`**: Templates for `Formula.toml` and Agent Prompts.
*   **`bin/`**: Additional utility scripts.
