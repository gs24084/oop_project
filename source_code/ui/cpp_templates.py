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


def dp_cpp_code():
    return """#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> dp(n + 1, 0);

    dp[0] = 1;

    for(int i = 1; i <= n; i++){
        dp[i] = dp[i - 1];
    }

    cout << dp[n] << "\\n";

    return 0;
}
"""