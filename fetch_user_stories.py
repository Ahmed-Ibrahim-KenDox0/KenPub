"""
Fetch User Stories with 10-20 story points from Azure DevOps backlog.

Source backlog:
  https://dev.azure.com/loboag/lobo.ecm8/_backlogs/backlog/lobo.ecm8%20Team/Stories

Filters applied:
  - WorkItemType : User Story
  - AreaPath     : lobo.ecm8
  - State        : New
  - AssignedTo   : @Me, _Unassigned_, or aibrahim@lobo.ag
  - IterationPath: @currentIteration, lobo.ecm8,
                   lobo.ecm8\\Feature Requests,
                   lobo.ecm8\\Not assigned yet
  - StoryPoints  : 10 – 20 (inclusive)
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error
from typing import Dict, List, Optional

ORGANIZATION = "loboag"
PROJECT = "lobo.ecm8"
TEAM = "lobo.ecm8 Team"
API_VERSION = "7.1"

# Azure DevOps REST API base URL
ADO_BASE = f"https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis"

# WIQL query that mirrors all filters present in the backlog URL and adds the
# story-points range requested in the issue.
WIQL_QUERY = f"""
SELECT
    [System.Id],
    [System.Title],
    [System.State],
    [System.AssignedTo],
    [System.IterationPath],
    [System.AreaPath],
    [Microsoft.VSTS.Scheduling.StoryPoints]
FROM WorkItems
WHERE
    [System.WorkItemType] = 'User Story'
    AND [System.AreaPath] = 'lobo.ecm8'
    AND [System.State] = 'New'
    AND [Microsoft.VSTS.Scheduling.StoryPoints] >= 10
    AND [Microsoft.VSTS.Scheduling.StoryPoints] <= 20
    AND (
        [System.AssignedTo] = @Me
        OR [System.AssignedTo] = ''
        OR [System.AssignedTo] = 'aibrahim@lobo.ag'
    )
    AND (
        [System.IterationPath] = @currentIteration('[{PROJECT}]\\{TEAM}')
        OR [System.IterationPath] = 'lobo.ecm8'
        OR [System.IterationPath] = 'lobo.ecm8\\Feature Requests'
        OR [System.IterationPath] = 'lobo.ecm8\\Not assigned yet'
    )
ORDER BY [Microsoft.VSTS.Common.BacklogPriority] ASC
""".strip()


def _build_auth_header(pat: str) -> str:
    """Return a Basic-auth header value from an Azure DevOps PAT."""
    token = base64.b64encode(f":{pat}".encode()).decode()
    return f"Basic {token}"


def _request(url: str, method: str = "GET", body: Optional[Dict] = None,
             headers: Optional[Dict] = None) -> Dict:
    """Minimal HTTP helper – returns parsed JSON or raises on error."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"HTTP {exc.code} from {url}: {body_text}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network error reaching {url}: {exc.reason}"
        ) from exc


def run_wiql(pat: str) -> List[int]:
    """Execute the WIQL query and return the matching work-item IDs."""
    url = f"{ADO_BASE}/wit/wiql?api-version={API_VERSION}"
    auth = _build_auth_header(pat)
    result = _request(
        url,
        method="POST",
        body={"query": WIQL_QUERY},
        headers={"Authorization": auth},
    )
    return [item["id"] for item in result.get("workItems", [])]


def get_work_items(pat: str, ids: List[int]) -> List[Dict]:
    """Fetch work-item details in batches of 200 (API limit)."""
    if not ids:
        return []

    fields = (
        "System.Id,"
        "System.Title,"
        "System.State,"
        "System.AssignedTo,"
        "System.IterationPath,"
        "System.AreaPath,"
        "Microsoft.VSTS.Scheduling.StoryPoints"
    )
    auth = _build_auth_header(pat)
    items: List[Dict] = []

    # The batch endpoint accepts at most 200 IDs at a time.
    for i in range(0, len(ids), 200):
        batch = ids[i : i + 200]
        ids_param = ",".join(str(x) for x in batch)
        url = (
            f"{ADO_BASE}/wit/workitems"
            f"?ids={ids_param}&fields={fields}&api-version={API_VERSION}"
        )
        result = _request(url, headers={"Authorization": auth})
        items.extend(result.get("value", []))

    return items


def print_table(items: List[Dict]) -> None:
    """Print results as a plain-text table."""
    if not items:
        print("No User Stories with 10–20 story points found.")
        return

    rows = []
    for item in items:
        f = item.get("fields", {})
        assigned = f.get("System.AssignedTo", {})
        # AssignedTo may be a string or an identity dict
        if isinstance(assigned, dict):
            assigned = assigned.get("displayName", "")
        rows.append(
            {
                "ID": f.get("System.Id", ""),
                "Title": f.get("System.Title", ""),
                "State": f.get("System.State", ""),
                "Assigned To": assigned or "(Unassigned)",
                "Story Points": int(f.get("Microsoft.VSTS.Scheduling.StoryPoints") or 0),
                "Iteration": f.get("System.IterationPath", ""),
            }
        )

    # Column widths
    col_order = ["ID", "Story Points", "State", "Assigned To", "Iteration", "Title"]
    widths = {col: len(col) for col in col_order}
    for row in rows:
        for col in col_order:
            widths[col] = max(widths[col], len(str(row[col])))

    sep = "+-" + "-+-".join("-" * widths[c] for c in col_order) + "-+"
    header = "| " + " | ".join(c.ljust(widths[c]) for c in col_order) + " |"

    label = "User Story" if len(rows) == 1 else "User Stories"
    print(f"\nFound {len(rows)} {label} with 10–20 story points:\n")
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "| " + " | ".join(str(row[c]).ljust(widths[c]) for c in col_order) + " |"
        print(line)
    print(sep)


def main() -> None:
    pat = os.environ.get("AZURE_DEVOPS_PAT", "").strip()
    if not pat:
        print(
            "Error: set the AZURE_DEVOPS_PAT environment variable to your "
            "Azure DevOps Personal Access Token (needs 'Work Items (Read)' scope).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Querying Azure DevOps project '{PROJECT}' in org '{ORGANIZATION}' …")
    try:
        ids = run_wiql(pat)
        print(f"WIQL returned {len(ids)} work item ID(s). Fetching details …")
        items = get_work_items(pat, ids)
        print_table(items)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
