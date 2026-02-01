import json
import sys

def convert_to_bead(ot_output):
    # Logic to wrap OpenTruth JSON into a Gastown-compatible Bead
    bead = {
        "type": "verification_bead",
        "payload": ot_output,
        "integrity": "verified_by_ot"
    }
    return json.dumps(bead)

if __name__ == "__main__":
    # Integration logic here
    pass