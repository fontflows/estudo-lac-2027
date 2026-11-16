"""Build pipeline/raw/apac.json for the ICPC Asia Pacific Championship (2024-2026).

Solve counts come from the official DOMjudge final standings archived by ICPC Japan
(storage.googleapis.com/files.icpc.jp/championship<year>/standings.html), parsed by
apac_parse_standings.py. Statement summaries / solution ideas were written from the official
problem sets and the judges' "Problem Analysis" PDFs (downloads/apac/).
CF ratings/tags were read from the Codeforces API (problemset.problems) via WebFetch.

Usage (from pipeline/):  python -I scripts/apac_build.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apac_parse_standings as ps  # noqa: E402

ROOT = os.path.dirname(HERE)
DL = os.path.join(ROOT, "downloads", "apac")
G = "https://storage.googleapis.com/files.icpc.jp/championship{y}/"

CONTESTS = {
    2024: dict(date="2024-03-02", cf=1938, venue="Hanoi, Vietnam",
               statements="tasks.pdf", editorial="analysis.pdf"),
    2025: dict(date="2025-03-01", cf=2073, venue="Singapore (NUS)",
               statements="problemset.pdf", editorial="problem-analysis.pdf"),
    2026: dict(date="2026-03-08", cf=2206, venue="Taoyuan, Taiwan",
               statements="problemset.pdf", editorial="problemset-analysis.pdf"),
}

# CF ratings / tags (Codeforces mirror contests are on the main problemset).
CF = {
    2024: {"A": (3500, []), "B": (3000, []), "C": (1900, []), "D": (3300, []), "E": (2200, []),
           "F": (2400, []), "G": (2300, []), "H": (1600, []), "I": (2800, []), "J": (2100, []),
           "K": (2400, []), "L": (2800, []), "M": (3500, [])},
    2025: {"A": (1900, []), "B": (3500, []), "C": (2700, []), "D": (2400, []),
           "E": (3300, ["interactive"]), "F": (3500, []), "G": (2200, []),
           "H": (2700, ["interactive"]), "I": (3100, []), "J": (2000, []), "K": (2900, []),
           "L": (1300, []), "M": (3300, [])},
    2026: {"A": (3500, ["interactive"]), "B": (2500, ["binary search", "games", "trees"]),
           "C": (2200, ["dfs and similar"]), "D": (2600, ["data structures", "dp", "trees"]),
           "E": (2500, ["data structures", "geometry"]), "F": (2400, ["fft", "number theory"]),
           "G": (3100, ["graphs"]), "H": (1800, ["number theory"]),
           "I": (2900, ["combinatorics", "dp", "math", "number theory"]), "J": (1700, ["math"]),
           "K": (1300, ["binary search"]), "L": (3500, []), "M": (2900, [])},
}

# letter -> (statement_summary, solution_idea, candidate_tags)
P = {}
P[2024] = {
    "A": ("Strings over {A,P}; operations: replace P by APA, replace A by PAP, delete a block of exactly a consecutive A's or p consecutive P's (5<=a,p<=20). Decide whether S can be transformed into E (|S|,|E|<=50) and output a sequence of at most 35000 operations.",
          "Treat the operations as relations of a group presentation (A^a = P^p = 1, P = APA, A = PAP); derived moves give A^4 = P^4 = 1 so exponents reduce to gcd(a,4), gcd(p,4), and every word reduces to one of 8 normal forms (A..AAAA, P, AP, AAP, AAAP). The group is a quotient of the quaternion group Q8 (trivial, Z2, Z2xZ2 or Q8), so S->E is possible iff both map to the same group element. Construct the answer with a rewriting procedure (delete A^a, rewrite rightmost PA, leftmost PP, insert AAAA) to normal form, then reverse the procedure for E; step count ~8nk+24k^2.",
          ["group theory word problem", "string rewriting normal form", "quaternion group invariant", "constructive output", "gcd reduction"]),
    "B": ("Planar straight-line graph with n<=1e5 cities and m<=3e5 weighted highways; score of a vertex subset = sum of edge weights inside minus 1e6*(number of missing pairs)^2. Maximize over non-empty subsets.",
          "Penalty argument plus planarity (<=3v-6 edges) show the optimum is a clique (<=4 vertices, K5 is non-planar) or a clique missing one edge (<=5 vertices). Enumerate all O(n) cliques with a degeneracy order: repeatedly remove a min-degree vertex u (degree<=5) and brute-force subsets of its neighbourhood. For 'clique minus one edge' with the missing edge not at u, the extra vertex d forms a 4-clique with the three neighbours, so precomputed best clique extensions give it in O(1). O(n log n).",
          ["planar graph degeneracy", "clique enumeration", "bounded degree brute force", "case analysis on penalty", "graph"]),
    "C": ("Given a sequence a_1..a_n (n<=5e5, a_i<=60), find the smallest x>=0 with popcount(x+i-1)=a_i for all i, or -1.",
          "If p(y)-p(y+1)=t>=0 then y ends with exactly t+1 ones preceded by a 0. Take the first index k of the maximum value: the drop a_k-a_{k+1} fixes the low t+1 bits of x+k-1, and maximality forces the minimal completion to be (1^s 0 1^{t+1}) with s=a_k-(t+1) (or 2^{a_n}-1 when k=n). Compute x from that, then verify all popcounts in O(n); reject if s<0, x<0 or a mismatch.",
          ["bit manipulation", "popcount", "constructive minimal number", "observation on carries"]),
    "D": ("Count r x c binary grids (r multiple of 6 up to 66666, c multiple of 7 up to 77777) in which every 6x7 subgrid has the same number of ones, modulo 998244353.",
          "Equal window sums give the 'quadrangle equation' g[i][j]+g[i-6][j-7]=g[i-6][j]+g[i][j-7], so the grid is determined by the first 6 rows and 7 columns, and each residue cell (i,j) of the 6x7 lattice is constant, horizontally striped or vertically striped. Fix the stripe type per residue cell, count fillings with products of binomial sums (row/column sum constraints) and handle overlaps by inclusion-exclusion into 'strictly vertical' vs 'horizontal'. Summing over 2^42 type assignments is done with a DP with pruning or with generating functions per row raised to the 6th power via FFT/NTT.",
          ["combinatorics counting", "inclusion-exclusion", "generating functions", "ntt polynomial power", "grid periodicity structure"]),
    "E": ("n x n matrix (n<=100) with values in 1..n; change the minimum number of entries so every row and every column contains a duplicate value, and output the changes.",
          "Call a row/column colorful if all values distinct; one change fixes at most one row and one column, so the answer is at least max(#colorful rows, #colorful columns). It is achievable greedily: while both a colorful row i and colorful column j exist, change (i,j) to any other value; when only colorful columns remain, change an entry in the first row of that column to a value that creates a duplicate in the column while keeping row 1 non-colorful (symmetric for rows). O(n^2)-O(n^3).",
          ["greedy", "lower bound matching construction", "constructive", "matrix"]),
    "F": ("n students (n<=1e6) in a fixed line except student 1 who chooses where to stand; choose k>1 dividing n, assign positions round-robin into k groups; minimize max group sum / min group sum, output as reduced fraction.",
          "For fixed k, slide student 1 from the leftmost position to the right: each shift changes the sums of only two groups, so maintain group sums in a multiset to get max/min in O(log n) per shift. Merging pairs of groups never worsens the ratio, so k only needs to be prime divisors of n (<=7 of them). Compare fractions with cross multiplication; O(7 n log n).",
          ["sliding simulation", "multiset max min", "number theory prime divisors", "fraction comparison", "exchange argument"]),
    "G": ("n<=5000 answer strings of length m<=3000 over A-Z or '.'; two students are similar if they share >=k (k<=5) identical answered questions. Find the similar pair with smallest b, then largest a, or -1.",
          "Process students b in order and increment a counter for every earlier i that matches b on each answered question (iterate only over earlier students with the same letter in that column via per-(column,letter) lists). Stop as soon as a counter reaches k: before that every pair counter is <k, so the total number of increments is bounded by (k-1)*C(n,2) (pigeonhole/amortization). O(nm*sigma + k n^2).",
          ["amortized counting", "pigeonhole bound", "brute force with early termination", "strings"]),
    "H": ("n tables each with a binary string of orders; move the minimum number of people (no new tables) so that every table is monochromatic (or empty).",
          "Per table, moving the minority bits is optimal if minorities can be absorbed by existing tables whose majority has that type. If all tables have the same majority type, one table must be dedicated to the other type (paying its majority instead of minority); choose the best such table in one pass. Alternatively a DP over tables with a 4-bit mask (need table for 0/1, dedicated table for 0/1). O(total length).",
          ["greedy", "case analysis", "bitmask dp", "counting"]),
    "I": ("Convex polygon with n<=30 vertices (integer coords <=1000); find the minimum-area convex point-symmetric region having all vertices on its boundary, or -1.",
          "For center X, the reflected points Q_i=2X-P_i together with P_i must all be on their convex hull. The n^2 lines through (P_a+P_b)/2 and (P_{a+1}+P_b)/2 partition the plane into cells where every orientation test is fixed, so validity is constant and the hull area is linear in X inside each cell; hence the minimum is attained at an arrangement vertex. Enumerate the O(n^4) pairwise line intersections, check validity and compute hull area for each: O(n^5 log n).",
          ["computational geometry", "convex hull", "line arrangement vertices", "linear function minimum at vertex", "point symmetry"]),
    "J": ("Undirected weighted graph (n<=1e5, m<=3e5); travel 1->n and back n->1 by walks whose sets of used roads differ; minimize total time or -1.",
          "One trip is a shortest path P (Dijkstra). The other must use some edge not in P (any walk inside a simple shortest path's edge set uses all of it), and walks may repeat edges, so its cost is min over edges (u,v) not on P of dist1[u]+w+distn[v] (both orientations). Answer = d(1,n) + that minimum. Two Dijkstras, O(m log n).",
          ["dijkstra", "second shortest walk", "shortest path from both ends", "graph"]),
    "K": ("Rooted tree n<=1e5; array L of all n^2 values (x-1)n^2+(LCA(x,y)-1)n+(y-1) sorted; answer q<=1e5 queries for the k-th element.",
          "x = ceil(k/n); within x, count pairs per LCA: ancestor a_i of x contributes |S(a_i) \\ S(a_{i-1})| values of y. A persistent segment tree indexed by node label storing these counts (moving x across an edge changes two entries) finds the LCA l by k-th-sum descent. Then find the m'-th smallest y in S(l)\\S(child) using persistent segment trees over subtree membership built by small-to-large (heavy child reuse), and descend on the difference of two trees. O((n+q) log^2 n).",
          ["persistent segment tree", "kth order statistic", "lca", "small to large", "tree"]),
    "L": ("Given a_1..a_n (n<=2e5, a_i<2^30), an operation picks i!=j and XORs a_i^a_j into both b_i and b_j (B starts at 0). Count reachable sequences B mod 998244353.",
          "View as vectors over GF(2): reachable set is the span of vectors v_ij with a_i+a_j in blocks i and j, so the answer is 2^rank. Replace a_i by 2a_i+1 (parity bit) and let s be the rank of these vectors (linear basis); the rank of the system is C(s,2)+(n-s)(s-1). Linear basis O(n*30), answer by fast power.",
          ["linear algebra gf2", "xor basis", "rank counting", "math"]),
    "M": ("Count compositions of n (n<=3e5, up to 3e5 queries) whose parts alternate up/down (a1<a2>a3<... or a1>a2<a3>...), mod 998244353.",
          "Count via inclusion-exclusion turning each '>' into 'no condition' minus '<=': weighted 'almost increasing' compositions a1<a2<=a3<a4... have length O(sqrt n), so their signed counts a(n) come from a DP over (sum, length) in O(N^1.5). Concatenations of blocks give C(x)=1/(1-A(x)), computed with one power-series inverse via NTT in O(N log N); the other parity/shape cases are handled the same way.",
          ["generating functions", "inclusion-exclusion", "power series inverse ntt", "partition dp sqrt length", "combinatorics"]),
}
P[2025] = {
    "A": ("r x c grid (r,c<=2000) with blocked cells; count ordered placements of 4 towers in distinct empty cells such that consecutive towers share a row or column.",
          "DP over tower index: DP[k][cell] = ways with tower k at cell, transitions via precomputed row sums and column sums of DP[k-1] (excluding the same cell). This forbids only adjacent coincidences; remove the cases A=C or B=D with inclusion-exclusion (SUM4 - 2*SUM3 + SUM2) and A=D separately (A,B,C collinear in one row/column: subtract p(p-1)(p-2) per row/column with p empty cells). O(rc).",
          ["dp on grid", "row column prefix sums", "inclusion-exclusion", "counting"]),
    "B": ("Embed a graph with n<=1600 vertices, max degree 5, in the integer cube [0,400]^3: vertices at z=0, edges as axis-parallel polylines with <=30 nodes, no intersections.",
          "Constructive: each vertex gets a gadget fanning its <=5 edge ports. Greedy edge colouring partitions the edges into few matchings; each matching is routed on its own pair of z-layers without collisions. To fit the box, arrange gadgets in a sqrt(n)/3 x d grid, colour a contracted graph (columns of gadgets) into 10d-1 matchings, and route same-column edges in single layers; dimensions become about 9sqrt(n) x 3sqrt(n) x 7sqrt(n) <= 400. O(n sqrt n).",
          ["constructive", "graph embedding", "greedy edge coloring", "matching decomposition", "sqrt grid layout"]),
    "C": ("Given a cactus (n<=1e5, m<=2e5), compute its connectivity value: smallest k such that every k-edge-connected supergraph stays connected after deleting the cactus edges.",
          "Prove connectivity value = max-cut + 1 (a max cut S|T can be padded with cliques to show mc is insufficient; any larger cut contradicts the max). Max-cut of a cactus: take a spanning tree, 2-colour it, count all tree edges plus non-tree edges whose endpoints differ, i.e. m minus the number of odd cycles. Answer = that + 1, O(n+m).",
          ["max cut", "cactus graph", "bipartite coloring", "proof by cut argument", "dfs spanning tree"]),
    "D": ("Array p of rods (1..3) for disks 1..n; q<=1e5 operations: point update of p_x, or query the minimum number of Tower-of-Hanoi moves to gather disks l..r (initially on rods p_i) on rod 1, mod 998244353.",
          "Reverse view: from the largest disk down, if the current disk is not where it must go, all smaller disks must first go to the third rod, costing 2^x-1 for x smaller disks plus the move; the target rod for smaller disks is determined by the block. For a block of disks store, for each of 3 target rods, the number of moves and the rod required for the smaller disks above it; blocks compose associatively, so keep them in a segment tree (function composition) with point updates. O((n+q) log n).",
          ["segment tree", "function composition", "tower of hanoi recursion", "powers of two modular", "point update range query"]),
    "E": ("Interactive: hidden fully-parenthesized expression with n<=200 leaves using the binary operator a-b = a AND NOT b; query any assignment of bits to leaves (<=500 queries) and identify the expression.",
          "Determine the parenthesis pattern around each leaf from left to right. Knowing the prefix, set to 1 only the leaves that directly lie on the nesting chain of the current leaf (others 0), which reduces the expression to x-(x-(x-(...?x?...))). A small decision tree of queries distinguishes '(x', 'x', 'x)', 'x))', ... using 2 queries for open/plain and about r/2+2 for closing r parentheses; amortized total <= 2.5n queries.",
          ["interactive", "expression parsing", "adaptive queries", "amortized query count", "boolean logic"]),
    "F": ("n<=1e9 rooms on a line, m<=1e5 characters at r_i with movement cost s_i per step; the star must reach character m by relays (pick up, carry, drop). Answer q<=1e5 levels with different star start l_j: minimum total cost.",
          "Assume the star is right of character m (mirror the other side). Optimal strategy: one first carrier (possibly walking right to fetch, or left) and then a relay of characters at their own positions with strictly decreasing s (suffix-minimum chain between r_m and l_j). Sort levels by l_j, maintain the suffix-minimum chain with a monotonic stack and dp[x] = cost of relay starting from x; the fetch cost for each first carrier is linear in l_j, so query min over lines with a convex hull trick (plus suffix minima of dp for left-moving carriers). O((m+q) log).",
          ["greedy structure", "monotonic stack", "convex hull trick", "offline sorting queries", "dp"]),
    "G": ("Bit string B (n<=1e5) can repeatedly have two adjacent bits replaced by their AND; decide whether it can become C.",
          "Merging a contiguous block gives AND of the block, so run-length encode B: runs can be shortened to any positive length, and blocks containing a 0 merge several runs into one 0 (deleting 1-runs in between). Greedily match C's runs left to right with a pointer in B: a 0-run of length k consumes runs until k zeros are covered, a 1-run needs a later B run of ones with length >=k. Also B's first/last run being 0 forces C's to be 0. O(n+m).",
          ["greedy two pointers", "run length encoding", "string transformation", "invariants"]),
    "H": ("Interactive: n<=100 hidden flowers (lily/rose); queries: type of flower i, or l_j*r_j (lilies in prefix j times roses in suffix). With <=10 queries find k with l_k=r_k.",
          "Key insight: k = total number of roses always works. Binary search with type queries (dummy rose at 0, lily at n+1) for a position x with rose at x and lily at x+1, then use two multiply queries among x-1,x,x+1 (they give l_x(r_x+1), l_x r_x, (l_x+1) r_x) to solve for l_x and r_x, hence the number of roses. ceil(log2 n)+2 queries.",
          ["interactive", "binary search", "invariant observation", "math equations"]),
    "I": ("n x n unit grid (n<=2000); for q<=1e5 real areas s, count squares (any orientation) whose 4 vertices lie on cell boundaries, or -1 if infinitely many.",
          "Classify: squares with all vertices on grid corners (not all on the border) give 'unlimited' areas; otherwise the vertices alternate horizontal/vertical edge points (or are border lattice points) and the square is centred at a lattice point or a cell centre. For a pivot centre, each unit grid segment in one quadrant yields an interval of areas 2d^2 for its vertex, weighted by the number of translations of the centre that keep the square inside; collect O(n^2) weighted intervals plus the set of unlimited areas, then sweep intervals against sorted queries. O((n^2+q) log n).",
          ["computational geometry", "counting squares", "sweep line over intervals", "offline queries", "case analysis"]),
    "J": ("n<=500 sharks on a line, group numbers a permutation; repeatedly the group b moves to the position of the next-smaller existing group number c and they merge (keeping number b). Minimize total travel time.",
          "Relabel by group number with positions pos[i]; a merge means element x erases its successor y in the current list at cost |pos[x]-pos[y]|, preserving relative order. Interval DP: dp[l][r] = min cost for l to absorb l+1..r; choose p, the last element absorbed directly by l: dp[l][r] = min_p dp[l][p-1] + dp[p][r] + |pos[l]-pos[p]|. O(n^3).",
          ["interval dp", "merge order", "dynamic programming"]),
    "K": ("Permutation of n<=5e5 books; operations: adjacent swap, move a book to the front, move a book to the back. Minimum number of operations to sort.",
          "Optimal: books with labels < l are moved to the front, > r to the back, labels l..r are sorted with adjacent swaps, costing (l-1)+(n-r)+inv(a_l..a_r) where a is the inverse permutation. Maximize f(l,r)=r-l-inv over intervals by sweeping r and maintaining the set S_r of 'record' left ends where f increases by exactly 1 each; a new element a_{r+1} with existing larger elements a_l removes the largest member of S that is <= l per inversion; std::set with amortized deletions gives O(n log n).",
          ["inversion count", "sweep line", "ordered set", "amortized analysis", "permutations"]),
    "L": ("Snake-like queue of n travelers in an r x c grid (consecutive travelers adjacent); each step the front leaves and everyone moves into the previous traveler's cell. For traveler p, compute the fraction of other travelers that are ever adjacent to p before p boards.",
          "After p-i steps you occupy traveler i's initial cell and traveler j+(p-i) occupies traveler j's initial cell. So for each i<=p and each grid neighbour j of traveler i's cell, mark traveler j+(p-i) (if <=n and != p). Count distinct marks, output count/(n-1). O(rc).",
          ["simulation", "grid", "index shifting observation", "counting"]),
    "M": ("n<=1e5 marked points; from S choose marked P,Q, set T=P+(Q-S) and move anywhere on segment ST. For q<=1e5 queries decide whether (c,d) is reachable from (a,b).",
          "Case analysis: with one marked point you can reach exactly the segment from S to its reflection through P; with two points (or all points collinear) you can translate by integer multiples of the direction vectors between marked points and reach exactly the open strip between two lines parallel to the marked line (plus specific lattice points on the boundary lines; collinear corner cases); with three non-collinear points everything is reachable. Implement with cross products (side-of-line tests) and checks that boundary points differ from S by an integer multiple of the marked direction vector. O(n+q).",
          ["computational geometry", "case analysis", "reflection and translation", "cross product", "strip region reachability"]),
}
P[2026] = {
    "A": ("Interactive: hidden string of length n<=1000 over a-z; query compares suffixes S(i) and S(j). Output the suffix array using at most 6260 queries (~6n+25log n).",
          "Insert suffixes from the end (S(n) down to S(1)) into the sorted order. Adjacent sorted suffixes whose successor suffixes are out of order must start with different letters ('splitting positions'), at most 25 of them, which partition the order into <=26 letter blocks. Binary search the new suffix S(k) over block representatives (indices y with S(p_y+1) < S(k+1), known from the existing order), then one confirm query; only when a new splitting position appears (<=25 times) fall back to a full binary search. Total n(log2 26 + 1) + 25 log2 n queries.",
          ["interactive", "suffix array", "binary insertion", "alphabet size bound", "string comparisons"]),
    "B": ("Rooted tree n<=5e5, leaves labelled by their index; players alternately delete a subtree as long as a labelled leaf remains; first player minimizes, second maximizes the final remaining leaf. Find the result.",
          "Binary search on the answer v: label leaves <=v as F (good for minimizer) and >v as S. For the binary game define D(leaf)=+1/-1 and D(x)=sign(sum of D over children); by induction D>0 means F wins regardless of who starts, D<0 means S wins, D=0 means the player to move wins. Evaluate D bottom-up in O(n) per check, O(n log n) total.",
          ["game theory", "binary search on answer", "tree dp", "induction on game states"]),
    "C": ("Dijkstra implemented with a max-heap on a connected graph (n<=1e5, m<=2e5); given the visiting order S, assign weights in [1,1e9] so the buggy algorithm produces S, or report impossible.",
          "A max-heap Dijkstra always continues from the most recently reached vertex with the largest distance, so the visit order is exactly a DFS order: the next vertex must be adjacent to the deepest stack vertex that still has unvisited neighbours. Check S with a stack (pop while the top has no unvisited neighbour; next vertex must be a neighbour of the top), then assign weights from the stack/tree structure (tree edges large and increasing along the DFS, others small) so distances reproduce the order. O(n+m) with care when scanning adjacency.",
          ["dfs order validation", "stack simulation", "constructive weights", "dijkstra", "graph"]),
    "D": ("Rooted tree (n<=2e5) with a_i ornaments; one operation removes one ornament from every vertex on a root path. Answer min operations initially and after each of q<=2e5 point updates of a_u.",
          "Static DP: dp(u)=max(a_u, sum of dp over children). For updates use dynamic DP on heavy-light decomposition: with b_u = sum of dp of light children, dp(top of chain) = max over i of (a_{c_i} + b_{c_1}+...+b_{c_{i-1}}); maintain these prefix-sum terms per chain in a lazy segment tree (range add on b changes, range max), and propagate changes of chain tops to their parents' b. O(n log n + q log^2 n).",
          ["dynamic dp", "heavy-light decomposition", "lazy segment tree", "tree dp", "point updates"]),
    "E": ("Given all window sums s_i of length m of an unknown integer array a_1..a_n (n<=2e5), answer q<=1e5 queries: minimal possible max(a_l..a_r), or unbounded.",
          "a_{i+m}-a_i = s_{i+1}-s_i, so a_i = base_{i mod m} + w_i with known offsets w and one constraint sum of bases = s_0. If r-l+1<m some residue is free -> unbounded; otherwise with y_j = max w over residue j inside [l,r], the answer is ceil((s_0 + sum y_j)/m). Sum of per-residue range maxima via sqrt decomposition: for m<=sqrt n use a sparse table per residue; for m>sqrt n each residue has <sqrt n elements, precompute prefix sums over residues of range maxima for every pair of element ranks. O((n+q) sqrt n).",
          ["sqrt decomposition", "sparse table range max", "telescoping difference equations", "math", "offline precomputation"]),
    "F": ("Digit string of length n<=5e5 laid out in a grid of width w; non-zero digits are mines; f(w) = sum over zero cells of mines in 4-neighbours. Find the k-th largest f(w) over all widths.",
          "Start from 4*sum(digits) and subtract boundary losses: vertical neighbours at distance w (via one convolution of the digit array with the reversed non-zero indicator, FFT/NTT), first/last column membership (for each position update all divisors of p and p+1), first/last row (difference array over w intervals), and horizontal neighbours split across rows (divisors of p+1). Then nth_element for the k-th largest. O(n log n).",
          ["fft convolution", "divisor enumeration", "difference array", "counting contributions", "harmonic sum"]),
    "G": ("Connected graph (n,m<=2e5) is 'well-designed' if every vertex lies on a simple 1-n path and no two inner vertices can appear in both orders on simple 1-n paths. Check it, and sum w_i w_j over non-adjacent pairs whose added edge keeps it well-designed.",
          "Well-designed is equivalent to being a two-terminal series-parallel graph with terminals 1 and n (proof via dominator tree of the induced DAG). Test by repeatedly applying series reductions (degree-2 vertices) and parallel reductions (merge multi-edges) with a queue. An added edge (u,v) keeps it series-parallel iff u and v lie on a common chain contracted by one (extended) series operation, so accumulate sum w_i w_j over pairs within each contracted path during the reduction (prefix sums of weights). O(m log n).",
          ["series-parallel graph", "graph reduction", "two terminal st paths", "dominator tree proof", "counting pairs"]),
    "H": ("Array a (n<=1e5); operation reflects a prefix or suffix around a_i (a_j -> 2a_i - a_j). Make the array non-decreasing and positive while minimizing a_n.",
          "Reflections preserve all |a_i-a_{i+1}|, so the final array is a_1 + prefix sums of these absolute differences; minimize a_1. Two prefix reflections shift a_1 by 2(a_{x+1}-a_x) and suffix reflections flip signs freely, so a_1 can change by any multiple of g = gcd of 2|a_i-a_{i+1}|. Final a_1 = a_1 mod g (or g if 0), answer a_1' + sum |diff|. O(n log A).",
          ["invariant", "gcd bezout", "number theory", "reflection operations"]),
    "I": ("Count sequences b_1..b_n with 1<=b_i<=a_i and b_i | b_{i+1} (n, a_i <= 2e5), mod 998244353.",
          "Replace a_i by suffix minima (b is non-decreasing). Values change at most log2(M)~18 times along a sequence (each proper divisor step at least doubles), so f_v(l) (prefixes of length l ending at v) is a polynomial in l written in the binomial basis C(l,k) with <=18 coefficients; transitions from proper divisors u|v use the hockey-stick identity sum_{j=L}^{l-1} C(j,k) = C(l,k+1)-C(L,k+1) with lower bound L(u,v) from first indices where a allows the values. Iterate u and its multiples (harmonic sum). O(n + M log^2 M).",
          ["divisor chain dp", "harmonic sum over multiples", "binomial basis polynomial", "hockey-stick identity", "combinatorics"]),
    "J": ("Cyclic playlist permutation a, desired listening order permutation b (n<=2e5); with d<=2e5 swap updates on a or b, report min skips to hear b_1..b_n in order each day.",
          "Total songs played = pos_a(b_n) + n*k where k = number of i with pos_a(b_{i+1}) < pos_a(b_i) (wrap-arounds); skips = that - n. Maintain pos array and k; a swap in a or b changes only O(1) adjacent comparisons, so update k in O(1). O(n+d).",
          ["permutations", "counting descents", "maintain under swaps", "implementation"]),
    "K": ("Digit multiset (n<=1e6 total); each clock HH:MM with HH in 00..11 and MM in 00..59 uses 4 stickers; maximize the number of displays.",
          "Split displays into type A (hour 0x) and type B (hour 1x). For fixed counts (x,y) check feasibility greedily filling the most constrained positions first: x zeros, y ones for first H digit, y of {0,1} for second, x+y of {0..5} for first M digit, then 2x+y arbitrary digits. Enumerate x and binary search y (feasibility monotone in y). O(n log n) on digit counts.",
          ["greedy feasibility check", "binary search", "counting digits", "enumeration"]),
    "L": ("Points (x, (ax+b) mod n) for x=0..n-1 (n<=1e9); peel convex hull layers k<=300 times, output doubled area of each hull.",
          "Pigeonhole gives u<=ceil(sqrt n), |v|<sqrt n with v = a u (mod n); then the points split into O(sqrt n) groups of collinear consecutive points (arithmetic progressions with step (u,v) until wrap-around). Only group endpoints can be hull vertices, so each layer's hull is computed on O(sqrt n) candidates; peeling removes the top and bottom groups and boundary endpoints of other groups in O(1) each. O(k sqrt n log n).",
          ["convex hull", "onion peeling", "pigeonhole principle", "modular arithmetic lattice", "computational geometry"]),
    "M": ("Parenthesis string S (n<=1e6 total); 'deformed' strings follow the grammar E ::= ')' | E ')' E | '(' E '('; find the minimum number of characters to prepend and append so the result is deformed and becomes balanced after adding ')'.",
          "Rewrite '(' as '{' or '}' depending on the parity of preceding ')', turning the grammar into tracking two counters: x = nesting of parentheses and y = nesting of the {} brackets; a valid string keeps x,y>=0 and ends at (1,0). For the original problem the useful prefixes X are only L^f, L^f R L^g, L^f R L^g R; the suffix length is a closed formula of the final state, so total cost is 4f + const and one scans f to find the minimum feasible. O(n).",
          ["grammar characterization", "bracket sequences", "prefix balance counters", "greedy formula", "strings"]),
}


def main():
    contests, problems = [], []
    for y, c in CONTESTS.items():
        cid = f"apac{y}"
        base = G.format(y=y)
        probs, teams = ps.parse(os.path.join(DL, f"{y}_standings.html"))
        nteams, st = ps.stats(probs, teams)
        unsolved = [s["letter"] for s in st if s["solved"] == 0]
        notes = (f"Held in {c['venue']}. Counts from the official DOMjudge final scoreboard archived by ICPC Japan "
                 f"(all {nteams} listed teams are official; no guest/mirror teams). ")
        if y in (2024, 2025):
            notes += "Archived page header says 'preliminary results - not final' but it is the unfrozen post-contest board (no pending cells). "
        notes += f"Unsolved problems: {', '.join(unsolved) if unsolved else 'none'}. Online mirror is a Codeforces main-site contest {c['cf']} (rated difficulty available)."
        contests.append({
            "id": cid, "family": "apac", "name": f"The {y} ICPC Asia Pacific Championship",
            "short": f"APAC {y}", "year": y, "date": c["date"], "total_teams": nteams,
            "links": {"scoreboard": base + "standings.html", "statements": base + c["statements"],
                      "editorial": base + c["editorial"],
                      "mirror": f"https://codeforces.com/contest/{c['cf']}", "kattis": None},
            "notes": notes,
        })
        for s in st:
            L = s["letter"]
            summ, idea, tags = P[y][L]
            rating, cft = CF[y][L]
            problems.append({
                "id": f"{cid}-{L}", "contest": cid, "letter": L, "title": s["title"],
                "solved_teams": s["solved"], "attempted_teams": s["attempted"],
                "first_solve_min": s["first"],
                "links": {"mirror": f"https://codeforces.com/contest/{c['cf']}/problem/{L}",
                          "kattis": None, "statement": base + c["statements"]},
                "statement_summary": summ, "solution_idea": idea, "solution_source": "editorial",
                "candidate_tags": tags, "cf_tags": cft, "cf_rating": rating,
            })
    out = {"source": "apac", "contests": contests, "problems": problems}
    path = os.path.join(ROOT, "raw", "apac.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(path, len(contests), "contests", len(problems), "problems")


if __name__ == "__main__":
    main()
