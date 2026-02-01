#!/usr/bin/env python3
"""
OpenTruth Target-Aware Verification CLI (Delegator Mode)
--------------------------------------------------------
This script is the "Protocol Wrapper" for Gastown Agents (Gaugers & Spotters).

Instead of hardcoding verification logic (e.g., Godot vs React), this script 
**delegates** the verification to the target Rig itself.

The Contract:
    1. The Rig MUST provide executable scripts in its `.truth/` directory.
       - `.truth/verify_logic` (for Gaugers)
       - `.truth/verify_visual` (for Spotters)
    
    2. This script executes those hooks, captures the output, and wraps it 
       into a standardized JSONL Proof in the Town Ledger.

Usage:
    python verify_rig.py --target /path/to/rig --role gauger
    python verify_rig.py --target /path/to/rig --role spotter
"""

import argparse
import json
import datetime
import os
import sys
import subprocess

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOWN_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../")) 
CENTRAL_PROOFS_DIR = os.path.join(TOWN_ROOT, "data/truth_ledger")

# Fallback for non-standard layouts
if not os.path.exists(CENTRAL_PROOFS_DIR):
    CENTRAL_PROOFS_DIR = os.path.abspath("history/proofs")

def log_proof(target, role, action, status, details):
    """Logs the execution result to the Central Ledger."""
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    target_name = os.path.basename(os.path.abspath(target))

    proof = {
        "timestamp": timestamp,
        "agent": f"OpenTruth-{role.capitalize()}",
        "target_rig": target_name,
        "role": role,
        "action": action,
        "status": status,
        "details": details
    }
    
    os.makedirs(CENTRAL_PROOFS_DIR, exist_ok=True)
    proof_file = os.path.join(CENTRAL_PROOFS_DIR, f"{role}_log.jsonl")
    
    with open(proof_file, "a") as f:
        f.write(json.dumps(proof) + "\n")
    
    print(f"📝 {role.capitalize()} Proof logged: {action} -> {status}")
    print(f"   📍 Location: {proof_file}")

def find_executable(truth_dir, base_name):
    """
    Looks for an executable script with supported extensions.
    Priority: No extension -> .sh -> .py -> .rb -> .js
    """
    extensions = ["", ".sh", ".py", ".rb", ".js"]
    for ext in extensions:
        script_path = os.path.join(truth_dir, base_name + ext)
        if os.path.isfile(script_path) and os.access(script_path, os.X_OK):
            return script_path
    return None

def run_delegated_check(target_path, role):
    """
    Finds and runs the specific verification script for the role.
    
    Args:
        target_path (str): Path to the Rig.
        role (str): 'gauger' or 'spotter'.
        
    Returns:
        bool: True if the delegated script exited with code 0.
    """
    print(f"🔎 {role.capitalize()} checking: {target_path}")
    
    truth_dir = os.path.join(target_path, ".truth")
    script_name = "verify_logic" if role == "gauger" else "verify_visual"
    
    # 1. Locate the Hook
    script_path = find_executable(truth_dir, script_name)
    
    if not script_path:
        error_msg = f"❌ No executable '{script_name}' found in {truth_dir}"
        print(error_msg)
        log_proof(target_path, role, f"delegate_{role}", "failure", {"error": "missing_hook", "msg": error_msg})
        return False
        
    print(f"🚀 Executing: {script_path}")
    
    # 2. Execute the Hook
    try:
        # Run the script and capture output
        result = subprocess.run(
            [script_path], 
            cwd=target_path, # Run context is the Rig root
            capture_output=True,
            text=True
        )
        
        details = {
            "hook": os.path.basename(script_path),
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
        
        status = "success" if result.returncode == 0 else "failure"
        log_proof(target_path, role, f"delegate_{role}", status, details)
        
        # Echo output to console for the agent/user
        if result.stdout: print(f"--- Output ---\n{result.stdout}")
        if result.stderr: print(f"--- Errors ---\n{result.stderr}")
        
        return result.returncode == 0

    except Exception as e:
        print(f"❌ Execution Error: {e}")
        log_proof(target_path, role, f"delegate_{role}", "error", {"error": str(e)})
        return False

def main():
    parser = argparse.ArgumentParser(description='OpenTruth Verification CLI (Delegator)')
    parser.add_argument('--target', required=True, help='Path to the Rig/Repo to verify')
    parser.add_argument('--role', choices=['gauger', 'spotter'], required=True, help='Agent Role')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.target):
        print(f"❌ Target path not found: {args.target}")
        sys.exit(1)

    success = run_delegated_check(args.target, args.role)
        
    if not success:
        print(f"❌ {args.role.capitalize()} verification failed.")
        sys.exit(1)
        
    print(f"✅ {args.role.capitalize()} verification passed!")

if __name__ == "__main__":
    main()
