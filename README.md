# 🏙️ OpenTruth for Gastown
> **Status:** Alpha | **Target:** Gastown Swarms & Polyrepos

This repository contains the infrastructure tools required to integrate the **OpenTruth Framework** into a Gastown orchestrated environment. It enables specialized agents (**Gaugers**, **Spotters**, and **Watchdogs**) to verify the state of multiple repositories ("Rigs") against their local `.truth` definitions.

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
│   ├── .truth/              # <--- Local Specs & Hooks
│   │   ├── verify_logic.sh  # <--- Implementation (e.g., Godot CLI)
│   │   ├── verify_visual.py # <--- Implementation (e.g., ImageMagick)
│   │   └── verify_security.sh # <--- Implementation (e.g., Semgrep)
│   └── src/
└── Rig-B/
    ├── .truth/
    └── src/
```

---

## 🛠 Usage

OpenTruth follows an **Inversion of Control** model. The Framework provides the *Protocol* (Logging, Roles), but the **Town Developer** provides the *Implementation*.

### 1. Verification Hooks (The Contract)
Each Rig must provide executable scripts in its `.truth/` directory. These are just templates—you define what tools run inside them!

*   **Logic Verification (Gauger):** `.truth/verify_logic`
    *   *Purpose:* Unit tests, Syntax checks.
    *   *Recommended Tools:* `godot --run-tests`, `npm test`, `cargo test`.
*   **Visual Verification (Spotter):** `.truth/verify_visual`
    *   *Purpose:* Asset integrity, UI regression.
    *   *Recommended Tools:* `imagemagick` (compare), `perceptual-diff`, custom Python CV scripts.
*   **Security Verification (Watchdog):** `.truth/verify_security`
    *   *Purpose:* Vulnerability scanning, Secret detection.
    *   *Recommended Tools:* `bandit` (Python), `semgrep`, `gitleaks`.

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
*   **`gastown-orchestration/`**: **Template** configuration files.
    *   `Formula.toml`: Example role definitions.
    *   `agent-prompts.md`: Example system prompts.
*   **`bin/`**: Additional utility scripts.
