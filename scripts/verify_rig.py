#!/usr/bin/env python3
"""
OpenTruth Target-Aware Verification CLI (Delegator Mode)
--------------------------------------------------------
This script is the primary "Protocol Wrapper" for Gastown Agents (Gaugers, Spotters, & Watchdogs).

In a Polyrepo architecture (like Gastown), a central tool cannot know the specifics of every Rig.
Some Rigs use Godot, others use React, others use Rust.

Instead of hardcoding verification logic here, this script **delegates** the responsibility 
to the Target Rig itself using the "Inversion of Control" pattern.

The Protocol (The Contract):
----------------------------
1. **The Rig's Responsibility:**
   Every Rig MUST provide executable scripts in its `.truth/` directory matching the role names:
   - `.truth/verify_logic`    (for Gaugers: runs unit tests)
   - `.truth/verify_visual`   (for Spotters: compares screenshots)
   - `.truth/verify_security` (for Watchdogs: scans for vulnerabilities)

2. **The Framework's Responsibility (This Script):**
   - Locates the correct script for the requested Role.
   - Executes it within the context of the Rig.
   - Captures the Exit Code, Standard Output (stdout), and Standard Error (stderr).
   - Wraps this data into a JSONL Proof.
   - Commits the Proof to the Central Town Ledger.

Usage:
------
    python verify_rig.py --target /path/to/rig --role gauger
    python verify_rig.py --target /path/to/rig --role spotter
    python verify_rig.py --target /path/to/rig --role watchdog
"""

import argparse     # Standard library for parsing command-line flags (e.g., --target)
import json         # Standard library for creating structured data logs
import datetime     # Standard library for accurate timestamping (UTC)
import os           # Standard library for file system navigation
import sys          # Standard library for system exit codes
import subprocess   # Standard library for running external commands (the delegation part)

# --- Configuration Section ---

# We need to find where the "Central Ledger" lives. 
# Since this script lives in `tools/opentruth/scripts/`, we traverse up 3 levels to find the Town Root.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOWN_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../")) 
CENTRAL_PROOFS_DIR = os.path.join(TOWN_ROOT, "data/truth_ledger")

# Fallback: If the directory structure is non-standard (e.g. testing locally), fallback to a local folder.
if not os.path.exists(CENTRAL_PROOFS_DIR):
    CENTRAL_PROOFS_DIR = os.path.abspath("history/proofs")

def log_proof(target, role, action, status, details):
    """
    Logs the execution result to the Central Ledger.
    
    This function creates an immutable record of what happened. It is the "Truth" 
    that other agents (like the Auditor) will read later.

    Args:
        target (str): The path to the Rig being verified.
        role (str): The agent role (gauger, spotter, watchdog).
        action (str): The specific action (e.g., "delegate_gauger").
        status (str): "success" (exit code 0) or "failure".
        details (dict): The technical output (stdout, stderr, exit_code).
    """
    # Use UTC time to avoid timezone confusion across distributed teams.
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    
    # We use the folder name (e.g., "Rig-A") as the identifier.
    target_name = os.path.basename(os.path.abspath(target))

    proof = {
        "timestamp": timestamp,
        "agent": f"OpenTruth-{role.capitalize()}", # e.g. OpenTruth-Watchdog
        "target_rig": target_name,
        "role": role,
        "action": action,
        "status": status,
        "details": details
    }
    
    # Create the ledger directory if it doesn't exist (Lazy Initialization)
    os.makedirs(CENTRAL_PROOFS_DIR, exist_ok=True)
    
    # Log to a role-specific file (e.g., watchdog_log.jsonl). 
    # This segregation helps human auditors focus on specific concerns.
    proof_file = os.path.join(CENTRAL_PROOFS_DIR, f"{role}_log.jsonl")
    
    with open(proof_file, "a") as f:
        f.write(json.dumps(proof) + "\n")
    
    print(f"📝 {role.capitalize()} Proof logged: {action} -> {status}")
    print(f"   📍 Location: {proof_file}")

def find_executable(truth_dir, base_name):
    """
    Helper function to find the correct script file.
    
    It supports multiple languages/extensions, checking them in order.
    The script MUST be marked as executable (chmod +x) to be picked up.

    Args:
        truth_dir (str): Path to the .truth folder.
        base_name (str): The expected script name (e.g., "verify_logic").

    Returns:
        str | None: The absolute path to the script, or None if not found.
    """
    # We check these extensions in priority order.
    # Empty string "" checks for a script with no extension (common in Linux).
    extensions = ["", ".sh", ".py", ".rb", ".js"]
    
    for ext in extensions:
        script_path = os.path.join(truth_dir, base_name + ext)
        # Check if file exists AND is executable by the user
        if os.path.isfile(script_path) and os.access(script_path, os.X_OK):
            return script_path
            
    return None

def run_delegated_check(target_path, role):
    """
    The Core Logic: Finds and runs the specific verification script for the role.
    
    Args:
        target_path (str): Path to the Rig.
        role (str): 'gauger', 'spotter', or 'watchdog'.
        
    Returns:
        bool: True if the delegated script exited with code 0 (Success).
    """
    print(f"🔎 {role.capitalize()} checking: {target_path}")
    
    truth_dir = os.path.join(target_path, ".truth")
    
    # Map the Role to the Script Name (The Protocol Contract)
    script_map = {
        "gauger": "verify_logic",
        "spotter": "verify_visual",
        "watchdog": "verify_security"
    }
    
    script_name = script_map.get(role)
    if not script_name:
        print(f"❌ Unknown role: {role}")
        return False
    
    # 1. Locate the Hook
    script_path = find_executable(truth_dir, script_name)
    
    if not script_path:
        # If the hook is missing, we fail the verification.
        # This enforces that Rigs MUST be verifiable to participate in the Town.
        error_msg = f"❌ No executable '{script_name}' found in {truth_dir}"
        print(error_msg)
        log_proof(target_path, role, f"delegate_{role}", "failure", {"error": "missing_hook", "msg": error_msg})
        return False
        
    print(f"🚀 Executing: {script_path}")
    
    # 2. Execute the Hook
    try:
        # subprocess.run is the safest way to execute external commands.
        # cwd=target_path: We switch the "Current Working Directory" to the Rig root.
        #   This is crucial! It allows the script to reference files relatively (e.g., ./tests/).
        # capture_output=True: We grab what the script prints so we can log it.
        result = subprocess.run(
            [script_path], 
            cwd=target_path, 
            capture_output=True,
            text=True
        )
        
        # Structure the details for the log
        details = {
            "hook": os.path.basename(script_path),
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(), # Trim whitespace
            "stderr": result.stderr.strip()
        }
        
        # Determine Status: 0 is the universal Unix code for "Success".
        status = "success" if result.returncode == 0 else "failure"
        
        # Log the Proof (This is the most important step!)
        log_proof(target_path, role, f"delegate_{role}", status, details)
        
        # Echo output to console so the calling Agent can see what happened immediately.
        if result.stdout: print(f"--- Output ---\n{result.stdout}")
        if result.stderr: print(f"--- Errors ---\n{result.stderr}")
        
        return result.returncode == 0

    except Exception as e:
        # Handle unexpected crashes (e.g., Permission Denied, OS Error)
        print(f"❌ Execution Error: {e}")
        log_proof(target_path, role, f"delegate_{role}", "error", {"error": str(e)})
        return False

def main():
    """
    CLI Entry Point.
    Parses arguments -> Dispatches to Delegator -> Exits with Status Code.
    """
    parser = argparse.ArgumentParser(description='OpenTruth Verification CLI (Delegator)')
    
    # --target: Mandatory. Which folder are we checking?
    parser.add_argument('--target', required=True, help='Path to the Rig/Repo to verify')
    
    # --role: Mandatory. Who is checking it? Added 'watchdog'.
    parser.add_argument('--role', choices=['gauger', 'spotter', 'watchdog'], required=True, help='Agent Role')
    
    args = parser.parse_args()
    
    # Pre-flight Check: Does the target exist?
    if not os.path.exists(args.target):
        print(f"❌ Target path not found: {args.target}")
        sys.exit(1)

    # Run the logic
    success = run_delegated_check(args.target, args.role)
        
    # Exit with appropriate code (0=Good, 1=Bad)
    if not success:
        print(f"❌ {args.role.capitalize()} verification failed.")
        sys.exit(1)
        
    print(f"✅ {args.role.capitalize()} verification passed!")

if __name__ == "__main__":
    main()
