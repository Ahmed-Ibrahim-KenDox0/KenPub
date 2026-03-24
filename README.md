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

- Python 3.10 or later (no third-party packages required – uses the standard library only)
- An Azure DevOps **Personal Access Token (PAT)** with at least the
  **Work Items (Read)** scope for the `loboag` organisation.

### Usage

```bash
# 1. Export your PAT
export AZURE_DEVOPS_PAT="<your-pat-here>"

# 2. Run the script
python fetch_user_stories.py
```

**Example output**

```
Querying Azure DevOps project 'lobo.ecm8' in org 'loboag' …
WIQL returned 3 work item ID(s). Fetching details …

Found 3 User Story/Stories with 10–20 story points:

+-------+-------------+-------+-------------------+----------------------------+----------------------------------+
| ID    | Story Points | State | Assigned To       | Iteration                  | Title                            |
+-------+-------------+-------+-------------------+----------------------------+----------------------------------+
| 12345 | 13          | New   | aibrahim@lobo.ag  | lobo.ecm8\Feature Requests | Implement export to PDF          |
| 12346 | 20          | New   | (Unassigned)      | lobo.ecm8\Not assigned yet | Redesign dashboard overview page |
| 12347 | 10          | New   | Ahmed Ibrahim     | lobo.ecm8                  | Add bulk-upload endpoint         |
+-------+-------------+-------+-------------------+----------------------------+----------------------------------+
```

### Backlog URL

```
https://dev.azure.com/loboag/lobo.ecm8/_backlogs/backlog/lobo.ecm8%20Team/Stories
  ?System.WorkItemType=User%20Story
  &System.AssignedTo=%40me%2C_Unassigned_%2Caibrahim%40lobo.ag
  &System.IterationPath=%40currentIteration%2Clobo.ecm8%2Clobo.ecm8%5CFeature%20Requests%2Clobo.ecm8%5CNot%20assigned%20yet
  &System.AreaPath=lobo.ecm8
  &System.State=New
```
