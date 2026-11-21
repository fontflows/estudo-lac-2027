"""Generate a MOCK data/dataset.js in the exact final shape (see SPEC.md "Final dataset").

Only for developing the site before the real data exists. It is overwritten by
    python -I pipeline/build_dataset.py
Usage:
    python -I pipeline/mock_dataset.py                      # writes data/dataset.js
    python -I pipeline/mock_dataset.py --curriculum --out data/dataset.mock.js
        --curriculum  also emit a mock DATASET.curriculum (SPEC "Curriculum (v2)")
        --out PATH    write somewhere else (data/dataset.mock.js is gitignored), so the real
                      data/dataset.js is not overwritten
"""
import argparse
import datetime
import json
import os
import random


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "dataset.js")

FAMILIES = [
    {"id": "lac", "name": "ICPC Latin America Championship", "short": "LAC", "weight": 1.0, "group": "latam"},
    {"id": "latam_regional", "name": "ICPC Latin American Regional", "short": "Regional LATAM", "weight": 0.6, "group": "latam"},
    {"id": "nac", "name": "ICPC North America Championship", "short": "NAC", "weight": 0.8, "group": "world"},
    {"id": "nerc", "name": "ICPC Northern Eurasia Finals", "short": "NERC", "weight": 0.8, "group": "world"},
    {"id": "apac", "name": "ICPC Asia Pacific Championship", "short": "APAC", "weight": 0.8, "group": "world"},
]

AREAS = [
    ("graphs", "Grafos"), ("dp", "Programação dinâmica"), ("math", "Matemática e teoria dos números"),
    ("ds", "Estruturas de dados"), ("strings", "Strings"), ("geometry", "Geometria"),
    ("search", "Busca e técnicas"), ("greedy", "Guloso e ad hoc"), ("combinatorics", "Combinatória e probabilidade"),
    ("other", "Outros"),
]

CPA = "https://cp-algorithms.com/"
# (id, area, name, popularity, hardness 0..1, ref path)
TOPICS = [
    ("shortest-paths-states", "graphs", "Caminho mínimo em grafo de estados", 6, .45, "graph/dijkstra.html"),
    ("dijkstra-basic", "graphs", "Dijkstra", 4, .3, "graph/dijkstra.html"),
    ("bfs-grid", "graphs", "BFS em grid", 4, .15, "graph/breadth-first-search.html"),
    ("dsu", "graphs", "Union-find (DSU)", 5, .35, "data_structures/disjoint_set_union.html"),
    ("mst", "graphs", "Árvore geradora mínima", 2, .35, "graph/mst_kruskal.html"),
    ("scc-2sat", "graphs", "Componentes fortemente conexas e 2-SAT", 2, .7, "graph/2SAT.html"),
    ("max-flow", "graphs", "Fluxo máximo e corte mínimo", 3, .8, "graph/dinic.html"),
    ("bipartite-matching", "graphs", "Emparelhamento bipartido", 2, .7, "graph/kuhn_maximum_bipartite_matching.html"),
    ("lca-binary-lifting", "graphs", "LCA com binary lifting", 3, .55, "graph/lca_binary_lifting.html"),
    ("tree-dp", "dp", "DP em árvore", 5, .55, "graph/depth-first-search.html"),
    ("dp-bitmask", "dp", "DP com bitmask", 4, .65, "dynamic_programming/profile-dynamics.html"),
    ("dp-intervals", "dp", "DP em intervalos", 3, .55, "dynamic_programming/intro-to-dp.html"),
    ("dp-knapsack", "dp", "Mochila e variações", 4, .35, "dynamic_programming/knapsack.html"),
    ("dp-digits", "dp", "DP de dígitos", 2, .6, "dynamic_programming/intro-to-dp.html"),
    ("dp-optimizations", "dp", "Otimizações de DP (CHT, D&C)", 2, .9, "geometry/convex_hull_trick.html"),
    ("dp-probability", "dp", "DP com probabilidade e esperança", 3, .65, "dynamic_programming/intro-to-dp.html"),
    ("modular-arith", "math", "Aritmética modular e inverso", 4, .4, "algebra/module-inverse.html"),
    ("sieve-factorization", "math", "Crivo e fatoração", 3, .35, "algebra/sieve-of-eratosthenes.html"),
    ("gcd-diophantine", "math", "MDC e equações diofantinas", 2, .45, "algebra/extended-euclid-algorithm.html"),
    ("matrix-expo", "math", "Exponenciação de matrizes", 2, .6, "algebra/binary-exp.html"),
    ("fft", "math", "FFT e convolução", 1, .9, "algebra/fft.html"),
    ("game-theory", "math", "Teoria dos jogos (Grundy)", 2, .6, "game_theory/sprague-grundy-nim.html"),
    ("segtree-lazy", "ds", "Segment tree com lazy", 5, .65, "data_structures/segment_tree.html"),
    ("segtree-basic", "ds", "Segment tree e BIT", 5, .45, "data_structures/fenwick.html"),
    ("sparse-table", "ds", "Sparse table e RMQ", 2, .4, "data_structures/sparse-table.html"),
    ("sweep-line", "ds", "Sweep line com estrutura", 3, .7, "geometry/intersecting_segments.html"),
    ("offline-queries", "ds", "Consultas offline (Mo, ordenação)", 2, .75, "data_structures/sqrt_decomposition.html"),
    ("sqrt-decomp", "ds", "Decomposição em raiz", 1, .7, "data_structures/sqrt_decomposition.html"),
    ("hld-centroid", "ds", "HLD e decomposição em centroides", 2, .85, "graph/hld.html"),
    ("hashing", "strings", "Hashing de strings", 3, .5, "string/string-hashing.html"),
    ("kmp-z", "strings", "KMP e função Z", 3, .5, "string/prefix-function.html"),
    ("suffix-array", "strings", "Suffix array e LCP", 2, .85, "string/suffix-array.html"),
    ("aho-corasick", "strings", "Aho-Corasick", 1, .8, "string/aho_corasick.html"),
    ("palindromes", "strings", "Palíndromos (Manacher)", 1, .6, "string/manacher.html"),
    ("convex-hull", "geometry", "Fecho convexo", 3, .6, "geometry/convex-hull.html"),
    ("geo-primitives", "geometry", "Primitivas geométricas (produto vetorial)", 4, .5, "geometry/basic-geometry.html"),
    ("polygon-area", "geometry", "Área e pontos em polígono", 2, .45, "geometry/area-of-simple-polygon.html"),
    ("circles", "geometry", "Círculos e interseções", 1, .75, "geometry/circle-circle-intersection.html"),
    ("binary-search-answer", "search", "Busca binária na resposta", 7, .45, "num_methods/binary_search.html"),
    ("two-pointers", "search", "Dois ponteiros", 4, .3, "num_methods/binary_search.html"),
    ("ternary-search", "search", "Busca ternária", 1, .5, "num_methods/ternary_search.html"),
    ("meet-in-middle", "search", "Meet in the middle", 1, .65, "num_methods/binary_search.html"),
    ("backtracking", "search", "Busca exaustiva com poda", 2, .5, "num_methods/binary_search.html"),
    ("greedy-exchange", "greedy", "Guloso com argumento de troca", 6, .4, "schedules/schedule_one_machine.html"),
    ("greedy-sorting", "greedy", "Ordenação e guloso por eventos", 5, .25, "schedules/schedule_with_completion_duration.html"),
    ("adhoc-observation", "greedy", "Ad hoc por observação", 7, .3, "index.html"),
    ("prefix-sums", "greedy", "Somas de prefixo e diferenças", 4, .15, "data_structures/fenwick.html"),
    ("counting-binomials", "combinatorics", "Contagem com binomiais", 4, .5, "combinatorics/binomial-coefficients.html"),
    ("inclusion-exclusion", "combinatorics", "Inclusão-exclusão", 2, .65, "combinatorics/inclusion-exclusion.html"),
    ("expected-value", "combinatorics", "Valor esperado e linearidade", 2, .6, "combinatorics/inclusion-exclusion.html"),
    ("constructive", "other", "Construtivo", 5, .5, "index.html"),
    ("interactive", "other", "Interativo", 2, .55, "index.html"),
    ("simulation", "other", "Simulação e implementação", 5, .2, "index.html"),
]

CONTESTS = [
    ("lac", 2024, "03-16", 60), ("lac", 2025, "03-15", 62), ("lac", 2026, "03-14", 60),
    ("latam_regional", 2019, "11-09", 412), ("latam_regional", 2020, "11-21", 380),
    ("latam_regional", 2021, "11-13", 401), ("latam_regional", 2022, "11-12", 455),
    ("latam_regional", 2023, "11-11", 471), ("latam_regional", 2024, "11-09", 489),
    ("latam_regional", 2025, "11-08", 503),
    ("nac", 2021, "08-05", 48), ("nac", 2022, "05-28", 52), ("nac", 2023, "05-27", 50), ("nac", 2024, "05-25", 50),
    ("nerc", 2019, "12-01", 300), ("nerc", 2021, "04-21", 260), ("nerc", 2022, "12-07", 290), ("nerc", 2024, "12-04", 310),
    ("apac", 2024, "03-03", 64), ("apac", 2025, "03-01", 66),
]

W1 = ["Lazy", "Broken", "Hidden", "Twin", "Circular", "Magic", "Secret", "Balanced", "Fast", "Long",
      "Lost", "Silent", "Golden", "Crazy", "Royal", "Final", "Mirror", "Prime", "Little", "Endless"]
W2 = ["Robots", "Bridges", "Tokens", "Gardens", "Towers", "Trains", "Queries", "Fences", "Coins", "Cards",
      "Lamps", "Rivers", "Islands", "Palindromes", "Permutations", "Paths", "Shelves", "Dice", "Buses", "Grid"]
COMPLEX = ["O(n log n)", "O(n)", "O(n log^2 n)", "O(n sqrt n)", "O(n · 2^k)", "O(n^2)", "O((n + m) log n)"]


# ---- Mock curriculum (SPEC "Curriculum (v2)"), only with --curriculum ------------------------
INSIGHT_GROUPS = [
    ("time-order", "Tempo e ordem de processamento"),
    ("fix-sweep", "Fixar uma escolha e varrer"),
    ("counting", "Contagem por troca de ordem"),
    ("decide", "Decidir em vez de otimizar"),
    ("invariants", "Invariantes"),
    ("implicit-graphs", "Grafos implícitos"),
    ("answer-shape", "Forma da solução ótima"),
    ("coordinates", "Coordenadas e eventos"),
]

# (id, group, generality, popularity, only_families, name, statement, signal, contexts, known, hows)
INSIGHTS = [
    ("reverse-removals", "time-order", 3, 5, None,
     "Inverter o tempo: remoções viram inserções",
     "Se o processo só remove elementos e as consultas são sobre o estado atual, processe de trás para frente: cada remoção vira uma inserção, que estruturas como DSU suportam bem.",
     "operações de apagar ou cortar intercaladas com consultas de conectividade ou de máximo",
     ["DSU offline com remoção de arestas", "manter o máximo de um conjunto que só perde elementos", "ilhas que afundam com o nível da água"],
     ["CSES — Road Construction (variação)"],
     ["As arestas cortadas são adicionadas na ordem inversa e cada consulta é respondida no DSU.",
      "Os pontos removidos entram de volta do último para o primeiro, e o componente máximo só cresce."]),
    ("offline-sorted-queries", "time-order", 3, 4, None,
     "Ordenar consultas junto com os eventos",
     "Quando as consultas podem ser respondidas fora de ordem, ordene consultas e atualizações pelo mesmo parâmetro e faça uma única varredura com uma estrutura que só cresce.",
     "muitas consultas com um limiar (peso ≤ x, tempo ≤ t) sobre dados fixos",
     ["consultas de conectividade com arestas de peso ≤ x", "contagem de pontos dominados", "k-ésimo menor com limiar"],
     [],
     ["As consultas são ordenadas pelo limite de peso e as arestas entram no DSU conforme o limite sobe.",
      "Ordenando consultas por tempo, cada evento é inserido uma vez numa BIT."]),
    ("activate-by-value", "time-order", 2, 3, None,
     "Ativar elementos em ordem de valor",
     "Para perguntas sobre o mínimo ou máximo de regiões conectadas, ative os elementos do maior para o menor (ou o contrário) e una vizinhos já ativos: cada componente nasce com seu extremo conhecido.",
     "soma ou contagem sobre todos os subarrays/caminhos do mínimo (ou máximo)",
     ["maior retângulo em histograma", "soma do mínimo de todos os caminhos de uma árvore"],
     ["AtCoder ABC 214 D — Sum of Maximum Weights"],
     ["Os vértices são ativados em ordem crescente de peso; ao unir componentes conta-se quantos caminhos passam a ter aquele vértice como máximo."]),
    ("fix-max-sweep", "fix-sweep", 3, 5, None,
     "Fixar o máximo e varrer",
     "Quando o custo depende do máximo (ou mínimo) de um conjunto, fixe qual elemento é o máximo; o resto vira uma restrição simples (todos ≤ ele) que se conta ou otimiza em ordem.",
     "custo da forma max(...) + soma(...), ou escolher um subconjunto limitado pelo seu pior elemento",
     ["escolher k itens minimizando max(a) · soma(b)", "contar subconjuntos cujo máximo é x", "intervalos com o maior elemento na ponta"],
     ["Codeforces 1101F — Trucks and Cities"],
     ["Ordenando por a, o elemento i é o máximo e os k−1 menores b entre os anteriores vêm de um heap.",
      "Fixado o maior valor, os candidatos restantes formam um prefixo da ordenação."]),
    ("fix-one-endpoint", "fix-sweep", 2, 4, None,
     "Fixar uma ponta do intervalo",
     "Para contar ou otimizar sobre todos os intervalos [l, r], fixe r e mantenha a informação de todos os l possíveis numa estrutura que se atualiza quando r avança.",
     "“para todo subarray”, “quantos pares (l, r)”, com n até 2·10^5",
     ["número de subarrays com soma no intervalo", "subarrays com no máximo k valores distintos", "soma de max − min de todos os subarrays"],
     [],
     ["Com r fixo, as contribuições de cada l ficam numa segment tree e são atualizadas por pilha monotônica.",
      "Para cada r, o menor l válido só anda para a direita."]),
    ("enumerate-small", "fix-sweep", 3, 4, None,
     "Enumerar a dimensão pequena",
     "Se algum parâmetro é pequeno (k ≤ 20, valores ≤ 100, um lado da grade ≤ 10), enumere-o explicitamente e resolva o resto com ele fixo.",
     "um limite destoa dos outros no enunciado (n ≤ 2·10^5, mas k ≤ 15)",
     ["grade n × m com min(n, m) ≤ 10", "poucos tipos de item", "alfabeto pequeno em strings"],
     [],
     ["Como há no máximo 12 cores, testa-se cada subconjunto de cores e o resto vira BFS.",
      "O lado curto da grade (≤ 8) vira máscara de bits; o lado longo é percorrido em DP."]),
    ("contribution", "counting", 3, 6, None,
     "Contribuição por elemento",
     "Em vez de somar sobre todas as estruturas (subarrays, pares, caminhos, subconjuntos), troque a ordem da soma: conte em quantas estruturas cada elemento aparece e com quanto contribui.",
     "“soma, sobre todos os ...,” de algo que se decompõe em elementos",
     ["soma das distâncias de todos os pares numa árvore", "soma do mínimo de todos os subarrays", "valor esperado como soma de indicadores"],
     ["CSES — Tree Distances II"],
     ["Cada aresta contribui com tamanho(sub) · (n − tamanho(sub)) caminhos.",
      "Cada posição é o mínimo de (i − L) · (R − i) subarrays, achados com pilha monotônica."]),
    ("complement", "counting", 2, 4, None,
     "Contar o complemento",
     "Quando a condição “bom” é difícil de contar diretamente mas “ruim” tem estrutura simples, conte o total e subtraia os ruins.",
     "“pelo menos um”, “não todos”, “existe algum par que…”",
     ["subconjuntos com pelo menos um elemento par", "strings que contêm um padrão", "caminhos que passam por algum obstáculo"],
     [],
     ["Conta-se o total de permutações e subtraem-se as que mantêm todos os elementos fora do lugar."]),
    ("sort-pairs-linear", "counting", 2, 3, None,
     "Pares ficam lineares depois de ordenar",
     "Somas sobre pares de |a_i − a_j| ou max(a_i, a_j) ficam lineares depois de ordenar: cada elemento entra com um coeficiente que só depende da sua posição.",
     "soma sobre todos os pares de uma diferença absoluta ou de um máximo",
     ["soma das distâncias Manhattan entre todos os pontos", "soma do maior de cada par"],
     [],
     ["Ordenando as coordenadas, o i-ésimo ponto entra com sinal + i vezes e − (n − 1 − i) vezes."]),
    ("decide-not-optimize", "decide", 3, 6, None,
     "Decidir é mais fácil que otimizar",
     "Se verificar “dá para fazer com custo ≤ X?” é simples e a resposta é monótona em X, transforme a otimização numa sequência de perguntas de decisão.",
     "minimizar o máximo ou maximizar o mínimo",
     ["dividir um array em k partes minimizando a maior soma", "tempo mínimo para todas as máquinas terminarem", "maior distância mínima entre pontos escolhidos"],
     ["CSES — Factory Machines"],
     ["Com X fixo, um guloso da esquerda para a direita diz se bastam k grupos.",
      "Fixado o tempo T, a pergunta vira um teste de matching completo."]),
    ("answer-small-set", "decide", 2, 3, None,
     "A resposta só assume poucos valores",
     "Se dá para provar que a resposta é sempre pequena (no máximo 2 ou 3, ou O(log n)) ou vem de poucos candidatos, teste cada candidato do menor para o maior.",
     "perguntas de “número mínimo de operações” em que exemplos sempre dão 0, 1 ou 2",
     ["mínimo de operações para ordenar com uma operação forte", "número de cores necessárias em casos especiais"],
     [],
     ["Prova-se que 2 operações sempre bastam; resta checar 0 e 1."]),
    ("parity-only", "invariants", 2, 3, None,
     "O custo só depende da paridade",
     "Quando cada operação altera uma quantidade em ±1 ou troca dois elementos, a paridade (de inversões, da soma, da distância) costuma ser o único obstáculo.",
     "trocas adjacentes, rotações ou movimentos de uma casa; pergunta “é possível?”",
     ["15-puzzle e variações", "permutação alcançável por 3-ciclos", "tabuleiro com movimentos de cavalo"],
     [],
     ["Cada operação inverte a paridade de inversões, então só permutações pares são alcançáveis."]),
    ("find-invariant", "invariants", 3, 4, None,
     "Achar o que a operação preserva",
     "Para decidir se um estado alcança outro, procure uma quantidade que nenhuma operação muda (soma mod k, xor, multiconjunto de algo); muitas vezes tudo o que respeita o invariante é alcançável.",
     "“é possível transformar A em B?” com uma operação local repetida",
     ["somar 1 em dois vizinhos", "trocar pedras entre pilhas", "operações de xor entre adjacentes"],
     [],
     ["A soma alternada a_1 − a_2 + a_3 − … nunca muda; com ela igual, a construção é direta.",
      "O xor de todos os elementos é preservado e determina a resposta."]),
    ("state-graph", "implicit-graphs", 3, 5, None,
     "Estado = posição + o que importa do passado",
     "Quando a regra de movimento depende de algo além da posição (última direção, combustível, paridade, chaves coletadas), coloque essa informação no vértice e rode o algoritmo de grafo usual.",
     "regras de movimento que dependem do passo anterior ou de um recurso limitado",
     ["menor caminho com no máximo k arestas grátis", "labirinto com chaves e portas", "carro que não pode virar duas vezes seguidas"],
     ["CSES — Flight Discount"],
     ["O vértice vira (cidade, cupom usado) e roda-se Dijkstra no grafo dobrado.",
      "O estado guarda a direção da última jogada; são 4n vértices."]),
    ("equalities-components", "implicit-graphs", 2, 3, None,
     "Restrições de igualdade viram componentes",
     "Restrições do tipo “x_i = x_j” (ou “x_i = x_j + c”) formam um grafo; cada componente tem um único grau de liberdade e as contradições aparecem como ciclos inconsistentes.",
     "lista de pares que devem ser iguais, opostos ou diferir de um valor",
     ["palíndromos com posições ligadas", "atribuição de potenciais com diferenças dadas", "2-coloração com restrições de igualdade/diferença"],
     [],
     ["As posições espelhadas são unidas e cada componente escolhe um único caractere."]),
    ("conflicts-coloring", "implicit-graphs", 2, 2, {"nerc", "apac"},
     "Conflitos dois a dois viram 2-coloração",
     "Se os itens precisam ir para dois lados e há pares que não podem ficar juntos, o problema é testar bipartição do grafo de conflitos; cada componente tem duas escolhas.",
     "dividir em dois grupos com pares incompatíveis",
     ["dividir alunos em duas salas", "orientar segmentos sem cruzamento"],
     [],
     ["Os pares de intervalos que se cruzam viram arestas e verifica-se se o grafo é bipartido."]),
    ("bound-then-build", "answer-shape", 3, 5, None,
     "Provar o limite e construir quem o atinge",
     "Encontre um limite simples para a resposta (grau máximo, contagem por cor, metade do total) e construa uma solução que o atinge; o limite costuma ser exatamente a resposta.",
     "pedido de construir uma solução ótima, com saída “−1 se impossível”",
     ["coloração de arestas com Δ cores em bipartidos", "emparelhar itens de cores diferentes", "torneios com resultados prescritos"],
     [],
     ["O número de rodadas não pode ser menor que o maior grau; alternar os vértices desse grau já atinge o limite.",
      "Metade do total arredondada para cima é limite e é atingida intercalando os grupos."]),
    ("only-extremes", "answer-shape", 2, 4, None,
     "Só os extremos importam",
     "Em muitas configurações ótimas só o primeiro, o último, o mínimo ou o máximo influenciam o custo; os outros elementos podem ser descartados ou fixados.",
     "operações em intervalos ou subsequências em que o meio parece irrelevante",
     ["custo de um caminho que só depende do maior salto", "subsequência ótima que só usa os extremos"],
     [],
     ["Basta comparar o menor e o maior de cada bloco; os elementos internos nunca mudam a resposta."]),
    ("decide-backwards", "answer-shape", 2, 3, None,
     "Decidir de trás para frente",
     "Quando a escolha de agora depende do que vem depois, tome as decisões começando pelo fim: a informação do futuro já está disponível e o guloso fica correto.",
     "prazos, últimos usos, ou jogos com número fixo de rodadas",
     ["agendamento com prazos", "cache com política ótima (Bélády)", "jogos resolvidos da última jogada para a primeira"],
     [],
     ["Percorrendo os dias do último para o primeiro, sempre se atende a tarefa disponível de maior valor."]),
    ("separate-axes", "coordinates", 2, 3, None,
     "Separar coordenadas",
     "Se o custo é a soma de termos em x e em y (distância Manhattan, movimentos independentes), resolva cada eixo separadamente e combine.",
     "distância Manhattan, ou movimentos em x e y que não interagem",
     ["mediana para minimizar soma de distâncias", "torres que atacam linha e coluna", "robôs que movem em eixos independentes"],
     [],
     ["As coordenadas x e y são tratadas como dois problemas 1D e a resposta é a soma."]),
    ("only-event-points", "coordinates", 2, 3, {"nerc", "nac", "apac"},
     "Só os pontos de evento importam",
     "Quando uma função muda de comportamento só em finitos pontos (extremos de intervalos, cruzamentos), basta testar esses pontos ou varrer entre eles.",
     "coordenadas até 10^9 mas poucos objetos",
     ["ponto coberto pelo maior número de intervalos", "melhor posição de uma reta entre pontos"],
     [],
     ["Os candidatos ao ótimo são as extremidades dos intervalos; varre-se só por elas."]),
]

# (id, base technique, generality, popularity, name, property, why, signal, contexts, hows)
DEEPENINGS = [
    ("segtree-descent", "Segment tree", 3, 5, "Descida na segment tree",
     "Achar o primeiro índice cuja soma de prefixo passa de x (ou o primeiro elemento > x) em O(log n), descendo pela árvore em vez de fazer busca binária por fora.",
     "Cada nó já guarda o agregado do seu intervalo, então decidir entre esquerda e direita só olha o filho esquerdo.",
     "consultas “primeira posição em que…” com atualizações",
     ["k-ésimo elemento ativo", "primeiro assento livre a partir de i", "primeiro prefixo com soma ≥ x"],
     ["A posição do k-ésimo livre sai por descida na árvore de contagens."]),
    ("segtree-composite-node", "Segment tree", 2, 4, "Nó com prefixo, sufixo e melhor",
     "Guardar em cada nó o melhor prefixo, o melhor sufixo, o total e o melhor do intervalo permite combinar subarrays ótimos em O(1) por junção.",
     "O melhor subarray de um intervalo ou está num dos filhos ou atravessa o meio, e aí é sufixo da esquerda mais prefixo da direita.",
     "subarray de soma máxima (ou maior sequência de 1s) com atualizações",
     ["maior sequência de 1s com flips", "soma máxima de subarray com updates pontuais"],
     ["Cada nó guarda a maior sequência de assentos livres no prefixo, no sufixo e no meio."]),
    ("matching-in-every-max", "Matching bipartido (Kuhn/Hopcroft-Karp)", 2, 2, "Vértices que estão em todo matching máximo",
     "Um vértice está em todo matching máximo se e só se não é alcançável por caminho alternante a partir de um vértice livre do mesmo lado.",
     "Se fosse alcançável, trocar as arestas do caminho alternante daria outro matching máximo sem ele.",
     "“quais itens são obrigatórios em qualquer solução ótima de pareamento”",
     ["arestas que estão em algum matching máximo", "jogos em grafos bipartidos (quem começa ganha)"],
     ["Depois do matching, uma BFS alternante a partir dos livres marca os vértices dispensáveis."]),
    ("konig", "Matching bipartido (Kuhn/Hopcroft-Karp)", 2, 3, "Teorema de König",
     "Em grafo bipartido, a menor cobertura por vértices tem o mesmo tamanho do matching máximo, e o maior conjunto independente é n menos isso.",
     "A dualidade de fluxo/corte aplicada à rede do matching transforma o corte mínimo numa cobertura.",
     "escolher o menor número de linhas/colunas que cobre todas as marcas",
     ["cobrir células de uma grade com linhas e colunas", "maior conjunto de itens sem conflito em bipartido"],
     ["As células marcadas são arestas linha–coluna; a resposta é o tamanho do matching."]),
    ("dsu-parity", "DSU", 3, 4, "DSU com paridade até a raiz",
     "Guardar em cada nó a paridade (ou diferença) até o pai permite testar bipartição e restrições “x − y = c” online, com caminho comprimido.",
     "A paridade até a raiz se compõe por xor ao comprimir o caminho, então continua correta após cada find.",
     "restrições de igual/diferente chegando uma a uma, com pergunta “ainda é consistente?”",
     ["bipartição online", "pesos relativos entre objetos", "quebra-cabeças de paridade"],
     ["Cada aresta impõe paridade 1; a primeira contradição dá a resposta."]),
    ("dijkstra-virtual-source", "Dijkstra", 2, 4, "Fonte virtual para múltiplas origens",
     "Um vértice extra ligado a todas as origens com custo inicial transforma “distância à origem mais próxima” num único Dijkstra.",
     "Qualquer caminho a partir da fonte virtual começa por exatamente uma origem real.",
     "várias saídas, hospitais ou fontes de fogo",
     ["fogo que se espalha a partir de vários pontos", "distância ao posto mais próximo"],
     ["Todos os portões entram na fila com distância 0 ao mesmo tempo."]),
    ("parallel-binary-search", "Busca binária na resposta", 2, 2, "Busca binária paralela",
     "Quando muitas consultas precisam de uma busca binária sobre a mesma sequência de eventos, faça todas juntas: a cada rodada aplique os eventos uma vez e decida cada consulta.",
     "Cada rodada custa uma passagem pelos eventos; são O(log T) rodadas no total.",
     "muitas perguntas “em que momento X passa a valer?”",
     ["quando cada par de vértices fica conectado", "quando cada país atinge sua meta"],
     ["As consultas de cada país são decididas juntas, aplicando as chuvas em ordem a cada rodada."]),
    ("prefix-mod-pigeonhole", "Soma de prefixos", 3, 3, "Prefixos iguais módulo k",
     "Um subarray tem soma divisível por k exatamente quando dois prefixos têm o mesmo resto; com n ≥ k, pelo princípio da casa dos pombos sempre existe um.",
     "soma(l..r) = P[r] − P[l−1], que é 0 mod k sse os restos coincidem.",
     "subarray ou subconjunto com soma múltipla de k",
     ["contar subarrays com soma divisível por k", "construir subconjunto com soma múltipla de n"],
     ["Guarda-se a primeira posição de cada resto; o par mais distante dá o maior subarray."]),
    ("tree-knapsack-merge", "DP em árvore", 2, 3, "Mochila em árvore é O(n²) no total",
     "Combinar as tabelas dos filhos limitando cada dimensão pelo tamanho da subárvore dá O(n²) no total, e não O(n³).",
     "Cada par de vértices é “combinado” uma única vez, no seu LCA.",
     "DP em árvore com dimensão “quantos vértices escolhidos na subárvore”",
     ["escolher k vértices conexos de peso máximo", "cortar a árvore em componentes de tamanho dado"],
     ["A tabela de cada subárvore tem tamanho igual à subárvore e as junções somam O(n²)."]),
    ("grundy-pattern", "Sprague-Grundy", 2, 2, "Calcular Grundy pequeno e achar o padrão",
     "Para jogos com n até 10^18, calcule os valores de Grundy por força bruta até algumas centenas e procure periodicidade ou fórmula fechada.",
     "Jogos de subtração com conjunto finito de movimentos têm sequência de Grundy eventualmente periódica.",
     "jogo imparcial com parâmetro enorme e regras simples",
     ["jogos de subtração", "dividir pilhas em partes desiguais"],
     ["Os valores de Grundy têm período 7 a partir de 30; a resposta sai por tabela."]),
    ("cht-monotone", "Convex hull trick / Li Chao", 2, 2, "CHT com deque quando tudo é monotônico",
     "Se as inclinações chegam ordenadas e as consultas também, o envelope inferior se mantém com um deque em O(1) amortizado, sem Li Chao.",
     "Retas inúteis nunca voltam a ser ótimas quando consultas só avançam.",
     "dp[i] = min_j (dp[j] + b_j · a_i) com a e b ordenados",
     ["particionar array com custo quadrático", "cortar árvores com custo por altura"],
     ["Com os a_i crescentes, cada transição da DP é uma consulta no deque."]),
    ("mst-cycle-property", "MST (Kruskal/Prim)", 2, 3, "Propriedade do ciclo",
     "A aresta estritamente mais pesada de qualquer ciclo não está em nenhuma MST; uma aresta está em alguma MST sse não é a mais pesada de um ciclo que fecha.",
     "Trocar essa aresta pela mais leve do ciclo nunca piora a árvore.",
     "perguntas “esta aresta pode/deve estar na árvore mínima?”",
     ["classificar arestas em todas/alguma/nenhuma MST", "MST após alterar o peso de uma aresta"],
     ["Para cada aresta fora da árvore, compara-se com o máximo do caminho na MST."]),
    ("flow-lower-bounds", "Fluxo máximo (Dinic)", 1, 1, "Fluxo com limites inferiores",
     "Arestas com fluxo mínimo obrigatório se tratam subtraindo o mínimo, criando demandas nos vértices e resolvendo uma circulação com fonte e sumidouro novos.",
     "Depois da subtração, o problema é viável sse o fluxo máximo satura todas as arestas das demandas.",
     "cada aresta tem mínimo e máximo de uso",
     ["escalas de plantão com mínimo por dia", "rotas que precisam passar por certas ruas"],
     ["Cada turno tem mínimo de 2 pessoas; vira circulação com demandas."]),
]

TECH_POOL = [
    ("BFS", 6, None), ("BFS 0-1", 2, None), ("DFS", 5, None), ("Dijkstra", 6, None), ("Floyd-Warshall", 2, None),
    ("Ordenação topológica", 3, None), ("SCC (Tarjan/Kosaraju)", 2, None), ("2-SAT", 2, None), ("MST (Kruskal/Prim)", 3, None),
    ("DSU", 6, None), ("LCA (binary lifting)", 3, None), ("HLD", 1, None), ("Centroid decomposition", 1, {"nerc", "apac"}),
    ("Small-to-large", 2, None), ("Matching bipartido (Kuhn/Hopcroft-Karp)", 2, None), ("Blossom", 1, {"nerc"}),
    ("Fluxo máximo (Dinic)", 2, None), ("Fluxo de custo mínimo", 1, None), ("Segment tree", 6, None),
    ("Segment tree com lazy", 4, None), ("BIT", 4, None), ("Sparse table", 2, None), ("Mo's algorithm", 1, None),
    ("Soma de prefixos", 6, None), ("Pilha monotônica", 3, None), ("Dois ponteiros", 4, None),
    ("Busca binária na resposta", 6, None), ("Busca ternária", 1, None), ("Meet in the middle", 1, None),
    ("DP com bitmask", 3, None), ("DP em dígitos", 1, None), ("DP em árvore", 4, None), ("Rerooting", 2, None),
    ("DP de intervalos", 2, None), ("Mochila", 3, None), ("LIS", 2, None), ("Convex hull trick / Li Chao", 1, None),
    ("Matrix exponentiation", 1, None), ("KMP", 2, None), ("Função Z", 1, None), ("Hashing de strings", 3, None),
    ("Suffix array + LCP", 1, None), ("Aho-Corasick", 1, None), ("Trie", 2, None), ("Crivo de Eratóstenes", 2, None),
    ("Inverso modular", 3, None), ("Binomiais mod p", 3, None), ("Inclusão-exclusão", 2, None),
    ("Exponenciação rápida", 3, None), ("FFT/NTT", 1, None), ("Valor esperado por linearidade", 2, None),
    ("Sprague-Grundy", 1, None), ("Produto vetorial / orientação", 3, None), ("Convex hull", 2, None),
    ("Sweep line", 2, None), ("Shoelace (área)", 1, None),
]

TECH_TEXT = [
    "Aplicar {t} sobre a estrutura obtida na etapa anterior.",
    "Com o modelo pronto, {t} resolve cada caso em {c}.",
    "{t} no grafo reduzido; complexidade total {c}.",
    "Manter os valores com {t} para responder cada passo em tempo logarítmico.",
]
NULL_STEPS = [
    ("observação-chave", "Os casos com n ≤ 2 são tratados à parte."),
    ("otimização", "Os valores cabem em 64 bits se a multiplicação for feita antes do módulo."),
    ("reformulação", "Os índices são invertidos para que o laço principal ande da esquerda para a direita."),
]
DISCARD_EASY = [
    "simulação direta; {k} dos 40 melhores times resolveram",
    "implementação de uma fórmula fechada; {k} dos 40 melhores times resolveram",
    "ordenar e contar; {k} dos 40 melhores times resolveram",
    "leitura cuidadosa do enunciado e casos de borda; {k} dos 40 melhores times resolveram",
]
DISCARD_HARD = [
    "a parte difícil é só implementação (muitos casos de borda geométricos)",
    "simulação longa com estruturas comuns; nada reaproveitável",
    "força bruta com poda específica deste enunciado",
]


def build_curriculum(problems, rnd):
    """Fictitious curriculum consistent with the mock problems (same shape as SPEC 2-3)."""
    groups = [{"id": g, "name": n, "order": i + 1} for i, (g, n) in enumerate(INSIGHT_GROUPS)]
    ins_items = {i[0]: {"id": i[0], "group": i[1], "name": i[5], "statement": i[6], "signal": i[7],
                        "contexts": i[8], "known_problems": i[9], "generality": i[2], "problems": []}
                 for i in INSIGHTS}
    ins_meta = {i[0]: (i[3], i[4], i[10]) for i in INSIGHTS}
    dp_items = {d[0]: {"id": d[0], "base": d[1], "name": d[4], "property": d[5], "why": d[6], "signal": d[7],
                       "contexts": d[8], "generality": d[2], "problems": []}
                for d in DEEPENINGS}
    dp_meta = {d[0]: (d[3], d[9]) for d in DEEPENINGS}
    tech = {}
    steps_out = {}

    def pick(pool, weights, n):
        out = []
        for _ in range(n * 3):
            if len(out) >= n:
                break
            x = rnd.choices(pool, weights=weights)[0]
            if x not in out:
                out.append(x)
        return out

    ins_ids = [i[0] for i in INSIGHTS]
    dp_ids = [d[0] for d in DEEPENINGS]
    t_names = [t[0] for t in TECH_POOL]
    for p in problems:
        fam = p["family"]
        easy = p["difficulty"] == "easy"
        if easy and rnd.random() < .9:
            k = p.get("solved_top") or 40
            steps_out[p["id"]] = {"keep": False, "discard_reason": rnd.choice(DISCARD_EASY).format(k=k)}
            continue
        if not easy and rnd.random() < .08:
            steps_out[p["id"]] = {"keep": False, "discard_reason": rnd.choice(DISCARD_HARD)}
            continue
        iw = [ins_meta[i][0] if (ins_meta[i][1] is None or fam in ins_meta[i][1]) else 0 for i in ins_ids]
        tw = [t[1] if (t[2] is None or fam in t[2]) else 0 for t in TECH_POOL]
        n_c = rnd.choices([0, 1, 2], weights=[2, 6, 3])[0]
        n_b = rnd.choices([0, 1], weights=[3, 2])[0]
        n_a = rnd.choice([1, 1, 2])
        cs = pick(ins_ids, iw, n_c)
        bs = pick(dp_ids, [dp_meta[d][0] for d in dp_ids], n_b)
        As = pick(t_names, tw, n_a)
        steps = []
        for c in cs:
            how = rnd.choice(ins_meta[c][2])
            ins_items[c]["problems"].append({"id": p["id"], "how": how})
            steps.append({"kind": rnd.choice(["reformulação", "observação-chave"]), "text": how, "cat": "C", "ref": c})
        if rnd.random() < .35:
            k, t = rnd.choice(NULL_STEPS)
            steps.insert(rnd.randint(0, len(steps)), {"kind": k, "text": t, "cat": None, "ref": None})
        for a in As:
            tech.setdefault(a, []).append(p["id"])
            steps.append({"kind": "estrutura/algoritmo",
                          "text": rnd.choice(TECH_TEXT).format(t=a, c=rnd.choice(COMPLEX)), "cat": "A", "ref": a})
        for b in bs:
            how = rnd.choice(dp_meta[b][1])
            dp_items[b]["problems"].append({"id": p["id"], "how": how})
            steps.append({"kind": "otimização", "text": how, "cat": "B", "ref": b})
        steps_out[p["id"]] = {"keep": True, "steps": steps}
        if p.get("solution_source") == "own":
            steps_out[p["id"]]["unverified"] = True

    return {
        "techniques": [{"name": n, "problems": tech[n]} for n in t_names if n in tech],
        "deepenings": [dp_items[d] for d in dp_ids],
        "insight_groups": groups,
        "insights": [ins_items[i] for i in ins_ids],
        "problem_steps": steps_out,
    }


K = 40  # difficulty_k: top-K official teams (same as the real pipeline)


def difficulty(rate):
    # same bins as build_dataset.py (share of the top-K teams that solved it)
    if rate is None:
        return None
    if rate >= 0.7:
        return "easy"
    if rate >= 0.3:
        return "medium"
    if rate >= 0.1:
        return "hard"
    return "very_hard"


def main():
    ap = argparse.ArgumentParser(description="Write a fictitious dataset in the final shape.")
    ap.add_argument("--curriculum", action="store_true", help="also emit a mock curriculum")
    ap.add_argument("--out", default=OUT, help="output path (default: data/dataset.js)")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    rnd = random.Random(2027)
    fam = {f["id"]: f for f in FAMILIES}
    areas = [{"id": a, "name": n, "order": i + 1} for i, (a, n) in enumerate(AREAS)]
    topics = []
    for tid, area, name, pop, hard, ref in TOPICS:
        topics.append({
            "id": tid, "area": area, "name": name,
            "description": f"{name}: reconhecer quando aplicar, variações comuns e armadilhas de implementação.",
            "includes": [tid.replace("-", " ")],
            "refs": [{"label": f"cp-algorithms — {name}", "url": CPA + ref}],
        })
    pops = [t[3] for t in TOPICS]
    tinfo = {t[0]: t for t in TOPICS}

    contests, problems = [], []
    gym = 104000
    for fid, year, md, teams in CONTESTS:
        gym += rnd.randint(30, 260)
        cid = f"{fid}{year}"
        n = rnd.choice([11, 12, 12, 12, 13])
        mirror = f"https://codeforces.com/gym/{gym}"
        contests.append({
            "id": cid, "family": fid, "name": f"{fam[fid]['name']} {year}",
            "short": f"{fam[fid]['short']} {year}", "year": year, "date": f"{year}-{md}",
            "total_teams": teams,
            "links": {
                "scoreboard": f"https://example.org/{cid}/scoreboard",
                "statements": f"https://example.org/{cid}/problems.pdf",
                "editorial": f"https://example.org/{cid}/editorial.pdf" if rnd.random() < .6 else None,
                "mirror": mirror,
                "kattis": f"https://open.kattis.com/contests/{cid}" if fid == "nac" else None,
            },
            "notes": "dados fictícios (mock)",
        })
        # pick topics, order by hardness -> solve curve
        chosen = []
        while len(chosen) < n:
            t = rnd.choices(TOPICS, weights=pops)[0][0]
            if t not in chosen or rnd.random() < .1:
                chosen.append(t)
        chosen.sort(key=lambda t: tinfo[t][4] + rnd.uniform(-.25, .25))
        curve = sorted([rnd.uniform(.0, 1.0) ** 2.2 for _ in range(n)], reverse=True)
        curve[0] = max(curve[0], rnd.uniform(.8, .97))
        letters = [chr(65 + i) for i in range(n)]
        rnd.shuffle(letters)
        ps = []
        for i, t in enumerate(chosen):
            letter = letters[i]
            solved = int(round(curve[i] * teams))
            if i == n - 1 and rnd.random() < .5:
                solved = 0
            att = min(teams, solved + int(rnd.uniform(.05, .4) * teams)) if rnd.random() < .85 else None
            fs = None
            if solved:
                fs = int(4 + (1 - curve[i]) ** 1.5 * 260 * rnd.uniform(.6, 1.1))
                if rnd.random() < .08:
                    fs = None
            sec = []
            for _ in range(rnd.choice([0, 0, 0, 1, 1, 2])):
                s = rnd.choices(TOPICS, weights=pops)[0][0]
                if s != t and s not in sec:
                    sec.append(s)
            title = f"{rnd.choice(W1)} {rnd.choice(W2)}"
            cx = rnd.choice(COMPLEX)
            ps.append({
                "id": f"{cid}-{letter}", "contest": cid, "family": fid, "year": year, "letter": letter,
                "title": title, "solved": solved, "attempted": att, "total": teams,
                "first_solve_min": fs,
                "links": {
                    "mirror": f"{mirror}/problem/{letter}",
                    "kattis": f"https://open.kattis.com/problems/{title.lower().replace(' ', '')}" if fid == "nac" else None,
                    "statement": f"https://example.org/{cid}/problems.pdf",
                },
                "summary": f"Dado um conjunto de até 2·10^5 elementos, responder ao que o enunciado de \"{title}\" pede. Texto fictício.",
                "solution": f"Aplicar {tinfo[t][2].lower()} depois de reduzir o problema à forma certa; a observação central limita os estados. Complexidade {cx}.",
                "solution_source": rnd.choice(["editorial", "editorial", "community", "own"]),
                "key_idea": f"Reduzir a {tinfo[t][2].lower()} observando a monotonicidade da resposta.",
                "primary": t, "secondary": sec,
                "confidence": rnd.choice(["high", "high", "medium"]),
                "cf_tags": [], "cf_rating": None,
            })
        mx = max(p["solved"] for p in ps)
        for p in ps:
            if rnd.random() < .03:
                p["solved"] = None
            s = p["solved"]
            rel = (s / mx) if (s is not None and mx) else (0.0 if s == 0 else None)
            p["solve_rate"] = round(s / teams, 4) if s is not None else None
            p["rel_solve"] = round(rel, 4) if rel is not None else None
            # top-K share: the strongest teams solve a bit more than the whole field
            top = None if rel is None else min(1.0, rel ** 0.75)
            p["solved_top"] = None if top is None else int(round(top * K))
            p["k_used"] = None if top is None else K
            p["top_rate"] = None if top is None else round(p["solved_top"] / K, 4)
            p["difficulty"] = difficulty(p["top_rate"])
        contests[-1]["problem_count"] = len(ps)
        contests[-1]["max_solved"] = mx
        problems.extend(ps)

    # key order like build_dataset.py
    order = ["id", "contest", "family", "year", "letter", "title", "solved", "attempted", "total",
             "first_solve_min", "solve_rate", "rel_solve", "solved_top", "k_used", "top_rate", "difficulty", "links", "summary", "solution",
             "solution_source", "key_idea", "primary", "secondary", "confidence", "cf_tags", "cf_rating"]
    problems = [{k: p[k] for k in order} for p in problems]
    contests.sort(key=lambda c: (c["year"], c.get("date") or "", c["id"]))
    problems.sort(key=lambda p: (p["contest"], p["letter"]))
    dataset = {
        "generated": datetime.date.today().isoformat(),
        "mock": True,
        "target": {"name": "ICPC Latin America Championship 2027", "date": "2027-07-13T09:00:00-03:00"},
        "families": FAMILIES, "difficulty_k": K, "areas": areas, "topics": topics,
        "contests": contests, "problems": problems,
    }
    if args.curriculum:
        cur = build_curriculum(problems, random.Random(2028))
        dataset["curriculum"] = cur
        kept = sum(1 for v in cur["problem_steps"].values() if v["keep"])
        print(f"MOCK curriculum: {len(cur['techniques'])} techniques, {len(cur['deepenings'])} deepenings, "
              f"{len(cur['insights'])} insights, {kept} kept problems")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("window.DATASET = ")
        json.dump(dataset, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    print(f"MOCK contests={len(contests)} problems={len(problems)} topics={len(topics)} -> {out}")


if __name__ == "__main__":
    main()
