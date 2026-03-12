#include <vector>
#include <queue>
#include <climits>
#include <utility>
#include <algorithm>

extern "C" int find_path(
    int n,
    const int* adj_offsets,
    const int* adj_nodes,
    const int* adj_weights,
    int start,
    int end,
    int* out_path
) {
    std::vector<int> dist(n, INT_MAX);
    std::vector<int> prev(n, -1);
    std::vector<bool> visited(n, false);

    // (distance, node)
    std::priority_queue<
        std::pair<int, int>,
        std::vector<std::pair<int, int>>,
        std::greater<std::pair<int, int>>
    > pq;

    dist[start] = 0;
    pq.push({0, start});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (visited[u]) continue;
        visited[u] = true;

        if (u == end) break;

        for (int k = adj_offsets[u]; k < adj_offsets[u + 1]; k++) {
            int v = adj_nodes[k];
            int w = adj_weights[k];

            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                prev[v] = u;
                pq.push({dist[v], v});
            }
        }
    }

    // reconstruct path
    int len = 0;
    for (int v = end; v != -1; v = prev[v])
        out_path[len++] = v;

    std::reverse(out_path, out_path + len);
    return len;
}
