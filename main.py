import sqlite3
import ctypes
from typing import List

def load_hash_table(db_path: str):
    """
    Load bảng label -> node_id từ SQL
    (hashing + linear probing đã được đảm bảo trước đó)
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT label, node_id FROM labels")
    table = {}

    for label, node_id in cur.fetchall():
        table[label] = node_id

    conn.close()
    return table

def label_to_node_id(label: str, hash_table: dict) -> int:
    if label not in hash_table:
        raise ValueError(f"Label '{label}' không tồn tại trong hệ thống")
    return hash_table[label]

def load_graph_from_sql(db_path: str):
    """
    Convert SQL edges -> adjacency list dạng số nguyên
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT from_node, to_node, time FROM edges")

    adj = {}
    for u, v, w in cur.fetchall():
        if u not in adj:
            adj[u] = []
        adj[u].append((v, w))

    conn.close()
    return adj

def build_c_arrays(adj):
    """
    Convert adjacency list -> C-style arrays
    """
    nodes = sorted(adj.keys())
    index_map = {node: i for i, node in enumerate(nodes)}

    offsets = [0]
    adj_nodes = []
    adj_weights = []

    for node in nodes:
        for v, w in adj[node]:
            adj_nodes.append(index_map[v])
            adj_weights.append(w)
        offsets.append(len(adj_nodes))

    return nodes, offsets, adj_nodes, adj_weights, index_map

def call_cpp_dll(dll_path, nodes, offsets, adj_nodes, adj_weights, start, end):
    dll = ctypes.CDLL(dll_path)

    dll.find_path.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int)
    ]

    n = len(nodes)

    offsets_arr = (ctypes.c_int * len(offsets))(*offsets)
    adj_nodes_arr = (ctypes.c_int * len(adj_nodes))(*adj_nodes)
    adj_weights_arr = (ctypes.c_int * len(adj_weights))(*adj_weights)
    out_path = (ctypes.c_int * n)()

    path_len = dll.find_path(
        n,
        offsets_arr,
        adj_nodes_arr,
        adj_weights_arr,
        start,
        end,
        out_path
    )

    return [out_path[i] for i in range(path_len)]

def node_id_to_labels(db_path: str, node_id: int) -> List[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT label FROM labels WHERE node_id = ?", (node_id,))
    labels = [row[0] for row in cur.fetchall()]

    conn.close()
    return labels

def find_path_by_labels(db_path, dll_path, start_label, end_label):
    hash_table = load_hash_table(db_path)

    start_id = label_to_node_id(start_label, hash_table)
    end_id = label_to_node_id(end_label, hash_table)

    adj = load_graph_from_sql(db_path)
    nodes, offsets, adj_nodes, adj_weights, index_map = build_c_arrays(adj)

    path_indices = call_cpp_dll(
        dll_path,
        nodes,
        offsets,
        adj_nodes,
        adj_weights,
        index_map[start_id],
        index_map[end_id]
    )

    path_node_ids = [nodes[i] for i in path_indices]

    result = []
    for node_id in path_node_ids:
        result.append(node_id_to_labels(db_path, node_id))

    return result

if __name__ == "__main__":
    path = find_path_by_labels(
        "database/campus.db",
        "logic/pathfinder.dll",
        "Cổng A",
        "Phòng 204"
    )

    for step in path:
        print(" -> ".join(step))