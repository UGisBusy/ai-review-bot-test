"""Render a review report as a Markdown PR comment.

A report is a dict like the one in sample_report.json. Its "criteria" list
holds one result per point in criteria.json:

    {"id": "...", "status": "pass" | "fail" | "n/a",
     "explanation": "...", "requested_change": "..."}

The score gives each part an equal share of 100 points, split evenly among
the part's points. Points marked "n/a" don't count.
"""

import json
from pathlib import Path

CRITERIA_FILE = Path(__file__).with_name("criteria.json")

# Hidden marker so a later version can find and edit this comment
# instead of posting a new one.
MARKER = "<!-- pr-bot-report -->"

ICONS = {"pass": "✅", "fail": "❌", "n/a": "➖"}


def load_parts():
    return json.loads(CRITERIA_FILE.read_text(encoding="utf-8"))["parts"]


def _applicable(part, results):
    return [p for p in part["points"] if results[p["id"]]["status"] != "n/a"]


def _passed(points, results):
    return sum(1 for p in points if results[p["id"]]["status"] == "pass")


def compute_score(parts, results):
    share = 100 / len(parts)
    score = 0.0
    for part in parts:
        applicable = _applicable(part, results)
        if not applicable:
            score += share
            continue
        score += share * _passed(applicable, results) / len(applicable)
    return round(score)


def render(report):
    parts = load_parts()
    results = {c["id"]: c for c in report["criteria"]}

    expected = {p["id"] for part in parts for p in part["points"]}
    missing = expected - results.keys()
    if missing:
        raise ValueError(f"Report has no result for: {', '.join(sorted(missing))}")

    score = compute_score(parts, results)
    failed = any(results[i]["status"] == "fail" for i in expected)
    verdict = "Changes requested" if failed else "Ready for human review"

    lines = [
        MARKER,
        f"## 🤖 PR review: {score}/100 · {verdict}",
        "",
        f"Reviewed commit `{report['head_sha'][:7]}` · requested by `{report['requested_by']}`",
        "",
        "| Part | Point | Result |",
        "|---|---|:-:|",
    ]

    for part in parts:
        applicable = _applicable(part, results)
        tally = f" ({_passed(applicable, results)}/{len(applicable)})" if applicable else ""
        for i, point in enumerate(part["points"]):
            title = f"**{part['title']}**{tally}" if i == 0 else ""
            icon = ICONS[results[point["id"]]["status"]]
            lines.append(f"| {title} | {point['label']} | {icon} |")

    if failed:
        lines += ["", "### What to fix"]
        for part in parts:
            fails = [p for p in part["points"] if results[p["id"]]["status"] == "fail"]
            if not fails:
                continue
            lines += ["", f"**{part['title']}**", ""]
            for point in fails:
                result = results[point["id"]]
                lines.append(f"- [ ] **{point['label']}:** {result['explanation']}")
                if result.get("requested_change"):
                    lines.append(f"  - Suggested: {result['requested_change']}")

    lines += [
        "",
        "---",
        "<sub>This bot only advises. A maintainer decides whether to merge. "
        "After you push a fix, ask a maintainer to comment <code>/review</code> again.</sub>",
    ]
    return "\n".join(lines)
