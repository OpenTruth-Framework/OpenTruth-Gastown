# Gastown Agent Integration Guide

This document defines how Gastown agents (Gaugers, Spotters) utilize the OpenTruth Framework.

## 1. Additional Agent Roles

- **The Gauger (Logic Verifier):** Responsible for executing unit tests and verifying logical truth via `verify_rig.py --role gauger`.
- **The Spotter (Visual Verifier):** Responsible for comparing visual assets/builds against `.truth` references via `verify_rig.py --role spotter`.
- **The Watchdog (Security Auditor):** Scans rigs for vulnerabilities and policy violations.

## 2. Proof Formatting

Agents MUST encapsulate OpenTruth findings in a JSONL proof format:
{
  "timestamp": "ISO-8601",
  "agent": "OpenTruth-Gauger",
  "target_rig": "aerobeat-feature-dance",
  "role": "gauger",
  "action": "verify_logic",
  "status": "success",
  "details": { ... }
}

## 3. Tool Hooks

Integration should be handled via Gastown Hooks. Before any `git commit` in the data plane:

1. Trigger `scripts/verify_rig.py` on the staged content.
2. If OpenTruth returns a failure, the commit is aborted.

### Command Line Usage for Agents

Agents should use the following syntax to communicate with the OpenTruth engine:

| Role | Command |
| :--- | :--- |
| **Gauger** | `python scripts/verify_rig.py --target /path/to/rig --role gauger` |
| **Spotter** | `python scripts/verify_rig.py --target /path/to/rig --role spotter` |