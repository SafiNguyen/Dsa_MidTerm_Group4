import json
import os

# Đường dẫn tới file database của bạn
DB_FILE = os.path.join("database", "graph_db.json")
OUTPUT_FILE = "active_nodes_report.txt"

def export_active_nodes():
    # 1. Kiểm tra file JSON có tồn tại không
    if not os.path.exists(DB_FILE):
        print(f"❌ Không tìm thấy file: {DB_FILE}")
        return

    try:
        # 2. Đọc dữ liệu từ JSON
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get("nodes", {})
        active_list = []

        # 3. Lọc các nút đang active
        # Sắp xếp theo ID (ép kiểu về int để sắp xếp đúng thứ tự số học)
        sorted_keys = sorted(nodes.keys(), key=lambda x: int(x))

        for node_id in sorted_keys:
            info = nodes[node_id]
            if info.get("active") is True:
                labels_str = ", ".join(info.get("labels", []))
                active_list.append(f"ID: {node_id.ljust(6)} | Labels: {labels_str}")

        # 4. Ghi ra file .txt
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"--- BÁO CÁO CÁC NÚT ĐANG HOẠT ĐỘNG (ACTIVE) ---\n")
            f.write(f"Tổng cộng: {len(active_list)} nút.\n")
            f.write("-" * 50 + "\n")
            if active_list:
                f.write("\n".join(active_list))
            else:
                f.write("Chưa có nút nào được kích hoạt.")
        
        print(f"✅ Đã xuất danh sách {len(active_list)} nút active ra file: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    export_active_nodes()
