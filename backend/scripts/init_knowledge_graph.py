"""
Initialize knowledge graph with predefined algorithm topics.

This script pre-populates the Neo4j knowledge graph with 22 fundamental
algorithm and data structure topics organized into categories, connected
by PREREQUISITE relationships.
"""

import asyncio
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, "/root/algo-edu-recommender/backend")

from src.db.neo4j import neo4j_execute_write, check_neo4j
from src.config import get_settings

settings = get_settings()


# Define 22 algorithm knowledge nodes organized by category
KNOWLEDGE_NODES = [
    # ── 基础 (6) ──
    {
        "node_id": "basics-variables",
        "title": "变量与数据类型",
        "category": "基础",
        "difficulty": "easy",
        "description": "编程中最基本的数据存储单元，包括整数、浮点数、字符串、布尔值等。",
        "content": "变量是存储数据的基本容器，数据类型决定了变量可以存储什么种类的数据以及如何解释它。",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "code_template": "# Python\nx = 10        # int\ny = 3.14      # float\nname = \"Alice\" # str\nis_valid = True # bool",
    },
    {
        "node_id": "basics-operators",
        "title": "运算符",
        "category": "基础",
        "difficulty": "easy",
        "description": "算术运算符、比较运算符、逻辑运算符、位运算符等。",
        "content": "运算符用于对变量和值进行操作，是构建表达式的基础。",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "code_template": "# 算术: +, -, *, /, //, %, **\n# 比较: ==, !=, <, >, <=, >=\n# 逻辑: and, or, not",
        "prerequisites": ["basics-variables"],
    },
    {
        "node_id": "basics-conditionals",
        "title": "条件语句",
        "category": "基础",
        "difficulty": "easy",
        "description": "if, elif, else 分支结构，用于根据条件选择执行路径。",
        "content": "条件语句让程序能够根据不同的情况做出不同的决策。",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "code_template": "if x > 0:\n    print('positive')\nelif x < 0:\n    print('negative')\nelse:\n    print('zero')",
        "prerequisites": ["basics-operators"],
    },
    {
        "node_id": "basics-loops",
        "title": "循环语句",
        "category": "基础",
        "difficulty": "easy",
        "description": "for 循环和 while 循环，用于重复执行代码块。",
        "content": "循环结构让程序能够重复执行一段代码，是算法实现的基础控制结构。",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "code_template": "# for 循环\nfor i in range(n):\n    print(i)\n\n# while 循环\nwhile condition:\n    do_something()",
        "prerequisites": ["basics-conditionals"],
    },
    {
        "node_id": "basics-functions",
        "title": "函数基础",
        "category": "基础",
        "difficulty": "easy",
        "description": "函数的定义、参数传递、返回值、作用域等基本概念。",
        "content": "函数是组织代码的基本单元，提高代码复用性和可读性。",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "code_template": "def greet(name: str) -> str:\n    return f\"Hello, {name}!\"\n\nresult = greet(\"Alice\")",
        "prerequisites": ["basics-loops"],
    },
    # ── 排序算法 (6) ──
    {
        "node_id": "sort-bubble",
        "title": "冒泡排序",
        "category": "排序",
        "difficulty": "easy",
        "description": "通过相邻元素比较和交换，将最大/最小元素逐步冒泡到序列一端。",
        "content": "冒泡排序是最简单的排序算法，平均时间复杂度 O(n²)，适合教学演示。",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "code_template": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
        "prerequisites": ["basics-loops"],
    },
    {
        "node_id": "sort-selection",
        "title": "选择排序",
        "category": "排序",
        "difficulty": "easy",
        "description": "在未排序序列中选择最小/最大元素，放到已排序序列的末尾。",
        "content": "选择排序无论数据如何分布，时间复杂度始终为 O(n²)。",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "code_template": "def selection_sort(arr):\n    for i in range(len(arr)):\n        min_idx = i\n        for j in range(i+1, len(arr)):\n            if arr[j] < arr[min_idx]:\n                min_idx = j\n        arr[i], arr[min_idx] = arr[min_idx], arr[i]\n    return arr",
        "prerequisites": ["basics-loops"],
    },
    {
        "node_id": "sort-insertion",
        "title": "插入排序",
        "category": "排序",
        "difficulty": "easy",
        "description": "将元素逐个插入已排序序列的正确位置，类似整理扑克牌。",
        "content": "插入排序对近乎有序的数据效率很高，最好情况 O(n)，广泛用于小规模或近乎有序数据的排序。",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "code_template": "def insertion_sort(arr):\n    for i in range(1, len(arr)):\n        key = arr[i]\n        j = i - 1\n        while j >= 0 and arr[j] > key:\n            arr[j+1] = arr[j]\n            j -= 1\n        arr[j+1] = key\n    return arr",
        "prerequisites": ["basics-loops"],
    },
    {
        "node_id": "sort-merge",
        "title": "归并排序",
        "category": "排序",
        "difficulty": "medium",
        "description": "分治策略，先递归分割数组，再合并两个有序子数组。",
        "content": "归并排序稳定且最坏情况 O(n log n)，适合外部排序和链表排序。",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "code_template": "def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i]); i += 1\n        else:\n            result.append(right[j]); j += 1\n    result.extend(left[i:]); result.extend(right[j:])\n    return result",
        "prerequisites": ["basics-functions", "sort-insertion"],
    },
    {
        "node_id": "sort-quick",
        "title": "快速排序",
        "category": "排序",
        "difficulty": "medium",
        "description": "分治策略，通过基准元素划分数组，递归排序子数组。",
        "content": "快速排序是实际应用中最常用的排序算法，平均 O(n log n)，原地排序空间 O(log n)。",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(log n)",
        "code_template": "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    mid = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + mid + quick_sort(right)",
        "prerequisites": ["basics-functions", "basics-loops"],
    },
    {
        "node_id": "sort-heap",
        "title": "堆排序",
        "category": "排序",
        "difficulty": "medium",
        "description": "利用堆这种完全二叉树结构进行的选择排序。",
        "content": "堆排序最坏、最好、平均都是 O(n log n)，但缓存性能不如快速排序。",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(1)",
        "code_template": "import heapq\n\ndef heap_sort(arr):\n    heapq.heapify(arr)\n    return [heapq.heappop(arr) for _ in range(len(arr))]",
        "prerequisites": ["sort-selection"],
    },
    # ── 搜索算法 (2) ──
    {
        "node_id": "search-binary",
        "title": "二分查找",
        "category": "搜索",
        "difficulty": "easy",
        "description": "在有序数组中每次将搜索范围缩小一半，时间复杂度 O(log n)。",
        "content": "二分查找是最基础的减治算法，必须在有序数据上操作。",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
        "code_template": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
        "prerequisites": ["basics-functions", "basics-conditionals"],
    },
    {
        "node_id": "search-hash",
        "title": "哈希表基础",
        "category": "搜索",
        "difficulty": "medium",
        "description": "通过哈希函数将键映射到数组索引，实现 O(1) 平均查找。",
        "content": "哈希表是工程中使用最广泛的常数时间查找数据结构。冲突处理方法包括链地址法和开放地址法。",
        "time_complexity": "O(1)",
        "space_complexity": "O(n)",
        "code_template": "hash_table = {}\n\n# 插入\nhash_table['name'] = 'Alice'\n\n# 查找\nif 'name' in hash_table:\n    print(hash_table['name'])\n\n# Python dict 使用开放地址+链表混合",
        "prerequisites": ["basics-functions"],
    },
    # ── 图论 (4) ──
    {
        "node_id": "graph-bfs",
        "title": "广度优先搜索 (BFS)",
        "category": "图论",
        "difficulty": "medium",
        "description": "从起点开始逐层遍历图，使用队列存储待访问节点。",
        "content": "BFS 找到的是无权图中的最短路径，常用于层次遍历和最短路径问题。",
        "time_complexity": "O(V+E)",
        "space_complexity": "O(V)",
        "code_template": "from collections import deque\n\ndef bfs(graph, start):\n    visited = set([start])\n    queue = deque([start])\n    while queue:\n        node = queue.popleft()\n        print(node)\n        for neighbor in graph[node]:\n            if neighbor not in visited:\n                visited.add(neighbor)\n                queue.append(neighbor)",
        "prerequisites": ["basics-functions", "basics-loops", "search-hash"],
    },
    {
        "node_id": "graph-dfs",
        "title": "深度优先搜索 (DFS)",
        "category": "图论",
        "difficulty": "medium",
        "description": "沿着一条路径走到尽头再回溯，使用栈或递归实现。",
        "content": "DFS 适合拓扑排序、连通分量检测、环检测等问题。递归实现简洁，迭代实现避免栈溢出。",
        "time_complexity": "O(V+E)",
        "space_complexity": "O(V)",
        "code_template": "def dfs_recursive(graph, node, visited=None):\n    if visited is None:\n        visited = set()\n    visited.add(node)\n    print(node)\n    for neighbor in graph[node]:\n        if neighbor not in visited:\n            dfs_recursive(graph, neighbor, visited)\n    return visited\n\ndef dfs_iterative(graph, start):\n    visited, stack = set(), [start]\n    while stack:\n        node = stack.pop()\n        if node not in visited:\n            visited.add(node)\n            stack.extend(graph[node])\n    return visited",
        "prerequisites": ["basics-functions", "basics-loops", "search-hash"],
    },
    {
        "node_id": "graph-dijkstra",
        "title": "Dijkstra 算法",
        "category": "图论",
        "difficulty": "hard",
        "description": "单源最短路径算法，使用优先队列优化，适用于非负权图。",
        "content": "Dijkstra 是贪心算法的经典应用，时间复杂度 O((V+E) log V)，使用斐波那契堆可达 O(E + V log V)。",
        "time_complexity": "O((V+E) log V)",
        "space_complexity": "O(V)",
        "code_template": "import heapq\n\ndef dijkstra(graph, start):\n    dist = {node: float('inf') for node in graph}\n    dist[start] = 0\n    pq = [(0, start)]\n    while pq:\n        d, u = heapq.heappop(pq)\n        if d > dist[u]:\n            continue\n        for v, w in graph[u]:\n            if dist[u] + w < dist[v]:\n                dist[v] = dist[u] + w\n                heapq.heappush(pq, (dist[v], v))\n    return dist",
        "prerequisites": ["graph-bfs", "search-hash"],
    },
    {
        "node_id": "graph-floyd",
        "title": "Floyd-Warshall 算法",
        "category": "图论",
        "difficulty": "hard",
        "description": "全源最短路径算法，动态规划方法，检测负环。",
        "content": "Floyd-Warshall 使用 DP 思想，dp[k][i][j] 表示经过前 k 个节点时 i 到 j 的最短路径。",
        "time_complexity": "O(V³)",
        "space_complexity": "O(V²)",
        "code_template": "def floyd_warshall(n, edges):\n    dist = [[float('inf')]*n for _ in range(n)]\n    for i in range(n):\n        dist[i][i] = 0\n    for u, v, w in edges:\n        dist[u][v] = w\n    for k in range(n):\n        for i in range(n):\n            for j in range(n):\n                if dist[i][k] + dist[k][j] < dist[i][j]:\n                    dist[i][j] = dist[i][k] + dist[k][j]\n    return dist",
        "prerequisites": ["graph-dijkstra"],
    },
    # ── 动态规划 (3) ──
    {
        "node_id": "dp-fibonacci",
        "title": "斐波那契数列",
        "category": "动态规划",
        "difficulty": "easy",
        "description": "经典的动态规划入门问题：F(n) = F(n-1) + F(n-2)。",
        "content": "通过记忆化或自底向上的 DP 将指数级复杂度优化到线性。",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "code_template": "# 自底向上 DP\ndef fib_dp(n):\n    if n <= 1:\n        return n\n    prev, curr = 0, 1\n    for _ in range(2, n+1):\n        prev, curr = curr, prev + curr\n    return curr\n\n# 记忆化递归\nfrom functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef fib_memo(n):\n    if n <= 1:\n        return n\n    return fib_memo(n-1) + fib_memo(n-2)",
        "prerequisites": ["basics-functions", "basics-loops"],
    },
    {
        "node_id": "dp-knapsack",
        "title": "0/1 背包问题",
        "category": "动态规划",
        "difficulty": "medium",
        "description": "每件物品只能选一次，在容量限制下最大化价值。",
        "content": "0/1 背包是 DP 的经典问题，状态 dp[i][w] 表示考虑前 i 件物品、容量为 w 时的最大价值。",
        "time_complexity": "O(n*W)",
        "space_complexity": "O(n*W)",
        "code_template": "def knapsack(weights, values, capacity):\n    n = len(weights)\n    dp = [[0]*(capacity+1) for _ in range(n+1)]\n    for i in range(1, n+1):\n        for w in range(capacity+1):\n            if weights[i-1] <= w:\n                dp[i][w] = max(\n                    dp[i-1][w],\n                    dp[i-1][w-weights[i-1]] + values[i-1]\n                )\n            else:\n                dp[i][w] = dp[i-1][w]\n    return dp[n][capacity]",
        "prerequisites": ["dp-fibonacci"],
    },
    {
        "node_id": "dp-lcs",
        "title": "最长公共子序列",
        "category": "动态规划",
        "difficulty": "medium",
        "description": "找两个序列的最长公共子序列（LCS），不要求连续。",
        "content": "LCS 广泛应用于字符串相似度比较、版本控制diff等。状态 dp[i][j] 表示 A 前 i 个和 B 前 j 个的 LCS 长度。",
        "time_complexity": "O(m*n)",
        "space_complexity": "O(m*n)",
        "code_template": "def lcs(s1, s2):\n    m, n = len(s1), len(s2)\n    dp = [[0]*(n+1) for _ in range(m+1)]\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            if s1[i-1] == s2[j-1]:\n                dp[i][j] = dp[i-1][j-1] + 1\n            else:\n                dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n    return dp[m][n]",
        "prerequisites": ["dp-fibonacci"],
    },
    # ── 其他 (3) ──
    {
        "node_id": "ds-union-find",
        "title": "并查集",
        "category": "其他",
        "difficulty": "medium",
        "description": "支持合并和查询的不相交集合数据结构。",
        "content": "并查集（Union-Find）通过路径压缩和按秩合并实现近乎 O(1) 的操作，常用于处理连通分量问题。",
        "time_complexity": "O(α(n))",
        "space_complexity": "O(n)",
        "code_template": "class UnionFind:\n    def __init__(self, n):\n        self.parent = list(range(n))\n        self.rank = [0]*n\n\n    def find(self, x):\n        if self.parent[x] != x:\n            self.parent[x] = self.find(self.parent[x])\n        return self.parent[x]\n\n    def union(self, x, y):\n        px, py = self.find(x), self.find(y)\n        if px == py:\n            return\n        if self.rank[px] < self.rank[py]:\n            px, py = py, px\n        self.parent[py] = px\n        if self.rank[px] == self.rank[py]:\n            self.rank[px] += 1",
        "prerequisites": ["basics-functions", "basics-loops"],
    },
    {
        "node_id": "ds-segment-tree",
        "title": "线段树",
        "category": "其他",
        "difficulty": "hard",
        "description": "用于区间查询和更新的二叉树结构。",
        "content": "线段树是一种平衡二叉树，能在 O(log n) 时间内完成区间修改和区间查询，广泛应用于 RMQ 和区间和等问题。",
        "time_complexity": "O(log n)",
        "space_complexity": "O(n)",
        "code_template": "class SegmentTree:\n    def __init__(self, arr):\n        self.n = len(arr)\n        self.tree = [0]*(4*self.n)\n        self._build(arr, 0, 0, self.n-1)\n\n    def _build(self, arr, node, l, r):\n        if l == r:\n            self.tree[node] = arr[l]\n        else:\n            mid = (l+r)//2\n            self._build(arr, 2*node+1, l, mid)\n            self._build(arr, 2*node+2, mid+1, r)\n            self.tree[node] = self.tree[2*node+1] + self.tree[2*node+2]\n\n    def query(self, ql, qr):\n        return self._query(0, 0, self.n-1, ql, qr)",
        "prerequisites": ["basics-functions", "basics-loops", "graph-dfs"],
    },
]


async def create_node(node: dict) -> None:
    """Create a single knowledge node."""
    cypher = """
    MERGE (n:KnowledgeNode {node_id: $node_id})
    SET n.title = $title,
        n.description = $description,
        n.category = $category,
        n.difficulty = $difficulty,
        n.content = $content,
        n.code_template = $code_template,
        n.time_complexity = $time_complexity,
        n.space_complexity = $space_complexity,
        n.mastery_level = 0.0,
        n.created_at = datetime(),
        n.updated_at = datetime()
    """
    await neo4j_execute_write(cypher, node)


async def create_prerequisite_links(prerequisites: list[str], target_id: str) -> None:
    """Create PREREQUISITE relationships."""
    for pre_id in prerequisites:
        cypher = """
        MATCH (a:KnowledgeNode {node_id: $source_id})
        MATCH (b:KnowledgeNode {node_id: $target_id})
        MERGE (a)-[:PREREQUISITE]->(b)
        """
        await neo4j_execute_write(cypher, {"source_id": pre_id, "target_id": target_id})


async def create_index() -> None:
    """Create indexes for better query performance."""
    indexes = [
        "CREATE INDEX knowledge_node_id IF NOT EXISTS FOR (n:KnowledgeNode) ON (n.node_id)",
        "CREATE INDEX knowledge_category IF NOT EXISTS FOR (n:KnowledgeNode) ON (n.category)",
        "CREATE INDEX knowledge_difficulty IF NOT EXISTS FOR (n:KnowledgeNode) ON (n.difficulty)",
    ]
    for idx in indexes:
        try:
            await neo4j_execute_write(idx, {})
        except Exception:
            pass  # Index might already exist


async def main() -> None:
    """Initialize the knowledge graph with predefined nodes."""
    print("🚀 Initializing knowledge graph...")

    # Check Neo4j connection
    if not await check_neo4j():
        print("❌ Cannot connect to Neo4j. Make sure it's running.")
        return

    print(f"📊 Creating {len(KNOWLEDGE_NODES)} knowledge nodes...")

    # Create all nodes
    for i, node in enumerate(KNOWLEDGE_NODES, 1):
        await create_node(node)
        print(f"  [{i}/{len(KNOWLEDGE_NODES)}] ✓ {node['node_id']}")

    print("\n🔗 Creating prerequisite relationships...")

    # Create prerequisite links
    link_count = 0
    for node in KNOWLEDGE_NODES:
        prereqs = node.get("prerequisites", [])
        if prereqs:
            await create_prerequisite_links(prereqs, node["node_id"])
            link_count += len(prereqs)
            print(f"  ✓ {node['node_id']} ← {prereqs}")

    print(f"\n📈 Creating indexes...")
    await create_index()

    print(f"""
✅ Knowledge graph initialized successfully!

Summary:
  • {len(KNOWLEDGE_NODES)} nodes created
  • {link_count} prerequisite relationships
  • 6 categories: 基础, 排序, 搜索, 图论, 动态规划, 其他

Categories:
  • 基础: basics-variables, basics-operators, basics-conditionals, basics-loops, basics-functions
  • 排序: sort-bubble, sort-selection, sort-insertion, sort-merge, sort-quick, sort-heap
  • 搜索: search-binary, search-hash
  • 图论: graph-bfs, graph-dfs, graph-dijkstra, graph-floyd
  • 动态规划: dp-fibonacci, dp-knapsack, dp-lcs
  • 其他: ds-union-find, ds-segment-tree
""")


if __name__ == "__main__":
    asyncio.run(main())
