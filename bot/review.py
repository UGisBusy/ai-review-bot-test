# Dummy review script.
#
# Builds a dummy result for every point in criteria.json and prints the
# rendered PR comment on stdout. The workflow posts that output as a PR comment.
#
# Points with an entry in sample_report.json use that entry. Any other point,
# for example one just added to criteria.json, passes with a placeholder text.
# The real checks and the Claude API call replace this later.


import json
import os
import sys
from pathlib import Path

from report import load_parts, render

SAMPLE_FILE = Path(__file__).with_name("sample_report.json")


def dummy_results(parts, samples):
    results = []
    for part in parts:
        for point in part["points"]:
            results.append(
                samples.get(
                    point["id"],
                    {
                        "id": point["id"],
                        "status": "pass",
                        "explanation": "Not checked yet (dummy).",
                        "requested_change": "",
                    },
                )
            )
    return results


sample = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
samples = {c["id"]: c for c in sample["criteria"]}

report = {
    "pr": int(os.environ.get("PR_NUMBER", sample["pr"])),
    "head_sha": sample["head_sha"],
    "requested_by": os.environ.get("REQUESTED_BY", sample["requested_by"]),
    "criteria": dummy_results(load_parts(), samples),
}

# The comment contains emoji; make sure stdout can encode them on any OS.
sys.stdout.reconfigure(encoding="utf-8")
print("> ⚠️ **Dummy data:** the checks are not implemented yet.\n")
print(render(report))
