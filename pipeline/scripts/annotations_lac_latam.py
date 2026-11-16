# -*- coding: utf-8 -*-
"""Hand-written annotations (titles, summaries, solution ideas, tags) for
LAC 2024-2026 and Latin American Regional 2024-2025. Numbers are NOT here: they are parsed
from the BOCA scoreboards by build_lac_latam_raw.py."""

SL = 'https://scorelatam.naquadah.com.br'

CONTESTS = {
    'lac2024': {
        'id': 'lac2024', 'family': 'lac',
        'name': 'The 2024 ICPC Latin America Championship (Programadores de America 2024)',
        'short': 'LAC 2024', 'year': 2024, 'date': '2024-03-17',
        'links': {'scoreboard': f'{SL}/pda24/', 'statements': f'{SL}/pda24/contest.pdf',
                  'editorial': f'{SL}/pda24/editorial.pdf',
                  'mirror': 'https://codeforces.com/gym/105053', 'kattis': None},
        'notes': ("Counts from the 'PdA' sub-scoreboard (sitegroup 1) of the BOCA final scoreboard: 40 official "
                  "teams; 1 guest team of the parallel Chilean CCL contest excluded. Final (unfrozen) scoreboard; "
                  "first_solve_min = minute shown in the scoreboard cell."),
        '_html': 'pda24.html', '_gym': 105053,
    },
    'lac2025': {
        'id': 'lac2025', 'family': 'lac',
        'name': 'The 2025 ICPC Latin America Championship (Programadores de America 2025)',
        'short': 'LAC 2025', 'year': 2025, 'date': '2025-03-16',
        'links': {'scoreboard': f'{SL}/pda25/', 'statements': f'{SL}/pda25/contest.pdf',
                  'editorial': f'{SL}/pda25/editorial.pdf',
                  'mirror': 'https://codeforces.com/gym/105789', 'kattis': None},
        'notes': ("Counts from the 'PdA' sub-scoreboard (sitegroup 1): 40 official teams; 9 CCL guest teams "
                  "(teamccl*) excluded. E, H, J unsolved by official teams. Editorial is a slide deck "
                  "(its per-problem stats include post-freeze data and differ slightly from the final board)."),
        '_html': 'pda25.html', '_gym': 105789,
    },
    'lac2026': {
        'id': 'lac2026', 'family': 'lac',
        'name': 'The 2026 ICPC Latin America Championship (Programadores de America 2026)',
        'short': 'LAC 2026', 'year': 2026, 'date': '2026-03-07',
        'links': {'scoreboard': f'{SL}/pda26/', 'statements': f'{SL}/pda26/contest.pdf',
                  'editorial': None,
                  'mirror': 'https://codeforces.com/gym/106416', 'kattis': None},
        'notes': ("Counts from the 'PdA' sub-scoreboard (sitegroup 1): 41 official teams; 11 CCL guest teams "
                  "excluded. C, D, H unsolved by official teams. No official editorial found (scorelatam "
                  "editorial link is 404; CF blog entry 151965 says it is 'in the works'; the CMU PDF is only a "
                  "scoreboard printout). Solution ideas were checked against the jury reference solutions shipped in "
                  "scorelatam's pda26/contest-packages.tar (solutions/ folder of each BOCA package) and the CF gym "
                  "thread (blog entry 151965), hence solution_source='community'."),
        '_html': 'pda26.html', '_gym': 106416,
    },
    'latam_regional2024': {
        'id': 'latam_regional2024', 'family': 'latam_regional',
        'name': '2024-2025 ICPC Latin American Regional Programming Contest',
        'short': 'LATAM Regional 2024', 'year': 2024, 'date': '2024-11-09',
        'links': {'scoreboard': f'{SL}/latam-2024/', 'statements': f'{SL}/latam-2024/contest.pdf',
                  'editorial': f'{SL}/latam-2024/icpcla24_solution_sketches.pdf',
                  'mirror': 'https://codeforces.com/gym/105505', 'kattis': None},
        'notes': ("Counts from the 'Global' sub-scoreboard (sitegroup 1) of the BOCA final scoreboard: 490 "
                  "official teams over all Latin American sites; the 26 CCL guest teams (only in 'Global+CCL') "
                  "excluded. B and C unsolved by official teams."),
        '_html': 'latam-2024.html', '_gym': 105505,
    },
    'latam_regional2025': {
        'id': 'latam_regional2025', 'family': 'latam_regional',
        'name': '2025-2026 ICPC Latin American Regional Programming Contest',
        'short': 'LATAM Regional 2025', 'year': 2025, 'date': '2025-11-08',
        'links': {'scoreboard': f'{SL}/latam-2025/', 'statements': f'{SL}/latam-2025/contest.pdf',
                  'editorial': None,
                  'mirror': 'https://codeforces.com/gym/106178', 'kattis': None},
        'notes': ("Counts from the 'Global' sub-scoreboard (sitegroup 1): 558 official teams (matches the "
                  "organizers' '558 official teams'); 'Global+CCL' has 593 rows: 34 CCL guests plus one team "
                  "(teamcbpr003) not listed in Global, all excluded. D and G unsolved by official teams. No "
                  "official editorial published (scorelatam link commented out/404), so solution ideas are own "
                  "analysis (solution_source='own'), except F and I, checked against sketches in the CF gym "
                  "thread (blog entry 148306, via web.archive.org). The scorelatam contest-packages.tar for this "
                  "contest contains no jury solutions."),
        '_html': 'latam-2025.html', '_gym': 106178,
    },
}


def P(title, summary, idea, tags, source='editorial'):
    return {'title': title, 'summary': summary, 'idea': idea, 'tags': tags, 'source': source}


OWN = 'own'
COMM = 'community'

PROBLEMS = {
    # ------------------------------------------------------------------ LAC 2024
    'lac2024': {
        'A': P('Almost Aligned',
               'N (up to 1e6) points move linearly, (X+t*VX, Y+t*VY); find the minimum area of an axis-aligned '
               'rectangle containing all points at some time t >= 0.',
               'Width(t)=max(X+VX t)-min(X+VX t) and height(t) are convex piecewise-linear functions obtained as '
               'upper/lower envelopes of lines (convex hull trick). Their product is not convex, so ternary search '
               'fails; between consecutive breakpoints the area is a quadratic whose minimum is at an endpoint, so '
               'evaluate t=0 and every envelope breakpoint. O(N log N).',
               ['convex hull trick', 'upper/lower envelope of lines', 'piecewise linear functions',
                'kinetic bounding box', 'candidate breakpoints']),
        'B': P('Beating the Record',
               'A speedrun game has N<=4 levels, each with two risky strategies (success probability, good/bad '
               'times); the player may restart at any time. Minimize the expected total play time until beating '
               'the record T.',
               'Model a global strategy as a binary decision tree over level outcomes (choose strategy 1/2 and '
               'whether to restart on failure at every node); there are f(n)=2(f(n-1)^2+f(n-1)) ~ 2.1e7 trees for '
               'n=4, enumerate them by backtracking, computing success probability p and conditional expected '
               'times eg, eb; answer eg+(1/p-1)eb (care with precision). Alternative: binary search on the answer E '
               'and run a DP over (level, elapsed time) where a restart costs the guessed E (fixed-point monotone).',
               ['expected value', 'probability', 'exhaustive search over strategies',
                'binary search on answer (fixed point)', 'dp over time']),
        'C': P('Clever Cell Choices',
               'On an N x M grid (N,M<=50) with blocked cells, players alternately place stones each adjacent to '
               'the previous one; count starting cells from which the first player wins.',
               'Undirected vertex geography: the first player wins from v iff v is NOT covered by every maximum '
               'matching of the (bipartite) grid graph. Compute one max matching (Hopcroft-Karp/Dinic) and find '
               'vertices reachable by alternating paths from unmatched vertices of the same side (residual-graph '
               'reachability from source/sink); those are the winning cells. O(E sqrt V).',
               ['bipartite matching', 'game theory', 'undirected vertex geography', 'alternating paths',
                'max flow residual graph']),
        'D': P('DiviDuelo',
               'Players alternately pick divisors of N (N<=1e12) until all are taken; the first player wins if '
               'the gcd of his picks is not 1. Decide the winner.',
               'Case analysis on the factorization: if N=p^a the first player loses only if forced to take 1 '
               '(odd number of divisors); if N=p*q he wins by taking pq then p or q; otherwise (p^a q^b with a>=2 '
               'or >=3 primes) the second player pairs sets like {1,q},{p,p^2} to force gcd 1. First player wins '
               'iff N=p^a with a odd or N=p*q. Factor by trial division O(sqrt N).',
               ['game theory', 'number theory', 'prime factorization', 'case analysis', 'pairing strategy']),
        'E': P('Expanding STACKS!',
               'Given 2N enter/leave events of N customers (N<=1000), assign each customer to one of two LIFO '
               'lines so every departure is from the back of its line, or report impossible.',
               'Two customers can share a stack unless their intervals cross (+a +b -a -b). Build the conflict '
               'graph of crossing intervals in O(N^2) and 2-color it (bipartiteness check); colors give the '
               'lines. (Linear-time alternative maintains a stack of pairs of item lists.)',
               ['bipartite graph check', 'graph coloring', 'interval crossing', 'two-stack sorting']),
        'F': P('Fair Distribution',
               'N blueprints (ground height G, residential floor height R, >=1 residential floor each); decide if '
               'they can be split between two children so that some choice of floor counts makes total heights '
               'equal. N<=2e5, sum G<=2e5.',
               'By Bezout, the residential floors can compensate exactly the differences that are multiples of '
               'g=gcd of all R, so a fair split exists iff some achievable ground-floor difference sumG(A)-sumG(B) '
               '(both parts non-empty) is divisible by g. Enumerate achievable subset sums of G with a knapsack '
               'over O(sqrt S) distinct values (binary splitting / bitset). O(S sqrt S).',
               ['number theory', 'bezout identity', 'gcd', 'subset sum', 'bounded knapsack sqrt trick',
                'bitset']),
        'G': P('Greek Casino',
               'A token starts at slot 1 of N (N<=1e5); repeatedly a weighted random y is drawn and the token moves '
               'to lcm(x,y) if <=N (earning a coin), else the game ends. Compute the expected number of coins.',
               'Let E_a be the expected number of visits to a; then E = p (lcm-convolution) E + delta_1. The '
               'divisor-sum (zeta) transform T(A)_k = sum_{d|k} A_d turns lcm-convolution into pointwise '
               'products, so T(E) = 1/(1-T(p)) pointwise, then invert (Mobius over divisors); answer sum E_a - 1. '
               'O(N log N). Alternative: forward DP over multiples with divisor enumeration, O(N log^2 N).',
               ['expected value', 'lcm convolution', 'zeta/mobius transform over divisors', 'dp over divisors',
                'harmonic sum complexity']),
        'H': P('Harmonic Operations',
               'Given a string S and K operations (reverse, rotate right/left by D), count pairs (i,j) such that '
               'applying operations i..j to S yields S. |S|,K<=2e5.',
               'The operations form the dihedral group; keep prefix compositions P(i) as (reflected?, shift). '
               'Reduce S to its primitive root (period via KMP) so that at most two group elements fix S: the '
               'identity and possibly one reflection+rotation (found by matching reverse(S) inside S+S). Count '
               'pairs with P(i)^{-1}P(j) in that set using a hashmap of prefix elements. O(|S|+K).',
               ['dihedral group', 'prefix composition counting', 'kmp', 'string periodicity',
                'hashmap pair counting']),
        'I': P('Insects, Mathematics, Accuracy, and Efficiency',
               'N<=1e4 integer points lie inside a circle of radius R<=1e4 centered at the origin; add one point '
               'inside the circle to maximize the area of the convex hull.',
               'Take the convex hull (lattice points in a radius-1e4 disc give at most ~1600 hull vertices, '
               'O(R^{2/3})). The new point lies on the circle; for each pair of hull vertices (i,j) that remain '
               'neighbors of the new point, the area is the hull area minus the cut-off chain plus the triangle '
               'with apex at the circle point farthest from chord ij; maintain running areas for O(H^2) (or '
               'O(H log H) via angular critical segments). Watch precision.',
               ['convex hull', 'computational geometry', 'lattice convex hull bound', 'polygon area updates',
                'circle geometry', 'floating point precision']),
        'J': P('Joys of Trading',
               'Two villages produce N resources with per-unit costs A_i and B_i and fixed current outputs; '
               're-allocate production (each village within its current person-hours) to produce the same totals '
               'with minimum total person-hours. N<=1e5.',
               'Exchange argument (comparative advantage): sort resources by B_i/A_i; some optimal solution has '
               'village A producing a prefix and B a suffix with at most one shared resource. Try every split '
               'resource with prefix/suffix sums and greedily split it given remaining capacities. O(N log N).',
               ['greedy', 'sort by ratio', 'exchange argument', 'comparative advantage', 'prefix sums']),
        'K': P('KMOP',
               'Build the shortest acronym taking a 1-3 letter prefix of each of N words (total length 1e6) so '
               'that it never has three consecutive consonants, or report impossible.',
               'Shortest path / DP over states (word index, letters taken from current word 1..3, trailing '
               'consonant run 0..2) with two transitions (take next letter or move to next word); O(N). A greedy '
               'that fixes the first bad consonant triple also works.',
               ['dp', 'shortest path on dag', 'strings', 'greedy']),
        'L': P('LED Matrix',
               'A R x C LED matrix with broken LEDs scrolls an R x K pattern from right to left; decide whether '
               'every required LED can be lit at every step.',
               'Every pattern column passes over every matrix column, so each row works iff its matrix row has no '
               'broken LED or its pattern row has no lit LED. O(R(C+K)).',
               ['ad hoc', 'implementation', 'observation']),
    },
    # ------------------------------------------------------------------ LAC 2025
    'lac2025': {
        'A': P('Ananna',
               'Directed multigraph with N,M<=5000 and a letter on each edge; count ordered pairs (U,V), U!=V, '
               'with a walk from U to V whose letter sequence is a palindrome.',
               'BFS over pair states (u,v) = "there is a palindromic walk u->v": start from (u,u) (and single '
               'edges as odd centers), and from (u,v) extend to (u\',v\') for every edge u\'->u and v->v\' with '
               'the same letter. Total work sum indeg(u)*outdeg(v) = O(M^2).',
               ['bfs on pair states', 'palindromes', 'product graph', 'graph reachability']),
        'B': P('Brazilian FootXOR',
               'Given N binary strings of length K (N,K<=1500), pick two disjoint non-empty teams of equal size '
               'with equal XOR, or report impossible.',
               'Equivalent to finding a non-empty even-size subset with XOR 0 (split it in halves). Append an '
               'extra bit 1 to every vector so that any XOR-zero subset has even size, then find a linear '
               'dependency with Gaussian elimination over GF(2) using bitsets, tracking combinations. O(N K^2/64).',
               ['linear algebra over gf(2)', 'gaussian elimination', 'xor basis', 'bitset', 'constructive']),
        'C': P('Coatless in Yakutsk',
               'A coat can be worn at most C consecutive days before washing; given N daily temperatures, '
               'schedule washes to maximize the minimum temperature endured without the coat.',
               'Answer is the largest t such that no run of more than C consecutive days has temperature < t; '
               'temperatures are in [-50,50], so try every t with a linear scan (or binary search on t). '
               'O(101 N).',
               ['binary search on answer', 'brute force over values', 'greedy', 'sliding window']),
        'D': P('Dangerous City',
               'Connected graph with N,M<=3e5 and danger D_i on vertices; f(u,v) = min over paths of the max '
               'vertex danger; output sum_v f(u,v) for every u.',
               'Minimax path costs live on the MST; build a Kruskal reconstruction tree (DSU, edges weighted by '
               'max endpoint danger, processed increasingly) whose internal node weight is the bottleneck. For a '
               'leaf, answer = sum over its root path of (leaves(v_i) - leaves(v_{i+1})) * w(v_i) + D_u, computed '
               'with one DFS. O(N log N). (Small-to-large merging also works.)',
               ['kruskal reconstruction tree', 'dsu', 'minimax bottleneck path', 'mst', 'tree dp']),
        'E': P('Exciting Business Opportunities',
               'Tree with N<=1e5 nodes and P<=1e5 proposals (sponsor node or business node); a contiguous range of '
               'proposals is valid if every business lies on a path between two sponsors of the range (or is '
               'sponsored). For every start i, output the longest valid range.',
               'For each business at node B, find the nearest sponsors to the left/right (in proposal order) '
               'lying in different subtrees around B (segment tree over proposals with Euler-tour subtree '
               'info); they define for which starts which ends become invalid. Sweep the start position and keep '
               'valid ends with a lazy segment tree (range add + min / first invalid). O((N+P) log). '
               'Alternative: divide and conquer.',
               ['segment tree', 'sweep line', 'euler tour', 'tree paths', 'lazy propagation']),
        'F': P('Festival Signs',
               'Process N events: add or remove a rectangle [A,B] x [0,H) and query, for an interval [L,R], the '
               'lowest uncovered height (min over x in [L,R] of the max height covering x).',
               'Insertions plus queries are a segment tree with lazy range chmax and range min. Removals are '
               'handled offline with the "offline dynamic connectivity" trick: segment tree over time, each '
               'rectangle added to O(log N) time nodes, DFS with a rollback-able segment tree (stack of changes or '
               'persistence). O(N log^2 N).',
               ['offline deletion (segment tree over time)', 'rollback', 'segment tree lazy propagation',
                'range chmax', 'divide and conquer on time']),
        'G': P('Game of Pieces',
               'Simplified Tetris on an infinite board: N<=2e5 vertical (L x 1) or horizontal (1 x L) pieces '
               'dropped at columns up to 1e18; a piece that creates a hole is removed. Output safe/unsafe per '
               'piece.',
               'If the board is always hole-free it is described by column heights; a horizontal piece is unsafe '
               'iff the heights on its span are not all equal (vertical pieces are always safe). Maintain heights '
               'as a set of [l,r,h] intervals in an ordered map, or a sparse / coordinate-compressed segment tree '
               'with "all equal" query and range assign. O(N log N).',
               ['interval set (ordered map of ranges)', 'segment tree', 'coordinate compression', 'simulation']),
        'H': P('Horrible Restaurants',
               'N<=2e5 restaurants each get 0..3 stars with increasing costs C1<C2<C3; output the minimum cost to '
               'reach exactly k total stars for every k=1..3N.',
               'From an optimal solution for k stars, an optimal one for k+1 is reachable by a small exchange: '
               '+1 on one restaurant, +2/-1, +3/-2, +3/-1/-1 or +2/+2/-3. Maintain heaps/sets of candidate '
               'deltas for each restaurant state and apply the cheapest move each step. O(N log N).',
               ['greedy exchange', 'priority queue', 'incremental optimal solutions', 'knapsack with small items']),
        'I': P('Infinite Arrays',
               'Maintain an array P of distinct values under insert-before and delete; answer queries: the longest '
               'common subarray between the infinite repetitions of P and of a query array A (or * if unbounded).',
               'A common subarray of the periodic sequences is a run of A (scanned over A concatenated twice) '
               'where each element is the cyclic successor of the previous one in P; maintain P as a doubly '
               'linked list keyed by value (hash/array next/prev, wrap from last to first). If A is one full '
               'consistent cycle of P the answer is infinite. O(1) per update, O(|A|) per query.',
               ['linked list', 'cyclic sequences', 'two pointers', 'implementation', 'hashing']),
        'J': P('Just Look Up',
               'N<=500 stars in 3D; find the largest half-angle of a cone with apex at the origin containing no '
               'star (90 if a half-space is empty).',
               'Project stars on the unit sphere; this is the largest empty spherical cap. Its circle passes '
               'through >=3 points (or 2 with a constrained center); candidates are circumcircles of faces of the '
               '3D convex hull of the projected points (spherical Delaunay), or iterate pairs plus center '
               'direction in O(n^3). Check the empty-hemisphere case.',
               ['3d convex hull', 'spherical geometry', 'largest empty circle', 'delaunay/voronoi duality',
                'computational geometry']),
        'K': P('Keep Fighting',
               'Card game with N<=50 cards (multiply power, add power, attack); the deck is replayed in cycles, '
               'each card once per cycle in any order; find the minimum number of turns to deal H damage.',
               'If one cycle is not enough, play attacks first, then multipliers, then adders in every full cycle '
               '(power only grows), simulating O(sqrt H) cycles; for the final partial cycle brute force how many '
               'cards of each type to play, taking the best adders/multipliers sorted by value (handle x1 cards '
               'and zero power). O(N sqrt H).',
               ['greedy', 'brute force', 'simulation', 'case analysis', 'exchange argument']),
        'L': P('LED Counter',
               'A seven-segment counter has stuck-on/stuck-off LEDs; for each of N positions output the intended '
               'digit or * if ambiguous.',
               'For each position try all 10 digits, ignoring stuck segments and matching the good ones. '
               'O(70 N).',
               ['brute force', 'implementation', 'ad hoc']),
    },
    # ------------------------------------------------------------------ LAC 2026 (no editorial)
    'lac2026': {
        'A': P('Ants on a Ring',
               'N<=1000 labeled ants on a ring of L<=1e9 spots must reach given target spots; ants move one spot '
               'per second and can never meet or pass each other. Find the minimum time or report impossible.',
               'Ants cannot overtake, so the cyclic order is preserved. Sort ants by start position and unwrap '
               'the ring: fix the unwrapped target of the first ant (only two candidates matter, its nearest '
               'target clockwise or counter-clockwise), then each next ant takes its own target at the first '
               'unwrapped position clockwise after the previous ant\'s; if this passes one full lap (first target '
               '+ L) the order is broken and that candidate is impossible. Order-preserving moves on a line '
               'achieve makespan max_i |start_i - target_i|; answer = min over the two candidates, or *. '
               'O(N log N) (jury reference solution).',
               ['ad hoc', 'cyclic order invariant', 'unwrapping a circle', 'minimize max displacement',
                'case analysis'], COMM),
        'B': P('Booksort',
               'N<=5000 stacks with A_i<=1e5 books; a command (i,j) replaces A_i, A_j by floor/ceil of their '
               'average (floor at the first index). Output at most 1e5 commands that sort the stacks '
               'non-decreasingly.',
               'Constructive: repeatedly pair the k-th smallest stack with the k-th largest and average them; '
               'the value range roughly halves per round, so after O(log V) rounds (~N/2 commands each) all values '
               'are in {q,q+1}. Then a command on (i,j), i<j, with A_i=q+1, A_j=q swaps them; match leftmost '
               'q+1s with rightmost qs. About 1.4e4 commands for N=5000 (checked by simulation). Jury solutions '
               'do the same (repeatedly average the global min and max until the range is <= 1, then swap) or, '
               'even simpler, fix positions left to right: while A_i exceeds the minimum of the suffix, average '
               'i with that minimum (an ordered set gives the minimum).',
               ['constructive', 'averaging/balancing', 'greedy pairing', 'invariants'], COMM),
        'C': P('Crop Circles',
               'Given N<=40 sprinkler disks, find the largest circle whose whole perimeter lies inside the union '
               'of the disks (the inside may be dry).',
               'Candidates are each sprinkler circle itself plus every circle through three vertices of the union '
               'boundary, i.e. pairwise circle-circle intersection points that are not strictly inside any other '
               'disk (deduplicated). Verify each candidate by intersecting it with every sprinkler disk, turning '
               'the covered parts into angular intervals and checking that their union is the full 2*pi; keep the '
               'largest radius. O(V^3 * N log N) with V = boundary vertices; careful epsilons (jury reference '
               'solution).',
               ['computational geometry', 'union of disks', 'circle-circle intersection',
                'angular interval coverage', 'candidate enumeration', 'circumcircle of three points'], COMM),
        'D': P('Dropshipping',
               'N<=2e5 requests with even prices A_i; every (X+1)-th purchase gets 50% off; request i must be '
               'bought within the first i+K purchases. Choose the purchase order maximizing total discount.',
               'Fill purchase slots from the last one backwards: slot t can hold any not-yet-placed request with '
               'index >= t-K, so going from t=N down to 1 the set of eligible requests is a window that only gains '
               'one request per step (request t-K-1). Keep it in a multiset; at a discounted slot (t multiple of '
               'X+1) take the most expensive eligible request (add half its price), otherwise discard the '
               'cheapest. Every slot is forced to take someone from the window, so this exchange-argument greedy '
               'is optimal. O(N log N) (jury reference solution; also explained in the CF gym thread).',
               ['greedy with multiset', 'scheduling with deadlines', 'backward sweep', 'exchange argument',
                'sliding window'], COMM),
        'E': P('Eye Exam',
               'Given N<=1000 answers "A closer", "B closer" or "equal" for lens pairs A<B, output the minimum and '
               'maximum integer prescription x consistent with all answers, or *.',
               'Each answer is a half-line on 2x: "A" means 2x < A+B, "B" means 2x > A+B, "E" means 2x = A+B. '
               'Intersect all constraints and output the integer range. O(N).',
               ['math', 'interval intersection', 'implementation'], COMM),
        'F': P('Fun with Balls',
               'N<=150 colored balls are added one by one to a stable 2D pile, always at the highest available '
               'place; find the maximum size of a same-color connected cluster over all possible piles.',
               'The highest-place rule forces the pile to be a triangle grown by diagonals: while the pyramid is '
               'not full the next ball goes to the forced row; only when it is full can the ball go to the left '
               'or right end of the ground row. So a pile is determined by ~16 left/right choices: backtrack over '
               'all of them (jury reference), place the balls and compute same-color clusters with DFS on the '
               'triangular lattice (6 neighbours).',
               ['brute force', 'backtracking', 'simulation', 'flood fill', 'structural observation'], COMM),
        'G': P('GATA-CAT',
               'For Q<=1000 queries (G, C <= 1e6) build a DNA string of length <= 500 whose number of GATA '
               'subsequences is G and number of CAT subsequences is C.',
               'Build the string as groups [G..G C..C] followed by "AT", repeated r times. A G followed by j '
               'remaining "AT" blocks completes C(j+1,3) GATA subsequences (tetrahedral number) and a C followed '
               'by j blocks completes j(j+1)/2 CAT subsequences (triangular number), with no cross-talk. So write '
               'G as a sum of tetrahedral numbers and C as a sum of triangular numbers (take the largest, then the '
               'remainder with a precomputed min-terms BFS/DP, or plain greedy) and put each letter before the '
               'right number of AT blocks; fits in 500 letters (jury reference solution).',
               ['constructive', 'subsequence counting', 'triangular/tetrahedral numbers',
                'greedy decomposition', 'coin change'], COMM),
        'H': P('Holes and Tunnels',
               'In a tree with N<=2e5 vertices, for each k=1..N-1 count ordered pairs of paths sharing exactly k '
               'edges (mod 998244353).',
               'The intersection of two tree paths is a path u..v; the pair intersects exactly there iff both '
               'paths extend past u (and v) into different branches or stop there. With F(u->v) = S^2 - sum s_i^2 '
               '(S = vertices on u\'s side, s_i = sizes of branches at u away from v), answer_k = sum over paths '
               'u..v of length k of F(u->v) F(v->u). Compute this distance-indexed sum with centroid decomposition '
               '+ NTT convolution of weighted depth polynomials (per centroid, sum over pairs of child polynomials via (sum P)^2 - sum P^2). O(N log^2 N) (matches the jury reference solution).',
               ['centroid decomposition', 'ntt/fft convolution', 'counting paths in trees', 'combinatorics',
                'subtree sizes'], COMM),
        'I': P('Inversion Game',
               'Two players alternately move elements of a multiset S (N<=1e5) to the end of an array; Evelyn '
               'wins if the final number of inversions is even. Decide among Evelyn/Todd/first/second player wins.',
               'Picking x adds (#remaining elements smaller than x) to the inversion count, and copying the '
               'opponent\'s value cancels contributions, so only values with odd multiplicity matter. With m = '
               'number of values of odd multiplicity: m<=1 -> E, m even >=2 -> F, m odd >=3 -> S (Todd never wins '
               'regardless of order); verified by brute force on small multisets and identical to the jury solutions. O(N).',
               ['game theory', 'parity argument', 'mirroring strategy', 'inversions'], COMM),
        'J': P('Jaime\'s Palace',
               'P<=2000 plates in a stack; on day i the top K_i plates are used and returned on top in an '
               'adversarial order. Find the largest t such that some plate is surely used at least t times after '
               'D<=2000 days.',
               'Simulate the adversary greedily: after each day put the used plates back with the least-used ones '
               'on top (so heavily used plates sink and usage stays balanced); the answer is the final maximum '
               'count. Exchange argument; matches exhaustive search on small cases and the jury reference (increment the top K counts, re-sort them so the smallest is on top). O(D P log P), or counting sort.',
               ['greedy', 'simulation', 'adversarial argument', 'sorting'], COMM),
        'K': P('Kitten Greetings',
               'N<=4000 cats with distinct x and distinct y coordinates; a circuit alternates horizontal/vertical '
               'segments, each segment having a distinct cat at its midpoint, and returns to the start facing the '
               'same way. Maximize total length.',
               'Each step is a point reflection through a cat; horizontal and vertical steps alternate, so for '
               'consecutive cats b,c,d: 2c.x = b.x + d.x when c is on a horizontal step (2c.y = b.y + d.y on a '
               'vertical one). Since coordinates are distinct, an ordered pair of consecutive cats determines the '
               'next cat uniquely (hash lookup), giving a permutation on O(N^2) pair states; walk its cycles, keep '
               'those with even length, no repeated cat, and return to the start, and take the max perimeter. '
               'O(N^2) with hashing; a bitset marks visited (direction, pair) states (same as the jury reference).',
               ['functional graph / permutation cycles', 'point reflection', 'hashing', 'geometry', 'brute force '
                'over pairs'], COMM),
        'L': P('Late and Disobedient',
               'N<=1000 pedestrians move linearly on a line; for Q<=2e6 increasing times decide whether the '
               'crosswalk [0,L] has a free gap of width >= C between consecutive pedestrians/endpoints.',
               'Kinetic sorted order: pedestrians swap order at O(N^2) crossing times; maintain the sorted list '
               '(with the two crosswalk ends as fixed sentinels and entry/exit events) and for each adjacent pair '
               'schedule the times its gap crosses C. Process events in a priority queue while sweeping the sorted '
               'query times, keeping a count of adjacent pairs with gap >= C. All times are compared as exact fractions. O(N^2 log N + Q) (matches the jury reference solution).',
               ['kinetic data structure', 'event sweep', 'priority queue', 'offline queries',
                'linear motion'], COMM),
    },
    # ------------------------------------------------------------------ Regional 2024
    'latam_regional2024': {
        'A': P('Append and Panic!',
               'A string t was followed by its sorted, duplicate-free version; given the concatenation (|S|<=2000) '
               'recover |t|.',
               'The appended part has exactly one copy of each distinct letter, so |t| = |S| - (#distinct '
               'letters). O(|S|).',
               ['strings', 'counting', 'ad hoc']),
        'B': P('Biketopia\'s Cyclic Track',
               'Connected simple graph (N<=2e5, M<=3e5) with all degrees >= 3; find a cycle whose edges can be '
               'removed while keeping the graph connected.',
               'Always possible: build a DFS tree, choose the back edge xy maximizing min(depth) of its endpoints '
               '(x ancestor of y) and take it with the tree path x..y. Degree >= 3 guarantees every cycle vertex '
               'has another edge that leads (possibly down to a leaf and through a back edge) above x. O(N+M).',
               ['dfs tree', 'back edges', 'graph connectivity', 'constructive proof', 'cycles']),
        'C': P('Cindy\'s Christmas Challenge',
               'Given R, B and a string S over {R,B,G} (|S|<=5e5), answer W<=1e5 queries: edit distance between '
               'r^R b^B and substring S[L..U].',
               'Edit distance to a unary string has a closed form d(a^x,S)=max(|S|-x,0)+max(x-cnt_a(S),0); split S '
               'at m into an r-part and a b-part and minimize over m. Each of the four max-terms switches on/off '
               'monotonically in m, so binary search the switch points, and on each resulting segment minimize a '
               'fixed sum of linear prefix-count terms with one of 16 RMQ structures (sparse tables). '
               'O((|S|+W) log |S|).',
               ['edit distance closed form', 'prefix sums', 'range minimum query', 'sparse table',
                'binary search on monotone terms']),
        'D': P('Diverse T-Shirts',
               'Given the N x N "shares a color" adjacency matrix of N<=1000 T-shirt models (text color, '
               'background color), find the maximum number of models with pairwise distinct colors.',
               'The graph is the line graph of a bipartite graph (colors = nodes, models = edges); reconstruct it '
               'by greedily enumerating maximal cliques (line graphs of bipartite graphs are diamond-free, so each '
               'edge lies in one maximal clique), then the answer is a maximum bipartite matching. O(N^2) + '
               'matching.',
               ['line graph reconstruction', 'maximal cliques', 'bipartite matching',
                'maximum independent set in line graph']),
        'E': P('Evereth Expedition',
               'Complete a partially known permutation (zeros = unknown, N<=1e5) into a strictly increasing then '
               'strictly decreasing (mountain) permutation, or report impossible.',
               'In a mountain permutation value 1 is at an end, and removing it leaves a mountain; so place values '
               '1,2,3,... greedily at the left or right end. When both ends are unknown, compare the nearest known '
               'values from each side and put the small value on the side with the smaller neighbor (tie: shorter '
               'gap); exchange argument. O(N). (Alternative: max flow over blocks of zeros.)',
               ['greedy', 'two pointers', 'permutations', 'exchange argument', 'constructive']),
        'F': P('Finding Privacy',
               'K people choose toilets in a row of N so that nobody is adjacent to another and no additional '
               'person could fit; output a valid occupancy or *.',
               'This is a maximal independent set of size K in a path: possible iff ceil(N/3) <= K <= ceil(N/2). '
               'Build it from blocks "X-" (n2 = 3K-N) and "-X-" (n3 = N-2K), special case N = 2K-1 ending with '
               '"X". O(N).',
               ['constructive', 'math', 'maximal independent set', 'greedy']),
        'G': P('Grand Glory Race',
               'Runners start at every leaf of a weighted tree (N,Q<=1e5) and run toward a finish vertex T; each '
               'vertex is claimed by the first runner to reach it (ties to smaller id). Queries (S,T): how many '
               'vertices leaf S claims.',
               'For a fixed root each vertex is claimed by the nearest leaf in its subtree; compute best and '
               'second-best leaf (from different children) per vertex and reroot the tree with DFS, updating only '
               'the two vertices whose claims change when the root moves to a neighbor, maintaining claimed counts '
               'per leaf and answering queries offline at their root. O(N+Q) (online: LCA + binary lifting).',
               ['tree rerooting', 'dfs', 'offline queries', 'nearest leaf', 'tree dp']),
        'H': P('Heraclosures',
               'DAG of N<=8000 functions with M<=8000 calls; T(i) = B_i + sum of T over callees. Process E<=1e6 '
               'events: update B_i or query T(i).',
               'Sqrt decomposition over the event list: every k updates recompute all T in O(M) by topological '
               'order; a query is corrected by the pending updates using C(x,y) = number of call paths x->y '
               '(N x N matrix precomputed by DP in O(N M)). Choose k ~ sqrt(M). O(NM + E sqrt M).',
               ['sqrt decomposition on queries', 'dag path counting', 'topological order dp', 'batch rebuild']),
        'I': P('Inversion Insight',
               'Permutations of 1..N (N<=2e5) are sorted by number of inversions, then lexicographically; output '
               'the K-th (K<=4e18).',
               'f(n,x) = #permutations of n with x inversions via prefix-sum DP, capped at K+1 to avoid overflow; '
               'since f grows very fast, x stays tiny (<15 for n>100). Find x, then build the permutation '
               'lexicographically by choosing each next element with counts f(n-1, x-i). O(n x).',
               ['combinatorics', 'counting dp', 'k-th lexicographic object', 'inversions', 'overflow capping']),
        'J': P('Jigsaw of Shadows',
               'N people at positions X with heights H cast shadows of length H*cot(theta) to the east; compute '
               'the total length of road covered by shadows.',
               'Each shadow is the interval [X, X + H cot theta]; sort by X and compute the length of the union '
               'of intervals. O(N log N).',
               ['sorting', 'union of intervals', 'trigonometry', 'sweep line']),
        'K': P('Kool Strings',
               'Flip the minimum number of bits of a binary string (|S|<=1e5) so that it has no K consecutive '
               'equal characters; output the string.',
               'Lower bound sum over runs of floor(len/K). For K>2 flip every K-th bit inside each run, shifting '
               'the last flip of runs whose length is divisible by K so run endpoints are never flipped (runs stay '
               'independent); for K=2 compare the two alternating strings. O(N).',
               ['greedy', 'strings', 'runs', 'constructive', 'corner cases']),
        'L': P('Latin Squares',
               'Given T row/column swaps on an N x N matrix (N<=500), find a Latin square that is unchanged by '
               'the sequence, or report none exists.',
               'The swaps induce permutations r (rows) and c (columns); we need M[i][j] = M[r(i)][c(j)]. All '
               'cycles of r and c must have the same length S (otherwise a row repeats a value). Relabel so cycles '
               'are consecutive blocks and fill a "Latin square of Latin squares": S x S cyclic blocks, block '
               '(i,j) using symbols k*S+1..k*S+S with k = (i+j) mod (N/S). O(N^2 + T).',
               ['permutation cycles', 'constructive', 'latin squares', 'group action invariance']),
    },
    # ------------------------------------------------------------------ Regional 2025 (no editorial)
    'latam_regional2025': {
        'A': P('Apple Pie',
               'A valid sequence lists 1..N (N<=1000) so that every unordered pair appears adjacent exactly once; '
               'given a known prefix and suffix (middle hidden), decide whether the full sequence could be valid.',
               'A valid sequence is an Eulerian trail of the complete graph K_N (exists only for N odd or N=2). '
               'Check the visible parts use no repeated pair and no equal neighbours, then the unused edges (K_N '
               'minus used, length limits included) must form a trail from the last prefix value to the first '
               'suffix value: degree-parity condition plus connectivity of the remaining edges (BFS on the '
               'complement, O(N^2)).',
               ['eulerian path', 'complete graph', 'degree parity', 'graph connectivity', 'case analysis'], OWN),
        'B': P('Balanced Balloons',
               'Count sequences of N (<=1e9) contributions in [1,K] (K<=2000) such that each prefix sum is '
               'divisible by its length, mod 998244353.',
               'Write prefix sums as i*m_i (m_i = running average); then c_{i+1} = (i+1)m_{i+1} - i m_i must be in '
               '[1,K]. For i >= K the average can no longer change, so the sequence becomes constant. DP over '
               '(step, average) for the first min(N,K) steps, transitions are ranges of m (prefix sums, harmonic '
               'total work), then each state continues in exactly one way. O(K^2) or better.',
               ['dp', 'counting', 'prefix sums optimization', 'number theory observation'], OWN),
        'C': P('Clean Streets',
               'Hire cleaners (time H_i per street, accepted pay per street in [L_i,U_i]) to clean S streets in '
               'at most K hours, with equal pay per hour p_i/H_i for all hired; minimize total payment (as a '
               'fraction).',
               'With common rate r, p_i = r H_i, so cleaner i is eligible iff r in [L_i/H_i, U_i/H_i] and the cost '
               'is r * sum s_i H_i. For fixed r, minimize hours by greedily filling the S streets with the fastest '
               'eligible cleaners (capacity floor(K/H_i)). Optimal r is some L_i/H_i: sweep r over these '
               'candidates with intervals entering/leaving and a Fenwick/segment tree indexed by H (descend to '
               'take the first S units). Compare fractions exactly (128-bit). O(N log N).',
               ['sweep over rational parameter', 'fenwick tree descent', 'greedy', 'fractions',
                'event sorting'], OWN),
        'D': P('Displaying Decimals',
               'For N<=1e5 values A_i<=1e5, compute the expected number of digits to display A_i/A_j (integer part '
               '+ pre-period + first period) for random i,j, mod 998244353.',
               'For a/b with reduced denominator b\' = b/gcd(a,b): digits = digits(floor(a/b)) + max(v2(b\'), '
               'v5(b\')) + ord_{m}(10) where m is b\' without factors 2 and 5. Count integer-part digits with '
               'frequency prefix sums over value ranges [b*10^k, ...); count pairs by reduced denominator via '
               'divisor enumeration and Mobius inversion over gcd; precompute multiplicative order of 10 for all '
               'm <= 1e5 from the factorization of phi(m). Then multiply by the modular inverse of N^2.',
               ['number theory', 'multiplicative order', 'mobius inversion', 'gcd counting',
                'harmonic-sum enumeration', 'modular inverse'], OWN),
        'E': P('Emergency Rations',
               'A multiset of box sizes changes by Q<=3e5 insertions/removals; after each change output the '
               'minimum days to empty all boxes if each day you either empty one box or remove one ration from '
               'every box.',
               'Optimal: empty the k largest boxes individually and decrement the rest: answer = min over k of '
               '(k + a_{k+1}) with a sorted decreasingly (a_{n+1} = 0). Offline coordinate-compress all values '
               '(one slot per occurrence) into a segment tree ordered decreasingly; each node stores count and '
               'min(rank-before + value), merged as min(left, right + left.count). O(Q log Q).',
               ['segment tree', 'offline coordinate compression', 'greedy', 'dynamic multiset'], OWN),
        'F': P('Fuzzy Factorization',
               'Given X up to 10^1000, output the prime factorization of some Y with relative error |X-Y|/X <= 1e-9 '
               'and all primes <= 1e18.',
               'Only ~10 significant digits matter: keep the first 12-15 digits m of X and drop the rest, '
               'Y = m * 10^e = m * 2^e * 5^e (relative error < 1e-11); factor m by trial division up to '
               'sqrt(m) and add e to the exponents of 2 and 5 (CF gym thread). Alternative: Y = 2^e * p with p a '
               'prime near X/2^e around 1e17-1e18 found with Miller-Rabin (error ~ prime gap / p).',
               ['big number truncation', 'approximation', 'trial division factorization', 'miller-rabin primality',
                'constructive'], COMM),
        'G': P('Gridoland Power Gauge',
               'N x M grid (<=300 x 300) with vertex capacities C+tR changing linearly in time and some cables '
               'between adjacent blocks; maximize over integer t in [0,K] the max flow from (1,1) to (N,M).',
               'Max flow = min vertex cut = min of linear functions of t, hence concave in t: ternary search over '
               'integer t. Each evaluation computes the min vertex cut of the planar grid graph as a shortest path '
               'in the dual (Dijkstra over blocks and missing-cable gaps from one boundary side to the other), '
               'O(NM log(NM)) per step; use 128-bit sums.',
               ['max flow min cut', 'planar duality', 'dijkstra', 'ternary search on concave function',
                'parametric min cut'], OWN),
        'H': P('Harder Horizons',
               'Split a list of N task difficulties into the maximum number of consecutive groups whose maxima '
               'are strictly increasing.',
               'Each group\'s maximum must exceed all earlier tasks, i.e. be a strict prefix maximum, and cutting '
               'right before every new prefix maximum is valid; answer = number of strict left-to-right maxima. '
               'O(N).',
               ['greedy', 'prefix maximum', 'ad hoc'], OWN),
        'I': P('Infiltration Route',
               'DAG on floors 1..2N (codes S<T, N<=500, M<=1000); find a path 1 -> 2N that never uses both floors '
               'i and i+N.',
               'Route = increasing path in the lower half, exactly one crossing code (a -> b+N), increasing path '
               'in the upper half. Identifying floor i+N with i, we need two vertex-disjoint monotone paths (1->a '
               'in the lower-code DAG, b->N in the upper-code DAG) linked by a crossing code; if b>a they are '
               'automatically disjoint. Otherwise, for each crossing code, BFS over pairs (x, y) of path fronts '
               '(lower path at x, upper path at y, both moving forward) always advancing the lagging front and '
               'never landing on the other front: this rule guarantees the two paths never share a floor without '
               'storing visited sets. O(N^2 + N M) states/transitions per crossing code, with back-pointers for '
               'the route (CF gym thread sketch).',
               ['dag', 'two disjoint paths', 'pair-state bfs', 'lagging pointer rule', 'reconstruction'], COMM),
        'J': P('Judgmental Crowd',
               'Given a string (|S|<=1000), add 1 per occurrence of "ha", 3 per "bravo" and subtract 1 per '
               '"boooo"; output the score.',
               'Count (possibly overlapping) occurrences of each pattern by scanning every position. O(|S|).',
               ['strings', 'implementation', 'substring counting'], OWN),
        'K': P('Kings Conquest',
               'N<=1e5 chess kings on a grid; with K moves (king moves, no collisions) maximize the area of the '
               'bounding box.',
               'Moving one extreme king diagonally outward grows both width and height by 1 per move once it '
               'leaves the box, which dominates splitting moves. Try every king and each of the 8 directions with '
               'all K moves, computing the box of the remaining kings in O(1) from the top-2 extremes on each '
               'side; handle N=1 (area stays 1). O(N).',
               ['greedy', 'case analysis', 'geometry', 'top-2 extremes', 'brute force over candidates'], OWN),
        'L': P('Lonely Creatures',
               'N<=1e5 lines y=Mx+C; count pairs whose intersection lies strictly inside the parabola region '
               'y > Ax^2+B.',
               'A line meets the region in an open chord between the roots x1<x2 of Ax^2 - Mx + (B-C) = 0 (lines '
               'with non-positive discriminant never enter). Two chords of a convex region intersect inside iff '
               'their endpoints interleave, so count crossing interval pairs (l_i<l_j<r_i<r_j) by sorting and a '
               'Fenwick tree. Endpoints are (M +- sqrt(D))/(2A): compare them exactly with integer arithmetic. '
               'O(N log N).',
               ['computational geometry', 'chord intersection interleaving', 'fenwick tree counting',
                'exact arithmetic with square roots', 'sorting'], OWN),
    },
}
