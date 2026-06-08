def default_cpp_code():
    return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    cout << n << "\\n";

    return 0;
}
"""


def graph_cpp_code():
    return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<vector<int>> g(n + 1);

    for(int i = 0; i < m; i++){
        int a, b;
        cin >> a >> b;
        g[a].push_back(b);
        g[b].push_back(a);
    }

    queue<int> q;
    vector<int> visited(n + 1, 0);

    q.push(1);
    visited[1] = 1;

    while(!q.empty()){
        int x = q.front();
        q.pop();

        cout << x << ' ';

        for(int nx : g[x]){
            if(!visited[nx]){
                visited[nx] = 1;
                q.push(nx);
            }
        }
    }

    return 0;
}
"""


def dijk_cpp_code():
    return """#include <bits/stdc++.h>
using namespace std;

using ll = long long;
const ll INF = 1e18;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<vector<pair<int, ll>>> graph(n + 1);

    for(int i = 0; i < m; i++){
        int u, v;
        ll w;
        cin >> u >> v >> w;

        graph[u].push_back({v, w});

        // 무방향 그래프라면 아래도 추가
        // graph[v].push_back({u, w});
    }

    int start;
    cin >> start;

    vector<ll> dist(n + 1, INF);

    priority_queue<
        pair<ll, int>,
        vector<pair<ll, int>>,
        greater<pair<ll, int>>
    > pq;

    dist[start] = 0;
    pq.push({0, start});

    while(!pq.empty()){
        auto [curDist, now] = pq.top();
        pq.pop();

        if(curDist != dist[now]) continue;

        for(auto [next, cost] : graph[now]){
            if(dist[next] > dist[now] + cost){
                dist[next] = dist[now] + cost;
                pq.push({dist[next], next});
            }
        }
    }

    for(int i = 1; i <= n; i++){
        if(dist[i] == INF) cout << "INF\\n";
        else cout << dist[i] << '\\n';
    }

    return 0;
}
"""


def dp_cpp_code():
    return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<long long> dp(n + 1, 0);

    dp[0] = 1;

    for(int i = 1; i <= n; i++){
        dp[i] = dp[i - 1];
    }

    cout << dp[n] << "\\n";

    return 0;
}
"""