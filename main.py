import json
import os
import ctypes
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def serialization(indexes, labels, edges, all_nodes_dict):
    DB_FILE = os.path.join(BASE_DIR, "database", "graph_db.json")
    if not os.path.exists(DB_FILE):
        print("Lỗi: Cần chạy file init_fixed_db.py trước!")
        return False
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Dùng Dictionary cho all_nodes để find_id đạt tốc độ O(1) thay vì O(n)
    for node_id, node_info in data["nodes"].items():
        all_nodes_dict[node_id] = node_info["labels"]
        
        if node_info["active"]:
            labels.append(node_info["labels"]) # Danh sách các list labels
            indexes.append(int(node_id))       # Map index mảng -> ID thật
    
    # Tạo mapping ngược để tìm index từ ID nhanh hơn khi xử lý edges
    id_to_idx = {id_val: i for i, id_val in enumerate(indexes)}
    
    for edge in data["edges"]:
        u_id = int(edge["from"])
        v_id = int(edge["to"])
        # Chỉ thêm cạnh nếu cả 2 node đều active
        if u_id in id_to_idx and v_id in id_to_idx:
            edges.append((id_to_idx[u_id], id_to_idx[v_id], int(edge["weight"])))
    return True

def find_id(label, all_nodes_dict):
    hash_hex = hashlib.md5(label.encode('utf-8')).hexdigest()
    possible_node = int(hash_hex[:8], 16) % 10000 + 1
    
    # Dò tuyến tính để tìm ID chứa label đó
    for i in range(10000):
        current_id = str(((possible_node + i - 1) % 10000) + 1)
        if current_id in all_nodes_dict and label in all_nodes_dict[current_id]:
            return int(current_id)
    return None

def load_graph(num_active_nodes, edges):
    adj = [[] for _ in range(num_active_nodes)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w)) 

    adj_offsets = [0]
    adj_nodes = []
    adj_weights = []

    for i in range(num_active_nodes):
        for v, w in adj[i]:
            adj_nodes.append(v)
            adj_weights.append(w)
        adj_offsets.append(len(adj_nodes))

    return (
        num_active_nodes,
        (ctypes.c_int * len(adj_offsets))(*adj_offsets),
        (ctypes.c_int * len(adj_nodes))(*adj_nodes),
        (ctypes.c_int * len(adj_weights))(*adj_weights)
    )

def main():
    # Khởi tạo dữ liệu
    labels = []    # Chứa danh sách nhãn của các node active
    indexes = []   # Chứa ID thực tế (1-10000) của các node active
    edges = []     # Chứa tuple (index_u, index_v, weight)
    all_nodes_dict = {} 

    if not serialization(indexes, labels, edges, all_nodes_dict):
        return

    num_active = len(indexes)
    print(f"Đã tải {num_active} nút active vào bộ nhớ!")

    # Load Graph cho C++ (Lưu ý: truyền số lượng node active)
    graph_data = load_graph(num_active, edges)

    # Load DLL
    try:
        dll_path = os.path.join(BASE_DIR, "path_finder", "pathfinder.dll")
        lib = ctypes.CDLL(dll_path)
        # Giả định hàm find_path: (n, offsets, target_nodes, weights, src, dest, out_path)
        lib.find_path.argtypes = [
            ctypes.c_int, ctypes.POINTER(ctypes.c_int), 
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)
        ]
        lib.find_path.restype = ctypes.c_int
    except Exception as e:
        print(f"Lỗi load DLL: {e}")
        return

    while True:
        l1 = input("\nNhập nhãn xuất phát (hoặc 'exit'): ").strip()
        if l1.lower() == 'exit': break
        l2 = input("Nhập nhãn đích: ").strip()

        id1 = find_id(l1, all_nodes_dict)
        id2 = find_id(l2, all_nodes_dict)

        if id1 is None or id2 is None:
            print("Không tìm thấy nhãn trong database!")
            continue

        try:
            src_idx = indexes.index(id1)
            dest_idx = indexes.index(id2)
        except ValueError:
            print("Nút tồn tại nhưng chưa được kích hoạt (Active=False)!")
            continue

        # Gọi C++ tìm đường
        # out_path nên đủ lớn để chứa tối đa số node
        out_path = (ctypes.c_int * num_active)()
        # Giả sử hàm C++ trả về độ dài đường đi, và điền -1 vào out_path để kết thúc
        path_len = lib.find_path(
            graph_data[0], graph_data[1], graph_data[2], graph_data[3],
            src_idx, dest_idx, out_path
        )

        if path_len <= 0:
            print(f"--- Không tìm thấy đường đi từ {l1} đến {l2} ---")
        else:
            print(f"--- Đường đi ngắn nhất ({path_len} bước) ---")
            path_results = []
            for i in range(path_len):
                idx_in_active = out_path[i]
                real_id = indexes[idx_in_active]
                node_labels = labels[idx_in_active]
                path_results.append(f"ID {real_id}: {node_labels[0]}")
            
            print(" -> ".join(path_results))

if __name__ == "__main__":
    main()