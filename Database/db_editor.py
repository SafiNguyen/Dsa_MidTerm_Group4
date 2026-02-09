# database/db_editor.py

import sqlite3
from typing import Optional

# =========================
# Hash Table - Linear Probing
# =========================

class HashEntry:
    def __init__(self, key: str, value: int):
        self.key = key
        self.value = value


class HashTable:
    def __init__(self, size: int = 101):
        self.size = size
        self.table = [None] * size
        self.count = 0

    def _hash(self, key: str) -> int:
        """
        Simple linear probing hash
        """
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) % self.size
        return h

    def insert(self, key: str, value: int):
        if self.count >= self.size:
            raise RuntimeError("Hash table is full")

        idx = self._hash(key)

        start_idx = idx
        while self.table[idx] is not None:
            if self.table[idx].key == key:
                raise ValueError(f"Label '{key}' đã tồn tại")
            idx = (idx + 1) % self.size
            if idx == start_idx:
                raise RuntimeError("Linear probing failed")

        self.table[idx] = HashEntry(key, value)
        self.count += 1

    def search(self, key: str) -> Optional[int]:
        idx = self._hash(key)
        start_idx = idx

        while self.table[idx] is not None:
            if self.table[idx].key == key:
                return self.table[idx].value
            idx = (idx + 1) % self.size
            if idx == start_idx:
                break
        return None

    def items(self):
        for entry in self.table:
            if entry is not None:
                yield entry.key, entry.value

# =========================
# Database Editor
# =========================

class DatabaseEditor:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.hash_table = HashTable()
        self._load_existing_labels()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _load_existing_labels(self):
        """
        Load labels from SQL into hash table
        """
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                label TEXT PRIMARY KEY,
                node_id INTEGER NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                from_node INTEGER,
                to_node INTEGER,
                time INTEGER
            )
        """)

        cur.execute("SELECT label, node_id FROM labels")
        for label, node_id in cur.fetchall():
            self.hash_table.insert(label, node_id)

        conn.commit()
        conn.close()

    # =========================
    # Node & Label Operations
    # =========================

    def add_node(self, name: str, labels: list[str]):
        if not labels:
            raise ValueError("Một node phải có ít nhất một nhãn")

        conn = self._connect()
        cur = conn.cursor()

        cur.execute("INSERT INTO nodes (name) VALUES (?)", (name,))
        node_id = cur.lastrowid

        for label in labels:
            self.hash_table.insert(label, node_id)
            cur.execute(
                "INSERT INTO labels (label, node_id) VALUES (?, ?)",
                (label, node_id)
            )

        conn.commit()
        conn.close()

        print(f"✔ Đã thêm node {node_id} với nhãn {labels}")

    def add_label(self, node_id: int, label: str):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("SELECT node_id FROM nodes WHERE node_id = ?", (node_id,))
        if cur.fetchone() is None:
            conn.close()
            raise ValueError("Node không tồn tại")

        self.hash_table.insert(label, node_id)
        cur.execute(
            "INSERT INTO labels (label, node_id) VALUES (?, ?)",
            (label, node_id)
        )

        conn.commit()
        conn.close()

        print(f"✔ Đã gán nhãn '{label}' cho node {node_id}")

    # =========================
    # Edge Operations
    # =========================

    def add_edge(self, from_node: int, to_node: int, time: int):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("SELECT node_id FROM nodes WHERE node_id = ?", (from_node,))
        if cur.fetchone() is None:
            raise ValueError("from_node không tồn tại")

        cur.execute("SELECT node_id FROM nodes WHERE node_id = ?", (to_node,))
        if cur.fetchone() is None:
            raise ValueError("to_node không tồn tại")

        cur.execute(
            "INSERT INTO edges (from_node, to_node, time) VALUES (?, ?, ?)",
            (from_node, to_node, time)
        )

        conn.commit()
        conn.close()

        print(f"✔ Đã thêm cạnh {from_node} → {to_node} ({time})")

    # =========================
    # Debug & Visualization
    # =========================

    def print_hash_table(self):
        print("\nHash Table (Linear Probing):")
        for i, entry in enumerate(self.hash_table.table):
            if entry is None:
                print(f"[{i}] EMPTY")
            else:
                print(f"[{i}] {entry.key} → {entry.value}")

# =========================
# CLI
# =========================

def main():
    editor = DatabaseEditor("campus.db")

    while True:
        print("\n=== DATABASE EDITOR ===")
        print("1. Thêm node")
        print("2. Thêm nhãn cho node")
        print("3. Thêm cạnh")
        print("4. Xem hash table")
        print("0. Thoát")

        choice = input("Chọn: ")

        try:
            if choice == "1":
                name = input("Tên node: ")
                labels = input("Nhãn (phân cách bởi dấu phẩy): ").split(",")
                labels = [l.strip() for l in labels if l.strip()]
                editor.add_node(name, labels)

            elif choice == "2":
                node_id = int(input("Node ID: "))
                label = input("Nhãn mới: ")
                editor.add_label(node_id, label)

            elif choice == "3":
                u = int(input("From node: "))
                v = int(input("To node: "))
                t = int(input("Quãng đường: "))
                editor.add_edge(u, v, t)

            elif choice == "4":
                editor.print_hash_table()

            elif choice == "0":
                break

        except Exception as e:
            print("❌ Lỗi:", e)

if __name__ == "__main__":
    main()
