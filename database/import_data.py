import json
import os
import hashlib

DB_FILE = "./graph_db.json"
MAX_SLOTS = 10000

# --- Hashing & ID Logic (Same as manage_db.py) ---
def get_base_id(label):
    """Sử dụng MD5 để băm nhãn thành một con số cố định"""
    hash_hex = hashlib.md5(label.encode('utf-8')).hexdigest()
    return (int(hash_hex[:8], 16) % MAX_SLOTS) + 1

def find_free_id(data, label):
    """Finds an ID for the label using linear probing."""
    base_id = get_base_id(label)
    
    # Check if label already exists
    for node_id, node_data in data["nodes"].items():
        if node_data["active"] and label in node_data["labels"]:
            return node_id

    # Find new slot
    for i in range(MAX_SLOTS):
        current_id = str(((base_id + i - 1) % MAX_SLOTS) + 1)
        if not data["nodes"][current_id]["active"]:
            return current_id
            
    return None

# --- Data Import Logic ---

def init_empty_db():
    """Tạo cấu trúc DB trống nếu chưa có file"""
    return {
        "metadata": {"total_slots": MAX_SLOTS},
        "nodes": {str(i): {"labels": [], "active": False} for i in range(1, MAX_SLOTS + 1)},
        "edges": []
    }

def load_or_create_db():
    if not os.path.exists(DB_FILE):
        print(f"⚠️ {DB_FILE} not found. Creating new database...")
        return init_empty_db()
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Đảm bảo có danh sách edges
        if "edges" not in data:
            data["edges"] = []
        return data

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def import_data():
    data = load_or_create_db()
    
    # Để tránh duplicate node cũ (ví dụ "Phòng 03" vs "Phòng 03 (Tòa F)"), 
    # ta có thể reset graph hoặc chỉ thêm mới. Ở đây ta thêm mới (append).
    # Khuyến khích xóa file json cũ trước khi chạy script này lần đầu.

    print("🚀 Starting Data Import...")

    chains = [
        # --- TÒA F: Tầng Trệt (Ground Floor) ---
        [
            ("Cầu thang trái Tòa F (Tầng trệt)", 4.0),
            ("Nhà vệ sinh nữ Tòa F (Tầng trệt 1)", 3.6), 
            ("Phòng Tổ chức - Hành chính (Tòa F)", 4.0), 
            ("Phòng Thông tin - Truyền thông (Tòa F)", 2.0),
            ("Phòng 03 (Tòa F)", 6.0),
            ("Bộ môn Di truyền (Tòa F)", 2.0),
            ("Phòng 04 (Tòa F)", 2.2),
            ("Phòng 09 (Tòa F - Tầng trệt)", 6.0),
            ("Cửa không nhãn (Tòa F - Tầng trệt)", 3.0),
            ("Văn phòng Khoa SH-CNSH (Tòa F)", 5.8),
            ("Phòng 07 (Tòa F)", 6.4), 
            ("Cầu thang trung tâm & Giảng đường (Tòa F - Trệt)", 4.0), 
            ("Phòng 08 (Tòa F)", 6.0),
            ("Phòng 09 (Tòa F - Phải - Tầng trệt)", 2.0),
            ("Phòng không tên (Tòa F - Tầng trệt)", 6.0),
            ("Phòng mất nhãn (Tòa F - Tầng trệt)", 1.6),
            ("Phòng 12 (Tòa F)", 6.0),
            ("Phòng 13 (Tòa F)", 3.2),
            ("Cầu thang phải Tòa F (Tầng trệt)", 0) 
        ],
        # --- TÒA F: Tầng Trệt (Cánh Phải) ---
        [
            ("Cầu thang phải Tòa F (Tầng trệt)", 2.0),
            ("Phòng 14 (Tòa F)", 4.0),
            ("Phòng KH & CN (Tòa F)", 0)
        ],
        [
            ("Phòng 14 (Tòa F)", 7.0),
            ("Cầu thang nhỏ xuống bãi xe (Tòa F)", 0)
        ],
        [
            ("Phòng 14 (Tòa F)", 7.8),
            ("Phòng 15 (Tòa F)", 7.6),
            ("Phòng 16 (Tòa F)", 8.4),
            ("Phòng 17 (Tòa F)", 3.2),
            ("Nhà vệ sinh nam Tòa F (Tầng trệt - Phải)", 3.0),
            ("Phòng 18 (Tòa F)", 0) 
        ],
        
        # --- TÒA F: Tầng 1 ---
        [
            ("Cầu thang trái Tòa F (Tầng 1)", 4.0),
            ("Nhà vệ sinh nam Tòa F (Tầng 1)", 5.8),
            ("Phòng 100 (Tòa F)", 4.0),
            ("Phòng 101 (Tòa F)", 2.0),
            ("Phòng 101a (Tòa F)", 3.8),
            ("Phòng 101b (Tòa F)", 4.4),
            ("Phòng họp F102 (Cửa 1)", 5.6),
            ("Phòng họp F102 (Cửa 2)", 1.2),
            ("Restroom GV/Khách (Tòa F - T1)", 2.8),
            ("Phòng 103 (Tòa F)", 6.0),
            ("Cầu thang trung tâm Tòa F (Tầng 1)", 4.8),
            ("Phòng F.105", 4.0),
            ("Phòng 106a (Tòa F)", 6.0),
            ("Văn phòng Đoàn (Tòa F)", 4.0),
            ("Văn phòng Tiếp dân & TTPCH (Tòa F)", 1.4),
            ("Văn phòng Hội đoàn (Tòa F)", 5.8),
            ("Phòng không tên (Tòa F - T1)", 2.6),
            ("Cầu thang phải (Tầng 1) & Giao điểm Tòa E", 2.2), # Điểm nối E-F
            ("Phòng 109 (Tòa F)", 8.0),
            ("Phòng 110 (Tòa F)", 8.0),
            ("Phòng 111 (Tòa F)", 8.0),
            ("Phòng 112 (Tòa F)", 4.2),
            ("Phòng họp Khoa KHVL (Tòa F)", 3.2),
            ("Văn phòng Khoa KHVL (Tòa F)", 3.6),
            ("Cầu thang phải 2 Tòa F (Tầng 1)", 0)
        ],

        # --- TÒA F: Tầng 2 ---
        [
            ("Cầu thang trái Tòa F (Tầng 2)", 4.8),
            ("Phòng đọc Khoa MTR (Tòa F)", 7.2),
            ("Phòng F200", 3.2),
            ("Phòng 202 (Tòa F - Cửa 1)", 4.8),
            ("Phòng 202 (Tòa F - Cửa 2)", 2.4),
            ("Phòng 203 (Tòa F - Cửa 1)", 9.6),
            ("Phòng 203 (Tòa F - Cửa 2)", 1.0),
            ("Giao điểm Tòa B (tại Tòa F)", 4.8),
            ("Phòng Hội đồng (Tòa F - IDK)", 5.6),
            ("Cầu thang trung tâm Tòa F (Tầng 2)", 5.6),
            ("Văn phòng Đảng ủy (Tòa F)", 5.6),
            ("Văn phòng Hội đồng trường (Tòa F)", 2.4),
            ("Phòng F205b", 6.0),
            ("Phòng không tên (Tòa F - T2)", 2.0),
            ("Phòng F206a", 6.4),
            ("Phòng 206 (Tòa F)", 2.4),
            ("Cầu thang phải (Tầng 2) & Giao điểm Tòa E", 3.2), # Điểm nối E-F
            ("Phòng 207 (Tòa F)", 7.2),
            ("Phòng 208 (Tòa F - Phòng máy Toán Tin)", 8.4),
            ("Phòng 209 (Tòa F - Phòng máy)", 8.0),
            ("Phòng F210", 6.0),
            ("Cầu thang phải 2 Tòa F (Tầng 2)", 0)
        ],

        # --- TÒA F: Tầng 3 ---
        [
            ("Phòng 300 (Tòa F)", 1.6),
            ("Phòng F301", 2.4),
            ("Phòng GV F302", 8.0),
            ("Cầu thang trung tâm Tòa F (Tầng 3)", 0)
        ],
        [
            ("Cầu thang trung tâm Tòa F (Tầng 3)", 4.8),
            ("Phòng F303 (Cửa 1)", 6.4),
            ("Phòng F303 (Cửa 2)", 2.0),
            ("Phòng F304 (Cửa 1)", 6.0),
            ("Phòng F304 (Cửa 2)", 2.0),
            ("Phòng F305 (Cửa 1)", 6.0),
            ("Phòng F305 (Cửa 2)", 1.6),
            ("Giao điểm Tòa E (Lầu 3)", 0) # Điểm nối E-F
        ],

        # --- TÒA E: LẦU 1 ---
        [
            ("Cầu thang y tế (Tòa E)", 0),
            ("Nhà vệ sinh nữ cạnh cầu thang y tế (Lầu1)", 0.5),
            ("Cầu thang phải (Tầng 1) & Giao điểm Tòa E", 3.0), # Kết nối về Tòa F
            ("Phòng E101b - DesLab (Lầu1)", 3.0),
            ("Phòng E101a - Phòng họp (Lầu1)", 6.6),
            ("Phòng E102", 2.85),
            ("Phòng E103a", 4.8),
            ("Phòng E103b", 2.4),
            ("Phòng E104", 6.0),
            ("Phòng Thí nghiệm Điện tử (Lầu1)", 1.8),
            ("Bộ môn Điện tử (Lầu1)", 6.0),
            ("Cầu thang 2 (Lầu1)", 2.85),
            ("Phòng E106", 3.0),
            ("Phòng E107", 6.0)
        ],

        # --- TÒA E: LẦU 2 ---
        [
            ("Cầu thang y tế (Tòa E) - Lầu2", 0),
            ("Nhà vệ sinh nam cạnh cầu thang (Lầu2)", 0.5),
            ("Phòng 201a (Tòa E)", 3.0),
            ("Phòng 201b (Tòa E)", 6.6),
            ("Cầu thang phải (Tầng 2) & Giao điểm Tòa E", 3.0), # Kết nối về Tòa F
            ("Phòng 202b (Tòa E)", 3.0),
            ("Phòng 202a (Tòa E)", 6.6),
            ("Cửa 1 phòng E203", 1.8),
            ("Cửa 2 phòng E203", 6.0),
            ("Cửa không tên (Lầu2)", 1.8), 
            ("Cửa E204", 6.0),
            ("Cầu thang 2 (Lầu2)", 2.85),
            ("Phòng E205", 3.0),
            ("Phòng E206", 6.0)
        ],

        # --- TÒA E: LẦU 3 ---
        [
            ("Cầu thang y tế (Tòa E) - Lầu3", 0),
            ("Nhà vệ sinh nữ cạnh cầu thang (Lầu3)", 0.5),
            ("Cửa E301 (1)", 3.2),
            ("Cửa E301 (2)", 6.0),
            ("Giao điểm Tòa E (Lầu 3)", 2.4), # Kết nối về Tòa F
            ("Cửa E302 (1)", 2.4),
            ("Cửa E302 (2)", 6.4),
            ("E303b", 2.0),
            ("E303a", 6.4),
            ("E304", 1.6),
            ("Bộ môn Vật lý - Tin học (Lầu3)", 6.4),
            ("Cầu thang 2 (Lầu3)", 2.4),
            ("Phòng không tên (Lầu3)", 3.2),
            ("E305", 6.0)
        ],

        # --- TÒA E: LẦU 4 ---
        [
            ("Cầu thang y tế (Tòa E) - Lầu4", 0),
            ("Nhà vệ sinh nam cạnh cầu thang (Lầu4)", 0.5),
            ("Phòng không tên A (Lầu4)", 3.2),
            ("Phòng không tên B - cửa 2 (Lầu4)", 6.4),
            ("E402 (1)", 2.4),
            ("E402 (2)", 6.0),
            ("E403 (1)", 2.0),
            ("E403 (2)", 6.4),
            ("E404 (1)", 2.0),
            ("E404 (2)", 6.4),
            ("Cầu thang 2 (Lầu4)", 2.4),
            ("Phòng không tên C (Lầu4)", 3.2),
            ("Phòng không tên D - cửa 2 (Lầu4)", 6.4)
        ]
    ]

    # Process all chains
    for chain in chains:
        prev_id = None
        for i, item in enumerate(chain):
            label = item[0]
            distance_to_next = item[1]

            # 1. Get or Create ID for this Node
            node_id = find_free_id(data, label)
            
            # Activate and label the node
            if node_id:
                if not data["nodes"][node_id]["active"]:
                    data["nodes"][node_id]["active"] = True
                    data["nodes"][node_id]["labels"] = [label]
                    print(f"✅ Created Node: '{label}' -> ID: {node_id}")
                else:
                    # Append label if unique
                    if label not in data["nodes"][node_id]["labels"]:
                        data["nodes"][node_id]["labels"].append(label)
                    print(f"ℹ️  Existing Node: '{label}' -> ID: {node_id}")
            else:
                print(f"🛑 DB Full, could not add {label}")
                continue

            # 2. Add Edge from Previous Node
            if prev_id and node_id:
                # Check for existing edge
                existing_edge = False
                for edge in data["edges"]:
                    if (edge["from"] == prev_id and edge["to"] == node_id) or \
                       (edge["from"] == node_id and edge["to"] == prev_id):
                        existing_edge = True
                        break
                
                if not existing_edge:
                    # Get distance from previous item in the chain
                    dist = chain[i-1][1] 
                    data["edges"].append({
                        "from": prev_id,
                        "to": node_id,
                        "weight": dist
                    })
                    print(f"   🔗 Linked {prev_id} <-> {node_id} (Dist: {dist}m)")

            prev_id = node_id

    save_db(data)
    print("\n✅ Validated and Saved all imported data!")

if __name__ == "__main__":
    import_data()