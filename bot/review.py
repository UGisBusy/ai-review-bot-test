"""Dummy review script.

Renders the sample report as a Markdown PR comment on stdout. The workflow
posts that output as a PR comment. The real checks and the Claude API call
replace the sample data later.
"""

import json
import os
import sys
from pathlib import Path

from report import render

SAMPLE_FILE = Path(__file__).with_name("sample_report.json")

report = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
report["pr"] = int(os.environ.get("PR_NUMBER", report["pr"]))
report["requested_by"] = os.environ.get("REQUESTED_BY", report["requested_by"])

# The comment contains emoji; make sure stdout can encode them on any OS.
sys.stdout.reconfigure(encoding="utf-8")
print("> ⚠️ **Dummy data:** the checks are not implemented yet.\n")
print(render(report))
