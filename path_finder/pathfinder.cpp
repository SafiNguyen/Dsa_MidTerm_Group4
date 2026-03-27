#include <algorithm>
#include <climits>
#include <cmath>

float powf(int n, int p){
    if(p==1) return n;
    if(p==0) return 1;
    float u = powf(n,p/2);
    if(p%2==0) return u*u;
    return u*u*n;
}

int max(int a,int b){
    return (a>b?a:b);
}

extern "C" {

int find_path(
    int n,
    const int* adj_offsets,
    const int* adj_nodes,
    const int* adj_weights,
    int start,
    int end,
    int* out_path
) {
    if (start < 0 || start >= n || end < 0 || end >= n) return 0;
    if (start == end) {
        out_path[0] = start;
        return 1;
    }

    const int INF = INT_MAX;

    // 1. Tính toán Delta (Step Size) - Tính một lần duy nhất
    float log_n = std::log2f((float)(n > 1 ? n : 2));
    int k_param = max(2, (int)powf(log_n, 0.3333f));
    int delta = max(1, (int)(log_n / (float)k_param));

    // 2. Cấp phát mảng phẳng thay cho std::vector/deque để tối ưu Cache
    int* dist = new int[n];
    int* prev = new int[n];
    bool* in_frontier = new bool[n];
    
    // Hai mảng này thay thế cho std::deque (Frontier và Next Frontier)
    int* frontier = new int[n];
    int* next_frontier = new int[n];
    int f_size = 0, nf_size = 0;

    for (int i = 0; i < n; i++) {
        dist[i] = INF;
        prev[i] = -1;
        in_frontier[i] = false;
    }

    dist[start] = 0;
    frontier[f_size++] = start;
    in_frontier[start] = true;

    // 3. Vòng lặp chính xử lý theo dải khoảng cách
    while (f_size > 0) {
        nf_size = 0;
        
        // Tìm d_min thực tế trong frontier
        int current_min_dist = INF;
        for (int i = 0; i < f_size; ++i) {
            if (dist[frontier[i]] < current_min_dist) 
                current_min_dist = dist[frontier[i]];
        }

        int threshold = current_min_dist + delta;

        // Xử lý các đỉnh trong cửa sổ [d_min, d_min + delta]
        // Sử dụng mảng phẳng giúp CPU prefetch dữ liệu tốt hơn deque
        for (int i = 0; i < f_size; ++i) {
            int u = frontier[i];

            if (dist[u] > threshold) {
                next_frontier[nf_size++] = u;
                continue;
            }

            in_frontier[u] = false;

            for (int idx = adj_offsets[u]; idx < adj_offsets[u + 1]; ++idx) {
                int v = adj_nodes[idx];
                int w = adj_weights[idx];
                int new_dist = dist[u] + w;

                if (new_dist < dist[v]) {
                    dist[v] = new_dist;
                    prev[v] = u;

                    if (!in_frontier[v]) {
                        if (w <= delta) {
                            // Short-cut: Thêm trực tiếp vào frontier hiện tại
                            // Để tránh làm hỏng vòng lặp i, ta mở rộng f_size 
                            // nhưng cần đảm bảo i không vượt quá n.
                            frontier[f_size++] = v;
                        } else {
                            next_frontier[nf_size++] = v;
                        }
                        in_frontier[v] = true;
                    }
                }
            }
        }

        // Dừng sớm nếu đã tìm thấy end ổn định
        if (dist[end] != INF && current_min_dist > dist[end]) break;

        // Swap frontier và next_frontier
        std::swap(frontier, next_frontier);
        f_size = nf_size;
    }

    int path_len = 0;
    if (dist[end] != INF) {
        for (int v = end; v != -1; v = prev[v]) {
            out_path[path_len++] = v;
        }
        for (int i = 0; i < path_len / 2; ++i) {
            int tmp = out_path[i];
            out_path[i] = out_path[path_len - 1 - i];
            out_path[path_len - 1 - i] = tmp;
        }
    }

    delete[] dist; delete[] prev; delete[] in_frontier;
    delete[] frontier; delete[] next_frontier;

    return path_len;
}

} 