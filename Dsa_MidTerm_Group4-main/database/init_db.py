import json

def init_fixed_database(filename="./graph_db.json"):
    # Tạo 10,000 nút trống với ID từ 1 đến 10,000
    nodes = {str(i): {"labels": [], "active": False} for i in range(1, 10001)}
    
    data = {
        "metadata": {"total_slots": 10000},
        "nodes": nodes,
        "edges": []
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Đã tạo database với 10,000 slot trống tại {filename}")

if __name__ == "__main__":
    init_fixed_database()