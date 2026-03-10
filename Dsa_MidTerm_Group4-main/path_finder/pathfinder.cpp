#include <climits>
#include <utility>

struct LinkedList {
    int val, dist;
    LinkedList *next, *prev;

    LinkedList(int v, int d): val(v), dist(d), next(nullptr), prev(nullptr) {}

    static void push(int val, int dist,
                     LinkedList *&head,
                     LinkedList *&tail) {
        if (!head) {
            head = tail = new LinkedList(val, dist);
        } else {
            tail->next = new LinkedList(val, dist);
            tail->next->prev = tail;
            tail = tail->next;
        }
    }

    static void del(LinkedList *node,
                    LinkedList *&head,
                    LinkedList *&tail) {
        if (!node) return;

        if (node == head && node == tail) {
            head = tail = nullptr;
        } else if (node == head) {
            head = head->next;
            if (head) head->prev = nullptr;
        } else if (node == tail) {
            tail = tail->prev;
            if (tail) tail->next = nullptr;
        } else {
            node->prev->next = node->next;
            node->next->prev = node->prev;
        }
        delete node;
    }
};

extern "C" int find_path(
    int n,
    const int* adj_offsets,
    const int* adj_nodes,
    const int* adj_weights,
    int start,
    int end,
    int* out_path
) {
    int* dist = new int[n];
    int* prev = new int[n];
    LinkedList** inList = new LinkedList*[n];

    for (int i = 0; i < n; i++) {
        dist[i] = INT_MAX;
        prev[i] = -1;
        inList[i] = nullptr;
    }

    LinkedList *head = nullptr, *tail = nullptr;

    dist[start] = 0;
    LinkedList::push(start, 0, head, tail);
    inList[start] = head;

    while (head) {
        int pivot = head->dist;
        LinkedList* cur = head;

        while (cur) {
            LinkedList* next = cur->next;
            int u = cur->val;

            if (cur->dist <= pivot) {
                for (int k = adj_offsets[u]; k < adj_offsets[u + 1]; k++) {
                    int v = adj_nodes[k];
                    int w = adj_weights[k];

                    if (dist[u] != INT_MAX && dist[u] + w < dist[v]) {
                        dist[v] = dist[u] + w;
                        prev[v] = u;

                        if (!inList[v]) {
                            LinkedList::push(v, dist[v], head, tail);
                            inList[v] = tail;
                        } else {
                            inList[v]->dist = dist[v];
                        }
                    }
                }
            }

            inList[u] = nullptr;
            LinkedList::del(cur, head, tail);
            cur = next;
        }
    }

    int len = 0;
    for (int v = end; v != -1; v = prev[v])
        out_path[len++] = v;

    for (int i = 0; i < len / 2; i++)
        std::swap(out_path[i], out_path[len - 1 - i]);

    delete[] dist;
    delete[] prev;
    delete[] inList;

    // dọn list nếu còn (an toàn tuyệt đối)
    while (head)
        LinkedList::del(head, head, tail);

    return len;
}
