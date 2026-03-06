// logic/pathfinder.h
#ifndef PATHFINDER_H
#define PATHFINDER_H

extern "C" {

    /**
     * Tìm đường đi ngắn nhất từ start đến end
     *
     * @param n              số lượng node
     * @param adj_offsets    mảng offset (size n+1)
     * @param adj_nodes      danh sách đỉnh kề
     * @param adj_weights    trọng số tương ứng
     * @param start          node bắt đầu (index)
     * @param end            node kết thúc (index)
     * @param out_path       mảng output (ghi kết quả)
     *
     * @return số lượng node trên đường đi
     */
    int find_path(
        int n,
        const int* adj_offsets,
        const int* adj_nodes,
        const int* adj_weights,
        int start,
        int end,
        int* out_path
    );

} // extern "C"

#endif
