#!/usr/bin/env python3
"""
OpenTruth CLI - Gastown Edition
-------------------------------
This Command Line Interface (CLI) is a utility wrapper designed for the Gastown Swarm.

While the primary verification work (Logic & Vision) is handled by `verify_rig.py` 
for the Gauger and Spotter roles, this CLI provides *ad-hoc utility functions* 
that any agent in the swarm might need during an investigation.

Intended Use Cases:
-------------------
1. **Ad-Hoc Verification:** A 'Truth-Scout' agent finds a claim on the web and needs to 
   verify it against known facts.
2. **Asset Scanning:** A 'Watchdog' agent finds a suspicious file and needs to 
   scan its metadata for manipulation.

Extension Guide (For Developers):
---------------------------------
To add a new capability (e.g., "Deepfake Detection"):
1. Define a new sub-parser in the `main()` function (e.g., `deepfake_parser`).
2. Add the corresponding logic block in the `if/elif` dispatch section.
3. Ensure the output supports the `--proof` flag to emit a JSON object compatible 
   with the Gastown Data Plane.

Usage Examples:
---------------
    # Human-Readable Output (for debugging):
    python opentruth_cli.py verify "The sky is green"

    # Machine-Readable Output (for piping to Data Plane):
    python opentruth_cli.py verify "The sky is green" --proof
"""

import argparse  # Standard library for parsing command-line arguments.
                 # This handles flags like --proof and commands like 'verify'.
import json      # Standard library for handling JSON data.
                 # Crucial for structured communication between agents.
import sys       # Standard library for system-level operations (exit codes).

def main():
    """
    Main Entry Point.
    Sets up the argument parser and dispatches commands to their logic handlers.
    """
    
    # 1. Setup the Argument Parser
    # description: Shown when the user runs the tool with --help
    parser = argparse.ArgumentParser(description='OpenTruth Framework CLI - Gastown Edition')
    
    # We use 'subparsers' to create distinct commands (like git commit, git push)
    subparsers = parser.add_subparsers(dest='command', help='Operational Commands')

    # --- Command: Verify ---
    # Purpose: Verifies a text string or claim against the Town's knowledge base.
    # Logic Location: See "Logic Dispatch" section below.
    verify_parser = subparsers.add_parser('verify', help='Verify a textual claim')
    verify_parser.add_argument('input', help='The string input to verify')
    verify_parser.add_argument('--proof', action='store_true', help='Output in Gastown Proof format (JSON)')

    # --- Command: Scan ---
    # Purpose: Scans a file path for metadata anomalies or manipulation.
    # Logic Location: See "Logic Dispatch" section below.
    scan_parser = subparsers.add_parser('scan', help='Scan a file for anomalies')
    scan_parser.add_argument('file', help='The file path to scan')
    scan_parser.add_argument('--proof', action='store_true', help='Output in Gastown Proof format (JSON)')

    # Parse the arguments provided by the user/agent
    args = parser.parse_args()

    # --- Logic Dispatch ---
    # This section routes the command to the actual code that performs the work.

    if args.command == 'verify':
        # [PLACEHOLDER LOGIC]
        # In a real implementation, this would call a library or API to check facts.
        # For now, we return a mocked success result.
        result = {
            "status": "success", 
            "score": 0.9, 
            "message": f"Claim '{args.input}' verified against internal knowledge base."
        }
        
        # Output Handling
        if args.proof:
            # If --proof is requested, wrap the result in a standard envelope.
            # This allows the 'ot_to_bead.py' script to ingest it easily.
            print(json.dumps({"type": "proof", "payload": result}))
        else:
            # Otherwise, print pretty JSON for human readability.
            print(json.dumps(result, indent=2))

    elif args.command == 'scan':
        # [PLACEHOLDER LOGIC]
        # In a real implementation, this would use a library like 'exiftool' or a ML model.
        result = {
            "status": "clean", 
            "metadata": {"format": "png", "layers": 1},
            "file": args.file
        }
        
        # Output Handling
        if args.proof:
            print(json.dumps({"type": "proof", "payload": result}))
        else:
            print(json.dumps(result, indent=2))
    
    else:
        # If no command was matched (or none provided), print the help text.
        parser.print_help()

# --- Execution Check ---
# This ensures the main() function runs only when executed as a script,
# not when imported as a module.
if __name__ == '__main__':
    main()
