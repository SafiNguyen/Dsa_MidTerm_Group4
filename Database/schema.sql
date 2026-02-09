-- =========================
-- Schema for Campus Pathfinding Project
-- =========================

PRAGMA foreign_keys = ON;

-- =========================
-- TABLE: nodes
-- =========================
-- Lưu các nút trong trường
-- Mỗi nút đại diện cho một vị trí vật lý
-- (cổng, phòng học, toà nhà, ngã rẽ, ...)
-- =========================

CREATE TABLE IF NOT EXISTS nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL
);

-- =========================
-- TABLE: labels
-- =========================
-- Lưu nhãn (tên gọi) của các nút
-- Mỗi nhãn là duy nhất (được đảm bảo bởi HashTable + linear probing ở Python)
-- SQL chỉ enforce uniqueness
-- =========================

CREATE TABLE IF NOT EXISTS labels (
    label   TEXT PRIMARY KEY,
    node_id INTEGER NOT NULL,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
        ON DELETE CASCADE
);

-- =========================
-- TABLE: edges
-- =========================
-- Lưu các cạnh của đồ thị
-- Đại diện cho đường đi giữa hai nút
-- time: thời gian di chuyển (giây/phút tuỳ quy ước)
-- =========================

CREATE TABLE IF NOT EXISTS edges (
    from_node INTEGER NOT NULL,
    to_node   INTEGER NOT NULL,
    time      INTEGER NOT NULL CHECK (time > 0),

    FOREIGN KEY (from_node) REFERENCES nodes(node_id)
        ON DELETE CASCADE,
    FOREIGN KEY (to_node) REFERENCES nodes(node_id)
        ON DELETE CASCADE
);

-- =========================
-- OPTIONAL INDEXES
-- =========================
-- Không bắt buộc, chỉ để tăng tốc truy vấn
-- Không ảnh hưởng đến logic hashing
-- =========================

CREATE INDEX IF NOT EXISTS idx_edges_from
ON edges(from_node);

CREATE INDEX IF NOT EXISTS idx_edges_to
ON edges(to_node);
