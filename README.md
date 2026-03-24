# KenPub

## Fetch User Stories from Azure DevOps Backlog

`fetch_user_stories.py` queries the **lobo.ecm8** Azure DevOps project and
returns all **User Stories in the `New` state whose Story Points are between
10 and 20** (inclusive).

The query mirrors every filter present in the backlog URL:

| Filter | Value |
|---|---|
| Work Item Type | User Story |
| Area Path | lobo.ecm8 |
| State | New |
| Assigned To | @Me · *(Unassigned)* · aibrahim@lobo.ag |
| Iteration Path | @currentIteration · lobo.ecm8 · lobo.ecm8\Feature Requests · lobo.ecm8\Not assigned yet |
| **Story Points** | **10 – 20 (inclusive)** |

### Prerequisites

- Python 3.8 or later (no third-party packages required – uses the standard library only)
- An Azure DevOps **Personal Access Token (PAT)** with at least the
  **Work Items (Read)** scope for the `loboag` organisation.

#### How to create a PAT

1. Sign in to Azure DevOps at <https://dev.azure.com/loboag>
2. Open **User Settings → Personal Access Tokens**
   (direct link: <https://dev.azure.com/loboag/_usersSettings/tokens>)
3. Click **New Token**
4. Give it a name (e.g. `fetch-stories`), set an expiry, and tick
   **Work Items → Read** under *Scopes*
5. Click **Create** and copy the token — it is shown only once

### Usage

```bash
# Option A – set the PAT as an environment variable first
export AZURE_DEVOPS_PAT="<your-pat-here>"   # Linux / macOS
set AZURE_DEVOPS_PAT="<your-pat-here>"      # Windows cmd

python fetch_user_stories.py

# Option B – run the script and type the PAT when prompted
python fetch_user_stories.py
# AZURE_DEVOPS_PAT is not set. …
# Azure DevOps PAT: <type here, input is hidden>
```

**Example output**

```
Querying Azure DevOps project 'lobo.ecm8' in org 'loboag' …
WIQL returned 3 work item ID(s). Fetching details …

Found 3 User Stories with 10–20 story points:

+-------+--------------+-------+------------------+----------------------------+----------------------------------+
| ID    | Story Points | State | Assigned To      | Iteration                  | Title                            |
+-------+--------------+-------+------------------+----------------------------+----------------------------------+
| 12345 | 13           | New   | aibrahim@lobo.ag | lobo.ecm8\Feature Requests | Implement export to PDF          |
| 12346 | 20           | New   | (Unassigned)     | lobo.ecm8\Not assigned yet | Redesign dashboard overview page |
| 12347 | 10           | New   | Ahmed Ibrahim    | lobo.ecm8                  | Add bulk-upload endpoint         |
+-------+--------------+-------+------------------+----------------------------+----------------------------------+
```

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Authentication failed (HTTP 401)` | PAT is missing, expired, or was typed incorrectly | Generate a new PAT at the link above and re-run |
| `Authentication failed (HTTP 403)` | PAT exists but lacks **Work Items (Read)** scope | Edit the PAT and add the *Work Items → Read* scope |
| `Network error reaching …` | No internet access or corporate proxy blocking the request | Check your network/VPN settings |
| `No User Stories … found` | Query returned no results | Verify you have items matching all the filters in the backlog URL |

### Backlog URL

```
https://dev.azure.com/loboag/lobo.ecm8/_backlogs/backlog/lobo.ecm8%20Team/Stories
  ?System.WorkItemType=User%20Story
  &System.AssignedTo=%40me%2C_Unassigned_%2Caibrahim%40lobo.ag
  &System.IterationPath=%40currentIteration%2Clobo.ecm8%2Clobo.ecm8%5CFeature%20Requests%2Clobo.ecm8%5CNot%20assigned%20yet
  &System.AreaPath=lobo.ecm8
  &System.State=New
```
