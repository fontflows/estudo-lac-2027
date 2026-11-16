"""Build pipeline/raw/latam_regional_2019_2023.json.

Solve counts come from the BOCA final scoreboards (parsed with parse_boca_regional_old.py);
problem summaries / ideas / tags are curated below from the statements and editorials.

Usage (from Dados_Latam/pipeline):
    python -I scripts/build_latam_regional_2019_2023.py
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
DL = os.path.join(PIPE, "downloads", "latam_regional_2019_2023")
OUT = os.path.join(PIPE, "raw", "latam_regional_2019_2023.json")

spec = importlib.util.spec_from_file_location("pbro", os.path.join(HERE, "parse_boca_regional_old.py"))
pbro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pbro)

SB = "https://scorelatam.naquadah.com.br"

# edition -> contest metadata. `group` = BOCA sitegroup id of the "Global" (official) scoreboard.
CONTESTS = [
    dict(edition=2019, id="latam2019", year=2019, date="2019-11-09", group=1,
         name="ICPC Latin American Regional 2019", short="LATAM 2019",
         scoreboard=f"{SB}/latam-2019/",
         statements="https://maratona.sbc.org.br/hist/2019/resultados19/prova/prova/contest_onesided.pdf",
         editorial=None, gym=102428, sol_source="own",
         notes="Held Nov 8-9 2019 (contest session Nov 9). No official editorial; community discussion only in the "
               "Codeforces thread 'The 2019 ACM-ICPC Latin America Regional Contest' (codeforces.com/topic/71826), "
               "which could not be fetched directly; the parallel thread blog entry 71296 (k790alex, with jury outlines by "
               "mnaeraxr/karupayun) was read via web.archive.org and all ideas except E and M (trivial) were checked "
               "against it (solution_source='community'). Counts = BOCA 'global' group "
               "(official regional teams only; CCL parallel-contest teams excluded; '[UH] TestMCL' kept, it is a regular "
               "team account). A, B, J unsolved."),
    dict(edition=2020, id="latam2021", year=2021, date="2021-07-10", group=1,
         name="ICPC Latin American Regional 2020 (held July 2021, remote)", short="LATAM 2020",
         scoreboard=f"{SB}/latam-2020/",
         statements="https://maratona.sbc.org.br/hist/2020/final20/resultados/contest/pdfs/contest.pdf",
         editorial="https://github.com/Diego1149/ICPC-Latam-2020", gym=103185, sol_source="community",
         notes="2020 edition postponed by COVID-19 and held remotely on 2021-07-10, hence year 2021 / id latam2021. "
               "No official editorial; solution ideas from the community editorial by Diego1149 (GitHub, linked from "
               "CF blog 'ICPC - Latin American Regional 2020 - Editorial and some comments'). Counts = BOCA 'Global' "
               "group. A, G, I, M solved by exactly one official team."),
    dict(edition=2021, id="latam2022", year=2022, date="2022-04-02", group=32,
         name="ICPC Latin American Regional 2021 (held April 2022)", short="LATAM 2021",
         scoreboard=f"{SB}/latam-2021/",
         statements="https://maratona.sbc.org.br/hist/2021/resultados21/icpcla.pdf",
         editorial=None, gym=103640, sol_source="own",
         notes="2021 edition held 2022-04-02, hence year 2022 / id latam2022. No editorial found (CF discussion "
               "blog entry 101550, read via web.archive.org); all ideas except A were checked against the sketches "
               "there (solution_source='community'); A (Ancient Towers) remains own reasoning. Counts = BOCA 'global' group (sitegroup 32; CCL teams excluded). A, E, G unsolved."),
    dict(edition=2022, id="latam2023a", year=2023, date="2023-03-18", group=1,
         name="ICPC Latin American Regional 2022 (held March 2023)", short="LATAM 2022",
         scoreboard=f"{SB}/latam-2022/",
         statements=f"{SB}/latam-2022/contest.pdf",
         editorial=f"{SB}/latam-2022/editorial.pdf", gym=104252, sol_source="editorial",
         notes="2022 edition held 2023-03-18; a second edition (2023) was held 2023-10-21, so ids latam2023a / "
               "latam2023b. Official editorial. Counts = BOCA 'Global' group (CCL excluded). J unsolved."),
    dict(edition=2023, id="latam2023b", year=2023, date="2023-10-21", group=1,
         name="ICPC Latin American Regional 2023", short="LATAM 2023",
         scoreboard=f"{SB}/latam-2023/",
         statements=f"{SB}/latam-2023/contest.pdf",
         editorial=f"{SB}/latam-2023/editorial.pdf", gym=104736, sol_source="editorial",
         notes="Held 2023-10-21 (second regional in calendar 2023, see latam2023a). Official solution sketches. "
               "Counts = BOCA 'Global' group (CCL excluded). E unsolved by official teams (the single accepted E run on the "
               "statistics page belongs to a non-team account)."),
]

# Per-problem solution_source overrides: ideas of an "own" contest that were later checked against
# community write-ups (CF discussion threads read via web.archive.org: blog entry 71296 for 2019,
# blog entry 101550 for the 2021 edition).
SOURCE_OVERRIDE = {
    **{f"latam2019-{L}": "community" for L in "ABCDFGHIJKL"},
    **{f"latam2022-{L}": "community" for L in "BCDEFGHIJKLM"},
}

# (letter, title, statement_summary, solution_idea, candidate_tags)
P = {}

P[2019] = [
    ("A", "Algorithm Teaching",
     "N<=100 teachers each know <=10 algorithms; a student is trained by one teacher in a non-empty subset of that teacher's algorithms. Find the largest team in which no student's set is contained in another's.",
     "Collect all distinct non-empty subsets of each teacher's set (<=100*1023 nodes); the family is ordered by inclusion and the answer is its maximum antichain. By Dilworth's theorem this equals the minimum chain cover = |V| - maximum bipartite matching, where edges link each set to the sets obtained by removing one element (the family is downward closed). Hopcroft-Karp on ~1e5 nodes / ~1e6 edges. (Jury outline in the CF thread: Dilworth on the subset DAG; the reference used the transitive closure, up to N*3^K edges, but edges between sets differing in one element suffice because a Boolean lattice has a symmetric chain decomposition.)",
     ["dilworth theorem", "maximum antichain", "bipartite matching", "hopcroft-karp", "bitmask subsets"]),
    ("B", "Build the Perfect House",
     "Given N<=1e4 points (none at the origin), find the maximum perimeter of a square centered at the origin, with any rotation, that contains no point strictly inside.",
     "Binary search on the half-side s. For a rotation angle t (mod 90 degrees) a point p is strictly inside iff max(|p.u_t|, |p.v_t|) < s; for each point this forbids one angular interval centered at its polar angle minus 45 degrees. Check whether the union of the N forbidden arcs covers the whole [0, pi/2) circle by sorting endpoints; O(N log N) per check. (Jury outline: rotate points into the first quadrant, binary search the diagonal, intersect the per-point intervals of valid rotations; an expected-O(N) randomized incremental solution like minimum enclosing circle also exists.)",
     ["binary search on answer", "angular interval coverage", "rotating square", "computational geometry", "sweep over angles"]),
    ("C", "Cut Inequality Down",
     "Array of N<=1e5 monthly incomes and bounds L<=U; each month wealth += A_i then is clamped to [L, U]. Answer Q<=1e5 queries: starting wealth X at month B, wealth after month E.",
     "Each month is the function f_i(x) = clamp(x + A_i, L, U), and compositions of such clamp-shift functions stay in the closed form min(hi, max(lo, x + c)). Precompute compositions with a sparse table / binary lifting (or segment tree) and answer each query by composing O(log N) blocks; O((N + Q) log N). Alternative from the CF thread: a segment tree over prefix sums finds the first month the wealth leaves [L, U], after which it equals exactly L or U, so a sparse table of jumps between consecutive clamps answers queries (or an offline sweep merging queries with DSU).",
     ["function composition", "clamp functions", "sparse table", "binary lifting", "segment tree"]),
    ("D", "Dazzling Stars",
     "N<=1000 stars with coordinates and brightness; decide whether the picture can be rotated so that, printing top to bottom, every star is printed no later than any dimmer star.",
     "For every pair with B_S > B_T the printing direction d must satisfy d.(S - T) >= 0, so all O(N^2) difference vectors must fit in a closed half-plane. Sort the vectors by angle (exact integer comparator) and check whether some angular gap between consecutive vectors is >= pi; O(N^2 log N). This is the jury solution (intersection of the O(N^2) 180-degree ranges of valid directions); O(N log N) is possible using only convex hulls of consecutive brightness classes.",
     ["angular sort", "half-plane of vectors", "computational geometry", "cross product", "pairwise constraints"]),
    ("E", "Eggfruit Cake",
     "Circular string of 'E'/'P' of length <=1e5; count contiguous arcs (slices) with at most S fruits that contain at least one 'E'.",
     "Double the string; for each start position find the distance d to the next 'E' (precomputed right-to-left); slices starting there with length in [d+1, S] are valid, contributing max(0, S - d). O(n).",
     ["circular string", "next occurrence array", "counting substrings", "two pointers"]),
    ("F", "Fabricating Sculptures",
     "Count sequences of S positive stack heights summing to B (S<=B<=5000) that hold no water, i.e. unimodal compositions, modulo 1e9+7.",
     "A water-free base is unimodal: peeling the bottom layer (which spans all s stacks) leaves a unimodal base on a contiguous sub-interval of k stacks placed in s-k+1 ways. dp[s][b] = sum_k (s-k+1) * dp[k][b-s]; maintain prefix sums of dp[k] and k*dp[k] over k to make each state O(1); O(S*B). Slicker recurrence from the CF thread (after removing the bottom layer): DP(s,b) = DP(s,b-s) + 2*DP(s-1,b) - DP(s-2,b) (bottom level full / leftmost stack empty / rightmost stack empty, inclusion-exclusion).",
     ["dp counting", "prefix sums optimization", "unimodal sequences", "combinatorics", "modular arithmetic"]),
    ("G", "Gluing Pictures",
     "Given a city name C and several friend names (total length <=2e5), find for each name the minimum number of substrings of C concatenated to form it, or -1.",
     "Greedy is optimal because the set of substrings of C is closed under taking prefixes/suffixes: repeatedly take the longest prefix of the remaining name that is a substring of C. Walk the suffix automaton of C character by character, restarting at the root (and counting a new piece) when a transition fails; -1 if a letter never occurs. O(total length). (Suffix array with range narrowing by binary search also passes.)",
     ["suffix automaton", "greedy longest match", "string matching", "substring queries"]),
    ("H", "Hold or Continue?",
     "Two-player dice game Pig to exactly 75 (overshooting busts the turn); answer up to 1000 queries (my score, opponent score, turn total): is holding or continuing optimal?",
     "Win probability P(c, h, t) for the player to move; transitions to roll outcomes and to the opponent's turn P(h, c', 0) create cycles (a turn ending with no gain swaps roles). Process score pairs in decreasing order of c + h; for each pair the two unknowns P(c,h,0) and P(h,c,0) depend on each other monotonically, so solve them by fixed-point iteration / binary search, or simply run value iteration over all states until convergence. Then compare hold vs continue values. (Jury/CF thread: guess A = P(c,h,0), derive B = f(A) and g(B), binary search for g(f(A)) = A, or iterate monotone lower/upper bounds; naive value iteration converges quickly too.)",
     ["probability dp", "game theory", "value iteration", "fixed point", "expected value"]),
    ("I", "Improve SPAM",
     "N<=2000 addresses, the first L are mailing lists forming a DAG (lists contain clients and older lists). Count messages delivered when sending to list 1 (with duplicates, mod 1e9+7) and the number of distinct clients reached.",
     "Lists only contain lists created earlier, so the containment graph is a DAG. The 'before' count is the number of paths from node 1 to client nodes, computed by DP over a topological order (memoized DFS) modulo 1e9+7; the 'after' count is the number of distinct clients reachable from 1 via DFS. O(N + edges). Pitfall from the CF thread: compute reachability separately, a client reached a multiple of 1e9+7 times still counts.",
     ["dag path counting", "topological order dp", "dfs reachability", "modular arithmetic"]),
    ("J", "Jumping Grasshopper",
     "N, M<=2e5: heights with point increases; queries: grasshopper at plant J facing left/right repeatedly jumps to the first strictly taller plant in its facing direction and flips direction; report where it stops.",
     "The walk alternates sides with increasing heights, so only maxima matter: facing left from J, if nothing to the left is taller it stops at J; otherwise compare ML = max(1..J-1) and MR = max(J+1..N). If ML > MR it ends at the first plant left of J taller than max(MR, H_J), else at the first plant right of J taller than ML. Use a max segment tree with point updates, range max and 'first index with value > v' descent; O(log N) per operation. (CF thread confirms: the answer is one of two candidates, the record tower on each side; ties ML = MR need care.)",
     ["segment tree", "segment tree descent", "range maximum query", "observation simplifying simulation", "point updates"]),
    ("K", "Know your Aliens",
     "String of H/A of length N<=1e4 over points 2,4,...,2N; output a minimum-degree monic (+-1 leading) integer polynomial with integer roots that is positive on humans and negative on aliens.",
     "The minimum degree equals the number of sign changes between consecutive citizens; put a root at the odd integer 2i+1 between each pair whose sign differs and pick the leading sign so that P(2N) has the right sign. Expand the product of (x - r) iteratively in O(D^2) with 64-bit arithmetic (guaranteed to fit). Since coefficients must fit in 2^63-1, effectively D <= 16, so no FFT is needed (CF thread).",
     ["constructive", "polynomial multiplication", "sign changes", "math"]),
    ("L", "Leverage MDT",
     "N x M (<=1000) grid of G/B; whole rows can be flipped independently (the tool is toggled only outside the kingdom between row traversals). Find the largest all-good square achievable.",
     "Because each row can be flipped as a whole, a square is achievable iff every row segment inside it is uniform. Compute for each cell the length of the run of equal characters ending at it in its row; then for each column find the largest k such that k consecutive rows all have run length >= k (largest square under a histogram via monotonic stack, or binary search on k with sliding window). O(NM). (CF thread: or a largest-square DP dp(i,j) = 1 + max of the three neighbours when S[i][j]=S[i][j-1] and S[i-1][j]=S[i-1][j-1], or prefix sums + binary search.)",
     ["largest square", "monotonic stack", "histogram", "grid dp", "observation"]),
    ("M", "Mountain Ranges",
     "Given N<=1000 non-decreasing altitudes and X, find the longest run of consecutive viewpoints where each step up is at most X.",
     "Single linear scan: extend the current run while A[i+1] - A[i] <= X, otherwise restart; answer is the longest run. O(N).",
     ["linear scan", "implementation", "ad hoc"]),
]

P[2020] = [
    ("A", "Almost Origami",
     "Starting with known heights 1 on both borders of a unit sheet, each step crosses lines from the bottom corners to known heights L and R, creating height LR/(L+R). Given H = M/N (N<=100), output a shortest sequence of heights reaching H, or '*'.",
     "The crossing height satisfies 1/H = 1/L + 1/R, so in reciprocal space every new value is the sum of two existing ones starting from 1: all reachable heights are 1/k. Hence answer '*' unless M = 1, and otherwise the task is a shortest addition chain for N <= 100, found by iterative-deepening DFS with pruning (chain length <= ~9).",
     ["addition chain", "iterative deepening dfs", "math observation", "brute force search", "fractions"]),
    ("B", "Beautiful Mountains",
     "Array of N<=1e5 positive values with -1 wildcards; decide if it can be completed and split into consecutive 'mountains' (non-decreasing then non-increasing, length >= 3) of equal length k, except the last which may be shorter.",
     "Check each block length k; a block is mountain-fillable iff a small automaton (start/up/flat/down/invalid) over its known values accepts, wildcards acting as equal. Known strictly increasing adjacent pairs forbid any k whose blocks end there and strictly decreasing pairs forbid blocks starting there; mark invalid k via divisor/sieve-style elimination and only fully check survivors, giving harmonic-sum O(N log N).",
     ["harmonic series enumeration", "sieve", "finite automaton", "wildcard matching", "implementation"]),
    ("C", "Crisis at the Wedding",
     "N<=1e5 tables around a circle with glass counts summing to a multiple of N; a waiter moving only in one direction (clockwise or counterclockwise) carries surplus glasses; minimize total glass-distance.",
     "Subtract the average; for one direction the flow across each edge equals x + prefix_i and must be non-negative, and cost is the sum of flows, so x = -min prefix and cost = sum(prefix_i - min). Equivalently a DP over the doubled array for every start; do it for both directions and take the minimum. O(N).",
     ["prefix sums", "circular array", "greedy", "flow on a cycle"]),
    ("D", "Dividing Candy",
     "N<=1e5 boxes with 2^Ai candies (Ai<=1e5); can they be split between two brothers so each total is a power of two?",
     "Add all 2^Ai into a big binary counter with carries (amortized O(1) per addition). Answer Y iff the sum has exactly two set bits, or exactly one set bit and N >= 2 (powers of two can always be greedily split into equal halves). O(N + max A).",
     ["big binary number", "bit manipulation", "carry propagation", "powers of two"]),
    ("E", "Excellent Views",
     "N<=1e5 buildings with distinct heights on a line; from building i, j is worth visiting if no building within distance |i-j| of i is taller than j. For each i count worthwhile j.",
     "Fix the target j: let p be the nearest taller building on one side; j is worth it from i (on that side) iff i lies strictly closer to j than the midpoint (p+j)/2. So each j adds +1 to two index ranges; find nearest greater elements (monotonic stack or processing heights in decreasing order with an ordered set) and apply range additions with a difference array / segment tree. O(N log N) or O(N).",
     ["nearest greater element", "monotonic stack", "difference array", "range update", "counting contributions"]),
    ("F", "Fascinating Partitions",
     "Array of N<=8000; for every k, the minimum and maximum over partitions into k contiguous parts of the sum of part maxima.",
     "Layered DP dp[k][i] = min/max over j of dp[k-1][j] + max(A[j+1..i]). For each layer sweep i with a monotonic stack of (value, best dp before the previous greater element), popping elements <= A[i] and merging their best dp values, so each layer is O(N) amortized; O(N^2) total. (The maximum also equals the sum of the k largest elements.)",
     ["partition dp", "monotonic stack optimization", "o(n^2) dp", "range maximum"]),
    ("G", "Game of Slots",
     "Alice and Bob each get N<=100 random cards; Alice places hers on slots worth 1..N, then Bob, seeing everything, places his; the larger card wins the slot's points. Compute Alice's expected score under optimal play.",
     "Ties have negligible probability. Bob's best response: go through slots in decreasing value and beat each with his smallest card that exceeds Alice's, else dump his smallest card; an exchange argument shows Alice should place her cards in increasing order. Then the expectation is a DP over the merged descending order of the 2N cards, dp[n][m][k] (Alice cards left, Bob cards left, Bob cards available to beat), with probabilities n/(n+m) and m/(n+m); O(N^3).",
     ["probability dp", "expected value", "game theory", "exchange argument", "greedy best response"]),
    ("H", "Halting Wolf",
     "Program of N<=100 instructions: finite jumps with a multiset of targets (each used once) and infinite jumps; find the maximum number of times instruction 1 can execute, or '*' if unbounded.",
     "Model instructions as nodes, finite targets as unit-capacity edges and infinite jumps as 'infinite' (large) capacity edges; split node 1 into source (outgoing) and sink (incoming). Each unit of flow is a return to instruction 1, so the answer is 1 + maxflow (Dinic), and '*' if the flow reaches the infinite threshold (a cycle of infinite jumps through 1).",
     ["max flow", "dinic", "node splitting", "graph modeling", "eulerian walk"]),
    ("I", "Impenetrable Wall",
     "Given a house, a gate and N<=300 towers, count polygons that have the gate as a vertex, other vertices towers, strictly convex angles at towers, strictly contain the house and are fully visible from it (mod 1e9+7).",
     "Visibility forces vertices to appear in angular order around the house; sort towers by angle starting from the gate. Count cyclic sequences gate -> towers -> gate with DP over the last two vertices dp[j][k]: extend to l if (j,k,l) is a left turn (convex at tower k) and (house,k,l) is counter-clockwise (house strictly inside); the gate is fixed as first vertex so its angle is unconstrained. O(N^3).",
     ["angular sort", "dp over last two vertices", "convex polygon counting", "cross product", "computational geometry"]),
    ("J", "Job Allocator",
     "N<=1e5 events over K<=8 resource types: connect a machine with <=8 resources, disconnect a machine, or query how many connected machines contain a requested resource multiset.",
     "Represent a machine as a count vector (sum <= 8) and keep a table cnt[v] over all count vectors (multi-dimensional array / hash). On connect/disconnect, add +-1 to every vector dominated by the machine's vector (at most prod(c_i+1) <= 2^8 = 256 of them); a query is a single lookup. O(N * 2^8).",
     ["multiset enumeration", "sub-multiset counting", "precomputation", "hashing", "data structure"]),
    ("K", "Keylogger",
     "K<=750 keys, a K x K matrix T with non-decreasing rows, margin L and N-1<=1e4 measured delays; count key sequences of length N with T[s_i][s_{i+1}] within L of each delay (mod 1e9+7).",
     "DP over positions dp[i][key]. Since each row of T is sorted, the valid next keys from key a form a contiguous range found by two binary searches (lower/upper bound of P-L and P+L); push dp values with a difference array or pull with prefix sums. O(N K log K).",
     ["dp", "binary search", "prefix sums", "difference array", "counting sequences"]),
    ("L", "Lola's Schedule",
     "N<=1e4 non-overlapping activities and a period X<=720; choose the earliest start T in [0, 480] minimizing the number of times T + kX falls inside an activity (inclusive).",
     "Mark all blocked minutes on a timeline (<=2e5 minutes); for each T in [0, 480] count blocked times among T, T+X, ... (equivalently a DP over the timeline where dp[t] = blocked[t] + dp[t+X]). Take the minimal count with smallest T. O(timeline).",
     ["brute force", "simulation", "dp on timeline", "modular arithmetic"]),
    ("M", "May I Add a Letter?",
     "String of length <=1e5 with Q<=1e5 operations append-a-letter / delete-last; after each, output the number of distinct substrings occurring at least twice.",
     "Appending changes the answer by L2 - L3 where L2 / L3 are the longest suffixes occurring at least twice / three times; deletions undo. The community solution maintains a suffix automaton with persistent (rollback-able) structures: every cloned state q' and every non-split transition marks substrings occurring >= 2 times, and the count of repeated substrings is maintained incrementally; deletes restore the previous version. About O(N) amortized over the version stack.",
     ["suffix automaton", "persistent data structure", "rollback", "distinct substrings counting", "strings"]),
    ("N", "Non-Integer Donuts",
     "Given an initial balance and N<=1000 daily deposits as '$X.YY' strings, count days on which the balance is not an integer.",
     "Parse the cents part only, keep the running sum of cents modulo 100, and count days where it is non-zero. O(N).",
     ["string parsing", "simulation", "modular arithmetic"]),
]

P[2021] = [
    ("A", "Ancient Towers",
     "N<=400 points in general position and a value S; count simple quadrilaterals (vertex set and edges) with vertices among the points and area >= S.",
     "Every simple quadrilateral has an interior diagonal (i, j) with the other two vertices on opposite sides, and its area is the sum of the two triangles on that diagonal; convex quadrilaterals have two such diagonals, concave ones exactly one. For each pair (i, j) sort the points on each side by triangle area and count pairs with sum >= 2S using two pointers, then subtract the convex quadrilaterals counted twice (pairs whose segments cross). About O(N^3) to O(N^3 log N) with angular sorting.",
     ["computational geometry", "counting quadrilaterals", "two pointers", "angular sort", "inclusion-exclusion"]),
    ("B", "Because, Art!",
     "N<=1e5 font grades F and color grades C (can be negative); for every k output the minimum and maximum sum of k products F_i*C_j using distinct fonts and colors.",
     "For fixed chosen sets the best pairing is sorted-with-sorted (rearrangement inequality). Sort F and C; for the maximum, first take the index-aligned pairs F[i]*C[i] with positive product, largest first (they come from both ends: big*big and negative*negative). If k exceeds the number r of positive pairs, the remaining k-r pairs are forced to be non-positive and must use the elements of smallest absolute value (the middle of both arrays), multiplied in sorted order; the sums of these aligned middle windows for all k are a convolution, computed with FFT/NTT (precision care; Karatsuba also passes). The minimum is the same with C negated. O(N log N) (CF thread, Marckess).",
     ["rearrangement inequality", "greedy", "sorting", "fft convolution", "prefix sums"]),
    ("C", "Cyclists versus Clouds",
     "Grid points in [0,100]^2; N<=100 rectilinear polygon clouds each moving one unit per time step in a fixed cardinal direction; a cyclist moves along unit steps or waits at points, must never be strictly under a cloud while moving; find the minimum travel time.",
     "Time-expanded BFS over states (x, y, t): clouds leave the region after a bounded time (a few hundred steps), so t is bounded. Rasterize each polygon into unit cells/edges and, for each time step, precompute which unit moves are wet by shifting the cloud masks; then BFS with moves and waits. O(grid * T). (CF thread: all clouds leave within about 100 steps, so the answer and T are small.)",
     ["bfs", "time-expanded graph", "simulation", "rasterization", "grid geometry"]),
    ("D", "Daily Turnovers",
     "Array of N<=5e5 values; happiness = number of subarrays all of whose prefix sums are non-negative. Add X to exactly one element to maximize happiness.",
     "With prefix sums P, a subarray starting at l is valid up to R(l)-1 where R(l) is the first r >= l with P[r] < P[l-1] (next smaller via monotonic stack), so happiness = sum_l (R(l) - l). Adding X at position i shifts P[r] for r >= i: starts l > i and starts whose R(l) < i are unchanged, the others get a new first violation = first r >= i with P[r] < P[l-1] - X. Sweep the modified position i from right to left keeping each start's contribution updated (start l is affected iff l-1 <= i <= R(l)); for X > 0 first violations only move right, for X < 0 they can move left, handled with a segment tree over prefix values (lazy segment tree or treap, CF thread). O(N log N).",
     ["prefix sums", "monotonic stack", "next smaller element", "sparse table", "offline sweep"]),
    ("E", "Expedition Plans",
     "N<=3000 repeaters with sailing costs between neighbours, dive costs and segment fixing costs; design an adaptive search for the single faulty segment minimizing the worst-case total cost (sailing + diving + fixing).",
     "Minimax interval DP: state = interval of candidate segments [l, r] plus the side where the boat currently is (the last diagnosed repeater bounds the interval); choosing repeater m costs sail + D_m + max(left subinterval, right subinterval). The naive O(N^3) is too slow; the left term increases and the right term decreases with m, so the crossing point p where the left term overtakes the right is found by binary search, and on each side of p the needed minimum of F + D_k + sailing is a range minimum kept in per-l / per-r segment trees or Fenwick trees (O(N^2) memory). O(N^2 log N) (CF thread).",
     ["interval dp", "minimax", "decision tree", "monotonicity optimization", "binary search"]),
    ("F", "Fields Division",
     "Connected graph with N<=3e5 vertices, vertex i has weight 2^i; split vertices between Ana and Bob, both parts connected, sums as close as possible with Ana getting the larger.",
     "Vertex N outweighs all others, so Ana gets N; Bob should get N-1 and as much as possible. Bob's part is exactly the connected component of N-1 in the graph with N removed, and everything else (other components of G - N plus N) is connected through N and goes to Ana. One BFS/DFS, O(N + M).",
     ["greedy", "powers of two dominance", "graph connectivity", "bfs", "dfs"]),
    ("G", "Generator Tree",
     "N<=2e5 trees (total 4e5 vertices); for each tree count the other trees T1 such that copies of T1 joined by extra edges form a tree isomorphic to it.",
     "T2 is generated by a tree of size d iff d | |T2|, T2 can be cut into connected pieces of size d (unique: cut every edge whose lower subtree size is divisible by d; needs exactly |T2|/d such subtrees) and all pieces are isomorphic. For each tree and each divisor d that is a size present in the input, split it and compare canonical hashes of the pieces (unrooted tree hashing via centers); count input trees with that hash. Total about sum of |T| * d(|T|).",
     ["tree isomorphism", "tree hashing", "divisors", "subtree sizes", "tree partition"]),
    ("H", "Hamilton - The Musical",
     "Complete graph on N<=500 cities; a Hamiltonian path must have city i at position i for every even i; minimize total length.",
     "Even positions are fixed, so the odd cities must be assigned to odd positions; placing odd city c at odd position p costs L[c][p-1] + L[c][p+1] (existing neighbours). This is a minimum-cost assignment problem of size ~250, solved with the Hungarian algorithm in O(n^3).",
     ["assignment problem", "hungarian algorithm", "min cost bipartite matching", "modeling"]),
    ("I", "Invested Money",
     "Today's weekday and N<=1e5 deposit ages (<=1e9 days); deposits renew every 30 days, postponed to Monday when falling on a weekend; find the minimum days until some renewal.",
     "Simulate each deposit's renewal chain from its creation weekday: each renewal is creation + 30 (+1 or +2 if weekend), and the weekday pattern of renewals is periodic, so jump over full periods (or precompute the cycle over the 5 weekdays) to reach the first renewal at or after today. O(N) with constant work per deposit. (CF thread: starting on Mon/Wed/Fri the chain returns to the same weekday every 91 days.)",
     ["simulation", "modular arithmetic", "cycle detection", "calendar"]),
    ("J", "Joining Pairs",
     "W x H paper with N<=1e5 pairs of points; decide whether all pairs can be connected by non-crossing curves inside the paper.",
     "Pairs with at least one point strictly inside the paper never block anything and can be ignored. Map every boundary point to its position along the perimeter (cyclic order); pairs with both ends on the border are chords that must not interleave, checked by sorting positions and running a balanced-parentheses stack. O(N log N).",
     ["balanced parentheses", "stack", "perimeter mapping", "geometry", "sorting"]),
    ("K", "KIARA is a Recursive Acronym",
     "List of words (total length <=1e6); decide whether some word can be spelled entirely with first letters of words in the list.",
     "Build the set of first letters of all words; answer Y iff some word consists only of letters in that set. O(total length).",
     ["strings", "set membership", "ad hoc"]),
    ("L", "Leaving Yharnam",
     "Bus with N pairs of seats; G easygoing, then E extroverts, then I introverts board with randomized seat-choice rules; compute the expected number of happy passengers modulo 1e9+7 (values up to 1e6).",
     "Iterate over the number of easygoing passengers that end up sitting next to another easygoing passenger (equivalently the numbers of full / half-full pairs after the easygoing phase); its probability is a closed-form count with factorials and modular inverses, and once it is fixed the extrovert and introvert phases are deterministic, so their happiness is O(1) casework. O(N) (CF thread).",
     ["expected value", "combinatorics", "probability", "modular inverse", "casework"]),
    ("M", "Most Ordered Way",
     "N<=5000 jobs with durations and deadlines on one machine; output the lexicographically smallest order meeting all deadlines, or '*'.",
     "Feasibility of a set is checked by Earliest-Deadline-First. Build the answer greedily position by position: keep remaining jobs in EDF order with slack_m = D_m - (current time + prefix durations); putting job j next delays all jobs before it in EDF order by T_j, so j is feasible iff current + T_j <= D_j and the minimum slack of EDF-earlier jobs is >= T_j. Pick the smallest feasible index each step; O(N^2).",
     ["greedy lexicographic construction", "edf scheduling", "deadlines", "exchange argument", "prefix minimum"]),
]

P[2022] = [
    ("A", "Asking for Money",
     "N<=1000 people, each would ask two fixed others for $1 (pyramid scheme, each participates once); determine for each person whether some propagation order makes them lose money.",
     "K loses iff, ignoring K's own requests, some person can reach K, X_K and Y_K so that X_K and Y_K are reached before K asks them. On the reversed graph without edges X_K->K and Y_K->K, run BFS from K, X_K and Y_K and check for a node reached by all three. Three BFS per person, O(N^2).",
     ["graph reachability", "bfs", "reverse graph", "brute force per vertex"]),
    ("B", "Board Game",
     "T<=1e5 tokens (points) and P<=1e5 players taking turns; each player takes all remaining tokens strictly below their line y = Ax + B. Report each player's tokens.",
     "A token goes to the first player i such that max_{j<=i}(A_j x + B_j) > y, which is monotone in i. Answer all tokens with parallel binary search, inserting lines into a Li Chao tree / convex hull trick each round (O((P+T) log^2 P)), or binary search over snapshots of a persistent Li Chao tree.",
     ["parallel binary search", "li chao tree", "convex hull trick", "persistent data structure", "binary search"]),
    ("C", "City Folding",
     "A strip of 2^N sections (N<=60) is folded in half N times, each time left-over-right or right-over-left; choose folds so section P ends at layer H.",
     "Work backwards from the final height: at each stage, if the current height is in the lower half it was unchanged by the last fold, otherwise it came from height SH + 1 - AH. This gives the required height at every stage; then go forward and choose each fold direction from the current horizontal position, current height and the next required height. O(N) with 64-bit integers.",
     ["simulation", "reverse simulation", "bit manipulation", "constructive"]),
    ("D", "Daily Trips",
     "Simulate N<=1e4 days of commuting with umbrellas at home and work: bring one if raining or if none is at the destination; report decisions.",
     "Direct simulation keeping umbrella counts at home and at work. O(N).",
     ["simulation", "implementation", "ad hoc"]),
    ("E", "Empty Squares",
     "Board 1 x N (N<=1000) with tiles 1x1..1xN, tile K already placed leaving E empty squares on its left; place remaining tiles to minimize uncovered squares.",
     "Two holes of sizes A = E and B = N-K-E. If a hole size differs from K, cover it with the tile of its exact size (exchange argument); large holes (>=5) can always be covered with one of three tile combinations (A, A-1+1, A-2+2), so only small holes need brute force over tiles 1..4; the A = B = K case has small hand-solved answers. O(1) casework.",
     ["case analysis", "greedy exchange argument", "brute force small cases", "math"]),
    ("F", "Favorite Tree",
     "Two trees with up to 100 vertices; decide whether T1 has a connected subgraph isomorphic to T2.",
     "Subtree isomorphism DP over directed edges: can(goal subtree (u, parent), real subtree (v, parent)) is true iff the children of u can be matched injectively to children of v with can(child, child) true, a bipartite matching problem solved per pair (Kuhn's algorithm). Fix the root of one tree and try all roots of the other; cheap in practice since high-degree nodes are few.",
     ["tree isomorphism", "tree dp", "bipartite matching", "subtree embedding"]),
    ("G", "Gravitational Wave Detector",
     "Two disjoint convex polygons (up to 1e5 vertices) and N<=5e5 points; for each point decide whether there exist a in polygon 1 and b in polygon 2 such that the point, a and b are collinear with one of the three being the midpoint of the other two.",
     "The valid locations are the union of three convex sets: (P1 + P2)/2 (point in the middle), 2P1 - P2 (a in the middle) and 2P2 - P1 (b in the middle). Build each with a Minkowski sum of convex polygons (rotating calipers / merging edge vectors) in O(M1 + M2), then test each point with O(log M) point-in-convex-polygon (or sorting candidates).",
     ["minkowski sum", "convex polygon", "point in convex polygon", "computational geometry", "binary search"]),
    ("H", "Horse Race",
     "N<=300 horses, R small races each giving its participants and the overall placement of its winner; output any full ranking consistent with all races.",
     "Each race says all participants placed at W or worse and position W is held by one of them. Model as bipartite matching horses -> positions with allowed edges; or greedily process races from the worst winner: assign one horse common to all races with winner W to position W and the other participants to any free position below. Matching O(N^3) or linear greedy.",
     ["bipartite matching", "greedy", "constraint satisfaction", "constructive"]),
    ("I", "Italian Calzone & Pasta Corner",
     "R x C (<=100) grid of distinct order numbers; starting anywhere and walking freely (revisits allowed), eat dishes in increasing order, skipping allowed; maximize the number eaten.",
     "Eating order only forbids moving from a dish to an adjacent earlier one, so build a directed graph with edges from each cell to adjacent cells with larger numbers; the answer is the maximum number of nodes reachable from a start cell. BFS/DFS from every cell, O((RC)^2).",
     ["bfs", "graph reachability", "grid graph", "brute force"]),
    ("J", "Joining a Marathon",
     "R<=1000 runners with start times and speeds, P<=1e6 photos (time, segment) and Q<=1000 queries (start time, speed for an extra runner); for each query count photos still containing no runner.",
     "Kinetic sweep over time keeping runners sorted by position, swapping adjacent runners at their O(R^2) crossing events; each photo checks by binary search whether some runner is in its segment, discarding non-trash photos. Second sweep with the Q hypothetical runners: a segment tree over their current order receives range +1 for every remaining photo (binary search on the range of runners inside it) and supports adjacent swaps; final values answer queries. O((Q^2 + P) log(Q + P)).",
     ["kinetic sweep line", "event sorting", "segment tree", "binary search", "offline queries"]),
    ("K", "Kind Baker",
     "Using the minimum number of toppings, each applied to a connected set of cells of a 100x100 cake, create exactly K<=4000 distinct topping combinations; output the sets.",
     "ceil(log2 K) toppings are necessary and sufficient: write numbers 0..K-2 in separate cells and give topping i to cells whose number has bit i set, plus a comb-shaped connector region that receives all toppings (so every topping region is connected; the all-toppings combination is the extra K-th type).",
     ["constructive", "bitmask encoding", "grid construction", "connectivity"]),
    ("L", "Lazy Printing",
     "String T (<=2e5) and D; the machine prints prefixes of infinite repetitions of a string of length <=D. Minimize instructions to print T.",
     "A piece is valid iff it has period <= D, and substrings of valid pieces are valid, so greedily take the longest valid prefix each time. Compute it with a prefix-function (KMP) pass that stops when the minimal period exceeds D, or with sqrt decomposition (O(N sqrt N)) / suffix array LCP. O(N) total.",
     ["greedy", "prefix function", "kmp", "string periods", "sqrt decomposition"]),
    ("M", "Maze in Bolt",
     "Nut pattern (circular binary string of length C<=100) and a bolt maze of R<=1000 circular rows; the nut moves up/down/rotates if all its tips are over empty cells, and may be flipped before entering; decide if it can traverse the maze.",
     "BFS over states (row, rotation offset) for the nut and for its flipped (reversed) version; a state is valid iff every tip at the rotated position lies on a '0' of that row. Moves: rotate +-1 (cyclic), row up/down. O(R * C^2).",
     ["bfs", "state space search", "circular strings", "simulation"]),
]

P[2023] = [
    ("A", "Analyzing Contracts",
     "N<=2e5 suppliers sorted by start day (increasing) and price (decreasing); online operations add a client (revenue R, end day E) or ask, for a supplier i, the maximum profit (R - P_i)(E - S_i + 1) over current clients (0 if none positive).",
     "Each client is a function f_j over supplier indices; any two such functions cross at most once (a dominance / rectangle-area argument as in WF2017 'Money for Nothing'). Hence clients can be inserted in a Li Chao tree over the index domain [1, N] with careful handling of the zero-profit regions, answering point queries in O(log N). Alternative: sqrt decomposition on queries with the divide-and-conquer optimization per block.",
     ["li chao tree", "functions crossing once", "divide and conquer optimization", "online queries", "sqrt decomposition"]),
    ("B", "Blackboard Game",
     "3N numbers (N<=1000); in each round Carlinhos circles one number, Equalizer squares one and erases one; Carlinhos wins if final sums differ. Decide the winner.",
     "Equalizer must always copy Carlinhos's value (otherwise Carlinhos can run away by always taking the extreme), and the losing positions for Carlinhos are exactly those where every value's frequency is divisible by 3; otherwise Carlinhos can keep some frequency non-divisible until a singleton appears. Count frequencies. O(N).",
     ["game theory", "invariant", "frequency counting", "math"]),
    ("C", "Candy Rush",
     "Array of N<=4e5 brands in 1..K; find the longest contiguous block in which all K brands appear equally often.",
     "A block is valid iff the difference of prefix frequency vectors is a multiple of the all-ones vector. Normalize prefix vectors by subtracting 1 from every entry whenever all are >= 1 (amortized O(1)), keep a polynomial hash sum b_i * freq_i updated in O(1), and find for each prefix the earliest prefix with the same normalized hash. O(N log N) (or O(N sqrt N) by splitting on K).",
     ["prefix frequency vectors", "hashing", "normalization", "longest equal-key pair", "sqrt decomposition"]),
    ("D", "Deciphering WordWhiz",
     "Wordle-like game with N five-distinct-letter words, the first being the secret; for each feedback pattern given, count dictionary words that would produce it.",
     "Compute each dictionary word's feedback against the secret (green/yellow/gray per position) and count matches per query; brute force is fast enough.",
     ["simulation", "brute force", "strings"]),
    ("E", "Elevated Profits",
     "Tree with N<=3e5 vertices labelled 1..N, start at R; visit order must have each new city adjacent to visited ones (parent first); maximize sum of i * label of i-th visited city.",
     "Tree-precedence scheduling ('Color a Tree'): think backwards and group vertices into buckets that are taken consecutively, ordered by average value. Recursively turn each child subtree into a sorted list of buckets, merge children with small-to-large sets ordered by average, then append the root and repeatedly merge it with the last bucket while its value exceeds the bucket average (stack). Keep size, sum and weighted sum per bucket. O(N log^2 N).",
     ["greedy exchange argument", "tree precedence scheduling", "small to large merging", "average ratio merging", "color a tree"]),
    ("F", "Forward and Backward",
     "Given N<=1e12, list all bases b in [2, N] in which N is a palindrome.",
     "Palindromes with >= 3 digits need b <= sqrt(N-1): check those bases directly. Two-digit palindromes dd_b mean N = d(b+1) with d < b, so enumerate divisors d <= sqrt(N+1)-1 and set b = N/d - 1. Total O(sqrt(N) log N).",
     ["number theory", "base conversion", "palindromes", "sqrt enumeration", "divisors"]),
    ("G", "GPS on a Flat Earth",
     "N<=1e5 towers with exact Manhattan distances to the user; list all integer points consistent with all measurements (guaranteed finite and non-empty).",
     "Rotate coordinates by 45 degrees (u = x + y, v = y - x) so each Manhattan circle becomes an axis-aligned square boundary made of 4 segments. Maintain the candidate set as a small list of segments/points and intersect it with each new square segment-wise (same-orientation overlap or perpendicular crossing); finally enumerate points with the right parity and map back. O(N).",
     ["manhattan distance", "45 degree rotation", "segment intersection", "geometry casework"]),
    ("H", "Health in Hazard",
     "N<=2e5 lines arrive in order, each becomes an uncrossable wall; find the first moment when the bear at the origin can no longer reach any point at Euclidean distance exactly D.",
     "Binary search on the number of lines. For a prefix, the reachable region is the intersection of half-planes containing the origin; the bear fails iff that region is bounded and all its vertices are within distance < D (half-plane intersection O(n log n)). Alternatively each line cuts an open arc from the circle of radius D; check whether the arcs cover the whole circle with an angular event sweep. O(N log^2 N).",
     ["binary search on answer", "half-plane intersection", "circle arc coverage", "computational geometry", "angular sweep"]),
    ("I", "Inversions",
     "String S (<=1e5) repeated N<=1e12 times; count inversions modulo 1e9+7.",
     "inv(S^N) = N * inv(S) + C(N, 2) * cross(S, S), where cross counts pairs (a in first copy, b in second copy, a > b) = sum over letter pairs c1 > c2 of cnt[c1] * cnt[c2]. Count with 26-letter frequency arrays, careful modular arithmetic. O(26 |S|).",
     ["counting inversions", "combinatorics", "modular arithmetic", "frequency counting"]),
    ("J", "Journey of the Robber",
     "Tree with N<=1e5 vertices labelled 1..N; for each vertex i find the closest vertex with a larger label (ties to smaller label).",
     "Centroid decomposition: for each centroid store the vertices of its component with their distances, sorted by label, with suffix minima of (distance, label). For a vertex i, at every ancestor centroid c query the best vertex with label > i via binary search and combine dist(i, c) + suffix-min. O(N log^2 N). (Alternative O(N sqrt N) with block processing and multi-source BFS.)",
     ["centroid decomposition", "tree distances", "suffix minimum", "binary search", "sqrt decomposition"]),
    ("K", "Keen on Order",
     "Sequence of N<=300 values in 1..K (K<=300); decide whether every permutation of 1..K is a subsequence, otherwise output one that is not.",
     "If K >= 25 a greedy always succeeds: repeatedly pick the unpicked value whose next occurrence (after the previous pick) is latest; since 1+2+...+25 > 300 some value runs out. For K <= 24 use bitmask DP dp[mask] = max over x in mask of next(x, dp[mask without x]) (the latest possible minimal end of embedding a permutation of mask), reconstructing a non-subsequence permutation when it reaches 'infinity'. O(K * 2^K).",
     ["bitmask dp", "subsequence greedy", "next occurrence", "pigeonhole", "constructive"]),
    ("L", "Latam++",
     "String of length <=2e5 over lowercase letters, parentheses and + - * /; count substrings that are valid expressions.",
     "Map letters to 'a' and operators to '+'. A substring is valid iff parentheses are balanced (all prefix balances >= 0, total 0), it contains none of the forbidden adjacent pairs (), (+, +), ++, )(, )a, a( and does not start or end with '+'. Split at forbidden pairs and count balanced substrings with valid endpoints by divide and conquer (match good suffix/prefix balances across the cut) or by prefix balances with RMQ + binary search. O(N log N).",
     ["counting balanced substrings", "prefix balance", "divide and conquer", "sparse table rmq", "parsing"]),
    ("M", "Meeting Point",
     "Weighted graph with N, M<=1e5; find all vertices V such that every shortest path from P to V passes through G exactly at its midpoint.",
     "Run Dijkstra from P; candidates satisfy dist(V) = 2 * dist(G). G lies on every shortest path to V iff removing G strictly increases the distance, so run Dijkstra again skipping G and keep candidates whose new distance is larger. O(M log N).",
     ["dijkstra", "shortest paths", "vertex on all shortest paths", "graph"]),
]


def main():
    contests, problems = [], []
    for c in CONTESTS:
        y = c["edition"]
        html_path = os.path.join(DL, f"latam-{y}-index.html")
        stats, _ = pbro.parse(html_path, c["group"], pbro.DEFAULT_EXCLUDE)
        letters = [p[0] for p in P[y]]
        assert letters == stats["letters"], (y, letters, stats["letters"])
        gym = f"https://codeforces.com/gym/{c['gym']}" if c["gym"] else None
        contests.append({
            "id": c["id"], "family": "latam_regional", "name": c["name"], "short": c["short"],
            "year": c["year"], "date": c["date"], "total_teams": stats["total_teams"],
            "links": {"scoreboard": c["scoreboard"], "statements": c["statements"],
                      "editorial": c["editorial"], "mirror": gym, "kattis": None},
            "notes": c["notes"] + f" {stats['teams_with_submissions']} of {stats['total_teams']} official teams submitted at least once.",
        })
        for L, title, summ, idea, tags in P[y]:
            st = stats["problems"][L]
            problems.append({
                "id": f"{c['id']}-{L}", "contest": c["id"], "letter": L, "title": title,
                "solved_teams": st["solved"], "attempted_teams": st["attempted"],
                "first_solve_min": st["first_solve_min"],
                "links": {"mirror": f"{gym}/problem/{L}" if gym else None, "kattis": None,
                          "statement": c["statements"]},
                "statement_summary": summ, "solution_idea": idea,
                "solution_source": SOURCE_OVERRIDE.get(f"{c['id']}-{L}", c["sol_source"]), "candidate_tags": tags,
                "cf_tags": [], "cf_rating": None,
            })
    out = {"source": "latam_regional_2019_2023", "contests": contests, "problems": problems}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"wrote {OUT}: {len(contests)} contests, {len(problems)} problems")


if __name__ == "__main__":
    main()
