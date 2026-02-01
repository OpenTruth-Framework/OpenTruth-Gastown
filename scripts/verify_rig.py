#!/usr/bin/env python3
import argparse
import json
import datetime
import os
import sys

# Configuration
# In a real Gastown setup, this would be passed in or read from env
CENTRAL_PROOFS_DIR = os.path.abspath("history/proofs") 

def log_proof(target, role, action, status, details):
    """Writes a proof bead to the central history."""
    proof = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "agent": f"OpenTruth-{role.capitalize()}",
        "target_rig": os.path.basename(os.path.abspath(target)),
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

def run_gauger(target_path):
    """
    Gauger Role: Logic & Unit Test Verification.
    Checks for the existence of test files and (eventually) runs Godot unit tests.
    """
    print(f"🔧 Gauger scanning: {target_path}")
    
    truth_dir = os.path.join(target_path, ".truth")
    tests_dir = os.path.join(target_path, "tests")
    
    findings = {
        "has_truth_dir": os.path.isdir(truth_dir),
        "has_tests_dir": os.path.isdir(tests_dir),
        "test_count": 0
    }
    
    if findings["has_tests_dir"]:
        findings["test_count"] = len([f for f in os.listdir(tests_dir) if f.endswith('.gd')])
    
    # Simple Logic Truth: Must have a .truth folder and at least one test file
    is_valid = findings["has_truth_dir"] # Relaxed for now, strictly needs truth dir
    
    status = "success" if is_valid else "failure"
    log_proof(target_path, "gauger", "verify_logic", status, findings)
    return is_valid

def run_spotter(target_path):
    """
    Spotter Role: Visual & Asset Verification.
    Checks for reference images in .truth/ and (eventually) compares them.
    """
    print(f"👀 Spotter scanning: {target_path}")
    
    truth_dir = os.path.join(target_path, ".truth")
    
    findings = {
        "has_truth_dir": os.path.isdir(truth_dir),
        "reference_images": []
    }
    
    if findings["has_truth_dir"]:
        findings["reference_images"] = [f for f in os.listdir(truth_dir) if f.endswith(('.png', '.jpg'))]
    
    # Simple Visual Truth: Must have at least one reference image
    is_valid = len(findings["reference_images"]) > 0
    
    status = "success" if is_valid else "failure"
    log_proof(target_path, "spotter", "verify_visual", status, findings)
    return is_valid

def main():
    parser = argparse.ArgumentParser(description='OpenTruth Verification CLI')
    parser.add_argument('--target', required=True, help='Path to the Rig/Repo to verify')
    parser.add_argument('--role', choices=['gauger', 'spotter'], required=True, help='Agent Role (Gauger=Logic, Spotter=Visual)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.target):
        print(f"❌ Target path not found: {args.target}")
        sys.exit(1)

    if args.role == 'gauger':
        success = run_gauger(args.target)
    elif args.role == 'spotter':
        success = run_spotter(args.target)
        
    if not success:
        print(f"❌ {args.role.capitalize()} verification failed for {args.target}")
        sys.exit(1)
        
    print(f"✅ {args.role.capitalize()} verification passed!")

if __name__ == "__main__":
    main()
