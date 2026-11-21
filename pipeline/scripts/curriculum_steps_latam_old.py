"""Curriculum v2, decomposition step for group "latam_old".

Contests: latam2019, latam2021, latam2022, latam2023a, latam2023b (66 problems).
Writes pipeline/curriculum/steps_latam_old.json and validates it (see SPEC.md, "Curriculum (v2)").

Usage (from Dados_Latam/):  python -I pipeline/scripts/curriculum_steps_latam_old.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
RAW = os.path.join(PIPE, "raw", "latam_regional_2019_2023.json")
OUT = os.path.join(PIPE, "curriculum", "steps_latam_old.json")
CONTESTS = {"latam2019", "latam2021", "latam2022", "latam2023a", "latam2023b"}

CANONICAL = [
    "BFS", "BFS 0-1", "DFS", "Dijkstra", "Bellman-Ford", "Floyd-Warshall", "Ordenação topológica",
    "SCC (Tarjan/Kosaraju)", "Pontes e articulações", "Componentes biconexas", "Caminho euleriano", "2-SAT",
    "MST (Kruskal/Prim)", "DSU", "DSU com rollback", "LCA (binary lifting)", "HLD", "Centroid decomposition",
    "Small-to-large", "Euler tour em árvore", "Matching bipartido (Kuhn/Hopcroft-Karp)", "Blossom",
    "Fluxo máximo (Dinic)", "Corte mínimo", "Fluxo de custo mínimo", "Segment tree", "Segment tree com lazy",
    "Segment tree persistente", "BIT", "BIT 2D", "Sparse table", "Sqrt decomposition", "Mo's algorithm", "Treap",
    "Soma de prefixos", "Array de diferenças", "Pilha monotônica", "Deque monotônico", "Dois ponteiros",
    "Busca binária na resposta", "Busca ternária", "Meet in the middle", "Backtracking com poda",
    "DP com bitmask", "SOS DP", "DP em dígitos", "DP em árvore", "Rerooting", "DP de intervalos", "Mochila", "LIS",
    "Convex hull trick / Li Chao", "Divide and conquer DP", "Knuth", "Slope trick", "Matrix exponentiation",
    "KMP", "Função Z", "Manacher", "Hashing de strings", "Suffix array + LCP", "Suffix automaton", "Aho-Corasick",
    "Trie", "Crivo de Eratóstenes", "Fatoração", "Euclides estendido", "Inverso modular", "CRT",
    "Exponenciação rápida", "Binomiais mod p", "Inclusão-exclusão", "Möbius", "Burnside", "Eliminação gaussiana",
    "Base XOR", "FFT/NTT", "Valor esperado por linearidade", "Sprague-Grundy", "Produto vetorial / orientação",
    "Convex hull", "Interseção de segmentos", "Sweep line", "Ordenação angular", "Rotating calipers",
    "Shoelace (área)", "Rotação 45° (Manhattan → Chebyshev)", "Busca interativa (bisseção)",
]
# Names added by this agent (nothing in the canonical list fits).
NEW_A = [
    "Algoritmo húngaro",
    "Escalonamento EDF (prazo mais cedo)",
    "Busca binária paralela",
    "Soma de Minkowski",
    "Ponto em polígono convexo",
    "Isomorfismo de árvores (hashing)",
]
KINDS = {"reformulação", "observação-chave", "redução", "estrutura/algoritmo", "otimização"}
FORBIDDEN = ["construtivo", "ad hoc", "análise de casos", "observação", "greedy", "matemática", "implementação"]


def A(kind, text, technique):
    return {"kind": kind, "text": text, "cat": "A", "technique": technique}


def B(kind, text, base, name, prop, why, signal, contexts, specific=False, known=None):
    d = {"kind": kind, "text": text, "cat": "B", "base": base, "name": name, "property": prop, "why": why,
         "signal": signal, "contexts": contexts, "specific": specific}
    if known:
        d["known_problems"] = known
    return d


def C(kind, text, name, statement, signal, contexts, known=None, specific=False):
    return {"kind": kind, "text": text, "cat": "C", "name": name, "statement": statement, "signal": signal,
            "contexts": contexts, "known_problems": known or [], "specific": specific}


def N(kind, text):
    return {"kind": kind, "text": text, "cat": None}


def keep(pid, steps, reason=None):
    return {"id": pid, "keep": True, "keep_reason": reason, "steps": steps}


def drop(pid, reason):
    return {"id": pid, "keep": False, "discard_reason": reason}


# ---------------------------------------------------------------- shared insights (reused across problems)

def c_angular(kind, text):
    return C(kind, text,
             "Parâmetro angular: cada restrição vira um arco de ângulos",
             "Se a resposta depende de um ângulo ou direção contínua (rotação de uma figura, direção de projeção, "
             "ponto sobre um círculo), traduza cada objeto em um intervalo de ângulos permitido ou proibido. A pergunta "
             "vira interseção ou união de arcos, resolvida ordenando os extremos e varrendo o círculo em O(n log n).",
             "rotação livre de uma figura, escolha de uma direção, ou 'existe um ângulo tal que...' com n objetos "
             "que restringem independentemente",
             ["direção de projeção que ordena pontos como exigido (cada par dá um semicírculo de direções)",
              "região limitada por retas que cobre ou não um círculo (cada reta corta um arco)",
              "posicionar um holofote/setor de abertura fixa para iluminar o máximo de pontos"],
             ["LATAM 2019 — Build the Perfect House", "LATAM 2019 — Dazzling Stars", "LATAM 2023 — Health in Hazard"])


def c_hereditary(kind, text):
    return C(kind, text,
             "Maior pedaço possível é ótimo quando a validade é hereditária",
             "Se é preciso cortar uma sequência no menor número de pedaços válidos e todo trecho contíguo de um pedaço "
             "válido também é válido, pegar a cada passo o maior prefixo válido é ótimo: por troca, o k-ésimo corte "
             "do método nunca fica antes do k-ésimo corte de uma solução ótima. Resta só calcular rápido o maior "
             "prefixo válido a partir de cada posição.",
             "minimizar o número de partes/instruções que formam uma string ou array, quando cada parte deve ser "
             "substring de X, ter período ≤ D, soma ≤ S, elementos distintos etc.",
             ["cortar array no menor número de blocos com soma ≤ S ou elementos distintos",
              "formar uma string com o menor número de substrings de um texto",
              "imprimir uma string com pedaços que são repetições de um bloco de tamanho ≤ D"],
             ["LATAM 2019 — Gluing Pictures", "LATAM 2023 — Lazy Printing"])


def c_prefix_min(kind, text):
    return C(kind, text,
             "Condição em todos os prefixos ⇒ mínimo das somas de prefixo",
             "'Todo prefixo do subarray [l..r] tem soma ≥ 0' equivale a min(P[l..r]) ≥ P[l−1], com P = somas de prefixo. "
             "Assim cada início l é válido até o primeiro r com P[r] < P[l−1] (próximo menor, por pilha monotônica), e "
             "contagens de subarrays válidos viram Σ (R(l) − l) ou contagem de P[r] = P[l−1] dentro de [l, R(l)).",
             "subarrays/substrings em que um saldo acumulado nunca fica negativo: parênteses balanceados, saldo bancário, "
             "caminhos que não descem abaixo do início",
             ["contar substrings de parênteses balanceadas",
              "dias consecutivos em que o saldo nunca fica negativo",
              "maior subarray em que toda soma de prefixo é ≥ 0"],
             ["LATAM 2022 — Daily Turnovers", "LATAM 2023 — Latam++"])


# ---------------------------------------------------------------- problems

P = []

# ======================= LATAM 2019
P.append(keep("latam2019-A", [
    N("reformulação", "Os conjuntos possíveis (todos os subconjuntos não vazios de cada professor, sem repetição) "
      "formam uma ordem parcial por inclusão; o time pedido é a maior anticadeia."),
    B("redução", "Maior anticadeia = |V| − matching máximo entre cópia de saída e cópia de entrada das relações ⊂.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)",
      "Dilworth: anticadeia máxima = cobertura mínima por cadeias",
      "Em uma ordem parcial (DAG transitivamente fechado), a maior anticadeia tem o tamanho da menor cobertura por "
      "cadeias, que é |V| − matching máximo no grafo bipartido com uma aresta u_saída → v_entrada para cada u < v.",
      "Cada aresta do matching emenda dois elementos na mesma cadeia e reduz em 1 o número de cadeias (cobertura por "
      "caminhos disjuntos); com o fecho transitivo os caminhos podem pular elementos, então caminhos = cadeias. "
      "Dilworth (equivalente a König no grafo bipartido) garante que esse mínimo é igual à maior anticadeia.",
      "pede o maior conjunto de itens dois a dois incomparáveis (nenhum contém/domina outro) ou o menor número de "
      "cadeias/rotas que cobrem todos os itens",
      ["menor número de caminhos (vértices podem se repetir) que cobrem um DAG: fecho transitivo + matching",
       "maior conjunto de pontos 2D/caixas em que nenhum domina outro",
       "menor número de veículos para cobrir viagens com horários compatíveis"]),
    N("otimização", "O fecho transitivo tem no máximo cerca de N·3^K arestas (subconjunto ⊂ superconjunto dentro de "
      "cada professor), o que cabe com Hopcroft-Karp."),
    A("estrutura/algoritmo", "Hopcroft-Karp em ~1e5 vértices.", "Matching bipartido (Kuhn/Hopcroft-Karp)"),
]))

P.append(keep("latam2019-B", [
    A("reformulação", "Busca binária no meio-lado s: quadrado maior contém mais pontos (monótono).",
      "Busca binária na resposta"),
    c_angular("observação-chave", "Com s fixo, cada ponto proíbe um único intervalo de rotações t (mod 90°), centrado "
              "no seu ângulo polar menos 45°; existe rotação válida sse a união dos intervalos não cobre [0°, 90°)."),
    A("estrutura/algoritmo", "Ordenar extremos dos intervalos e varrer para testar cobertura do círculo.", "Sweep line"),
]))

P.append(keep("latam2019-C", [
    C("reformulação", "Cada mês é f_i(x) = clamp(x + A_i, L, U) e a composição de duas dessas funções ainda tem a forma "
      "min(hi, max(lo, x + c)).",
      "Fechar a família de funções sob composição",
      "Se cada passo aplica uma função de uma família simples (soma + saturação, min/max com constante, afim mod p, "
      "mapeamento de um conjunto pequeno) e as consultas pedem 'aplique os passos l..r ao valor x', verifique se a "
      "composição de duas funções da família continua na família com O(1) parâmetros. Então pré-componha blocos "
      "(segment tree, sparse table disjunta ou binary lifting) e responda cada consulta compondo O(log n) blocos.",
      "processo sequencial com estado escalar e consultas 'começando com x no passo l, qual o valor após o passo r', "
      "com operações de soma, clamp, min/max",
      ["operações afins a·x + b mod p aplicadas em intervalos de passos",
       "saldo com teto e piso (saturação) consultado a partir de qualquer dia",
       "permutações/funções em um conjunto pequeno compostas em intervalos (autômato aplicado a substring)"]),
    A("estrutura/algoritmo", "Segment tree cujo nó guarda a composição (lo, hi, c) do seu intervalo; a consulta compõe "
      "os nós na ordem.", "Segment tree"),
]))

P.append(keep("latam2019-D", [
    c_angular("reformulação", "Cada par com brilho B_S > B_T exige d·(S − T) ≥ 0 para a direção de impressão d: um "
              "semicírculo de direções válidas; precisa existir d em todos."),
    B("observação-chave", "Ordenar os O(N²) vetores de diferença por ângulo e procurar lacuna ≥ π entre consecutivos.",
      "Ordenação angular",
      "Vetores cabem num semiplano ⇔ existe lacuna angular ≥ π",
      "Um conjunto de vetores admite d com d·v ≥ 0 para todos sse, ordenados por ângulo, alguma lacuna entre "
      "consecutivos (circularmente) é ≥ π. O teste é exato com comparador inteiro (meio-plano + produto vetorial).",
      "Todos estarem num semiplano fechado equivale a existir um arco aberto de tamanho π sem vetores; reciprocamente, "
      "se há tal lacuna, o arco ocupado tem tamanho ≤ π e a direção do seu meio serve como d.",
      "existe uma direção/rotação que deixa todas as diferenças 'para frente', ou verificar se vetores ficam de um "
      "lado de alguma reta pela origem",
      ["origem fora do fecho convexo de um conjunto de vetores",
       "existe rotação que torna uma sequência de movimentos sempre 'para cima'",
       "maior número de pontos em um semiplano pela origem (janela angular de tamanho π)"]),
]))

P.append(drop("latam2019-E", "contagem direta em string circular (duplicar + próxima ocorrência de 'E'); 40/40 dos top-40"))

P.append(keep("latam2019-F", [
    C("reformulação", "Remover a camada inferior (que cobre todas as s pilhas) deixa uma base sem água sobre k pilhas "
      "contíguas, posicionada de s − k + 1 formas.",
      "Descascar a camada de baixo",
      "Para contar formas feitas de colunas empilhadas com condição de 'convexidade' (unimodal, sem buracos, sem reter "
      "água), remova a camada inferior inteira: o que sobra é uma forma do mesmo tipo, menor, apoiada num subintervalo "
      "contíguo. Isso dá uma recorrência dp[largura][área] em termos de larguras menores e área − largura.",
      "contar sequências de alturas/histogramas com soma fixa e restrição de forma (unimodal, convexa, sem água)",
      ["partições de inteiros via diagrama de Young (remover a primeira linha/coluna)",
       "contar polígonos de colunas convexos com área fixa",
       "contar sequências unimodais de soma fixa"]),
    B("otimização", "dp[s][b] = Σ_k (s − k + 1)·dp[k][b − s] em O(1) por estado com prefixos de dp[k] e k·dp[k].",
      "Soma de prefixos",
      "Peso afim no índice: duas somas de prefixo",
      "Uma transição Σ_k (s − k + 1)·dp[k] (qualquer peso afim em k) se calcula em O(1) mantendo prefixos de dp[k] "
      "e de k·dp[k]: (s + 1)·Σ dp[k] − Σ k·dp[k].",
      "O peso se separa em termos que só dependem de s multiplicando somas que só dependem de k, e essas somas são "
      "pré-computáveis.",
      "DP cuja transição soma dp[k] multiplicado por (s − k + 1), (i − j) ou número de posições de encaixe",
      ["DP de contagem que encaixa um bloco de tamanho k em n − k + 1 posições",
       "custo Σ_j (i − j)·a[j] em DP de agrupamento",
       "soma de distâncias |i − j| de cada i a todos os j anteriores"]),
]))

P.append(keep("latam2019-G", [
    c_hereditary("observação-chave", "Substrings de uma substring de C também são substrings de C, então o melhor é "
                 "pegar sempre o maior prefixo restante que ocorre em C."),
    A("estrutura/algoritmo", "Percorrer o autômato de sufixos de C caractere a caractere, voltando à raiz (novo "
      "pedaço) quando a transição falha.", "Suffix automaton"),
], reason="fácil (36/40), mas o passo central é o critério de quando o maior pedaço é ótimo — mesma ideia de Lazy Printing (LATAM 2023)"))

P.append(keep("latam2019-H", [
    C("reformulação", "A soma das pontuações nunca diminui; os ciclos (turno sem ganho troca os papéis) ficam dentro de "
      "um mesmo par de pontuações.",
      "Ordem por potencial que nunca diminui",
      "Se a DP tem ciclos, procure uma quantidade que nunca diminui ao longo das transições (soma de pontuações, "
      "itens usados, tempo). Processando os níveis dessa quantidade em ordem, os ciclos ficam confinados dentro de um "
      "nível, que é pequeno e pode ser resolvido à parte.",
      "DP de jogo/probabilidade em que um estado pode voltar a si mesmo (turno perdido, passe, troca de jogador sem "
      "progresso)",
      ["jogos de dados com passagem de turno sem ganho",
       "cadeias de Markov em que só algumas transições não avançam um contador",
       "caminho mínimo em que só arestas de custo 0 formam ciclos (resolver cada componente)"]),
    C("otimização", "Em cada nível, P(c,h,0) e P(h,c,0) dependem um do outro de forma monótona: chute um, propague e "
      "faça busca binária no ponto fixo (ou itere até convergir).",
      "Ponto fixo monótono: chute e verifique",
      "Quando poucas incógnitas dependem umas das outras em ciclo (A = f(B), B = g(A)) com funções monótonas, chute "
      "A, propague e faça busca binária em A = g(f(A)). Alternativa: iteração de valor, que converge geometricamente "
      "quando cada volta do ciclo tem probabilidade positiva de terminar.",
      "probabilidades/expectativas definidas circularmente entre poucos estados (meu turno ↔ turno do oponente)",
      ["valor esperado com auto-laço resolvido algebricamente (E = c + p·E)",
       "probabilidade de vitória em jogos alternados com passe",
       "equações de Bellman de jogos estocásticos resolvidas por iteração"]),
]))

P.append(drop("latam2019-I", "contagem de caminhos em DAG + alcançabilidade, aplicação direta; 40/40"))

P.append(keep("latam2019-J", [
    C("observação-chave", "Os saltos alternam de lado com alturas crescentes; o destino depende só dos máximos à "
      "esquerda e à direita de J.",
      "Processo de saltos crescentes só depende dos recordes",
      "Se um processo salta sempre para um valor estritamente maior e alterna de lado, ele termina perto de um recorde "
      "(máximo de prefixo/sufixo); o destino sai de comparações entre esses máximos, sem simular os Θ(n) saltos.",
      "simulação de 'pular para o próximo maior' com troca de direção, com muitas consultas e atualizações",
      ["processo de 'próximo maior' iterado alternando lados"],
      specific=True),
    B("estrutura/algoritmo", "Achar o primeiro índice à esquerda/direita com altura maior que um limiar, com "
      "atualizações pontuais.",
      "Segment tree",
      "Descida na segment tree",
      "Encontrar o primeiro índice a partir de j com valor > v em O(log n), com atualizações pontuais, descendo pela "
      "árvore de máximos em vez de busca binária + consulta (O(log² n)).",
      "Cada nó guarda o máximo do seu intervalo: se o filho da esquerda (restrito ao intervalo) tem máximo > v, a "
      "resposta está nele; senão, no da direita. Só um caminho raiz-folha é aprofundado.",
      "consultas 'primeira posição a partir de j com valor > v' ou 'com soma de prefixo ≥ k', com atualizações",
      ["k-ésimo elemento / primeira posição com soma de prefixo ≥ k",
       "próximo maior elemento com valores mudando",
       "alocar o primeiro bloco livre com capacidade ≥ k"]),
]))

P.append(drop("latam2019-K", "uma raiz entre cada troca de sinal + expansão do produto; 37/40"))
P.append(drop("latam2019-L", "reformulação imediata (cada linha do quadrado uniforme) + maior quadrado em grade padrão; 40/40"))
P.append(drop("latam2019-M", "varredura linear; 40/40"))

# ======================= LATAM 2021
P.append(keep("latam2021-A", [
    C("reformulação", "A altura do cruzamento satisfaz 1/H = 1/L + 1/R: em recíprocos, cada novo valor é soma de dois "
      "existentes a partir de 1.",
      "Recíprocos linearizam combinações 'em paralelo'",
      "Uma operação da forma L·R/(L + R) (resistores em paralelo, trabalho conjunto, cruzamento de retas a partir dos "
      "cantos) é soma em 1/x: 1/H = 1/L + 1/R. Troque para recíprocos e o conjunto alcançável/ótimo vira um problema "
      "aditivo.",
      "fórmula de produto sobre soma, ou enunciado com 'juntos', 'em paralelo', 'média harmônica'",
      ["resistência equivalente de circuitos série/paralelo",
       "dois trabalhadores/torneiras juntos: tempos combinam por recíprocos",
       "altura do cruzamento de duas escadas apoiadas em paredes opostas"]),
    N("redução", "As alturas alcançáveis são exatamente 1/k; a resposta é '*' se M ≠ 1 e senão a menor cadeia de adição "
      "até N ≤ 100."),
    A("estrutura/algoritmo", "Aprofundamento iterativo com poda: se dobrar o maior valor em todos os passos restantes "
      "não alcança N, corte.", "Backtracking com poda"),
]))

P.append(keep("latam2021-B", [
    N("observação-chave", "A validade de um bloco com curingas depende só da ordem das subidas e descidas estritas "
      "entre valores conhecidos; com 'próxima subida/descida' pré-computada, cada bloco se testa em O(1)."),
    C("otimização", "Testar todo tamanho de bloco k custa Σ N/k = O(N log N).",
      "Série harmônica: todos os tamanhos de bloco custam O(n log n)",
      "Se é preciso testar todo tamanho/período k e para k fixo há n/k blocos, torne o teste de um bloco O(1) "
      "(pré-computando 'próximo evento' ou somas de prefixo) e enumere todos os k: o total é Σ n/k = O(n log n).",
      "testar todos os comprimentos de bloco k que particionam o array, ou percorrer todos os múltiplos de cada d",
      ["para cada d, percorrer os múltiplos de d (crivo, contagem de pares por gcd)",
       "achar todo k para o qual a string se divide em blocos com uma propriedade",
       "para todo k, dividir em blocos de tamanho k e contar algo por bloco"]),
]))

P.append(keep("latam2021-C", [
    C("reformulação", "Fixando o fluxo x numa aresta, a aresta i carrega x + prefixo_i do excesso; com sentido único e "
      "fluxo ≥ 0, x = −min prefixo.",
      "Fluxo num ciclo: parametrize por uma aresta",
      "Em redistribuição ao redor de um ciclo, fixe x = quantidade que cruza uma aresta escolhida; por conservação, o "
      "fluxo em cada outra aresta é x + p_i (somas de prefixo dos excessos). O custo vira função de uma variável: "
      "Σ |x + p_i| (mínimo na mediana de −p_i) ou, com sentido único e fluxo ≥ 0, x = −min p_i.",
      "itens em círculo que devem ser equalizados movendo unidades entre vizinhos, custo = unidades × distância",
      ["equalizar moedas numa mesa redonda (mediana dos prefixos)",
       "posto de gasolina circular: comece logo após o prefixo mínimo",
       "transportar carga num anel em um ou nos dois sentidos"],
      ["UVa 11300 — Spreading the Wealth"]),
    A("estrutura/algoritmo", "Somas de prefixo dos excessos, nos dois sentidos.", "Soma de prefixos"),
], reason="fácil (39/40), mas o truque de parametrizar fluxo num ciclo é reutilizável"))

P.append(drop("latam2021-D", "soma de potências de 2 em contador binário com vai-um; 40/40"))

P.append(keep("latam2021-E", [
    C("reformulação", "Fixe o destino j: com o prédio mais alto mais próximo p de um lado, j é contado exatamente pelos "
      "i daquele lado a menos de (p + j)/2 — um intervalo de i.",
      "Contar pelo alvo: cada alvo cobre um intervalo de origens",
      "Se a resposta para cada i é 'quantos j satisfazem P(i, j)', inverta os papéis: para cada j descubra o conjunto "
      "de i que o contam. Se esse conjunto é um intervalo (ou poucos), some +1 nele com array de diferenças e todas as "
      "respostas saem em O(n) depois de achar os limites.",
      "'para cada i, conte os j tais que...' com n grande, e a condição, fixado j, vira um intervalo de i",
      ["para cada posição, quantos elementos a enxergam ou a dominam",
       "quantos intervalos contêm cada ponto",
       "contribuição de cada elemento a todos os subarrays em que ele é o máximo"]),
    A("estrutura/algoritmo", "Maior mais próximo de cada lado.", "Pilha monotônica"),
    A("estrutura/algoritmo", "+1 em intervalos de i.", "Array de diferenças"),
], reason="fácil (38/40), mas o passo central é contar pela contribuição de cada alvo"))

P.append(keep("latam2021-F", [
    N("reformulação", "DP em camadas dp[k][i] = min/max_j dp[k−1][j] + max(A[j+1..i]); O(N) por camada dá O(N²)."),
    B("otimização", "Em cada camada, varrer i mantendo uma pilha monotônica de máximos em que cada elemento guarda o "
      "melhor dp[k−1] do seu grupo.",
      "Pilha monotônica",
      "Pilha monotônica que guarda o melhor dp de cada grupo",
      "min_j (dp[j] + max(A[j+1..i])) para todo i em O(n) amortizado: os j com o mesmo máximo de sufixo formam um "
      "grupo contíguo na pilha; guarde em cada elemento o melhor dp do grupo e o mínimo acumulado de (melhor + máximo) "
      "até ele.",
      "Ao chegar A[i], os grupos com máximo ≤ A[i] passam a ter máximo A[i] e se fundem em um só, do qual só importa o "
      "melhor dp; cada grupo entra e sai da pilha uma vez, e o mínimo acumulado por nível se atualiza no topo.",
      "DP de partição em blocos contíguos com custo = máximo (ou mínimo) do bloco",
      ["dividir em blocos minimizando Σ dos máximos (com limite de soma por bloco, usando deque/multiset)",
       "agendamento em lotes em que o custo do lote é a maior duração",
       "somar max(subarray) sobre todos os subarrays terminando em i"]),
]))

P.append(keep("latam2021-G", [
    N("observação-chave", "Empates têm probabilidade desprezível; Bob vence cada slot, do mais valioso ao menos, com a "
      "menor carta que supera a de Alice (senão descarta a menor), e então Alice deve pôr as cartas em ordem crescente "
      "de valor de slot (troca)."),
    C("reformulação", "Primeiro a melhor resposta de Bob, que vê tudo; só depois a otimização de Alice contra ela.",
      "Resolva primeiro quem joga por último",
      "Em jogo de duas fases com informação completa, determine a melhor resposta do segundo jogador como função das "
      "escolhas do primeiro (muitas vezes: cubra cada alvo mais valioso com o menor recurso que o vence). Só então "
      "otimize o primeiro contra essa resposta, em geral por argumento de troca entre duas escolhas adjacentes.",
      "um jogador fixa uma configuração inteira e o outro responde vendo tudo",
      ["corrida de cavalos de Tian Ji: casar cartas para maximizar vitórias",
       "defensor distribui guardas e atacante escolhe o ponto mais fraco",
       "alocação de tropas em campos com resposta do adversário (Blotto sequencial)"]),
    C("otimização", "Percorrer as 2N cartas em ordem decrescente: a próxima é de Alice com probabilidade n/(n + m); "
      "DP sobre (cartas de Alice restantes, de Bob restantes, cartas de Bob disponíveis para vencer).",
      "Mesclar duas amostras aleatórias pela ordem global",
      "Quando dois conjuntos de valores distintos são sorteados da mesma distribuição e só comparações importam, gere "
      "a ordem global (do maior ao menor) passo a passo: o próximo elemento é do conjunto A com probabilidade "
      "a/(a + b), com a, b = quantos restam de cada. Isso vira uma DP em (a, b, estado) em vez de somar sobre todas as "
      "distribuições de valores.",
      "cartas/valores aleatórios entre jogadores, com resultado que depende só de quem tem a carta maior",
      ["probabilidade de os k maiores valores serem todos do mesmo jogador",
       "problema da votação/urna: A sempre à frente de B na ordem",
       "valor esperado de um duelo de cartas sorteadas com estratégia fixa"]),
]))

P.append(keep("latam2021-H", [
    B("redução", "Instruções = vértices, saltos finitos = arestas de capacidade 1 por ocorrência, saltos infinitos = "
      "capacidade infinita; instrução 1 dividida em fonte/sumidouro; resposta 1 + fluxo, '*' se o fluxo é ilimitado.",
      "Fluxo máximo (Dinic)",
      "Fluxo conta passeios com uso limitado de arestas",
      "Um passeio fechado que volta k vezes a v usando cada aresta no máximo c(e) vezes existe sse há fluxo k de "
      "v_saída para v_entrada (v dividido) com capacidades c. Os demais vértices podem se repetir à vontade.",
      "O fluxo inteiro se decompõe em k caminhos v → v (mais ciclos que não passam por v), que concatenados formam o "
      "passeio; reciprocamente, contar quantas vezes o passeio usa cada aresta dá um fluxo válido de valor k.",
      "transições que só podem ser usadas um número limitado de vezes e a pergunta é quantas vezes se consegue voltar "
      "a um ponto, ou quantas viagens cabem",
      ["número máximo de voltas a uma base com bilhetes de uso único entre cidades",
       "caminhos aresta-disjuntos (não vértice-disjuntos) entre s e t",
       "ciclo de capacidade infinita pela origem ⇒ resposta ilimitada"]),
    A("estrutura/algoritmo", "Dinic no grafo de ~100 vértices.", "Fluxo máximo (Dinic)"),
], reason="fácil (37/40), mas o modelo de fluxo para passeios (não caminhos) é uma propriedade pouco conhecida"))

P.append(keep("latam2021-I", [
    C("reformulação", "Visibilidade total a partir da casa força os vértices em ordem angular em torno dela, começando "
      "pelo portão.",
      "Estrelado em relação a um ponto ⇒ ordem angular fixa",
      "Se um polígono deve ser totalmente visível de um ponto interior P (estrelado em P), seus vértices aparecem em "
      "ordem angular estrita em torno de P. Ordene os candidatos por ângulo: contar polígonos vira escolher "
      "subsequências dessa ordem com condições locais.",
      "polígonos 'vistos', 'iluminados' ou que 'contêm' um ponto dado, com vértices escolhidos de um conjunto",
      ["contar polígonos convexos que contêm a origem",
       "maior polígono estrelado com vértices em um conjunto",
       "maior polígono convexo vazio (ordem angular a partir do vértice mais baixo)"]),
    B("estrutura/algoritmo", "dp[j][k] sobre os dois últimos vértices; estende para l se (j,k,l) curva à esquerda e "
      "(casa,k,l) é anti-horário. O(N³).",
      "Ordenação angular",
      "DP sobre as duas últimas arestas",
      "Para contar/otimizar polígonos convexos com vértices em ordem angular, basta o estado (penúltimo, último "
      "vértice): convexidade e 'contém o ponto' são testes de orientação sobre triplas consecutivas.",
      "Um polígono em ordem angular é convexo sse todas as curvas consecutivas são para o mesmo lado — condição local "
      "em triplas, então lembrar as duas últimas arestas é suficiente.",
      "contar ou maximizar polígonos convexos com vértices em n ≤ ~300 pontos",
      ["maior polígono convexo vazio",
       "contar polígonos convexos com área mínima/restrições",
       "caminho convexo de maior comprimento por DP O(n³)"]),
]))

P.append(keep("latam2021-J", [
    C("reformulação", "Cada máquina tem soma ≤ 8 recursos, logo ≤ 2^8 submulticonjuntos: na conexão some ±1 em todos, "
      "e a consulta é uma leitura.",
      "Atualização espalha nos subobjetos, consulta vira leitura",
      "Se cada objeto inserido tem poucos subobjetos (submulticonjuntos, prefixos, subconjuntos de um conjunto "
      "pequeno) e a consulta pergunta quantos objetos contêm Q, na inserção some +1 em todos os subobjetos e a "
      "consulta é um acesso a tabela. Um multiconjunto de soma s tem no máximo Π(c_i + 1) ≤ 2^s submulticonjuntos.",
      "objetos minúsculos (≤ 8–20 elementos) e consultas 'quantos contêm Q' com inserções e remoções online",
      ["contar palavras do conjunto que têm Q como prefixo (inserir todos os prefixos num hash)",
       "contar máscaras de ≤ 20 bits que contêm a máscara Q, com inserções online",
       "contar palavras que contêm um multiconjunto de letras pedido"]),
]))

P.append(drop("latam2021-K", "DP com transições em intervalo resolvidas por soma de prefixos, padrão; 40/40"))
P.append(drop("latam2021-L", "força bruta sobre a linha do tempo; 40/40"))

P.append(keep("latam2021-M", [
    B("observação-chave", "Ao anexar um caractere a resposta muda em L2 − L3 (maiores sufixos que ocorrem ≥ 2 e ≥ 3 "
      "vezes).",
      "Suffix automaton",
      "Variação ao anexar um caractere: só sufixos mudam",
      "Ao anexar c, as substrings que passam a ter ≥ k ocorrências são exatamente os sufixos com comprimento em "
      "(L_{k+1}, L_k], onde L_k = maior sufixo do novo texto com ≥ k ocorrências. Para k = 1 é o clássico: novas "
      "substrings distintas = |s| − len(link(last)).",
      "Só ocorrências que terminam na nova posição são criadas, e elas são sufixos; o número de ocorrências de um "
      "sufixo é não crescente no comprimento, então os sufixos com ≥ k ocorrências são os de comprimento ≤ L_k.",
      "contar substrings distintas (ou com frequência mínima) após cada anexação",
      ["número de substrings distintas de cada prefixo",
       "substrings que aparecem pelo menos 2 vezes, online",
       "maior substring repetida de cada prefixo"]),
    C("estrutura/algoritmo", "Remoções são sempre do último caractere: guardar a versão do autômato/resposta de cada "
      "push e restaurá-la no pop.",
      "Anexar/remover o último = pilha de versões",
      "Se as operações só mexem no fim (push/pop), as versões formam uma pilha: registre as alterações e a resposta de "
      "cada push e desfaça no pop. Cuidado: estruturas com custo amortizado (autômato de sufixos, DSU com compressão "
      "de caminho) podem degradar com desfazer/refazer repetido — use versões sem amortização ou persistentes.",
      "operações 'adicionar no fim' e 'remover o último' intercaladas com consultas sobre o estado inteiro",
      ["DSU com rollback na conectividade dinâmica offline",
       "backtracking que mantém uma estrutura incremental",
       "editor com desfazer mantendo estatísticas do texto"]),
]))

P.append(drop("latam2021-N", "parsing e soma dos centavos módulo 100; 40/40"))

# ======================= LATAM 2022
P.append(keep("latam2022-A", [
    C("reformulação", "Todo quadrilátero simples tem uma diagonal interna (i, j) com os outros dois vértices em lados "
      "opostos, e a área é a soma dos dois triângulos; convexos têm duas diagonais e são contados duas vezes.",
      "Fixar o segmento e separar os pontos por lado",
      "Em contagem geométrica com n ≤ ~500 pontos, fixe um par (i, j) e classifique os demais pelo lado da reta ij: "
      "grandezas como área se somam por lado e escolhas em lados opostos ficam independentes, então a contagem vira "
      "pares (um de cada lado) com ordenação + dois ponteiros. Se uma figura tem mais de um par canônico, corrija a "
      "dupla contagem.",
      "contar triângulos/quadriláteros com vértices em pontos dados e restrição de área ou orientação",
      ["contar triângulos que contêm a origem",
       "contar quadriláteros convexos (= pares de segmentos que se cruzam)",
       "maior área de quadrilátero com vértices em n pontos (diagonal + melhor triângulo de cada lado)"]),
    A("estrutura/algoritmo", "Para cada (i, j), áreas ordenadas de cada lado e contagem de pares com soma ≥ 2S.",
      "Dois ponteiros"),
    A("otimização", "Ordenar os pontos por ângulo em torno de i para obter os lados de cada reta ij sem refazer tudo.",
      "Ordenação angular"),
]))

P.append(keep("latam2022-B", [
    C("observação-chave", "Com fontes e cores escolhidas, o melhor é parear ordenado com ordenado (máximo) ou com "
      "invertido (mínimo).",
      "Pareamento ordenado (desigualdade do rearranjo)",
      "Escolhidos os elementos, Σ a_i·b_π(i) é máxima pareando ordenado com ordenado e mínima pareando ordenado com "
      "invertido. Assim só resta escolher quais elementos usar, e o pareamento por índice nos arrays ordenados passa a "
      "ser a estrutura do problema.",
      "maximizar/minimizar soma de produtos sobre emparelhamentos entre dois conjuntos",
      ["minimizar o produto escalar de dois vetores permutando um deles",
       "atribuir tarefas a trabalhadores com custo = produto de taxas",
       "Σ |a_i − b_π(i)| mínimo com ambos ordenados"]),
    N("observação-chave", "Para o máximo, primeiro os pares alinhados de produto positivo (grande×grande e "
      "negativo×negativo, pelas pontas); depois disso os pares restantes são não positivos e devem usar os elementos "
      "de menor valor absoluto (o meio dos arrays)."),
    B("otimização", "As somas das janelas alinhadas do meio, para todo k, saem de uma convolução.",
      "FFT/NTT",
      "Somas de produtos alinhados para todos os deslocamentos = convolução",
      "Os valores S(d) = Σ_i a[i]·b[i + d] para todo d (correlação) saem de uma única convolução de a invertido com b; "
      "somas de janelas alinhadas de todos os tamanhos se reduzem a isso.",
      "Invertendo a, o par (i, i + d) vira índices (n − 1 − i) + (i + d) = n − 1 + d, constante para cada d — "
      "exatamente um coeficiente da convolução.",
      "para todo k ou deslocamento, a soma de produtos de elementos alinhados de dois arrays",
      ["casamento de padrão com curingas via FFT",
       "deslocamento de duas strings com mais coincidências",
       "autocorrelação de sequências binárias"]),
]))

P.append(keep("latam2022-C", [
    C("reformulação", "As nuvens saem da região após algumas centenas de passos: BFS em (x, y, t) com t limitado.",
      "Estado (posição, tempo) com horizonte limitado",
      "Se o ambiente muda com o tempo (obstáculos que se movem, portas que abrem), use o estado (posição, t) e BFS no "
      "grafo expandido no tempo; limite t notando quando o ambiente fica estático (obstáculos saem da área) ou "
      "periódico (use t mod período).",
      "obstáculos móveis com velocidade constante, esperar é permitido, grade pequena",
      ["labirinto com portas que alternam a cada k passos (estado t mod k)",
       "fugir de fogo que se espalha (BFS multi-fonte do fogo + BFS do jogador)",
       "semáforos/trens periódicos num grafo"]),
    N("estrutura/algoritmo", "Rasterizar cada nuvem retilínea em células/arestas molhadas e deslocar as máscaras a "
      "cada instante."),
    A("estrutura/algoritmo", "BFS com movimentos e espera.", "BFS"),
]))

P.append(keep("latam2022-D", [
    c_prefix_min("reformulação", "Com P = somas de prefixo, o início l vale até R(l) − 1, onde R(l) é o primeiro r ≥ l "
                 "com P[r] < P[l − 1]; felicidade = Σ (R(l) − l)."),
    N("otimização", "Somar X na posição i só afeta os inícios com l − 1 ≤ i ≤ R(l); varrer i de trás para frente "
      "atualizando essas contribuições, com novo primeiro r ≥ i tal que P[r] < P[l − 1] − X."),
    A("estrutura/algoritmo", "Próximo menor nas somas de prefixo.", "Pilha monotônica"),
    A("estrutura/algoritmo", "Busca do primeiro prefixo abaixo de um limiar a partir de i.", "Segment tree"),
]))

P.append(keep("latam2022-E", [
    A("reformulação", "Estado = intervalo de segmentos candidatos + lado onde está o barco; escolher o repetidor m "
      "custa navegação + mergulho + max(subintervalo esquerdo, direito).", "DP de intervalos"),
    C("otimização", "O termo esquerdo cresce e o direito decresce com m: busca binária do cruzamento; de cada lado, o "
      "resto é mínimo em intervalo.",
      "min-max de termo crescente e termo decrescente: ache o cruzamento",
      "Para min_m max(f(m), g(m)) com f não decrescente e g não crescente em m, o ótimo está no cruzamento: ache por "
      "busca binária (ou ponteiro monótono) o primeiro m com f(m) ≥ g(m). De cada lado o max é um único termo "
      "conhecido, e o que sobra vira consulta de mínimo em intervalo.",
      "DP minimax de pior caso (busca adaptativa, árvore de decisão) com transição max(esquerda, direita) sobre um "
      "ponto de divisão m",
      ["queda de ovos: min sobre o andar de max(quebra, não quebra)",
       "adivinhar um número pagando pelo palpite (pior caso, DP de intervalos)",
       "dividir uma sequência entre duas máquinas minimizando o maior tempo"]),
    A("estrutura/algoritmo", "Mínimos de prefixo/sufixo por l e por r para a parte de cada lado do cruzamento.",
      "Segment tree"),
]))

P.append(keep("latam2022-F", [
    C("observação-chave", "O vértice N pesa mais que todos os outros juntos, então Ana fica com N, Bob com N − 1, e o "
      "resto se decide do maior para o menor.",
      "Pesos 2^i distintos: o maior elemento decide",
      "Com pesos 2^i distintos, 2^i > Σ_{j<i} 2^j: comparar dois conjuntos é compará-los pelo maior elemento em que "
      "diferem. Decida do maior índice para o menor, fixando cada um se ainda for viável — isso substitui qualquer "
      "otimização numérica.",
      "custos/pesos da forma 2^i (ou base ≥ 2 elevada a índices distintos)",
      ["MST/caminho mínimo com arestas de peso 2^i distintos: comparar pelo maior peso",
       "escolher subconjunto que minimiza Σ 2^i sob restrição de conectividade",
       "minimizar o maior elemento usado, depois o segundo maior..."]),
    A("estrutura/algoritmo", "Bob fica com a componente de N − 1 no grafo sem N.", "BFS"),
], reason="fácil (40/40), mas o argumento de pesos 2^i é um padrão recorrente"))

P.append(keep("latam2022-G", [
    C("observação-chave", "T2 se divide em pedaços conexos de tamanho d sse exatamente |T2|/d vértices têm subárvore "
      "de tamanho múltiplo de d; o corte é único.",
      "Cortar árvore em pedaços de tamanho d: único e por divisibilidade",
      "Uma árvore com n vértices se divide em componentes conexas de tamanho d sse exatamente n/d vértices têm tamanho "
      "de subárvore múltiplo de d. O corte é único: corte a aresta para o pai de cada vértice (exceto a raiz) com "
      "subárvore múltipla de d. Vale igual para pesos: partes de soma S ⇔ n/S subárvores com soma múltipla de S.",
      "particionar uma árvore em partes conexas de mesmo tamanho ou mesma soma",
      ["dividir árvore em k partes de mesma soma de pesos",
       "para quantos d a árvore se divide em blocos conexos de tamanho d",
       "cortar o máximo de arestas mantendo todas as componentes de tamanho par"]),
    A("estrutura/algoritmo", "Hash canônico de cada pedaço (não enraizado, via centro(s)) e contagem de árvores da "
      "entrada com o mesmo hash.", "Isomorfismo de árvores (hashing)"),
    N("otimização", "Só testar divisores d de |T| que são tamanhos presentes na entrada: custo Σ |T|·d(|T|)."),
]))

P.append(keep("latam2022-H", [
    C("redução", "Posições pares fixas: pôr a cidade ímpar c na posição ímpar p custa L[c][p−1] + L[c][p+1], "
      "independente das outras escolhas.",
      "Fixar posições alternadas desacopla as livres",
      "Se a sequência tem custo entre vizinhos e as posições de uma classe (as pares) são fixas, cada posição livre só "
      "tem vizinhos fixos: o custo de pôr o item x na posição p independe do resto, e o problema vira atribuição "
      "(matching bipartido de custo mínimo).",
      "caminho/ciclo com metade das posições fixada, ou grade em que as casas de uma cor do tabuleiro já estão "
      "definidas",
      ["tabuleiro com casas pretas fixas: preencher as brancas é uma atribuição independente",
       "colocar itens em slots cujo custo depende só de vizinhos já fixos",
       "sequência alternada A/B onde um dos tipos tem ordem fixa"]),
    A("estrutura/algoritmo", "Atribuição de custo mínimo ~250 × 250 em O(n³).", "Algoritmo húngaro"),
], reason="fácil (31/40), mas a redução a atribuição por desacoplamento é reutilizável"))

P.append(drop("latam2022-I", "simulação com ciclo de dias da semana; 38/40"))

P.append(keep("latam2022-J", [
    C("reformulação", "Pares com algum ponto no interior nunca bloqueiam; os pares com os dois pontos na borda são "
      "cordas e não podem se entrelaçar ao longo do perímetro.",
      "Fronteira desenrolada: cordas sem cruzamento = parênteses",
      "Ligações dentro de uma região simplesmente conexa (disco, retângulo) só podem se bloquear se ambos os extremos "
      "estão na fronteira. Mapeie cada ponto da fronteira para sua posição no perímetro (ordem cíclica 1D): as cordas "
      "não se cruzam sse os pares formam uma sequência de parênteses bem aninhada, testável com pilha.",
      "conectar pares de pontos sem cruzamento dentro de um polígono/círculo, com pontos na borda",
      ["emparelhar pontos num círculo sem cruzamentos (contagem = Catalan)",
       "grafo exterior-planar: arestas como cordas de um ciclo",
       "família de intervalos que não podem se cruzar parcialmente (laminar), testada com pilha"]),
    N("estrutura/algoritmo", "Ordenar os pontos de borda pela posição no perímetro e checar o aninhamento com uma "
      "pilha."),
], reason="fácil (40/40), mas o mapeamento da fronteira para parênteses é reutilizável"))

P.append(drop("latam2022-K", "conjunto de primeiras letras e verificação direta; 40/40"))

P.append(keep("latam2022-L", [
    C("reformulação", "Fixe quantos pares ficam cheios/meio cheios após a fase dos tranquilos; dado isso, extrovertidos "
      "e introvertidos são determinísticos.",
      "Condicionar na estatística que torna o resto determinístico",
      "Em processos aleatórios em fases, procure uma estatística pequena da fase aleatória (quantos pares cheios, "
      "quantos itens de cada tipo) que, fixada, torna as fases seguintes determinísticas. Então E[X] = Σ_k "
      "P(K = k)·f(k), com P(K = k) por contagem combinatória (fatoriais e inversos).",
      "valor esperado de processo em várias etapas onde só a primeira tem regra aleatória complicada; resposta mod "
      "primo",
      ["número esperado de componentes após um sorteio inicial seguido de regra fixa",
       "probabilidades em permutações aleatórias condicionando no número de pontos fixos/ciclos",
       "jogos em que, após um sorteio inicial, a estratégia ótima é determinada"]),
    A("estrutura/algoritmo", "Probabilidade de cada k por fatoriais e inversos modulares, O(N).", "Binomiais mod p"),
]))

P.append(keep("latam2022-M", [
    A("observação-chave", "Um conjunto de tarefas é viável sse executá-las em ordem de prazo cumpre todos os prazos.",
      "Escalonamento EDF (prazo mais cedo)"),
    C("estrutura/algoritmo", "Posição a posição, escolher o menor índice j que, colocado agora, mantém o resto viável "
      "em EDF.",
      "Menor lexicográfico = escolha mínima + oráculo de viabilidade",
      "Para a solução lexicograficamente menor, construa posição a posição tentando o menor candidato e aceitando-o "
      "se o restante ainda é completável. O problema se reduz a um teste rápido (de preferência incremental) de "
      "viabilidade para 'prefixo fixado + resto livre'.",
      "'imprima a menor (lexicográfica) ordem/sequência válida' ou '*' se impossível",
      ["menor ordenação topológica lexicográfica com restrições extras",
       "menor string lexicográfica que respeita contagens/restrições de vizinhança",
       "menor caminho lexicográfico entre os caminhos mínimos"]),
    N("otimização", "Pôr j na frente atrasa em T_j só as tarefas anteriores a j na ordem EDF: j é viável sse cumpre o "
      "próprio prazo e a folga mínima dessas tarefas é ≥ T_j. O(N²)."),
], reason="fácil (33/40), mas a construção lexicográfica com oráculo de viabilidade é geral"))

# ======================= LATAM 2023 (a)
P.append(drop("latam2023a-A", "modelagem do enunciado + três BFS no grafo reverso por pessoa, sem ideia reutilizável além de BFS; 30/40"))

P.append(keep("latam2023a-B", [
    C("reformulação", "Uma ficha vai para o primeiro jogador i com max_{j≤i}(A_j·x + B_j) > y — condição monótona em i.",
      "Item removido pelo primeiro que o captura = primeiro prefixo que cobre",
      "Se operações em sequência capturam e removem itens, o dono de cada item é o primeiro índice i cujo prefixo de "
      "operações 1..i o captura. A condição é monótona em i (prefixos só ganham operações), o que elimina a interação "
      "entre itens e permite busca binária por item.",
      "jogadores/eventos em ordem que levam todos os itens restantes que satisfazem uma condição",
      ["pintura de intervalos em ordem: a cor final é a da última operação que cobre a célula",
       "primeiro instante em que um ponto fica coberto/conectado",
       "em que momento cada elemento ultrapassa um limiar com atualizações acumuladas"]),
    A("estrutura/algoritmo", "Todas as fichas buscam binariamente juntas, inserindo retas em ordem a cada rodada.",
      "Busca binária paralela"),
    A("estrutura/algoritmo", "Máximo de retas no ponto x.", "Convex hull trick / Li Chao"),
]))

P.append(drop("latam2023a-C", "simulação reversa direta das dobras; 32/40"))
P.append(drop("latam2023a-D", "simulação direta; 40/40"))
P.append(drop("latam2023a-E", "força bruta em buracos pequenos + troca simples para os grandes; 40/40"))

P.append(keep("latam2023a-F", [
    A("reformulação", "DP sobre pares (subárvore do padrão, subárvore do alvo), testando todas as raízes.",
      "DP em árvore"),
    B("estrutura/algoritmo", "can(u, v) é verdadeiro sse os filhos de u se casam injetivamente com filhos de v com "
      "can verdadeiro: um matching por par.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)",
      "Matching como transição de DP em árvore",
      "Para decidir se a subárvore de u (padrão) cabe na de v (alvo), os filhos de u devem ser atribuídos "
      "injetivamente a filhos distintos de v com can(filho, filho) verdadeiro — um matching bipartido por par (u, v). "
      "Como os filhos não têm ordem, não há DP sequencial que resolva.",
      "Filhos diferentes de u precisam ocupar subárvores disjuntas de v, então a única restrição entre eles é a "
      "injetividade, que é exatamente um matching.",
      "embutir/casar árvores não ordenadas (isomorfismo de subárvore, inclusão de árvores) com n ≤ ~100",
      ["isomorfismo de subárvore em árvores não enraizadas (testar raízes)",
       "casar estruturas hierárquicas sem ordem (pastas, expressões comutativas)",
       "DP em que cada filho precisa de um recurso distinto do pai"]),
]))

P.append(keep("latam2023a-G", [
    C("reformulação", "Os pontos válidos são (P1 ⊕ P2)/2, 2P1 ⊕ (−P2) e 2P2 ⊕ (−P1): três convexos.",
      "Existenciais lineares viram soma de Minkowski",
      "'Existe a ∈ A e b ∈ B com p = α·a + β·b' é o mesmo que p ∈ αA ⊕ βB. Para convexos, a soma de Minkowski é convexa, "
      "tem O(|A| + |B|) vértices e se constrói mesclando as arestas por ângulo; a pergunta por ponto vira "
      "ponto-em-polígono-convexo.",
      "dois objetos convexos e 'existe ponto de A e ponto de B tal que...' com relação linear (ponto médio, diferença, "
      "colisão)",
      ["dois polígonos em movimento colidem ⇔ a origem entra em A ⊕ (−B)",
       "espaço de configuração de robô convexo (obstáculo ⊕ −robô)",
       "distância mínima entre convexos = distância da origem a A ⊕ (−B)"]),
    A("estrutura/algoritmo", "Mesclar as arestas dos dois polígonos por ângulo em O(M1 + M2).", "Soma de Minkowski"),
    A("estrutura/algoritmo", "Teste de cada ponto em O(log M).", "Ponto em polígono convexo"),
]))

P.append(keep("latam2023a-H", [
    N("reformulação", "Cada corrida diz que seus participantes ficam na posição W ou pior e que a posição W é de um "
      "deles: o cavalo h só vai para posições ≥ maior W das suas corridas, e a posição W só aceita cavalos presentes "
      "em todas as corridas com vencedor W."),
    A("estrutura/algoritmo", "Matching cavalos → posições permitidas.", "Matching bipartido (Kuhn/Hopcroft-Karp)"),
]))

P.append(drop("latam2023a-I", "alcançabilidade em grafo de grade por força bruta; 40/40"))

P.append(keep("latam2023a-J", [
    B("estrutura/algoritmo", "Varrer o tempo mantendo os corredores ordenados por posição, trocando vizinhos nos O(R²) "
      "cruzamentos; cada foto testa por busca binária se há corredor no seu trecho.",
      "Sweep line",
      "Varredura cinética: a ordem muda só em trocas de vizinhos",
      "Objetos com posição linear no tempo ficam ordenados por posição, e essa ordem só muda quando dois vizinhos se "
      "cruzam. Há no máximo O(n²) cruzamentos, cada um uma troca de adjacentes, então dá para manter a ordem (e uma "
      "segment tree indexada por ela) durante toda a varredura.",
      "Duas retas posição × tempo se cruzam no máximo uma vez; entre eventos a ordem é fixa, e no instante do "
      "cruzamento os dois objetos são adjacentes na ordem.",
      "objetos com velocidade constante e perguntas, em vários instantes, sobre quem está em um trecho",
      ["corredores/carros com velocidades constantes: ultrapassagens e líder em cada instante",
       "retas ordenadas por valor enquanto x varia (arranjo de retas)",
       "pontos em movimento linear e consultas por instante"]),
    N("redução", "Primeiro descartar as fotos que já contêm algum corredor original; só as restantes interessam às "
      "consultas."),
    A("estrutura/algoritmo", "Segunda varredura com os Q corredores hipotéticos: +1 em intervalo da ordem atual para "
      "cada foto restante, com trocas de adjacentes.", "Segment tree"),
]))

P.append(keep("latam2023a-K", [
    C("observação-chave", "t coberturas geram no máximo 2^t combinações, então t ≥ ⌈log2 K⌉; dar à k-ésima célula as "
      "coberturas dos bits de k atinge o limite.",
      "Contagem dá o limite, código binário dá a construção",
      "Com t atributos binários por objeto há no máximo 2^t combinações distintas, logo são necessários ⌈log2 K⌉ "
      "atributos para distinguir K coisas; e o limite é atingido dando ao k-ésimo objeto o conjunto de atributos dos "
      "bits de k.",
      "'número mínimo de testes/cores/rótulos para distinguir K coisas'",
      ["identificar a garrafa envenenada com ⌈log2 n⌉ provadores",
       "perguntas interativas por conjuntos para descobrir um elemento (bit a bit)",
       "rótulos mínimos para distinguir vértices/arestas"]),
    C("estrutura/algoritmo", "Uma região em pente que recebe todas as coberturas liga as células numeradas e torna cada "
      "cobertura conexa.",
      "Pente: espinha comum garante conexidade",
      "Em construções em grade em que cada rótulo deve formar região conexa, reserve uma espinha (linha/coluna) que "
      "recebe todos os rótulos e dentes que saem dela; cada célula encostada num dente conecta todas as suas regiões "
      "de uma vez.",
      "construir numa grade várias regiões que devem ser conexas e coexistir/sobrepor-se",
      ["desenhar duas ou mais regiões conexas entrelaçadas numa grade",
       "construir labirinto em grade com componentes prescritas",
       "colorir a grade com k cores, cada cor conexa com área dada"]),
]))

P.append(keep("latam2023a-L", [
    c_hereditary("observação-chave", "Um pedaço imprimível é um trecho com período ≤ D, e trechos de um pedaço "
                 "imprimível também o são: pegue sempre o maior prefixo imprimível."),
    B("estrutura/algoritmo", "Função prefixo a partir do início do pedaço, parando quando o menor período passa de D.",
      "KMP",
      "Menor período de cada prefixo pela função prefixo",
      "O menor período de s[0..i] é (i + 1) − π[i], e ele é não decrescente quando o prefixo cresce; rodando a função "
      "prefixo a partir do início do pedaço e parando no primeiro i com período > D, o maior prefixo válido sai em "
      "tempo linear no seu tamanho (O(N) no total).",
      "p é período de s[0..i] sse s tem borda de tamanho i + 1 − p; a maior borda dá o menor período; e um período de "
      "um prefixo maior também é período dos menores, por isso o menor período não diminui.",
      "string formada repetindo um bloco de tamanho ≤ D; 'menor bloco que gera o prefixo'",
      ["menor t tal que s = t^k (ou prefixo de t^∞)",
       "quantas vezes cada prefixo é uma potência",
       "maior prefixo com período ≤ D a partir de cada posição"]),
]))

P.append(drop("latam2023a-M", "BFS direta em estados (linha, rotação); 40/40"))

# ======================= LATAM 2023 (b)
P.append(keep("latam2023b-A", [
    B("estrutura/algoritmo", "Cada cliente é uma função sobre o índice do fornecedor; duas se cruzam no máximo uma vez, "
      "então vão para uma Li Chao sobre [1, N].",
      "Convex hull trick / Li Chao",
      "Li Chao para funções que se cruzam no máximo uma vez",
      "A Li Chao não exige retas: inserção e máximo pontual em O(log n) funcionam para qualquer família em que duas "
      "funções se cruzam no máximo uma vez no domínio — inclusive funções discretas sobre índices, como "
      "(R − P_i)(E − S_i + 1) com P decrescente e S crescente.",
      "Em cada nó, a função que perde no ponto médio só pode vencer em uma das metades (há no máximo uma troca de "
      "liderança), então só ela desce, exatamente como com retas.",
      "maximizar sobre um conjunto dinâmico uma expressão não linear (produto, área) em consultas pontuais, quando a "
      "comparação entre dois candidatos troca no máximo uma vez",
      ["maximizar a área (b − a)(d − c) de retângulos entre pontos dominantes",
       "parábolas transladadas (x − a)² + b, que diferem por funções lineares",
       "Li Chao com segmentos/funções definidas por partes"],
      known=["ICPC WF 2017 — Money for Nothing"]),
    N("otimização", "Tratar com cuidado as regiões em que o lucro é ≤ 0 (cliente não serve àquele fornecedor), para "
      "manter a propriedade de um só cruzamento."),
]))

P.append(drop("latam2023b-B", "jogo resolvido por estratégia de cópia e frequências múltiplas de 3; 40/40"))

P.append(keep("latam2023b-C", [
    C("reformulação", "O bloco é válido sse a diferença dos vetores de frequência de prefixo é múltipla de (1,…,1): "
      "normalize subtraindo 1 de tudo quando todos são ≥ 1.",
      "Frequências iguais ⇔ vetores de prefixo iguais após normalizar",
      "Um subarray tem todas as K frequências iguais sse a diferença dos vetores de contagem de prefixo é múltipla de "
      "(1,…,1). Normalize cada vetor (subtraia o mínimo ou a primeira coordenada) e procure pares de prefixos com a "
      "mesma chave; o subarray mais longo é a distância entre a primeira e a última ocorrência da chave.",
      "subarray mais longo ou número de subarrays com a 'mesma quantidade de cada tipo'",
      ["mesmo número de 0s e 1s (K = 2: soma de prefixo com ±1)",
       "substrings com mesma quantidade de a, b, c (chave (a − b, a − c))",
       "subarrays em que cada valor aparece múltiplo de 3 vezes (chave = contagens mod 3)"]),
    B("otimização", "Hash polinomial do vetor normalizado mantido em O(1) por passo.",
      "Hashing de strings",
      "Hash polinomial de vetor de contagens atualizado em O(1)",
      "O hash Σ b^i·cnt_i é linear: incrementar cnt_i soma b^i e subtrair 1 de todas as coordenadas subtrai Σ b^i. "
      "Assim o hash do vetor normalizado é mantido em O(1) por passo, sem reler as K coordenadas.",
      "Pela linearidade, a variação do hash depende só da variação do vetor, não do vetor inteiro.",
      "comparar/agrupar vetores grandes (K até ~1e5) que mudam em uma coordenada por passo",
      ["hash de multiconjunto (soma de aleatórios por valor) para testar se dois subarrays são permutações",
       "hash do estado de muitos contadores numa DP/BFS",
       "subarrays em que cada valor aparece um número par de vezes (XOR de aleatórios)"]),
    N("otimização", "A normalização custa O(K) e só acontece quando todas as contagens são ≥ 1, no máximo N/K vezes: "
      "O(N) amortizado."),
]))

P.append(drop("latam2023b-D", "simulação/força bruta; 40/40"))

P.append(keep("latam2023b-E", [
    C("observação-chave", "Agrupe vértices em blocos visitados consecutivamente e compare blocos pela média; o bloco de "
      "maior média se funde ao pai.",
      "Troca por razão: blocos se fundem ao pai em ordem de média",
      "Com objetivo Σ posição × peso e precedência em árvore, compare blocos consecutivos pela média (soma/tamanho): sem "
      "restrições, ordenar por média é ótimo (troca adjacente); com precedência, o bloco de maior média deve vir logo "
      "depois do pai, então funda-o ao pai e repita. Guarde (tamanho, soma, soma ponderada) por bloco.",
      "ordem de visita/execução com 'pai antes do filho' e custo que depende da posição na ordem (tempo de conclusão "
      "ponderado)",
      ["escalonamento minimizando Σ w_i·C_i (regra de Smith: ordenar por w/t)",
       "pintar nós de árvore com custo tempo × peso",
       "ordem de concatenação de blocos minimizando custo comparando por razão"],
      ["POJ 2054 — Color a Tree"]),
    A("estrutura/algoritmo", "Mesclar as listas de blocos dos filhos (ordenadas por média) e fundir a raiz com o último "
      "bloco enquanto ela o supera.", "Small-to-large"),
]))

P.append(keep("latam2023b-F", [
    C("observação-chave", "Palíndromo com ≥ 3 dígitos exige b ≤ √N (teste direto); com 2 dígitos, N = d(b + 1) com "
      "d < b, então enumere os divisores d pequenos.",
      "Divisão em √N: parâmetro pequeno por força bruta, grande degenera",
      "Se um parâmetro b vai até N, separe: para b ≤ √N enumere diretamente; para b > √N a estrutura degenera (no máximo "
      "2 dígitos, quociente N/b < √N, poucos múltiplos) e o caso grande se resolve enumerando a outra variável, que é "
      "pequena (o dígito/quociente).",
      "N até 1e12 ou mais com um parâmetro livre até N (base, divisor, tamanho de bloco)",
      ["Σ ⌊N/i⌋ em O(√N): os quocientes distintos são O(√N)",
       "N é potência perfeita / tem forma especial em alguma base",
       "consultas com passo k: k ≤ √N pré-computado, k > √N por força bruta"]),
], reason="fácil (40/40), mas é um exemplo limpo da divisão pequeno/grande em √N"))

P.append(keep("latam2023b-G", [
    A("reformulação", "Cada círculo de Manhattan vira a borda de um quadrado alinhado aos eixos.",
      "Rotação 45° (Manhattan → Chebyshev)"),
    A("estrutura/algoritmo", "Manter o conjunto candidato como poucos segmentos/pontos e intersectá-lo com os 4 lados de "
      "cada novo quadrado; respeitar a paridade ao voltar para (x, y).", "Interseção de segmentos"),
]))

P.append(keep("latam2023b-H", [
    A("reformulação", "Busca binária no número de paredes (mais paredes só restringem).", "Busca binária na resposta"),
    c_angular("observação-chave", "A região do urso é convexa e contém a origem, então ele alcança distância D sse a "
              "região toca o círculo de raio D; cada reta a distância < D corta um arco aberto, e ele falha sse os "
              "arcos cobrem o círculo."),
    A("estrutura/algoritmo", "Varredura angular dos eventos de arco.", "Sweep line"),
]))

P.append(drop("latam2023b-I", "separar pares dentro da mesma cópia e entre cópias; contagem direta com 26 letras; 40/40"))

P.append(keep("latam2023b-J", [
    B("estrutura/algoritmo", "Em cada centroide, lista por rótulo com mínimos de sufixo de (distância, rótulo); para i, "
      "combinar dist(i, c) + melhor com rótulo > i em todo centroide ancestral c.",
      "Centroid decomposition",
      "Mais próximo com propriedade via centroides ancestrais, sem excluir subárvore",
      "Para 'vértice mais próximo de v que satisfaz P', a resposta é o mínimo sobre centroides ancestrais c de "
      "dist(v, c) + melhor(c), em que melhor(c) olha o componente inteiro de c — não é preciso excluir a subárvore de "
      "onde v veio.",
      "Caminhos por c que voltam à subárvore de v só superestimam (dist(v, c) + dist(c, u) ≥ dist(v, u)), e o "
      "verdadeiro mais próximo é contado exatamente no centroide que primeiro separa v dele.",
      "consultas de distância mínima de um vértice até um conjunto (marcado, de certa cor, com rótulo numa faixa) em "
      "árvore",
      ["vértice marcado mais próximo com marcações online",
       "para cada vértice, o mais próximo de cor diferente",
       "mínimo de dist(v, u) + peso(u) sobre u com rótulo numa faixa"],
      known=["Codeforces 342E — Xenia and Tree"]),
]))

P.append(keep("latam2023b-K", [
    C("observação-chave", "Para K ≥ 25, 1 + 2 + … + K > N: sempre escolher o valor cuja próxima ocorrência é a mais "
      "tardia esgota algum valor e produz uma permutação ausente; só K ≤ 24 precisa de busca.",
      "Limiar de tamanho: grande se resolve por contagem, pequeno por busca exaustiva",
      "Quando um parâmetro K tem limite pequeno mas não minúsculo, procure um argumento de contagem/pombos que "
      "resolva todos os K grandes de uma vez (com uma regra simples de construção) e reserve a busca exponencial "
      "(bitmask) para K abaixo do limiar.",
      "limites como N, K ≤ 300 e pergunta sobre todas as permutações/subconjuntos, que seria exponencial",
      ["Erdős–Szekeres: n > (a − 1)(b − 1) garante subsequência monótona longa",
       "n > 2^k números garantem dois subconjuntos com a mesma soma/xor",
       "grafos com muitas arestas sempre têm a estrutura pedida; só os esparsos/pequenos exigem busca"]),
    B("estrutura/algoritmo", "dp[mask] = max_x next(x, dp[mask ∖ x]); se chega a ∞, a permutação que realiza o máximo "
      "não é subsequência.",
      "DP com bitmask",
      "Encaixe guloso de subsequência como valor da DP",
      "Para 'toda ordem de um conjunto é subsequência?', guarde em dp[mask] a posição mais tardia em que o encaixe "
      "(sempre a próxima ocorrência mais cedo) de alguma ordem de mask termina: dp[mask] = max_x next(x, dp[mask ∖ x]).",
      "Para uma ordem fixa, o encaixe mais cedo é ótimo; next(x, p) é monótona em p, então para o adversário basta "
      "maximizar a posição final de cada máscara, independentemente da ordem interna.",
      "verificar se todas as ordens/permutações de um conjunto pequeno aparecem como subsequência",
      ["menor string que não é subsequência (tabela de próxima ocorrência)",
       "ordem de tarefas que mais atrasa um encaixe guloso numa agenda",
       "pior ordem de pedidos atendidos por uma fila fixa"]),
]))

P.append(keep("latam2023b-L", [
    C("reformulação", "Com letras → 'a' e operadores → '+', ser expressão válida ⇔ sem pares adjacentes proibidos, não "
      "começar/terminar com '+' e parênteses balanceados.",
      "Gramática simples = restrições locais + balanceamento",
      "Para validar ou contar substrings de uma gramática simples de expressões, agrupe os caracteres em classes "
      "(operando, operador, parênteses) e mostre que ser válido equivale a: nenhum par adjacente proibido, extremos "
      "permitidos e parênteses balanceados. As restrições locais cortam a string em trechos independentes; o "
      "balanceamento vira condição sobre somas de prefixo.",
      "contar/verificar substrings que são expressões, listas ou estruturas bem formadas",
      ["contar substrings que são números/identificadores válidos",
       "validar expressões aritméticas sem parser recursivo",
       "subarrays que formam sequências bem formadas de tags abre/fecha"]),
    c_prefix_min("redução", "Dentro de cada trecho, conte pares l, r com P[r] = P[l − 1], extremos válidos e r antes do "
                 "primeiro ponto em que o saldo cai abaixo de P[l − 1]."),
    A("estrutura/algoritmo", "RMQ + busca binária para o primeiro ponto abaixo do saldo inicial.", "Sparse table"),
]))

P.append(keep("latam2023b-M", [
    A("estrutura/algoritmo", "Dijkstra a partir de P; candidatos com dist(V) = 2·dist(G).", "Dijkstra"),
    B("observação-chave", "G está em todo caminho mínimo até V sse a distância aumenta quando G é removido: um segundo "
      "Dijkstra sem G testa todos os candidatos.",
      "Dijkstra",
      "Vértice em todo caminho mínimo",
      "g está em todo caminho mínimo de s a v sse remover g aumenta estritamente dist(s, v); equivalentemente "
      "dist(s, g) + dist(g, v) = dist(s, v) e cnt(s, g)·cnt(g, v) = cnt(s, v) (contagens de caminhos mínimos mod um "
      "primo). Um só Dijkstra sem g testa todos os v de uma vez.",
      "Se algum caminho mínimo evita g, ele sobrevive à remoção e a distância não muda; se todos passam por g, todos "
      "somem. Pela contagem, os caminhos mínimos por g são exatamente cnt(s, g)·cnt(g, v).",
      "'todo caminho mínimo passa por', 'aresta/vértice indispensável', 'ponto de encontro obrigatório'",
      ["arestas que pertencem a todos os caminhos mínimos (contagem dos dois lados)",
       "vértices cujo bloqueio aumenta a distância s–t",
       "dominadores no DAG de caminhos mínimos"]),
], reason="fácil (40/40), mas usa uma propriedade de caminhos mínimos pouco conhecida"))


# ---------------------------------------------------------------- validation + write

def validate(problems):
    errs, warn = [], []
    raw = json.load(open(RAW, encoding="utf-8"))
    want = [p["id"] for p in raw["problems"] if p["contest"] in CONTESTS]
    got = [p["id"] for p in problems]
    if len(got) != len(set(got)):
        errs.append("ids duplicados")
    if set(want) != set(got):
        errs.append("faltando %s / sobrando %s" % (sorted(set(want) - set(got)), sorted(set(got) - set(want))))
    names = set(CANONICAL) | set(NEW_A)
    forb = re.compile("|".join(r"\b%s\b" % re.escape(f) for f in FORBIDDEN), re.I)

    def scan(where, s):
        if isinstance(s, str) and forb.search(s):
            errs.append("%s: rótulo proibido em %r" % (where, s[:60]))

    for p in problems:
        pid = p["id"]
        if not p["keep"]:
            if set(p) != {"id", "keep", "discard_reason"} or not p["discard_reason"]:
                errs.append(pid + ": esquema de descarte")
            scan(pid, p["discard_reason"])
            continue
        if set(p) != {"id", "keep", "keep_reason", "steps"} or not p["steps"]:
            errs.append(pid + ": esquema de mantido")
        scan(pid, p["keep_reason"])
        for i, s in enumerate(p["steps"]):
            w = "%s#%d" % (pid, i)
            if s["kind"] not in KINDS:
                errs.append(w + ": kind " + s["kind"])
            cat = s["cat"]
            base = {"kind", "text", "cat"}
            req = {None: base, "A": base | {"technique"},
                   "B": base | {"base", "name", "property", "why", "signal", "contexts", "specific"},
                   "C": base | {"name", "statement", "signal", "contexts", "known_problems", "specific"}}
            if cat not in req:
                errs.append(w + ": cat %r" % cat)
                continue
            extra = set(s) - req[cat] - ({"known_problems"} if cat == "B" else set())
            if not req[cat] <= set(s) or extra:
                errs.append(w + ": chaves %s" % sorted(set(s) ^ req[cat]))
            for k, v in s.items():
                if k == "kind":
                    continue
                for x in (v if isinstance(v, list) else [v]):
                    scan(w + "." + k, x)
            if cat == "A" and s["technique"] not in names:
                errs.append(w + ": técnica não canônica " + s["technique"])
            if cat == "B" and s["base"] not in names:
                errs.append(w + ": base não canônica " + s["base"])
            if cat in ("B", "C") and not s["specific"] and len(s["contexts"]) < 2:
                errs.append(w + ": menos de 2 contextos")
    return errs, warn


def main():
    errs, _ = validate(P)
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"group": "latam_old", "problems": P}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    kept = [p for p in P if p["keep"]]
    steps = [s for p in kept for s in p["steps"]]
    cnt = {c: sum(1 for s in steps if s["cat"] == c) for c in ("A", "B", "C", None)}
    spec = sum(1 for s in steps if s["cat"] in ("B", "C") and s["specific"])
    used_new = sorted({s["technique"] for s in steps if s["cat"] == "A"} - set(CANONICAL))
    print("ok: %d problemas, %d mantidos, %d descartados" % (len(P), len(kept), len(P) - len(kept)))
    print("passos: A=%d B=%d C=%d null=%d; specific=%d" % (cnt["A"], cnt["B"], cnt["C"], cnt[None], spec))
    print("nomes A novos:", used_new)
    print("->", OUT)


if __name__ == "__main__":
    main()
