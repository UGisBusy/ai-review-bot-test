"""Dummy review script.

Prints a placeholder review as Markdown on stdout. The workflow posts that
output as a PR comment. The real checks and the Claude API call replace this
later.
"""

import os

pr_number = os.environ.get("PR_NUMBER", "?")
requested_by = os.environ.get("REQUESTED_BY", "unknown")

print(f"""## PR review bot (dummy)

Review of PR #{pr_number}, requested by `{requested_by}`.

**Score:** 0 / 100 (placeholder)

The workflow works. Real checks come next.""")
