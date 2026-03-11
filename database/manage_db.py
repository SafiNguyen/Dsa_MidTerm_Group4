import json
import os
import hashlib

DB_FILE = "./graph_db.json"
MAX_SLOTS = 10000

def get_base_id(label):
    """Sử dụng MD5 để băm nhãn thành một con số cố định"""
    hash_hex = hashlib.md5(label.encode('utf-8')).hexdigest()
    # Chuyển 8 ký tự đầu của hex thành int để lấy số ID gốc
    return (int(hash_hex[:8], 16) % MAX_SLOTS) + 1

def load_db():
    if not os.path.exists(DB_FILE):
        print("❌ Lỗi: Cần chạy file init_fixed_db.py trước!")
        return None
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_node_linear_probing(data):
    print("\n--- THÊM NÚT (SỬ DỤNG LINEAR PROBING) ---")
    while True:
        label = input("Nhập nhãn nút (hoặc 'None' để dừng): ").strip()
        if label.lower() == 'none': break
        
        base_id = get_base_id(label)
        found_id = None
        
        # Bắt đầu dò tuyến tính từ base_id
        for i in range(MAX_SLOTS):
            # Công thức: (base_id + i - 1) % MAX_SLOTS + 1
            # Giúp vòng lặp quay lại 1 khi vượt quá 10000
            current_id = str(((base_id + i - 1) % MAX_SLOTS) + 1)
            
            if not data["nodes"][current_id]["active"]:
                found_id = current_id
                break
        
        if found_id:
            data["nodes"][found_id]["active"] = True
            data["nodes"][found_id]["labels"] = [label]
            print(f"✅ Đã cấp ID {found_id} cho nhãn '{label}' (Vị trí gốc: {base_id})")
            
            # Nhập thêm các nhãn khác nếu có
            while True:
                extra = input(f"   Thêm nhãn phụ cho ID {found_id} (hoặc 'None'): ").strip()
                if extra.lower() == 'none' or extra == '-': 
                    print(f" ❌Kết thúc nhập nhãn cho ID {found_id}.")
                    break
                data["nodes"][found_id]["labels"].append(extra)
        else:
            print("🛑 Database đã đầy, không thể thêm nút mới!")

def add_edges(data):
    print("\n--- THÊM CẠNH CÓ TRỌNG SỐ ---")
    while True:
        u = input("ID nút nguồn (From): ").strip()
        if u.lower() == 'none' or u == '-': break
        v = input("ID nút đích (To): ").strip()
        if v.lower() == 'none' or v == '-': break

        # Kiểm tra ID tồn tại và đã được kích hoạt chưa
        if u in data["nodes"] and v in data["nodes"]:
            if data["nodes"][u]["active"] and data["nodes"][v]["active"]:
                try:
                    w = float(input(f"Trọng số cạnh {u}-{v}: "))
                    data["edges"].append({"from": u, "to": v, "weight": w})
                    print(f"✅ Đã thêm cạnh: {u} --({w})--> {v}")
                except ValueError:
                    print("❌ Trọng số phải là con số!")
            else:
                print("❌ Một trong hai ID chưa được gán nhãn (active=False)!")
        else:
            print("❌ ID không hợp lệ (phải từ 1-10000)!")

def main():
    db = load_db()
    if not db: return

    while True:
        print("\n=== QUẢN LÝ ĐỒ THỊ (LINEAR PROBING) ===")
        print("1. Thêm nút mới (Tự động tìm ID trống)")
        print("2. Thêm cạnh (Kết nối ID)")
        print("3. Lưu và thoát")
        choice = input("Chọn (1/2/3): ")

        if choice == '1':
            add_node_linear_probing(db)
        elif choice == '2':
            add_edges(db)
        elif choice == '3':
            save_db(db)
            print("💾 Dữ liệu đã được đồng bộ vào file JSON.")
            break

if __name__ == "__main__":
    main()