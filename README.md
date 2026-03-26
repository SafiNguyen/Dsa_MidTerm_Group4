# Dsa_MidTerm_Group4 — Graph DB & Pathfinder

A small toolkit to build, manage and visualize a building/room graph and run shortest-path queries.  
This README explains how to use the project (English), how to add / remove labels and edges, naming notes, and what each file does.

---

## Prerequisites
- Python 3.8+ installed and on PATH.
- A browser (for visualization).
- (Optional) Visual Studio / a C++ toolchain to build the `pathfinder` DLL if you need to rebuild it.
- Run scripts from the repository root. In Visual Studio use the __Terminal__ window.

---

## Quick start (typical workflow)
1. Open a terminal at the project root (or use the __Terminal__ in Visual Studio).
2. Populate/update the JSON DB:
   - To import preset nodes/edges:  
     python database/import_data.py
   - To interactively add nodes/edges:  
     python database/manage_db.py
3. Visualize the graph (interactive HTML):  
   python database/visualize_db.py  
   This writes `database/graph_view.html` and opens it in your browser.
4. Query shortest paths (requires compiled `pathfinder` DLL):  
   python main.py  
   - The program will ask for a start label and an end label, then use the compiled DLL to compute the shortest path.

---

## "Label list" (how to view / enable)
- The database stores node labels inside `database/graph_db.json` under `nodes`. Each node has `"labels": [...]` and `"active": true/false`.
- To view active labels:
  - Open `database/graph_db.json` and inspect `nodes` → filter entries where `"active": true`.
  - Or run `python database/visualize_db.py` — nodes will show a tooltip listing all labels for a node (hover a node in the visualization).
- There is no separate "toggle" to enable labels — they are stored by default. Visualize / inspect the JSON to view them.

---

## Adding nodes / edges
Method A — interactive (recommended for correctness)
- Run: `python database/manage_db.py`
  - Choose `1` to add a node (linear probing ID allocation).
  - Choose `2` to add an edge between two existing node IDs.
- This script:
  - Uses MD5-based base ID + linear probing to select an available numeric ID (1..10000).
  - Marks `nodes[id]["active"] = true` and sets `labels`.

Method B — import script
- `database/import_data.py` contains preconfigured chains (floor-by-floor). Running it will:
  - Ensure `edges` exist in the JSON,
  - Create or reuse nodes (based on exact label match) and append edges between chain neighbors.

Notes:
- Prefer the interactive `manage_db.py` for manual additions and `import_data.py` for bulk imports.

---

## Deleting nodes / edges (manual steps)
There is no safe automated "delete" UI. Two supported approaches:

1. Soft-delete (recommended)
   - Open `database/graph_db.json`.
   - Find the node entry and set `"active": false` and optionally clear `"labels": []`.
   - Remove any edges that reference that node from the top-level `"edges"` array.
   - Save file.

2. Hard-delete (dangerous)
   - Manually remove the node object from `nodes` or rewrite `nodes` structure. This is error-prone — back up the file first.

Edge deletion:
- Remove entries from `data["edges"]` array where `edge["from"] == <id>` and/or `edge["to"] == <id>`.
- Save `database/graph_db.json`.

Always back up `database/graph_db.json` before manual edits.

---

## Naming conventions & important usage notes
- Label matching is exact: when searching or reusing nodes the code looks for the exact text in the node's `"labels"` list. Use 100% exact naming.
- To avoid ambiguous names across buildings, include the building in the label (recommended pattern): `Phòng 03 (Tòa F)` or `E101b` / `Phòng E101b`.
  - You already use this in some imports (e.g., `Phòng 03 (Tòa F)`).
- When adding new labels via scripts, consider the exact text you will later use for lookups. A tiny difference (extra space, punctuation) results in a new node.
- When running scripts from project root, prefer absolute DB path (scripts should use `database/graph_db.json`). If a script uses a relative path (like `./graph_db.json`), run it from the `database` directory or prefer the updated scripts that use `os.path.join(os.path.dirname(__file__), "graph_db.json")`.

---

## How to find a path
1. Ensure `database/graph_db.json` has:
   - `nodes` entries marked `"active": true`
   - a top-level `"edges"` array with objects: `{ "from": "<id>", "to": "<id>", "weight": <number> }`
2. Build `pathfinder` C++ code into a DLL:
   - Path: `path_finder/pathfinder.cpp` / `pathfinder.h`
   - Build process depends on your OS/toolchain. The Python `main.py` expects a DLL at `path_finder/pathfinder.dll`.
3. Run `python main.py` and input start label and end label exactly as stored in JSON (case matters if you didn't normalize).
4. The CLI will print the sequence of nodes on the found path.

---

## Files and responsibilities
- `database/graph_db.json`  
  Primary data store. Structure:
  - `metadata`
  - `nodes` — map of id (string) -> { "labels": [...], "active": bool }
  - `edges` — list of edges { "from": id, "to": id, "weight": number }
  - Keep a backup before manual edits.

- `database/init_db.py`  
  (Project helper) — creates an initial database with empty node slots and metadata. Use when starting fresh. If absent, `import_data.py` can create an empty DB if coded that way.

- `database/import_data.py`  
  Bulk importer: defines floor/room chains and converts distances into edges. It:
  - Finds or allocates numeric IDs using MD5-based hashing and linear probing.
  - Activates nodes and sets their labels.
  - Appends edges between consecutive chain nodes with distance weights.
  - Note: Changing label text will create new nodes on re-run; to avoid duplicates delete or reset `graph_db.json` first.

- `database/manage_db.py`  
  Interactive console utility to:
  - Add nodes (linear probing).
  - Add edges manually.
  - Save DB.
  - Useful for careful, manual edits without editing JSON directly.

- `database/visualize_db.py`  
  Generates a browser-based interactive visualization (`database/graph_view.html`) using vis.js:
  - Shows nodes (color-coded by keyword/building).
  - Edges labeled with weights.
  - Hover to see all labels for a node.

- `main.py`  
  CLI for path queries:
  - Serializes active nodes and edges into compact arrays.
  - Loads the native `pathfinder` DLL and calls `find_path`.
  - Prompts for start & end labels and prints the route.

- `path_finder/pathfinder.cpp` & `pathfinder.h`  
  C++ implementation of the shortest-path routine used by `main.py`.
  - Build to `path_finder/pathfinder.dll` for the Python wrapper to use.
  - If you don't have the DLL, `main.py` will fail to load it — visualize + manage are still usable.

- `active_nodes_report.txt`  
  (Project file) Possibly a generated report of active nodes. Open to view current active node list.

- `any.py`  
  (Spare / utility) Content not required for the main flow; check file if needed.

---

## Recommended safe workflow to update DB
1. Backup: copy `database/graph_db.json` → `database/graph_db.json.bak`.
2. If importing a large prepared dataset (like `import_data.py`) and you want only imported nodes, remove or rename `graph_db.json` first (so import script creates a fresh DB).
3. Run `python database/import_data.py` to seed nodes/edges.
4. Use `python database/manage_db.py` for fine adjustments (add node labels / edges).
5. Visualize with `python database/visualize_db.py`.
6. Run path queries in `python main.py` (ensure DLL available).

---

## Troubleshooting
- "Cannot find graph_db.json" — run scripts from repository root, or use the __Terminal__ in the folder, or ensure scripts use the absolute `os.path.join(os.path.dirname(__file__), ...)` pattern (many scripts already do).
- "DLL load error" — build the C++ `pathfinder` into the expected `pathfinder.dll` or change `main.py` to point to your built library.
- Duplicate nodes appear after re-running import: check exact label strings and consider deleting old DB before bulk import.

---

## Final tips
- Use exact naming when searching/adding labels. Include building identifiers in label strings to avoid collisions: e.g., `Phòng 101 (Tòa F)` or `E101b`.
- Keep a copy of `graph_db.json` before manual edits.
- If you want, I can generate a small helper script to produce a plain active-labels text file (`active_nodes_report.txt`) or add a safe delete function to `manage_db.py`.

---

If you want this README saved into the repo, I can write `README.md` for you now.
