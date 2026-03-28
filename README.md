# DSA Midterm — Group 4: Campus Graph Pathfinder

> **Ho Chi Minh City University of Science (HCMUS)**  
> Data Structures & Algorithms — Midterm Project

---

## Overview

Finding your way around a university campus — across multiple buildings, floors, staircases, and corridors — is a deceptively complex real-world problem. This project applies the **Single-Source Shortest Path (SSSP)** algorithm to campus navigation at HCMUS, computing the most efficient walking route between any two named locations on campus.

The campus is modeled as a **weighted undirected graph**, where:
- **Nodes** represent physical locations (rooms, staircases, hallways, intersections).
- **Edges** represent walkable connections between those locations.
- **Weights** represent the walking distance in meters between connected locations.

Given a start label and a destination label, the system resolves both to node IDs, runs the shortest-path algorithm via a native C++ library, and prints the optimal route.

### The Algorithm — Why SSSP?

The **Single-Source Shortest Path** problem asks: *"What is the minimum-cost route from a given starting point to every other reachable point in a graph?"* This is exactly what campus navigation requires.

The classical solution for non-negative weighted graphs is **Dijkstra's algorithm**, which has been a cornerstone of graph theory for decades. More recently, research has introduced SSSP methods that break the so-called **"sorting barrier"** — a long-standing theoretical limit that tied shortest-path computation time to comparison-based sorting. Our native C++ pathfinder (`pathfinder.dll`) implements an efficient SSSP approach well-suited for dense, indoor campus graphs.

---

## Table of Contents

- [1. Requirements](#1-requirements)
- [2. Project Structure](#2-project-structure)
- [3. Database Format](#3-database-format)
- [4. Quick Start](#4-quick-start)
- [5. Finding a Path (main.py)](#5-finding-a-path-mainpy)
- [6. Managing the Database](#6-managing-the-database)
  - [6.1 Bulk Import](#61-bulk-import-import_datapy)
  - [6.2 Interactive Editor](#62-interactive-editor-manage_dbpy)
  - [6.3 Manual Edits](#63-manual-edits)
- [7. Label Rules](#7-label-rules)
- [8. Building the Pathfinder DLL](#8-building-the-pathfinder-dll)
- [9. Troubleshooting](#9-troubleshooting)
- [10. File Responsibilities](#10-file-responsibilities)

---

## 1. Requirements

| Requirement | Details |
|---|---|
| Python | 3.8 or higher, available as `python` on your PATH |
| OS | Windows (project requires `path_finder/pathfinder.dll`) |
| Build tools | Visual Studio 2022 / MSVC *(optional — only needed to rebuild the DLL)* |

Run all commands from the **repository root**. In Visual Studio, use the integrated **Terminal**.

---

## 2. Project Structure

```
.
├── main.py                      # Unified interface: loads and runs the algorithm in pathfinder.dll
├── database/
│   ├── graph_db.json            # The campus graph (nodes + edges)
│   ├── import_data.py           # Bulk-import locations from predefined chains
│   ├── manage_db.py             # Interactive node/edge editor
│   └── init_db.py               # Initialize a fresh empty graph
├── path_finder/
│   ├── pathfinder.cpp           # C++ SSSP implementation
│   ├── pathfinder.h             # Exported function header
│   └── pathfinder.dll           # Compiled native library (required at runtime)
└── active_nodes_report.txt      # Debug utility — lists all currently active nodes
```

---

## 3. Database Format

The campus graph is stored in `database/graph_db.json` using a fixed-slot structure supporting up to 10,000 nodes.

### Top-level keys

| Key | Description |
|---|---|
| `metadata.total_slots` | Maximum node slots (default: `10000`) |
| `nodes` | Map of IDs `"1"` – `"10000"` to node objects |
| `edges` | Array of weighted undirected connections |

### Node object

| Field | Type | Description |
|---|---|---|
| `active` | `bool` | Whether the node is in use (`false` = soft-deleted) |
| `labels` | `string[]` | One or more names / aliases for this location |

### Edge object

| Field | Type | Description |
|---|---|---|
| `from` | `string` | Source node ID |
| `to` | `string` | Destination node ID |
| `weight` | `number` | Walking distance in meters (path cost) |

Edges are **undirected** — `main.py` automatically inserts both directions when building the adjacency structure.

### Example

```json
{
  "metadata": {
    "total_slots": 10000
  },
  "nodes": {
    "1": {
      "active": true,
      "labels": ["Phòng 101 (Tòa F)", "F101"]
    },
    "2": {
      "active": true,
      "labels": ["Cầu thang trái (Tầng 1)"]
    }
  },
  "edges": [
    { "from": "1", "to": "2", "weight": 15 }
  ]
}
```

---

## 4. Quick Start

```bash
# Step 1 — Seed the database (skip if graph_db.json already exists)
python database/import_data.py

# Step 2 — Run the pathfinder
python main.py
```

Enter the **exact** start and destination labels when prompted. Type `exit` to quit.

---

## 5. Finding a Path (`main.py`)

`main.py` is the **unified interface file** — it loads the campus graph, resolves location labels to node IDs, and invokes the shortest-path algorithm inside `pathfinder.dll`.

### Pipeline

1. Load `database/graph_db.json`.
2. Filter to nodes where `"active": true`.
3. Build a compact adjacency array from the edge list.
4. Load `path_finder/pathfinder.dll` via `ctypes` and call:
   ```
   find_path(n, adj_offsets, adj_nodes, adj_weights, src_idx, dest_idx, out_path)
   ```
5. Print the resulting shortest path as an ordered sequence of node IDs and their primary labels.

### Example output

```
Start label    : Cổng chính
End label      : Phòng F.101

Path found:
  ID  45  →  Cổng chính
  ID 312  →  Cầu thang trái (Tầng 1)
  ID 826  →  Phòng F.101

Total distance : 87m
```

### Input rules

- Labels must be typed **exactly** as they appear in `graph_db.json` — spacing, punctuation, and casing all matter.
- Any label in a node's `labels` array is valid for lookup (not just the first one).

### Why the path might fail

| Symptom | Likely cause | Fix |
|---|---|---|
| `DLL load error` | Wrong architecture or missing file | Rebuild for x64; verify the `.dll` path |
| `Không tìm thấy nhãn` | Label typo or node inactive | Check exact spelling in `graph_db.json` |
| No path returned | Graph is disconnected | Add missing edges to bridge the two segments |
| Path looks incorrect | Wrong edge weights or duplicate nodes | Verify weights are in meters; check for near-duplicate labels |

---

## 6. Managing the Database

### 6.1 Bulk Import (`import_data.py`)

Populates the graph from hardcoded **location chains** — ordered sequences of location labels and distances that represent walkable corridors or routes.

```bash
python database/import_data.py
```

**Behavior:**
- If a label already exists in an active node → that node is **reused**.
- If the label is new → a fresh node ID is assigned using MD5 hash of the label, with linear probing to find a free slot.

>**Renaming labels** (e.g. `Phòng 03` → `Phòng 03 (Tòa F)`) causes the importer to create entirely new nodes, since all lookups are exact-match. If performing bulk renames, re-initialize the database first with `init_db.py` and re-import from scratch.

### 6.2 Interactive Editor (`manage_db.py`)

Add individual nodes and edges through console prompts — no manual JSON editing required.

```bash
python database/manage_db.py
```

**Menu options:**

| Option | Action |
|---|---|
| Add a node | Enter a primary label; optionally add aliases. ID is auto-assigned. |
| Add an edge | Enter From ID, To ID, and distance weight (meters). |
| Save and exit | Writes all changes to `graph_db.json`. |

> Both endpoints of an edge must exist and have `"active": true`.

### 6.3 Manual Edits

There is no dedicated delete command. Use direct JSON editing for deletions.

**Soft-delete a node** (recommended over hard deletion):
1. Open `database/graph_db.json`.
2. Find the node by ID. Set `"active": false` (optionally clear `"labels": []`).
3. Remove any edges referencing that ID from the `edges` array.
4. Save the file.

**Delete an edge:**  
Remove the matching object from the `edges` array (match on both `from` and `to`).

> Always back up before editing: copy `graph_db.json` → `graph_db.json.bak`

---

## 7. Label Rules

Label accuracy is **critical** — the pathfinder uses exact string matching throughout.

### Avoid ambiguity across buildings

When multiple buildings share similar room numbers, always include the building name:

|  Correct |  Ambiguous |
|---|---|
| `Phòng 02 (Tòa F)` | `Phòng 02` |
| `Phòng 02 (Tòa E)` | `Phòng 02` |
| `E101a`, `F205b` | `Phòng 101` |

### Aliases

A node may carry multiple labels to support different search terms:

```json
"labels": ["Phòng F.101", "F101", "Lớp Giải Tích 1"]
```

Any of these can be used when running `main.py`. Avoid reusing generic strings like `"Cầu Thang"` across multiple distinct nodes — the first match will always win.

---

## 8. Building the Pathfinder DLL

`main.py` requires `path_finder/pathfinder.dll` to be present at runtime. A prebuilt DLL is included in the repository. If you need to rebuild it:

### Exported C function

```c
extern "C" int find_path(
    int    n,
    int*   adj_offsets,
    int*   adj_nodes,
    float* adj_weights,
    int    src_idx,
    int    dest_idx,
    int*   out_path
);
```

`main.py` calls this function via Python's `ctypes`, passing the adjacency arrays built from `graph_db.json`.

### Build steps (Visual Studio 2022)

1. Create a new **C++ DLL** project, targeting **x64**.
2. Add `path_finder/pathfinder.cpp` and `path_finder/pathfinder.h`.
3. Build in **Release** mode.
4. Copy the output `pathfinder.dll` to `path_finder/pathfinder.dll`.

>  The DLL architecture **must match** your Python interpreter. 64-bit Python requires an x64 DLL.

---

## 9. Troubleshooting

**`Cannot find graph_db.json`**  
The database has not been initialized. Run:
```bash
python database/import_data.py
```

**`DLL load error` / `OSError`**  
- Confirm `path_finder/pathfinder.dll` exists.
- Ensure the DLL was compiled for the same architecture as Python (x64 vs x86).
- Ensure the required MSVC runtime DLLs are installed on your system.

**`Không tìm thấy nhãn trong database!`** *(Label not found in database)*  
- The label was entered incorrectly. Check exact spelling in `graph_db.json`.
- Confirm the target node has `"active": true`.

**Path found but looks wrong**  
- Edge weights may be in inconsistent units — verify all are in meters.
- Duplicate nodes from inconsistent labeling can cause unexpected detours — search `graph_db.json` for near-identical label strings.
- Verify that edge `from`/`to` IDs correctly correspond to the intended locations.

---

## 10. File Responsibilities

| File | Role |
|---|---|
| `main.py` | Unified interface file. Loads `graph_db.json`, resolves labels to node IDs, builds the adjacency structure, and runs the SSSP algorithm inside `pathfinder.dll`. |
| `database/graph_db.json` | Persistent campus graph — all nodes and edges. |
| `database/import_data.py` | Bulk-imports nodes and weighted edges from predefined location chains. |
| `database/manage_db.py` | Interactive CLI for adding nodes (hash-based ID assignment) and edges. |
| `database/init_db.py` | Initializes a fresh empty fixed-slot graph structure. |
| `path_finder/pathfinder.cpp` | C++ source code of the SSSP algorithm. |
| `path_finder/pathfinder.h` | Header exposing the `find_path` function signature. |
| `path_finder/pathfinder.dll` | Compiled native library, loaded at runtime by `main.py` via `ctypes`. |
| `active_nodes_report.txt` | Debug utility listing all currently active nodes in the graph. |

---

*DSA Midterm Project — Group 4 | HCMUS | Faculty of Information Technology*