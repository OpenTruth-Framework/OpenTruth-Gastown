#!/usr/bin/env python3
"""
OpenTruth-to-Bead Converter (Adapter)
-------------------------------------
This script acts as an "Adapter" between the OpenTruth Framework and the Gastown Data Plane.

Purpose:
    When an OpenTruth agent (Gauger/Spotter) generates a raw finding (e.g., "Tests Passed"),
    this script wraps that finding into a standardized "Bead" format that the Gastown
    Refinery/Witness agents can consume.

    It effectively turns a "Log Entry" into a "Data Packet" for the swarm.

Usage:
    # Pipe raw OpenTruth JSON output into this script
    echo '{"status": "success"}' | python ot_to_bead.py
"""

import json  # Standard library for parsing and formatting JSON
import sys   # Standard library for reading from Stdin

def convert_to_bead(ot_output):
    """
    Wraps a raw OpenTruth output dictionary into a Gastown Bead.

    Args:
        ot_output (dict): The raw dictionary output from verify_rig.py (e.g., findings).

    Returns:
        str: A JSON-formatted string representing the fully formed Bead.
    """
    
    # Construct the Bead Structure
    # This schema must match what the Gastown 'Witness' agent expects.
    bead = {
        "type": "verification_bead",       # Identifies this packet as a Verification Result
        "source": "opentruth_framework",   # The provenance of the data
        "payload": ot_output,              # The actual data (findings, status, details)
        "integrity": "verified_by_ot"      # A simple flag (could be a hash in the future)
    }
    
    # Return the JSON string representation
    return json.dumps(bead)

def main():
    """
    Main Entry Point.
    Reads JSON from Stdin -> Converts to Bead -> Prints JSON to Stdout.
    """
    try:
        # Read all input from Standard Input (Stdin)
        # This allows the script to be part of a pipeline: `cmd | this_script`
        input_data = sys.stdin.read()
        
        if not input_data:
            return # Exit silently if no input

        # Parse the input string into a Python dictionary
        ot_output = json.loads(input_data)
        
        # Perform the conversion
        bead_json = convert_to_bead(ot_output)
        
        # Output the result to Standard Output (Stdout)
        print(bead_json)
        
    except json.JSONDecodeError:
        # Handle cases where the input isn't valid JSON
        sys.stderr.write("❌ Error: Input was not valid JSON.\n")
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        sys.stderr.write(f"❌ Error during conversion: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
