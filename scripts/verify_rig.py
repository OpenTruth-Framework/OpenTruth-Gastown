#!/usr/bin/env python3
"""
OpenTruth Target-Aware Verification CLI
---------------------------------------
This script is the "Lens" used by specialized Gastown agents (Gaugers & Spotters) 
to verify external repositories ("Rigs").

Unlike the Agent script (which looks at itself), this script looks at a *Target Path*.

Roles:
    - Gauger: Verifies Logic (Unit Tests, Scripts, Code Integrity)
    - Spotter: Verifies Perception (Visual Assets, Screenshots, Builds)

Usage:
    python verify_rig.py --target /path/to/rig --role gauger
    python verify_rig.py --target /path/to/rig --role spotter
"""

import argparse  # Standard library for parsing command-line arguments (flags like --target)
import json      # Standard library for handling JSON data
import datetime  # Standard library for timestamps
import os        # Standard library for file system navigation
import sys       # Standard library for system exit codes

# --- Configuration ---
# CENTRAL_PROOFS_DIR: The location of the "Truth Ledger" where all proofs are stored.
# In a Gastown setup, this script lives in `tools/opentruth/scripts/`.
# We assume the `data/truth_ledger` is located relative to the Town root.
# This logic navigates: scripts/ -> opentruth/ -> tools/ -> TownRoot/ -> data/truth_ledger/
# Note: Adjust verify_rig.py relative path logic if directory structure changes.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOWN_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../")) 
CENTRAL_PROOFS_DIR = os.path.join(TOWN_ROOT, "data/truth_ledger")

# Fallback: If we aren't in a standardized town structure, default to a local history/proofs
if not os.path.exists(CENTRAL_PROOFS_DIR):
    CENTRAL_PROOFS_DIR = os.path.abspath("history/proofs")

def log_proof(target, role, action, status, details):
    """
    Writes a 'Proof' to the Central Ledger.

    This function centralizes the history of the entire Town. Whether you are checking
    Rig A or Rig B, the proof lands here.

    Args:
        target (str): The path to the Rig being verified.
        role (str): The agent role performing the check (gauger/spotter).
        action (str): The specific check performed.
        status (str): "success" or "failure".
        details (dict): Technical details of the findings.
    """
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    # Extract just the folder name of the target (e.g., "aerobeat-feature-dance")
    # This keeps the log clean and readable.
    target_name = os.path.basename(os.path.abspath(target))

    proof = {
        "timestamp": timestamp,
        "agent": f"OpenTruth-{role.capitalize()}", # e.g., "OpenTruth-Gauger"
        "target_rig": target_name,
        "role": role,
        "action": action,
        "status": status,
        "details": details
    }
    
    # Ensure the central ledger directory exists
    os.makedirs(CENTRAL_PROOFS_DIR, exist_ok=True)
    
    # We segregate logs by role (gauger_log.jsonl vs spotter_log.jsonl)
    # This makes it easier for the "Witness" (Auditor) agent to review specific types of proofs.
    proof_file = os.path.join(CENTRAL_PROOFS_DIR, f"{role}_log.jsonl")
    
    with open(proof_file, "a") as f:
        f.write(json.dumps(proof) + "\n")
    
    print(f"📝 {role.capitalize()} Proof logged: {action} -> {status}")
    print(f"   📍 Location: {proof_file}")

def run_gauger(target_path):
    """
    The Gauger Workflow (Logic Verification).
    
    This function is responsible for ensuring the 'Left Brain' of the Rig is functional.
    It checks for:
    1. A .truth directory (The Spec)
    2. A tests directory (The Verification Logic)
    3. (Future) Runs the actual unit tests via Godot CLI
    
    Args:
        target_path (str): The absolute path to the Rig.
        
    Returns:
        bool: True if verification passes.
    """
    print(f"🔧 Gauger scanning: {target_path}")
    
    truth_dir = os.path.join(target_path, ".truth")
    tests_dir = os.path.join(target_path, "tests")
    
    findings = {
        "has_truth_dir": os.path.isdir(truth_dir),
        "has_tests_dir": os.path.isdir(tests_dir),
        "test_count": 0
    }
    
    # If tests exist, count them to give the human/agent more context
    if findings["has_tests_dir"]:
        # We look for .gd (Godot Script) files
        findings["test_count"] = len([f for f in os.listdir(tests_dir) if f.endswith('.gd')])
    
    # Validation Logic:
    # Strict Mode: Must have .truth AND .tests AND > 0 tests.
    # Relaxed Mode (Current): Just needs .truth and .tests folder presence.
    is_valid = findings["has_truth_dir"] and findings["has_tests_dir"]
    
    status = "success" if is_valid else "failure"
    log_proof(target_path, "gauger", "verify_logic", status, findings)
    return is_valid

def run_spotter(target_path):
    """
    The Spotter Workflow (Visual Verification).
    
    This function is responsible for ensuring the 'Right Brain' of the Rig is correct.
    It checks for:
    1. A .truth directory (The Spec)
    2. Reference Images (.png/.jpg) inside that directory
    3. (Future) Compares build screenshots against these references.
    
    Args:
        target_path (str): The absolute path to the Rig.
        
    Returns:
        bool: True if verification passes.
    """
    print(f"👀 Spotter scanning: {target_path}")
    
    truth_dir = os.path.join(target_path, ".truth")
    
    findings = {
        "has_truth_dir": os.path.isdir(truth_dir),
        "reference_images": []
    }
    
    if findings["has_truth_dir"]:
        # Find all image files that serve as 'Visual Truths'
        findings["reference_images"] = [f for f in os.listdir(truth_dir) if f.endswith(('.png', '.jpg'))]
    
    # Validation Logic:
    # Must have .truth folder AND at least one reference image to verify against.
    is_valid = findings["has_truth_dir"] and len(findings["reference_images"]) > 0
    
    status = "success" if is_valid else "failure"
    log_proof(target_path, "spotter", "verify_visual", status, findings)
    return is_valid

def main():
    """
    CLI Entry Point.
    Parses arguments -> Dispatches to correct Role Function -> Exits with Status Code.
    """
    parser = argparse.ArgumentParser(description='OpenTruth Verification CLI')
    
    # --target: Mandatory. Which folder are we checking?
    parser.add_argument('--target', required=True, help='Path to the Rig/Repo to verify')
    
    # --role: Mandatory. Who is checking it? (Gauger/Logic vs Spotter/Visual)
    parser.add_argument('--role', choices=['gauger', 'spotter'], required=True, help='Agent Role (Gauger=Logic, Spotter=Visual)')
    
    args = parser.parse_args()
    
    # Validate Target Existence
    if not os.path.exists(args.target):
        print(f"❌ Target path not found: {args.target}")
        sys.exit(1)

    # Dispatch based on Role
    success = False
    if args.role == 'gauger':
        success = run_gauger(args.target)
    elif args.role == 'spotter':
        success = run_spotter(args.target)
        
    # Exit Handling
    if not success:
        print(f"❌ {args.role.capitalize()} verification failed for {args.target}")
        sys.exit(1)
        
    print(f"✅ {args.role.capitalize()} verification passed!")

if __name__ == "__main__":
    main()
