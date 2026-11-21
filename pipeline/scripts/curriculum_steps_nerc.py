"""Curriculum v2 decomposition for NERC 2019-2025 -> pipeline/curriculum/steps_nerc.json

Usage (from repo root): python -I pipeline/scripts/curriculum_steps_nerc.py
Data below written from pipeline/raw/nerc.json (summary/idea), difficulty in data/dataset.js and the
official tutorials in pipeline/downloads/nerc/txt/. See pipeline/SPEC.md, section "Curriculum (v2)".
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "curriculum" / "steps_nerc.json"
RAW = ROOT / "raw" / "nerc.json"

CANON_A = {
    "BFS", "BFS 0-1", "DFS", "Dijkstra", "Bellman-Ford", "Floyd-Warshall", "Ordenação topológica",
    "SCC (Tarjan/Kosaraju)", "Pontes e articulações", "Componentes biconexas", "Caminho euleriano",
    "2-SAT", "MST (Kruskal/Prim)", "DSU", "DSU com rollback", "LCA (binary lifting)", "HLD",
    "Centroid decomposition", "Small-to-large", "Euler tour em árvore",
    "Matching bipartido (Kuhn/Hopcroft-Karp)", "Blossom", "Fluxo máximo (Dinic)", "Corte mínimo",
    "Fluxo de custo mínimo", "Segment tree", "Segment tree com lazy", "Segment tree persistente", "BIT",
    "BIT 2D", "Sparse table", "Sqrt decomposition", "Mo's algorithm", "Treap", "Soma de prefixos",
    "Array de diferenças", "Pilha monotônica", "Deque monotônico", "Dois ponteiros",
    "Busca binária na resposta", "Busca ternária", "Meet in the middle", "Backtracking com poda",
    "DP com bitmask", "SOS DP", "DP em dígitos", "DP em árvore", "Rerooting", "DP de intervalos",
    "Mochila", "LIS", "Convex hull trick / Li Chao", "Divide and conquer DP", "Knuth", "Slope trick",
    "Matrix exponentiation", "KMP", "Função Z", "Manacher", "Hashing de strings", "Suffix array + LCP",
    "Suffix automaton", "Aho-Corasick", "Trie", "Crivo de Eratóstenes", "Fatoração", "Euclides estendido",
    "Inverso modular", "CRT", "Exponenciação rápida", "Binomiais mod p", "Inclusão-exclusão", "Möbius",
    "Burnside", "Eliminação gaussiana", "Base XOR", "FFT/NTT", "Valor esperado por linearidade",
    "Sprague-Grundy", "Produto vetorial / orientação", "Convex hull", "Interseção de segmentos",
    "Sweep line", "Ordenação angular", "Rotating calipers", "Shoelace (área)",
    "Rotação 45° (Manhattan → Chebyshev)", "Busca interativa (bisseção)",
}
# New A names introduced by this group (same style as the canonical list).
NEW_A = {
    "Código de Prüfer",
    "Matching máximo em árvore",
    "Pesos multiplicativos (weighted majority)",
    "Análise retrógrada (jogos em grafo)",
    "Inteiros grandes (big integer)",
    "Ponto em polígono convexo (O(log n))",
}

FORBIDDEN = ["construtivo", "ad hoc", "análise de casos", "observação", "greedy", "matemática",
             "implementação"]


def A(kind, text, tech):
    return {"kind": kind, "text": text, "cat": "A", "technique": tech}


def N(kind, text):
    return {"kind": kind, "text": text, "cat": None}


def B(kind, text, base, name, prop, why, signal, contexts, specific=False):
    return {"kind": kind, "text": text, "cat": "B", "base": base, "name": name, "property": prop,
            "why": why, "signal": signal, "contexts": contexts, "specific": specific}


def C(kind, text, name, statement, signal, contexts, known=None, specific=False):
    return {"kind": kind, "text": text, "cat": "C", "name": name, "statement": statement,
            "signal": signal, "contexts": contexts, "known_problems": known or [], "specific": specific}


def D(pid, reason):
    return {"id": pid, "keep": False, "discard_reason": reason}


def K(pid, steps, keep_reason=None):
    return {"id": pid, "keep": True, "keep_reason": keep_reason, "steps": steps}


# Shared insight texts (same name used in more than one problem, to ease consolidation).
BUDGET_NAME = "Ler o limite da construção como dica de estrutura"
BUDGET_ST = ("O limite exato permitido numa construção (n+2 arestas, 24 cores com n ≤ 4·3^7, 2m operações) "
             "costuma se decompor como 'custo base por elemento + poucas exceções' ou 'custo por nível × número "
             "de níveis'. Fatore o número: ele diz quantas exceções caras são toleradas ou qual recursão (fator "
             "de redução por nível) os autores esperam.")
BUDGET_SIG = "limite numérico 'estranho' e justo na saída de uma construção (n+2, 24, 8748 = 4·3^7, 2m−1)"
BUDGET_CTX = ["24 cores e n ≤ 4·3^7 ⇒ recursão dividindo por 3 e gastando 3 cores por nível",
              "n+2 arestas ⇒ n−1 arestas 'normais' + no máximo 3 casos excepcionais",
              "⌈log2 n⌉ + c consultas ⇒ bisseção mais c verificações extras"]

ODD_NAME = "Vértices de grau ímpar contam extremidades abertas"
ODD_ST = ("Se um objeto é união de peças que dão grau par a cada vértice (ciclos, trilhas fechadas) mais peças "
          "'abertas' (pontes, caminhos), todo vértice de grau ímpar é extremidade de alguma peça aberta; logo "
          "#peças abertas ≥ #ímpares/2. Esse limite inferior costuma ser atingível e vira a fórmula da resposta "
          "ou a condição de existência.")
ODD_SIG = ("restrições sobre graus (sequência de graus dada, cobrir arestas por caminhos, ciclos que não podem "
           "compartilhar arestas)")
ODD_CTX = ["número mínimo de trilhas que cobrem todas as arestas de um grafo conexo = #ímpares/2",
           "carteiro chinês: as arestas duplicadas emparelham os vértices de grau ímpar",
           "cobrir uma árvore com o mínimo de caminhos aresta-disjuntos"]

EVENTS_NAME = "Integrar por eventos onde a estrutura discreta é constante"
EVENTS_ST = ("Para integrar ou otimizar uma função de um parâmetro contínuo (ângulo, tempo, nível), encontre os "
             "eventos em que a estrutura discreta muda (quais vértices são de apoio/submersos, qual é o mais "
             "baixo). Entre dois eventos a função tem forma fechada simples (polinômio, combinação de sin/cos, "
             "arco de cônica) e é integrada analiticamente; o total é a soma sobre O(n) intervalos.")
EVENTS_SIG = "média/integral/área ao longo de uma rotação ou movimento contínuo, com resposta real"
EVENTS_CTX = ["largura mínima de polígono via rotating calipers (ótimo só em eventos de vértice)",
              "área de interseção de dois polígonos em movimento ao longo do tempo",
              "área acima da água em função do nível (quadrática por partes)"]

P = []

# ---------------------------------------------------------------- NERC 2019
P.append(K("nerc2019-A", [
    N("observação-chave", "Sempre forjar a espada que termina mais cedo entre os mestres disponíveis é ótimo "
      "(argumento de troca de seleção de atividades)."),
    C("otimização", "A escolha só muda quando um mestre abre ou fecha; entre eventos, produz-se em bloco com "
      "o mestre mais rápido usando divisão.",
      "Simular só nos eventos, pular em bloco entre eles",
      "Se a decisão de uma simulação só muda quando ocorre um evento (abertura/fechamento, chegada, troca de "
      "líder), o comportamento entre dois eventos consecutivos é repetitivo: avance de uma vez com aritmética "
      "(divisão, multiplicação, mod) em vez de passo a passo. O número de iterações passa a ser O(#eventos), "
      "mesmo com tempos até 1e18.",
      "tempos/quantidades até 1e18 numa simulação passo a passo cuja regra depende só de quem está ativo",
      ["subtração repetida tipo Euclides: subtrair b de a muitas vezes = a mod b",
       "fila/máquina que repete o mesmo ciclo até a próxima chegada de cliente",
       "recurso que enche/esvazia com taxa constante entre eventos (calcular o instante do próximo evento)"]),
    A("estrutura/algoritmo", "Eventos ordenados por tempo com multiset dos mestres ativos ordenado por t_i.",
      "Sweep line"),
], keep_reason="Fácil (82% do top-40), mas o salto aritmético entre eventos é um insight C reutilizável."))

P.append(D("nerc2019-B", "Fácil (40/40 do top-40): compressão em blocos e checagem de simetria direta."))

P.append(K("nerc2019-C", [
    N("reformulação", "m = Σd/2 fixa o número de ciclos do cacto: c = m − (n − 1)."),
    C("observação-chave", "Vértice de grau ímpar não pode ter todas as arestas em ciclos; folhas e vértices "
      "ímpares forçam pontes: #pontes ≥ max(#ímpares/2, #folhas).",
      ODD_NAME, ODD_ST, ODD_SIG, ODD_CTX, known=["NERC 2020 — Cactus Not Enough"]),
    C("redução", "Emparelhar os vértices ímpares, contrair as arestas do emparelhamento, resolver o caso "
      "todo-par (triângulos colados) e expandir.",
      "Emparelhar ímpares para cair no caso todo-par",
      "Para construir/percorrer um grafo com graus prescritos, ligue os vértices de grau ímpar em pares com "
      "arestas auxiliares (adicionadas ou contraídas), resolva o caso em que todos os graus são pares (onde "
      "ciclos e trilhas fechadas sempre existem) e depois remova/expanda as auxiliares.",
      "construção ou percurso em que a paridade dos graus separa um caso fácil (todos pares) de um difícil",
      ["caminho euleriano: liga os dois ímpares por uma aresta fictícia e corta o circuito nela",
       "orientar arestas com |in − out| ≤ 1 em todo vértice: vértice fictício ligado aos ímpares",
       "carteiro chinês / Christofides: emparelhamento dos ímpares"]),
    N("estrutura/algoritmo", "Construção indutiva: árvore pendurando folhas no vértice de maior grau; caso par "
      "colando triângulos de dois vértices de grau 2 num vértice de grau ≥ 4."),
]))

P.append(K("nerc2019-D", [
    N("observação-chave", "Todas as arestas que saem de um servidor distribuem o mesmo conjunto; se um servidor "
      "já distribui exatamente o conjunto que outro precisa, uma aresta (com CT ligado) basta."),
    C("observação-chave", "A cobertura com duas arestas só é necessária uma vez por par de features (3 pares), "
      "daí n − 1 + 3 = n + 2.",
      BUDGET_NAME, BUDGET_ST, BUDGET_SIG, BUDGET_CTX, known=["NERC 2019 — Help BerLine"]),
    N("estrutura/algoritmo", "Processo repetido: aresta exata quando possível; senão cobrir um servidor de 2 "
      "features com duas arestas; servidor descoberto no fim ⇒ impossível."),
]))

P.append(D("nerc2019-E", "Fácil (40/40 do top-40, 8 min): fixar o rival e ordenar diferenças é direto."))

P.append(K("nerc2019-F", [
    A("estrutura/algoritmo", "Reconstrução de árvore a partir do código de Prüfer com fila de prioridade.",
      "Código de Prüfer"),
    B("observação-chave", "No código de uma árvore geradora de K_{n,m} há exatamente m−1 rótulos do lado "
      "esquerdo e n−1 do direito; existe resposta sse ka ≤ m−1 e kb ≤ n−1.",
      "Código de Prüfer", "Prüfer de árvores geradoras de K_{n,m}",
      "No código de Prüfer de uma árvore geradora de K_{n,m} aparecem exatamente m−1 rótulos do lado esquerdo "
      "e n−1 do direito, e quaisquer duas sequências com esses tamanhos se intercalam de modo único numa árvore "
      "válida (por isso há n^{m−1}·m^{n−1} árvores).",
      "Cada vértice aparece grau−1 vezes no código; a soma dos graus do lado esquerdo é o número de arestas "
      "n+m−1, logo os esquerdos aparecem (n+m−1)−n = m−1 vezes. Na reconstrução, a folha removida é ligada a um "
      "vértice do lado oposto, o que determina de qual sequência sai o próximo símbolo.",
      "contar/reconstruir árvores rotuladas com restrição de graus ou de bipartição; menção a código de Prüfer",
      ["contar árvores rotuladas com graus prescritos: (n−2)!/Π(d_i−1)!",
       "árvores que completam uma floresta com k componentes de tamanhos s_i: n^{k−2}·Π s_i",
       "árvore uniformemente aleatória gerada por sequência de Prüfer aleatória"]),
]))

P.append(K("nerc2019-G", [
    N("observação-chave", "Depois de comprar uma relíquia pelo preço, nunca mais vale apostar: o resto é "
      "comprado direto, em qualquer ordem."),
    C("reformulação", "Trocar 'comprar uma relíquia escolhida' por 'comprar uma aleatória não possuída' torna "
      "todos os subconjuntos de mesmo tamanho equiprováveis.",
      "Simetrizar trocando escolha livre por escolha aleatória",
      "Se a partir de certo ponto a ordem das ações determinísticas não altera o custo, substitua 'escolher "
      "qual item' por 'escolher um uniforme entre os restantes': a esperança não muda e todos os subconjuntos "
      "de mesmo tamanho ficam equiprováveis. A esperança vira uma soma sobre (tamanho, soma) dos subconjuntos, "
      "contada por uma DP de mochila e dividida por C(n, k).",
      "valor esperado sobre coleção de itens com custos distintos, n ≤ 100, estado natural seria o subconjunto",
      ["esperança de função de um subconjunto aleatório agrupando por (tamanho, soma)",
       "coupon collector com itens que também podem ser comprados",
       "jogos de cartas em que a ordem de revelação é simétrica entre as cartas"]),
    A("estrutura/algoritmo", "f[k][s] = número de subconjuntos de tamanho k e soma s.", "Mochila"),
    N("estrutura/algoritmo", "Para b faltantes de soma S, custo do próximo passo = min(S/b, (n/b + 1)·x/2) "
      "(espera geométrica do sorteio)."),
]))

P.append(K("nerc2019-H", [
    N("observação-chave", "Com 3 frequências qualquer instância de até 4 estações funciona (caso base)."),
    C("redução", "Dividir em trincas, marcar a primeira ativada de cada trinca, resolver recursivamente nos "
      "marcados e usar 3 cores novas nos demais: entre dois marcados ativos há ≤ 4 não marcados.",
      "Recursão em representantes",
      "Escolha um representante por bloco de tamanho c (p.ex. o primeiro a aparecer), resolva o problema "
      "recursivamente só nos representantes e trate os demais com O(1) recursos novos: entre dois "
      "representantes consecutivos sobra uma instância de tamanho limitado, resolvida pelo caso base. Cada "
      "nível divide n por c e custa O(1) recursos, dando O(log n) no total.",
      "recursos (cores, rótulos) em quantidade logarítmica em n; propriedade que deve valer em todo segmento",
      ["coloração 'conflict-free' de intervalos com O(log n) cores (função régua: cor = maior potência de 2)",
       "rótulos por nível de centroid decomposition: entre dois vértices de mesma cor há um de cor menor",
       "estruturas hierárquicas por amostragem (skip list, níveis de representantes)"]),
    C("observação-chave", "24 = 3 cores × 8 níveis e n ≤ 4·3^7 denunciam a recursão por 3.",
      BUDGET_NAME, BUDGET_ST, BUDGET_SIG, BUDGET_CTX, known=["NERC 2019 — DevOps Best Practices"]),
]))

P.append(D("nerc2019-I", "Fácil (82% do top-40): interativo cuja ideia (descartar o menor de dois mínimos de "
           "grupos nunca comparados entre si) é específica deste enunciado."))

P.append(K("nerc2019-J", [
    N("reformulação", "Só as contagens por categoria importam; para s fixo, f cabe em q = ⌈f/s⌉ telas sse "
      "q·(s−1) ≤ f."),
    C("otimização", "s ≤ f_min + 1 e k·f_min ≤ n: testar todo s custa O(n) no total.",
      "Enumerar até o menor grupo: k·min ≤ total",
      "Se o parâmetro enumerado é limitado pelo tamanho do menor de k grupos e cada valor custa O(k) para "
      "avaliar, o total é O(k·min) ≤ O(Σ tamanhos) = O(n). Limitar a enumeração pelo menor elemento transforma "
      "força bruta aparentemente quadrática em linear (mesma família do argumento harmônico).",
      "grupos/categorias com soma ≤ n e um parâmetro global que precisa servir a todos os grupos",
      ["dividir frequências em blocos de tamanho comum: o tamanho do bloco ≤ menor frequência",
       "número de frequências distintas é O(√n) — iterar só sobre elas",
       "iterar múltiplos/divisores: Σ n/d = O(n log n)"]),
], keep_reason="Fácil (40/40), mas o argumento de complexidade k·min ≤ n é um insight C geral."))

P.append(K("nerc2019-K", [
    N("reformulação", "A chave é determinada pela ordem dos restos (sistema de numeração fatorial): contar "
      "ordenações válidas do multiconjunto de restos."),
    C("estrutura/algoritmo", "Colocar os restos do maior para o menor: o valor v tem (posições ≥ v−1) − (já "
      "colocados) opções; dividir pelas multiplicidades.",
      "Contar arranjos do mais restrito para o menos restrito",
      "Se cada elemento só pode ocupar posições de um conjunto e esses conjuntos são encaixados (elemento mais "
      "restrito ⇒ conjunto contido no dos outros), coloque os elementos do mais restrito ao menos restrito: o "
      "número de opções do próximo é |seu conjunto| − (já colocados), independentemente de onde os anteriores "
      "foram. A resposta é o produto (dividindo por multiplicidades de iguais).",
      "contar permutações/atribuições com restrições do tipo 'a_i ≤ b_posição' ou 'valor v só em posição ≥ v'",
      ["contar permutações p com p_i ≤ b_i: ordene b e multiplique (b_(i) − (i−1))",
       "contar pareamentos de dois arrays com a_i < b_par(i)",
       "atribuir pessoas a cadeiras com limite de altura"]),
    N("otimização", "Subtrair as ordenações que terminam em zero (contagem do multiconjunto sem um zero)."),
], keep_reason="Fácil (40/40), mas a contagem 'do mais restrito ao menos' é um padrão C clássico e reutilizável."))

P.append(D("nerc2019-L", "Fácil (40/40 do top-40): preenchimento letra a letra direto."))

# ---------------------------------------------------------------- NERC 2020-21 onsite (nerc2021)
P.append(D("nerc2021-A", "Parsing por descida recursiva + renderização ASCII; a parte difícil é só codificar a "
           "especificação longa."))

P.append(K("nerc2021-B", [
    N("reformulação", "Sem RESET os conjuntos pressionados só crescem: a resposta é uma cobertura do DAG de "
      "inclusão por cadeias disjuntas, cada cadeia custando |último conjunto| + 1."),
    A("redução", "Cobertura por caminhos via matching no grafo bipartido (A_esq → B_dir se A ⊂ B).",
      "Matching bipartido (Kuhn/Hopcroft-Karp)"),
    B("otimização", "Fins de cadeia = vértices esquerdos não casados; maximizar o peso dos casados rodando Kuhn "
      "em ordem decrescente de |conjunto|.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)", "Kuhn em ordem de peso (peso nos vértices)",
      "Se o peso está nos vértices de um lado (não nas arestas), tentar aumentar a partir dos vértices em ordem "
      "decrescente de peso dá o matching de peso máximo; um vértice casado nunca é descasado pelos aumentos "
      "seguintes.",
      "Os conjuntos de vértices de um lado cobríveis por algum matching formam um matroide (transversal); em "
      "matroides o guloso por peso é ótimo, e caminhos aumentantes preservam os vértices já cobertos.",
      "matching ou cobertura por caminhos em que o valor depende só de quais vértices ficam (des)casados",
      ["cobertura de DAG por caminhos com custo associado ao fim de cada caminho",
       "escolher tarefas com lucro, cada uma precisando de uma máquina compatível",
       "atribuir prêmios a pessoas maximizando o valor total dos prêmios atribuídos"]),
    N("estrutura/algoritmo", "Grafo com 2^d vértices e 3^d arestas (enumeração de submáscaras)."),
]))

P.append(K("nerc2021-C", [
    N("observação-chave", "Cacto é forte sse, removidas as arestas de ciclos, cada componente de pontes tem "
      "no máximo uma aresta."),
    A("estrutura/algoritmo", "Separar arestas de ciclos das pontes.", "Pontes e articulações"),
    N("redução", "Cada árvore de pontes é independente: as arestas novas correspondem a caminhos "
      "aresta-disjuntos cuja remoção deixa só um emparelhamento."),
    B("observação-chave", "Cobrir as arestas restantes com caminhos custa #ímpares/2; logo escolha o "
      "emparelhamento que minimiza vértices de grau ímpar.",
      "Caminho euleriano", "Cobertura de arestas por caminhos = #ímpares/2",
      "O número mínimo de caminhos aresta-disjuntos que cobrem todas as arestas de um grafo conexo (com ao "
      "menos uma aresta) é max(1, #vértices de grau ímpar / 2); numa árvore eles se obtêm juntando "
      "extremidades em cada vértice de baixo para cima.",
      "Cada vértice ímpar é extremidade de ao menos um caminho; ligando os ímpares em pares por arestas "
      "fictícias o grafo vira euleriano, e cortar o circuito nas fictícias dá exatamente #ímpares/2 caminhos.",
      "cobrir/remover todas as arestas com o mínimo de caminhos, traços ou 'pinceladas'",
      ["desenhar uma figura com o mínimo de traços sem levantar a caneta",
       "decompor um multigrafo no mínimo de trilhas",
       "mínimo de arestas a adicionar para tornar o grafo euleriano"]),
    A("estrutura/algoritmo", "Emparelhamento máximo entre vértices ímpares da árvore, de baixo para cima.",
      "Matching máximo em árvore"),
]))

P.append(K("nerc2021-D", [
    N("observação-chave", "Descartar pares se d é ímpar e múltiplos de 5 se d ∉ {0, 5}."),
    C("reformulação", "Maximizar o produto = maximizar Σ log a_i.",
      "Produto gigante → soma de logaritmos",
      "Para maximizar ou comparar produtos que estouram qualquer tipo numérico, otimize a soma dos logaritmos: "
      "a ordem é preservada e as transições viram somas. Como só se compara (não se imprime o valor), o erro "
      "de ponto flutuante só importa em empates exatos, que raramente afetam a resposta.",
      "maximizar produto de muitos números (n até 1e5) dentro de uma DP ou caminho",
      ["caminho de probabilidade máxima (produto) via caminho mínimo com pesos −log p",
       "comparar a^b com c^d sem big integer",
       "DP de maior produto de subsequência com restrições"]),
    A("estrutura/algoritmo", "Mochila com estado = último dígito do produto (10 estados) e reconstrução.",
      "Mochila"),
], keep_reason="Fácil (40/40), mas 'produto → soma de logs' é um insight C reutilizável em DPs e grafos."))

P.append(K("nerc2021-E", [
    C("reformulação", "Representar cada sequência por (área, Σx·m, 3·Σy·m) inteiros, que se combinam por "
      "soma na gramática S → (S)S.",
      "Agregar por momentos, não por médias",
      "Médias e centros de massa não se combinam diretamente, mas (massa, Σx·massa, Σy·massa) se combinam por "
      "soma (com deslocamentos em fórmula fechada). Represente cada parte pelos momentos — de preferência "
      "inteiros, multiplicando denominadores — e só divida no fim.",
      "média, centro de massa ou baricentro de uma composição de pedaços; alvo racional exato",
      ["baricentro de polígono somando triângulos ponderados pela área",
       "média/variância de subárvore ou intervalo via (n, Σx, Σx²) em segment tree",
       "média máxima de subarray via busca binária em Σ(a_i − λ)"]),
    C("otimização", "Gerar sequências e guardar só os triplos distintos (~1,4e6 para n = 36).",
      "Deduplicar estados pelo vetor de características",
      "Se a busca exaustiva gera exponencialmente muitos objetos mas a resposta depende só de um vetor pequeno "
      "de características (soma, momentos, resto), guarde por tamanho apenas os vetores distintos alcançáveis: "
      "o número de estados distintos costuma ser polinomial e a busca vira uma DP sobre conjuntos de valores.",
      "n pequeno (≤ 36–40) com objetos combinatórios (parênteses, subconjuntos) e alvo numérico exato",
      ["subset sum com valores grandes porém poucos valores alcançáveis (set/bitset de somas)",
       "contar expressões distintas por valor gerado por uma gramática",
       "BFS em espaço de estados com hash de estados já vistos"]),
    A("estrutura/algoritmo", "Alternativa: metades da sequência com tabela hash dos momentos necessários.",
      "Meet in the middle"),
]))

P.append(K("nerc2021-F", [
    C("observação-chave", "Fixados os dois vértices de apoio A_i, A_j, a borda é um arco de elipse com focos "
      "neles (soma das distâncias constante).",
      "Perímetro fixo com apoio fixo ⇒ arco de elipse",
      "Num conjunto definido por 'perímetro do fecho convexo com um ponto extra ≤ L', enquanto os dois vértices "
      "tangentes não mudam a soma das distâncias do ponto a eles é constante: a borda é arco de elipse com focos "
      "nesses vértices.",
      "área de região definida por comprimento de corda/barbante em volta de polígono convexo",
      ["curva do jardineiro (elipse) em volta de um polígono"], specific=True),
    A("estrutura/algoritmo", "Dois ponteiros nos vértices de apoio ao girar a direção: O(n) arcos.",
      "Rotating calipers"),
    B("estrutura/algoritmo", "Somar a área dos arcos de elipse com a integral de contorno em forma fechada.",
      "Shoelace (área)", "Área por Green com arcos curvos",
      "A fórmula do laço é o caso particular de área = ½∮(x dy − y dx); para contornos formados por arcos "
      "parametrizados (círculos, elipses) some a integral em forma fechada de cada arco, e para segmentos ela "
      "vira o termo do shoelace (x_i y_{i+1} − x_{i+1} y_i)/2.",
      "Teorema de Green com o campo (−y/2, x/2): a integral de contorno é aditiva sobre pedaços da fronteira, "
      "então cada pedaço contribui independentemente.",
      "área de região delimitada por arcos de círculo/elipse ou curva paramétrica",
      ["área da união de círculos somando só os arcos da fronteira",
       "área da interseção de polígono com círculo",
       "área varrida por figura em rotação"]),
    C("estrutura/algoritmo", "Os arcos mudam só quando o ponto fica colinear com uma aresta.",
      EVENTS_NAME, EVENTS_ST, EVENTS_SIG, EVENTS_CTX, known=["NERC 2023 — Innovative Washing Machine"]),
]))

P.append(K("nerc2021-G", [
    C("observação-chave", "Visitar k vértices e voltar custa 2(k−1); não voltar economiza a profundidade do "
      "vértice final, então termine no mais profundo com profundidade ≤ k−1.",
      "Passeio em árvore: 2·arestas menos o trecho final",
      "Um passeio que visita um conjunto conexo de vértices de uma árvore e volta ao início custa 2·(#arestas "
      "do conjunto); se não precisa voltar, economiza exatamente a distância do início ao ponto final. Logo "
      "escolha o ponto final mais distante possível e faça desvios de ida e volta para o resto.",
      "percorrer/visitar vértices de uma árvore pelo menor caminho, sem obrigação de voltar",
      ["visitar todos os vértices de uma árvore começando onde quiser: 2(n−1) − diâmetro",
       "entregar em k cidades de uma árvore a partir da raiz",
       "DP em árvore com dois estados por vértice: 'volta' e 'não volta'"]),
    A("estrutura/algoritmo", "DFS para profundidades e para gerar os desvios.", "DFS"),
], keep_reason="Fácil (39/40), mas a fórmula 2·arestas − trecho final é um insight C muito recorrente."))

P.append(K("nerc2021-H", [
    C("reformulação", "Segmentos dois a dois encaixados ou disjuntos formam uma floresta de contenção "
      "(ordenação + pilha).",
      "Família laminar é uma floresta",
      "Se quaisquer dois intervalos/conjuntos são encaixados ou disjuntos, eles formam uma floresta por inclusão "
      "(pai = menor que contém), construída ordenando por (início, −fim) e usando uma pilha; problemas sobre "
      "eles viram DP em árvore sobre filhos e lacunas entre filhos.",
      "intervalos garantidamente aninhados ou disjuntos; parênteses; chamadas de função",
      ["sequência de parênteses → árvore",
       "intervalos [tin, tout] do Euler tour são laminares",
       "árvore de chamadas a partir de logs de entrada/saída"]),
    A("estrutura/algoritmo", "DP em árvore com estado (segmento, ponta esquerda usada, ponta direita usada, k "
      "subsegmentos a alocar nas lacunas).", "DP em árvore"),
    B("otimização", "k limitado pelo tamanho da subárvore: o merge dos filhos custa O(n²) no total.",
      "DP em árvore", "Merge tipo mochila em árvore é O(n²)",
      "Uma DP em árvore com estado indexado por k ≤ tamanho da subárvore, combinando filhos por laço duplo "
      "limitado pelos tamanhos já acumulados, custa O(n²) no total, não O(n³).",
      "Cada par de vértices (u, v) é contado uma única vez: no merge do LCA deles, quando suas subárvores se "
      "juntam.",
      "DP em árvore com dimensão extra 'quantos escolhidos na subárvore' e n ≤ 2000–5000",
      ["escolher k vértices de uma árvore com custo mínimo e restrições pai/filho",
       "mochila com dependências (só pega o filho se pegar o pai)",
       "contar subconjuntos de tamanho k com propriedade em árvore"]),
]))

P.append(K("nerc2021-I", [
    A("estrutura/algoritmo", "Peso β^(erros) para cada participante; prever 1 com probabilidade igual à fração "
      "ponderada que vota 1.", "Pesos multiplicativos (weighted majority)"),
    B("otimização", "Escolher β ≈ 0,75 para que o limite (b·ln(1/β) + ln n)/(1−β) caiba em 1,3b + 100; "
      "versão determinística falha.",
      "Pesos multiplicativos (weighted majority)", "Calibrar β pelo limite exigido e aleatorizar",
      "A versão aleatorizada garante E[erros] ≤ (b·ln(1/β) + ln n)/(1 − β), onde b é o erro do melhor "
      "especialista; escolhendo β obtém-se qualquer razão c > 1 com termo aditivo O(ln n). A versão "
      "determinística só garante ~2,41·b, insuficiente para c < 2.",
      "O potencial W = Σ pesos é ≥ β^b (peso do melhor) e, a cada passo, cai por um fator (1 − (1−β)·p), onde p "
      "é a probabilidade de errar; tomando log e somando, Σp ≤ (b ln(1/β) + ln n)/(1−β).",
      "online/interativo: desempenho exigido do tipo a·(erros do melhor) + constante com n previsores",
      ["problema dos especialistas / apostas com conselheiros",
       "multiplicative weights para aproximar LP e fluxos",
       "estratégia mista em jogo repetido contra adversário"]),
]))

P.append(K("nerc2021-J", [
    C("observação-chave", "A máscara de um perfil é obtida empurrando todos os blocos à esquerda: cada bloco "
      "perde suas k primeiras células, k = folga total.",
      "Obrigatório = interseção das soluções extremas",
      "Em problemas de encaixar blocos em ordem numa linha, uma célula está em todas as soluções sse está coberta "
      "pelo mesmo bloco tanto na solução mais à esquerda quanto na mais à direita; as duas soluções extremas "
      "resumem o conjunto inteiro de soluções.",
      "pergunta sobre o que é comum/obrigatório a todas as soluções de um posicionamento sequencial",
      ["nonograma linha a linha (método da sobreposição)",
       "quais caracteres são obrigatórios ao casar uma subsequência: casamento mais cedo vs. mais tarde",
       "tarefas com horário forçado em agendamento com janelas ordenadas"]),
    N("redução", "Iterar a folga k (k ≥ 4 reduz-se a k−2), estender blocos da máscara, preencher lacunas com "
      "blocos de tamanho 1 ou 2 que somem da máscara."),
]))

P.append(K("nerc2021-K", [
    C("observação-chave", "Ambas as operações são involuções: a sequência ótima alterna tipos; testar os dois "
      "inícios até o período da composição.",
      "Duas involuções ⇒ só sequências alternadas",
      "Se cada operação é uma involução (aplicar duas vezes desfaz), uma sequência ótima nunca repete a mesma "
      "operação seguida; com duas operações só há duas candidatas (ABAB… e BABA…), e a composição AB é uma "
      "permutação de ordem finita — basta simular até o período e checar.",
      "duas operações de troca/reflexão/inversão e pergunta de número mínimo de operações",
      ["grupo diedral gerado por duas reflexões",
       "dois botões que invertem estados (toggle)",
       "inverter prefixo / inverter tudo alternadamente"]),
], keep_reason="Fácil (40/40), mas o argumento 'involução ⇒ alternância' é um insight C geral."))

# ---------------------------------------------------------------- NERC 2021-22 (April 2022)
P.append(K("nerc2022apr-A", [
    C("observação-chave", "Toda substring que não é RLRL…RL determina sua largura de forma única pela posição do "
      "primeiro 'U' (ou do trecho D/L antes dele).",
      "Grade em ordem linha a linha: largura dedutível de um traço local",
      "Quando uma string descreve uma grade em ordem row-major e há restrições de borda, a primeira ocorrência "
      "de um símbolo 'vertical' fixa a largura; tratar à parte as strings sem essa informação.",
      "contar substrings que são descrições de grades válidas",
      ["mapas de setas em grade lidos linha a linha"], specific=True),
    A("estrutura/algoritmo", "Checar grau de entrada 1 por linha com hash polinomial de arrays indicadores "
      "deslocados.", "Hashing de strings"),
    A("estrutura/algoritmo", "Validar bordas por linha em O(1).", "Soma de prefixos"),
    N("otimização", "Agrupar inícios com mesma largura e mesmo l mod largura para obter O(s√s)."),
]))

P.append(K("nerc2022apr-B", [
    N("observação-chave", "A não-otimalidade de cada tópico é convexa, decrescente e linear-fracionária por "
      "partes no dinheiro extra recebido."),
    C("estrutura/algoritmo", "Combinar os tópicos igualando derivadas (water-filling) e montar a função ótima "
      "total com O(t) pedaços; consultas por busca binária.",
      "Distribuir recurso entre custos convexos: igualar derivadas",
      "Para minimizar Σ f_i(x_i) com Σ x_i = X e f_i convexas, no ótimo todas as f_i que recebem algo têm a "
      "mesma derivada λ. Varra λ (ou faça busca binária nele): para cada λ cada item recebe f_i'^{-1}(λ), e a "
      "função ótima de X pode ser pré-computada por partes para responder muitas consultas de X.",
      "distribuir uma quantidade (dinheiro, tempo, cortes) entre itens independentes com custo convexo; muitas "
      "consultas de X",
      ["alocar k unidades com ganhos marginais decrescentes (heap por ganho marginal)",
       "Aliens trick / relaxação lagrangiana: penalizar λ por unidade",
       "water-filling em capacidade de canais"]),
    N("estrutura/algoritmo", "Pedaços a_i/(x − b_i) ativos se combinam em (Σ√a_i)²/x deslocado."),
]))

P.append(D("nerc2022apr-C", "Fácil (40/40): mediana minimiza soma de distâncias Manhattan — clássico direto."))
P.append(D("nerc2022apr-D", "Fácil (40/40, 8 min): contagem de letras e simulação direta."))

P.append(K("nerc2022apr-E", [
    A("estrutura/algoritmo", "Busca binária do menor máximo possível e, separadamente, do maior mínimo "
      "possível, cada uma com verificação gulosa.", "Busca binária na resposta"),
    C("observação-chave", "Os dois ótimos (menor máximo, maior mínimo) são atingíveis simultaneamente.",
      "Amplitude: otimizar cada extremo separado e checar compatibilidade",
      "Quando o objetivo é (maior − menor), calcule separadamente o menor máximo possível e o maior mínimo "
      "possível (cada um por busca binária + verificação). Se as restrições formam intervalos de posições "
      "viáveis, teste se ambos os limites cabem ao mesmo tempo — quando cabem, a resposta é a diferença e a "
      "construção é uma só.",
      "minimizar maior − menor de comprimentos/cargas numa partição sequencial",
      ["dividir array em k blocos minimizando (maior soma − menor soma)",
       "escolher pontos em intervalos com espaçamento o mais uniforme possível",
       "agendamento minimizando desequilíbrio entre turnos"]),
    C("estrutura/algoritmo", "Para cada corte, intervalo [c_i, d_i] viável para frente; escolha dos cortes de "
      "trás para frente.",
      "Propagar intervalo viável para frente, reconstruir para trás",
      "Se numa cadeia de restrições locais (x_{i+1} − x_i ∈ [lo, hi], x_i ∈ [l_i, r_i]) o conjunto de valores "
      "viáveis de cada variável é sempre um intervalo, propague [c_i, d_i] para frente e reconstrua de trás "
      "para frente escolhendo em cada intervalo um valor compatível com o próximo já escolhido.",
      "sequência de posições/valores com restrições só entre vizinhos e pedido de construção",
      ["alturas com diferença limitada entre vizinhos e faixa permitida por posição",
       "escolher instantes em janelas com espaçamento mínimo e máximo",
       "DP de alcançabilidade em que o conjunto alcançável é sempre um intervalo"]),
], keep_reason="Fácil (72% do top-40) no limite; dois insights C (amplitude por extremos e reconstrução por "
   "intervalos) reutilizáveis."))

P.append(K("nerc2022apr-F", [
    C("estrutura/algoritmo", "Processar blocos do maior para o menor; o menor pode ir em qualquer fenda livre "
      "entre grandes já postos, e fendas livres continuam válidas para os menores seguintes.",
      "Inserção em ordem de valor: contar posições, não rastreá-las",
      "Para contar permutações com restrições de comparação entre vizinhos ou posições, insira os elementos em "
      "ordem de valor (do maior para o menor): cada novo elemento é menor que todos os já colocados, então o "
      "número de lugares válidos depende só de contadores (quantos 'grandes', quantos lugares ocupados), e a DP "
      "fica O(n²).",
      "contar permutações com padrão sobe/desce, picos ou posições pares crescentes, n ≤ 5000",
      ["contar permutações alternantes (zigue-zague)",
       "DP de inserção por 'componentes conexas' para montar permutações",
       "contar permutações com exatamente k descidas (números eulerianos)"]),
    N("otimização", "Tamanhos iguais: só o último de cada grupo de iguais pode ser 'grande'."),
], keep_reason="Fácil (95%), mas a DP por inserção em ordem de valor é um padrão C central de contagem."))

P.append(K("nerc2022apr-G", [
    C("reformulação", "Varrer o nível da água de cima para baixo, ativando vértices em altura decrescente e "
      "unindo com vizinhos mais altos via DSU; consultas ordenadas por altura.",
      "Varrer o limiar e unir com DSU",
      "Consultas do tipo 'componente conexa dos elementos com valor ≥ h' ficam fáceis offline: ordene elementos "
      "e consultas pelo limiar decrescente, ative os elementos em ordem, una com DSU e responda cada consulta "
      "no instante certo da varredura.",
      "consultas de conectividade com limiar (nível de água, peso mínimo, tempo), N e Q até 1e5",
      ["ilhas acima da água para vários níveis",
       "pares de vértices cujo caminho tem gargalo ≥ w (árvore de Kruskal)",
       "componentes após apagar arestas em ordem (inverter o tempo)"]),
    A("estrutura/algoritmo", "Unir componentes ao ativar vértices.", "DSU"),
    C("otimização", "A área acima do nível de cada triângulo é quadrática por partes no nível; cada componente "
      "guarda a soma dos coeficientes, atualizados quando um vértice é ultrapassado.",
      "Agregar contribuições como polinômio no parâmetro da varredura",
      "Se a contribuição de cada elemento a uma soma é um polinômio (por partes) no parâmetro da varredura, "
      "mantenha no agregado só a soma dos coeficientes; quando um elemento cruza uma quebra, troque os "
      "coeficientes dele. Cada consulta avalia o polinômio em O(1).",
      "consultas para muitos valores de um parâmetro contínuo somando áreas/comprimentos que variam suavemente",
      ["Σ|x − a_i| para vários x: coeficientes (contagem, soma) em BIT",
       "soma de distâncias com pontos se movendo linearmente no tempo",
       "volume de água em função do nível"]),
]))

P.append(K("nerc2022apr-H", [
    N("reformulação", "Minimizar o dano = intercalar as sequências de mortes de cada grupo maximizando a soma "
      "de somas de prefixos."),
    C("observação-chave", "Quebrar cada sequência em blocos pelo envelope convexo superior das somas de prefixo; "
      "blocos ficam contíguos e são ordenados pela média.",
      "Intercalar cadeias: blocos do envelope convexo ordenados por razão",
      "Ao intercalar várias sequências (cada uma com ordem interna fixa) para otimizar uma soma ponderada de "
      "prefixos, quebre cada sequência em blocos pelo envelope convexo superior das somas de prefixo (razões "
      "decrescentes). No ótimo cada bloco fica contíguo e os blocos de todas as sequências são ordenados por "
      "razão, como na regra de Smith (peso/tempo) para tarefas independentes.",
      "agendar/intercalar cadeias com precedência linear minimizando Σ peso × tempo de conclusão",
      ["regra de Smith: ordenar tarefas independentes por w/t",
       "agendamento com precedência em árvore unindo blocos por razão com heap",
       "derrotar inimigos em ordem minimizando o dano recebido"],
      known=["POJ 2054 — Color a Tree"]),
    B("otimização", "O envelope dos pontos (i, ⌊d·i/hp⌋) tem O(log) segmentos, achados por frações contínuas.",
      "Euclides estendido", "Pontos sob reta racional têm estrutura de frações contínuas",
      "O envelope convexo dos pontos inteiros (i, ⌊a·i/b⌋) tem O(log max(a,b)) vértices, obtidos por um "
      "algoritmo do tipo Euclides; o mesmo princípio calcula Σ⌊(a·i + c)/b⌋ em O(log).",
      "Cada passo de Euclides troca (a, b) por (b, a mod b), o que corresponde a uma transformação unimodular "
      "da reta; os vértices do envelope são os convergentes da fração a/b, que são O(log).",
      "somas ou envelopes envolvendo ⌊a·i/b⌋ com i até 1e9 ou mais",
      ["floor_sum (Σ⌊(a·i+b)/m⌋) da AtCoder Library",
       "melhor aproximação racional p/q com q ≤ N (Stern–Brocot)",
       "contar pontos inteiros sob uma reta"]),
]))

P.append(D("nerc2022apr-I", "Fácil (40/40): quatro consultas Manhattan nos cantos separam coordenadas — direto."))

P.append(K("nerc2022apr-J", [
    A("estrutura/algoritmo", "a[i][j] = min sobre a raiz k, como na BST ótima.", "DP de intervalos"),
    C("reformulação", "A aresta de k para a subárvore [i, k−1] é paga por todo par com exatamente um extremo "
      "em [i, k−1].",
      "Soma de distâncias = soma por aresta dos pares que ela separa",
      "Para custos Σ c_ij·dist(i, j) numa árvore, troque a ordem da soma: cada aresta paga c de todos os pares "
      "que ela separa. O custo fica local (subárvore × resto), calculável em O(1) com somas de prefixos 2D, e "
      "a DP sobre a árvore só precisa do corte de cada aresta.",
      "somar/minimizar distâncias entre todos os pares numa árvore dada ou construída",
      ["soma das distâncias entre todos os pares: Σ size·(n − size) por aresta",
       "quantos caminhos de um conjunto passam por cada aresta",
       "custo de comunicação ao escolher a posição de um servidor numa árvore"]),
    A("otimização", "Peso do corte [i, k−1] × fora em O(1).", "Soma de prefixos"),
], keep_reason="Fácil (40/40), mas a troca de ordem 'distância → pares por aresta' é um insight C central."))

P.append(K("nerc2022apr-K", [
    B("redução", "Duplicar cada vértice (v1, v2) e cada aresta em u1–v2 e u2–v1; A = ST, B = TS, C = SS.",
      "Corte mínimo", "Duplicar vértices para ter 3–4 estados num corte",
      "Representando cada vértice por duas cópias, cada uma no lado S ou T, obtêm-se quatro estados por vértice "
      "(SS, ST, TS, TT); com arestas cruzadas u1–v2 e u2–v1 o custo do corte reproduz matrizes de custo entre "
      "três grupos que um corte simples (dois estados) não expressa.",
      "O custo do corte entre as cópias é submodular em cada par; a simetria das arestas cruzadas faz o corte "
      "calcular exatamente a matriz pedida, e o estado excedente (TT) pode ser trocado por SS sem aumentar o "
      "custo.",
      "partição em 3 grupos (A, B, C) com custos por par de grupos e terminais fixos",
      ["rotular vértices com k valores ordenados e custo convexo (cadeia de cópias por valor)",
       "max-cut em grafo bipartido invertendo o lado de uma das partes",
       "seleção de projetos com mais de duas opções por item"]),
    A("estrutura/algoritmo", "Forçar a em ST e b em TS com arestas infinitas e rodar Dinic.",
      "Fluxo máximo (Dinic)"),
]))

P.append(K("nerc2022apr-L", [
    C("observação-chave", "Rotular cada vértice pelo filho de s em cuja subárvore DFS ele está; uma aresta "
      "chegando de outro rótulo dá os dois caminhos.",
      "Rotular vértices pelo ramo da raiz",
      "Para achar dois caminhos disjuntos a partir de s (ou um ciclo passando por s), faça DFS/BFS de s e "
      "rotule cada vértice pelo filho de s cujo ramo o contém; uma aresta entre vértices de rótulos diferentes "
      "junta dois ramos distintos e dá dois caminhos internamente disjuntos.",
      "dois caminhos disjuntos a partir de uma fonte; ciclo pela origem; pares em subárvores distintas da raiz",
      ["menor ciclo passando por um vértice: BFS rotulada pelo primeiro vizinho",
       "centroid decomposition: caminhos pela raiz combinam vértices de subárvores-filhas distintas",
       "segundo melhor caminho com primeiro passo diferente"]),
    A("estrutura/algoritmo", "Árvore DFS a partir de s.", "DFS"),
], keep_reason="Fácil (40/40), mas o rótulo 'ramo da raiz' é um insight C transferível."))

# ---------------------------------------------------------------- NERC 2022-23 (Dec 2022)
P.append(K("nerc2022dec-A", [
    N("observação-chave", "Escolhida q, a permutação p fica forçada pela equação a[p[q[i]]] = i."),
    C("estrutura/algoritmo", "Sortear q, calcular p e repetir até p também não ter pontos fixos; n ≤ 4 por "
      "força bruta.",
      "Sortear uma parte, forçar o resto, repetir",
      "Se escolher uma parte da solução determina o resto e uma escolha aleatória dá certo com probabilidade "
      "constante (p.ex. ~1/e para 'sem pontos fixos'), sorteie e verifique em O(n), repetindo; trate por força "
      "bruta só os n pequenos onde a probabilidade cai ou é zero.",
      "construir permutações com restrições locais fracas (sem ponto fixo, p_i ≠ a_i) e n grande",
      ["desarranjo aleatório: sucesso com probabilidade ~1/e por tentativa",
       "atribuição que evita poucos conflitos por elemento (embaralhar e checar)",
       "hash/semente aleatória até não haver colisão"]),
], keep_reason="Fácil (40/40), mas 'sortear, forçar e repetir' é um insight C útil em construções."))

P.append(K("nerc2022dec-B", [
    C("observação-chave", "Para a raiz verdadeira, o conjunto de vértices antes dela num percurso só assume 2 "
      "valores; para outros vértices, ≥ 4 com alta probabilidade.",
      "Estatística que só é constante para o elemento procurado",
      "Com muitas amostras aleatórias de uma estrutura escondida, procure uma estatística que tenha pouquíssimos "
      "valores possíveis só para o elemento procurado (raiz, centro, líder) e conte os valores distintos nas "
      "amostras; os demais candidatos variam com alta probabilidade.",
      "k ≥ 50 observações aleatórias de um objeto escondido e pedido de reconstrução",
      ["reconstruir árvore a partir de várias ordens DFS aleatórias",
       "achar o elemento fixo de várias permutações aleatórias parciais",
       "identificar o líder por frequência em amostras"]),
    B("estrutura/algoritmo", "Comparar conjuntos de prefixos via soma de valores aleatórios por vértice com "
      "somas de prefixos.",
      "Hashing de strings", "Hash de conjunto por soma de valores aleatórios",
      "Atribuindo um número aleatório de 64 bits a cada elemento, o hash de um conjunto é a soma (ou XOR) dos "
      "valores; subarrays comparam-se como conjuntos em O(1) usando somas de prefixos.",
      "A soma é comutativa (ignora a ordem) e, com valores aleatórios, dois conjuntos distintos colidem com "
      "probabilidade ~2^-64 por comparação.",
      "comparar conjuntos/multiconjuntos de subarrays ou subárvores independentemente da ordem",
      ["checar se um subarray é permutação de 1..k",
       "contar subarrays em que cada valor aparece múltiplo de 3 vezes (soma de vetores mod 3)",
       "igualdade de multiconjuntos de filhos em árvores"]),
    N("redução", "Removida a raiz, dividir em duas subárvores e recursar."),
], keep_reason="Fácil no limite (75%); hash de conjunto (B) e estatística identificadora (C) são reutilizáveis."))

P.append(K("nerc2022dec-C", [
    A("reformulação", "Substituir cada ciclo por um vértice especial ligado aos seus vértices (árvore de "
      "blocos).", "Componentes biconexas"),
    C("observação-chave", "Análise das classes de homotopia dos ciclos no toro: ≥ 2 classes exige ponto comum "
      "ou um ciclo que cruza todos; uma classe exige ciclos encadeados por caminhos de pontes.",
      "Ciclos não contráteis no toro",
      "Classificar mergulhos de cactos no toro pelas classes de homotopia dos ciclos.",
      "mergulho de grafos em superfícies",
      ["mergulho de cactos no toro"], specific=True),
    A("estrutura/algoritmo", "Checar caminho simples que domina todos os vértices especiais a distância 1.",
      "DFS"),
]))

P.append(K("nerc2022dec-D", [
    A("reformulação", "Ladrilhamento por dominós = matching perfeito no grafo bipartido do tabuleiro.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)"),
    C("observação-chave", "Pares da mesma cor sempre quebram o ladrilhamento: se C(n1,2)+C(n2,2) ≥ 1e6 a "
      "resposta é 1e6; senão há poucas células.",
      "Saída com teto: se a parte fácil estoura, o resto é pequeno",
      "Quando a saída é min(contagem, LIMITE), conte primeiro a parte trivial da contagem; se ela já passa do "
      "limite, pare. Caso contrário a instância é forçosamente pequena (aqui ~2000 células) e cabe um algoritmo "
      "quadrático que seria inviável no pior caso geral.",
      "'imprima min(resposta, 10^6)' ou 'no máximo K' na saída",
      ["listar até K pares/caminhos e parar (enumeração com corte)",
       "pigeonhole: muitos elementos ⇒ resposta garantida, poucos ⇒ força bruta",
       "k-ésimo menor com k ≤ 1e6 via enumeração parcial"]),
    B("estrutura/algoritmo", "Removendo u (preto) e v (branco), existe matching perfeito sse uv ∈ M ou há "
      "caminho alternante do par de v ao par de u; alcançabilidade de todos os vértices por DFS.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)", "Remover dois vértices de um matching perfeito ⇔ caminho "
      "alternante",
      "Dado um matching perfeito M, remover u e v (lados opostos) mantém um matching perfeito sse uv ∈ M ou existe "
      "caminho M-alternante entre os parceiros u' e v'; com o grafo dirigido por M, todos os pares se resolvem "
      "com uma busca de alcançabilidade por vértice.",
      "Os parceiros u' e v' ficam livres; um matching perfeito no restante é M ⊕ (caminho aumentante entre u' "
      "e v'), que é exatamente um caminho alternante em M.",
      "perguntas 'e se removermos/bloquearmos estes vértices' sobre um matching perfeito",
      ["arestas que pertencem a algum/todo matching perfeito (SCC no grafo dirigido por M)",
       "casas cuja remoção mantém um tabuleiro ladrilhável",
       "vértices essenciais de um matching máximo"]),
]))

P.append(D("nerc2022dec-E", "Fácil (40/40, 8 min): contar quebras entre vizinhos não consecutivos é direto."))
P.append(D("nerc2022dec-F", "Fácil (40/40, 5 min): construção direta de placares."))

P.append(K("nerc2022dec-G", [
    C("observação-chave", "Só a primeira pergunta que divide o conjunto atual importa, e todas as perguntas que "
      "o dividem são igualmente prováveis de vir primeiro.",
      "Ignorar passos sem efeito: o próximo passo efetivo é uniforme",
      "Num processo aleatório em que muitos passos não mudam o estado, condicione no próximo passo que muda: "
      "ele é uniforme entre os passos efetivos do estado atual. Isso dá uma recorrência sobre estados sem "
      "depender da ordem completa nem do número de passos inúteis.",
      "eventos em ordem aleatória (permutação) em que alguns são no-op dependendo do estado",
      ["cadeia de Markov com laços: dividir por (1 − p_ficar)",
       "coupon collector: só contam sorteios de itens novos",
       "jogo com cartas embaralhadas em que só a primeira carta relevante importa"]),
    A("estrutura/algoritmo", "f(t) sobre máscaras de jogadores restantes.", "DP com bitmask"),
    B("otimização", "Contar perguntas com t & a_i = s para toda submáscara s ⊆ t com tabela sobre 3^m "
      "máscaras ternárias.",
      "SOS DP", "SOS ternário (máscaras com coringa)",
      "Para contar, para cada t e cada s ⊆ t, quantos a_i têm t & a_i = s, construa g sobre 3^m máscaras "
      "ternárias (0/1/?) com g(..?..) = g(..0..) + g(..1..); cada par (t, s) é uma posição da tabela — "
      "O(3^m·m) no total, em vez de O(3^m·n).",
      "t & a_i = s significa que a_i coincide com s nos bits de t e é livre fora de t ('?'); somar sobre os dois "
      "valores do coringa é a transformada zeta da SOS, só que em base 3.",
      "m ≤ 15–17 e consultas por pares (máscara, submáscara) ou padrões com 'não importa'",
      ["contar strings binárias que casam com padrões com '?'",
       "consultas 'quantos elementos têm bits fixados em certas posições'",
       "probabilidades sobre submáscaras do estado atual"]),
]))

P.append(K("nerc2022dec-H", [
    N("reformulação", "Primeiro descobrir qual frase significa 'mais perto' com poucos movimentos nos cantos."),
    C("estrutura/algoritmo", "Visitar o centro do retângulo candidato e dar um passo unitário para a direita e "
      "outro para cima: cada resposta diz a metade em um eixo.",
      "Passo unitário em comparação de distância revela o lado",
      "Uma resposta 'mais perto/mais longe que a posição anterior' para um passo de 1 unidade num eixo diz de "
      "que lado da mediatriz o alvo está — isto é, em qual metade naquele eixo; com um passo por eixo, cada "
      "rodada faz bisseção 2D.",
      "interativo com respostas comparativas 'mais quente/mais frio' em relação à consulta anterior",
      ["achar pico de array unimodal comparando a[m] com a[m+1]",
       "minimizar função convexa por comparações de vizinhos (bisseção na derivada)",
       "hot/cold em 1D"]),
    A("estrutura/algoritmo", "Bisseção do retângulo até sobrar uma região pequena.",
      "Busca interativa (bisseção)"),
]))

P.append(K("nerc2022dec-I", [
    A("estrutura/algoritmo", "Pré-calcular os dígitos de todos os n! (n ≤ 5982) em base 1e9.",
      "Inteiros grandes (big integer)"),
    C("estrutura/algoritmo", "A cada passo, consultar a posição de dígito que minimiza o maior grupo de "
      "candidatos consistentes; pré-calcular as primeiras consultas.",
      "Árvore de decisão minimax sobre candidatos pré-computados",
      "Com poucas consultas e um universo finito de candidatos que dá para pré-computar, escolha a cada passo a "
      "consulta que minimiza o maior grupo de candidatos ainda consistentes (ou maximiza a entropia); restrinja "
      "as consultas candidatas às mais informativas e calcule offline as primeiras jogadas.",
      "interativo com universo pequeno de respostas (≤ ~10^4), limite de consultas apertado e sem estrutura",
      ["Mastermind / Wordle (minimax de Knuth)",
       "20 perguntas sobre um conjunto conhecido de candidatos",
       "adivinhar objeto com consultas que devolvem um de poucos valores"]),
]))

P.append(K("nerc2022dec-J", [
    B("observação-chave", "Em cada bloco biconexo toda árvore geradora usa (tamanho − 1) arestas: a soma do "
      "bloco é (k−1)·S mod p, o que fixa S.",
      "Componentes biconexas", "Toda árvore geradora usa (tamanho−1) arestas de cada bloco",
      "Em qualquer árvore geradora, o número de arestas dentro de cada componente biconexa é (#vértices do "
      "bloco − 1), qualquer que seja a árvore.",
      "Restrita a um bloco, a árvore geradora é uma árvore geradora do bloco: os blocos se ligam só por "
      "articulações, então a conectividade interna do bloco tem de vir de arestas do próprio bloco.",
      "operações 'some x em todas as arestas de uma árvore geradora' ou invariantes de soma por bloco",
      ["número de árvores geradoras = produto sobre os blocos",
       "posto do matroide gráfico somado por bloco",
       "decidir viabilidade de operações sobre árvores geradoras por invariantes"]),
    A("estrutura/algoritmo", "Resolver (k−1)·S ≡ T_bloco (mod p).", "Inverso modular"),
    C("estrutura/algoritmo", "Transferência: +x numa árvore T1 e −x em T2 = T1 − e1 + e2 move valor de e1 para "
      "e2; mover tudo para cima numa árvore DFS.",
      "Operação local como diferença de duas operações vizinhas",
      "Se as operações permitidas são 'grandes' (afetam um conjunto inteiro), combine duas que diferem "
      "minimamente com sinais opostos para obter uma operação local que só move valor entre dois elementos. "
      "Com essas transferências, concentre tudo num ponto e resolva o resto por um invariante global.",
      "operações que afetam muitos elementos de uma vez e pedido de atingir um alvo exato com poucas operações",
      ["somar em uma linha e subtrair na linha vizinha da grade para mexer em poucas células",
       "trocas entre bases vizinhas de um matroide",
       "comutadores em quebra-cabeças de permutação (A·B·A⁻¹·B⁻¹ mexe poucas peças)"]),
]))

P.append(K("nerc2022dec-K", [
    N("observação-chave", "k = n > 1 é impossível (graus 0 e n−1 não coexistem); k = 1 é um ciclo."),
    C("redução", "G(n, k) a partir de G(n−1, k) pendurando folha no vértice universal, ou de G(n−2, k−2) "
      "adicionando um vértice universal e uma folha.",
      "Indução com invariante sobre os parâmetros (n, k)",
      "Para construir um objeto para todo par (n, k), procure passos que vão de instâncias menores — (n−1, k), "
      "(n−2, k−2) — para (n, k) mantendo um invariante (p.ex. existe vértice universal e há folhas), de modo que "
      "adicionar 1–2 elementos desloque os parâmetros de forma controlada; os casos base pequenos se fazem à mão.",
      "'construa para quaisquer n e k', com n moderado e muitos casos possíveis",
      ["permutação com exatamente k inversões ou k ciclos, construída indutivamente",
       "sequência gráfica via redução de Havel–Hakimi",
       "grafo com exatamente k pontes/componentes"]),
], keep_reason="Fácil (40/40), mas a indução com invariante em (n, k) é um insight C geral de construção."))

P.append(K("nerc2022dec-L", [
    C("observação-chave", "Sempre existe solução ótima em que os elementos alterados viram +∞ ou −∞.",
      "Valores alterados vão para os extremos",
      "Quando se pode trocar elementos por qualquer valor para quebrar padrões de comparação (monotonia, "
      "igualdade), existe solução ótima que usa só valores extremos (+∞/−∞), pois eles quebram o máximo de "
      "padrões; isso reduz a escolha a 3 opções por posição e viabiliza uma DP.",
      "'altere o mínimo de elementos para que não exista padrão de ordem/igualdade', valores livres",
      ["evitar subarray monótono longo alterando elementos",
       "tornar um array zigue-zague com o mínimo de alterações",
       "quebrar triplas a < b < c consecutivas"]),
    C("reformulação", "Escrever o verificador de uma passada (direção, tamanho da sequência monótona, tamanho do "
      "bloco de iguais) e rodar a DP sobre as escolhas com esse estado.",
      "Transformar verificador de uma passada em DP",
      "Escreva primeiro um verificador de uma varredura com estado pequeno para a propriedade proibida; a DP de "
      "'modificar o mínimo' é esse verificador rodando sobre todas as escolhas, com estado da DP = estado do "
      "verificador (+ escolha anterior).",
      "minimizar alterações para que uma propriedade checável em uma varredura não ocorra",
      ["DP sobre autômato KMP/Aho-Corasick para evitar padrões",
       "corrigir string para não ter k caracteres iguais consecutivos",
       "DP em dígitos = verificador de '≤ N' rodando nas escolhas"]),
    C("otimização", "Guardar só o melhor (m, t, s) por (última escolha, direção): O(1) estados por posição.",
      "Descartar estados dominados",
      "Se dois estados da DP no mesmo ponto são comparáveis (um é melhor ou igual em todas as coordenadas que "
      "importam: menos alterações, sequência atual mais curta), descarte o dominado; manter só o melhor por chave "
      "discreta pequena derruba a DP para O(n·estados).",
      "DP com várias coordenadas inteiras em que 'menor é sempre melhor'",
      ["caminho mínimo com recurso guardando só rótulos não dominados",
       "mochila com fronteira de Pareto (custo, peso)",
       "DP de (valor, último) mantendo só o melhor por último"]),
]))

# ---------------------------------------------------------------- NERC 2023
P.append(K("nerc2023-A", [
    C("reformulação", "Cortar cada lista em blocos que terminam assim que a soma fica positiva, com (ganho, "
      "prefixo mínimo exigido); depois sempre aplicar o bloco disponível menos exigente.",
      "Requisito e ganho: blocos até ficar positivo, menor requisito primeiro",
      "Se cada ação exige saldo mínimo r e muda o saldo em g, faça primeiro as de g ≥ 0 em ordem crescente de r "
      "(heap com as disponíveis). Em listas de ordem fixa, agrupe prefixos até a soma ficar positiva: cada bloco "
      "vira um item (requisito, ganho > 0), e blocos que nunca ficam positivos são inúteis.",
      "saldo/energia/HP que não pode ficar negativo, com ganhos e perdas e ordem a escolher",
      ["derrotar monstros com força mínima e ganho de força",
       "escolher projetos com capital mínimo e lucro (IPO)",
       "masmorras em árvore com requisito (fusão de blocos por requisito)"]),
    A("estrutura/algoritmo", "Prefixo mínimo de cada bloco.", "Soma de prefixos"),
], keep_reason="Fácil (40/40), mas o padrão requisito/ganho com blocos é um insight C recorrente."))

P.append(K("nerc2023-B", [
    C("observação-chave", "Custo s(x) = x(x−1)/2 convexo: todas as 2k meias-filas têm tamanho ⌊n/2k⌋ ou ⌈n/2k⌉.",
      "Custo convexo com soma fixa ⇒ partes balanceadas",
      "Minimizar Σ f(t_j) com Σ t_j fixo e f convexa: no ótimo todas as partes têm tamanho ⌊N/k⌋ ou ⌈N/k⌉ "
      "(tirar 1 da maior e pôr na menor nunca piora). Para contar soluções ótimas, conte as maneiras de "
      "distribuir os tamanhos ⌊⌋/⌈⌉ respeitando a estrutura.",
      "dividir N em k partes com custo quadrático/convexo por parte (pares, x(x−1)/2, x²)",
      ["minimizar pares de mesma cor: grupos balanceados (Turán)",
       "distribuir tarefas entre máquinas com custo quadrático",
       "minimizar colisões Σ C(t, 2) em hash/caixas"]),
    A("estrutura/algoritmo", "Contar arranjos dos grupos do meio por número de grupos ímpares com "
      "multinomiais.", "Binomiais mod p"),
], keep_reason="Fácil (95%), mas 'convexo + soma fixa ⇒ balanceado' é um insight C clássico e geral."))

P.append(K("nerc2023-C", [
    N("observação-chave", "Impossível só quando os grafos diferem e o cacto é formado apenas por triângulos sem "
      "pontes."),
    C("redução", "Levar os dois cactos a um 'cacto estrela' canônico em torno do vértice 1 e concatenar a "
      "sequência do primeiro com o reverso da do segundo.",
      "Forma canônica + reversibilidade",
      "Para transformar A em B por operações reversíveis, leve ambos a uma forma canônica C fácil de atingir e "
      "responda (A → C) seguido do reverso de (B → C). A forma canônica não precisa ser ótima, só alcançável "
      "dentro do limite de operações.",
      "transformar um objeto em outro com operações reversíveis e limite folgado de passos",
      ["transformar uma árvore binária em outra por rotações passando pela árvore-caminho",
       "quebra-cabeças de permutação: resolver os dois para a identidade",
       "transformar string em outra com operações inversíveis via forma ordenada"]),
    N("estrutura/algoritmo", "Encurtar ciclos longos por re-cordas, mover pontes e triângulos para o vértice 1 e "
      "corrigir rótulos com gadgets de troca."),
]))

P.append(D("nerc2023-D", "Fácil (40/40): as regras equivalem a b^k ≡ 0, 1 ou −1 (mod n); iterar k é direto."))

P.append(K("nerc2023-E", [
    C("estrutura/algoritmo", "Gadget 'X+X−0' vale 2X lido para frente e 0 lido ao contrário; resposta = "
      "f(p/2) + rev(f(q/2)) após ajustar paridades.",
      "Peças que afetam só uma das exigências",
      "Para satisfazer duas exigências simultâneas sobre o mesmo objeto (duas leituras, duas projeções, dois "
      "restos), construa gadgets que valem algo numa delas e são neutros na outra; a solução é a combinação de "
      "um gadget para cada exigência, mais um ajuste de paridade/caso especial.",
      "construir um único objeto que deve ter dois valores prescritos sob duas leituras/medidas",
      ["teorema chinês do resto: e_i ≡ 1 (mod m_i) e ≡ 0 nos outros módulos",
       "matriz com somas de linhas e colunas prescritas ajustando célula a célula",
       "string com número prescrito de subsequências 'ab' e 'ba'"]),
], keep_reason="Fácil (39/40), mas o desacoplamento por gadgets neutros é um insight C geral de construção."))

P.append(K("nerc2023-F", [
    C("redução", "O jogo se reduz aos estados em que o policial está numa folha: o fugitivo sorteia uma folha e "
      "o policial escolhe uma folha para onde andar.",
      "Perseguição em árvore reduzida a decisões entre folhas",
      "Em perseguição com fugitivo rápido em árvore, os estados relevantes são o policial numa folha.",
      "jogo de perseguição em árvore com estratégias mistas",
      ["policial e ladrão em árvore com fugitivo rápido"], specific=True),
    C("estrutura/algoritmo", "Sistema de equilíbrio x_u = (|L|−1 + Σ dist(u,v)/x_v)/(Σ 1/x_v) resolvido por "
      "iteração de ponto fixo.",
      "Sistema implícito resolvido por iteração de ponto fixo",
      "Quando o valor/equilíbrio é dado por um sistema x = F(x) monótono ou contrativo sem forma fechada, itere "
      "x ← F(x) a partir de um chute razoável até estabilizar; para respostas reais com tolerância, dezenas a "
      "centenas de iterações costumam bastar.",
      "resposta real com tolerância definida por equações implícitas pequenas (≤ ~100 variáveis): jogos, "
      "esperanças com ciclos",
      ["value iteration em MDP / jogo estocástico",
       "esperança com ciclos sem montar eliminação gaussiana",
       "PageRank / distribuição estacionária por potência"]),
]))

P.append(K("nerc2023-G", [
    N("reformulação", "Água = Σ min(prefmax_i, sufmax_i) − Σ a_i."),
    C("observação-chave", "a[l..r] += 1 provoca no máximo um +1 em intervalo contíguo em prefmax (e um em "
      "sufmax).",
      "Atualização em intervalo induz um único intervalo nos máximos de prefixo",
      "Se a[l..r] += 1, o array de máximos de prefixo muda (+1) num único intervalo contíguo: do primeiro índice "
      "em [l, r] que supera max(a[0..l−1]) até antes do primeiro índice à direita de r que já era grande o "
      "bastante. Assim prefmax/sufmax podem ser mantidos com lazy sob atualizações de intervalo.",
      "atualizações de intervalo e consultas que dependem de máximos de prefixo/sufixo (recordes, visibilidade)",
      ["contar recordes (elementos visíveis da esquerda) sob atualizações",
       "manter Σ prefmax sob incrementos de intervalo",
       "água retida sob atualizações"]),
    B("estrutura/algoritmo", "Achar as pontas do intervalo afetado: primeiro índice com valor maior que um "
      "limiar.",
      "Segment tree", "Descida na segment tree",
      "Numa segment tree de máximos, o primeiro índice ≥ l com valor > x é encontrado em O(log n) descendo: em "
      "cada nó, vá para o filho esquerdo se ele cobre a região e tem máximo > x, senão para o direito.",
      "O máximo do nó diz se a resposta existe na subárvore; só O(log n) nós são visitados sem sucesso antes de "
      "descer pelo ramo certo.",
      "'primeiro elemento à direita de l maior que x' com atualizações",
      ["próximo maior elemento com atualizações", "k-ésimo zero/um num array dinâmico",
       "primeiro prefixo com soma ≥ S"]),
    C("otimização", "p_i − q_i é monótono, então {i : p_i < q_i} é um prefixo; a variação de Σ min(p, q) sob "
      "um incremento vira uma contagem.",
      "Min de sequências monótonas opostas troca uma vez",
      "Se p é não-decrescente e q não-crescente, p − q é monótona e {i : p_i < q_i} é um prefixo; logo "
      "Σ min(p, q) = Σ p no prefixo + Σ q no sufixo, e o ponto de troca se acha por busca binária (ou descida "
      "na segment tree).",
      "somas de min/max entre duas sequências monótonas em sentidos opostos",
      ["Σ min(a_i, b_i) com a crescente e b decrescente",
       "custo com dois depósitos nas pontas: cada cliente usa o mais barato, troca uma vez",
       "água retida = Σ min(prefmax, sufmax)"]),
    A("estrutura/algoritmo", "Incrementos de intervalo em prefmax, sufmax e p − q.", "Segment tree com lazy"),
]))

P.append(K("nerc2023-H", [
    C("observação-chave", "Componente fracamente conexa acíclica: k−1 lançamentos em ordem topológica; com "
      "ciclo: k lançamentos, e basta um grande ciclo.",
      "Limite por componente: k−1 por conectividade, +1 se houver ciclo",
      "Em problemas de atender todos os pedidos de um grafo de dependências, trate cada componente fracamente "
      "conexa à parte: são precisas ≥ k−1 operações para ligar k vértices e ≥ k se houver ciclo (alguém tem de "
      "agir antes e depois). Procure construções que atinjam exatamente esses limites.",
      "pedidos/transferências a→b entre n locais e minimizar operações ou movimentos",
      ["ordenar permutação por trocas: n − #ciclos",
       "estacionamento com uma vaga livre: cada ciclo custa um movimento extra",
       "trocar valores de variáveis com dependências cíclicas (precisa de temporário)"]),
    N("redução", "O primeiro lançamento v só quebra os pedidos que saem de v: testar cada v e checar se o resto "
      "é acíclico."),
    A("estrutura/algoritmo", "Checagem de aciclicidade para cada candidato (O(n·m)).", "Ordenação topológica"),
]))

P.append(K("nerc2023-I", [
    B("observação-chave", "A integral, numa volta completa, da projeção mínima dos vértices é −perímetro.",
      "Convex hull", "Fórmula de Cauchy: integral da função suporte = perímetro",
      "Para um polígono convexo, ∫_0^{2π} max_i ⟨v_i, u(θ)⟩ dθ = perímetro; em particular a largura média em "
      "todas as direções é perímetro/π.",
      "Cada vértice é o máximo num arco de ângulos de tamanho igual ao seu ângulo externo; integrar o produto "
      "escalar nesse arco dá a soma das projeções das arestas vizinhas, e somando sobre vértices obtém-se o "
      "perímetro.",
      "média sobre todas as rotações de largura, altura ou projeção extrema de um polígono convexo",
      ["largura média de polígono convexo girando = perímetro/π",
       "agulha de Buffon com figuras convexas",
       "comprimento esperado da sombra de um convexo em direção aleatória"]),
    C("estrutura/algoritmo", "Ângulos em que o conjunto de vértices submersos muda, por dois ponteiros; entre "
      "eventos, integrar sin/cos analiticamente.",
      EVENTS_NAME, EVENTS_ST, EVENTS_SIG, EVENTS_CTX, known=["NERC 2020 — Fiber Shape"]),
    A("estrutura/algoritmo", "Dois ponteiros sobre o polígono com áreas de prefixo por produto vetorial.",
      "Dois ponteiros"),
]))

P.append(K("nerc2023-J", [
    C("estrutura/algoritmo", "Para s = 2, 3: iterar o resíduo de uma variável módulo o coeficiente de outra e "
      "contar o resto por divisão ou soma de PA.",
      "Coeficientes pequenos, alvo enorme: enumerar resíduos",
      "Para contar soluções de Σ c_i·x_i = t (ou ≤ R) com coeficientes pequenos e t enorme, enumere o resíduo "
      "de uma variável módulo o coeficiente de outra (no máximo c valores); para cada resíduo, o restante vira "
      "contagem por divisão inteira ou soma de PA em fórmula fechada.",
      "equação/inequação linear com poucos coeficientes ≤ ~100 e lado direito até 1e9 ou mais",
      ["moedas com valores pequenos e quantia enorme: Dijkstra nos restos módulo a menor moeda",
       "contar pontos inteiros com a·x + b·y ≤ n (floor_sum)",
       "maior quantia não representável (Frobenius) para duas moedas"]),
], keep_reason="Fácil (77%), mas a enumeração por resíduos com fórmula fechada é um insight C geral."))

P.append(D("nerc2023-K", "Fácil (40/40, 10 min): DP direta com estado = paridades dos dois últimos."))
P.append(D("nerc2023-L", "Fácil (40/40, 3 min): força bruta sobre o ponto de corte."))

# ---------------------------------------------------------------- NERC 2024
P.append(K("nerc2024-A", [
    C("observação-chave", "Pares que terminam invertidos ultrapassam exatamente 1 vez, os demais no máximo 2: "
      "limite n(n−1) − inv; construção do último ao primeiro colocado atinge-o.",
      "Limite superior somando o máximo de cada par",
      "Se o processo é feito de eventos entre pares (ultrapassagens, trocas, partidas) e cada par tem um "
      "máximo de eventos determinado pelo estado inicial/final (paridade: 1 se termina invertido, 2 se não), "
      "some esses máximos para obter o limite superior e procure uma construção que esgote cada par — em geral "
      "processando os elementos um a um.",
      "maximizar o número de trocas/eventos entre pares com estado final dado; saída O(n²)",
      ["número de trocas adjacentes para ordenar = número de inversões (cada par 1 vez)",
       "maximizar comparações/trocas em bubble sort-like",
       "torneios: total de jogos limitado por par"]),
], keep_reason="Fácil (40/40), mas 'limite por par + construção que o esgota' é um insight C geral."))

P.append(D("nerc2024-B", "Construção para máquina esotérica (código auto-modificável) específica deste "
           "enunciado; 72% do top-40 resolveram."))

P.append(K("nerc2024-C", [
    C("observação-chave", "Cada vértice de grau par tem metade dos rótulos ímpares; contando por vértice, "
      "#arestas ímpares = |E|/2, logo o número de ciclos ímpares precisa ser par.",
      "Contagem dupla para condição necessária de paridade",
      "Antes de construir, conte a mesma quantidade de dois jeitos (por vértice e no total, como no aperto de "
      "mãos): restrições locais em cada vértice viram uma condição global de paridade/divisibilidade, que "
      "frequentemente é também suficiente.",
      "rótulos/cores em arestas com restrição local em cada vértice e pedido de construção ou 'impossível'",
      ["lema do aperto de mãos: número de vértices de grau ímpar é par",
       "torneio: soma de vitórias = C(n, 2)",
       "coloração de tabuleiro: dominós cobrem uma casa de cada cor"]),
    C("estrutura/algoritmo", "Indução sobre ciclos: escolher rótulos num ciclo com diferenças ±1/±2 de soma zero "
      "e deslocar os rótulos das subcomponentes.",
      "Rótulos intervalares em ciclos por diferenças de soma zero",
      "Rotular arestas de um ciclo com diferenças consecutivas em {±1, ±2} que somam zero, deslocando "
      "subcomponentes penduradas.",
      "coloração intervalar de arestas em cactos",
      ["coloração intervalar de arestas"], specific=True),
]))

P.append(K("nerc2024-D", [
    C("reformulação", "O registrador tem fases falso → verdadeiro → falso; cada resultado observado vira arcos "
      "extras (set-true → set-false → unset-true) no DAG.",
      "Fases de estado viram arestas de precedência",
      "Quando uma ordem precisa reproduzir resultados observados sobre um estado (registrador, pilha, contador), "
      "divida a linha do tempo em fases delimitadas pelos eventos que mudam o estado e traduza cada observação "
      "em 'ocorre entre os eventos X e Y' — arcos extras no grafo de precedência; resolva por ordenação "
      "topológica (ciclo ⇒ impossível).",
      "reconstruir uma ordem de operações compatível com resultados observados e restrições de precedência",
      ["verificar se um histórico de leituras/escritas é linearizável",
       "ordenar eventos de log com relações 'aconteceu antes' inferidas",
       "restrições de agendamento a pares (a antes de b) com recursos de estado"]),
    A("estrutura/algoritmo", "Ordem topológica do DAG aumentado.", "Ordenação topológica"),
], keep_reason="Fácil (40/40), mas modelar fases de estado como precedências é um insight C reutilizável."))

P.append(D("nerc2024-E", "Fácil (40/40): força bruta de movimentos + parsing cuidadoso; só implementação."))
P.append(D("nerc2024-F", "Fácil (40/40, 10 min): varredura com dominós forçados em faixa 2×n."))

P.append(K("nerc2024-G", [
    C("reformulação", "Normalizar o desenho: juntar segmentos colineares sobrepostos/adjacentes por direção, "
      "ordenar e transladar para o menor ponto; testar rotações de 45°, 90°, 180°.",
      "Forma canônica para igualdade a menos de simetria",
      "Para testar se dois objetos são iguais a menos de translação/rotação, normalize-os: funda partes "
      "sobrepostas (segmentos colineares, intervalos), ordene e translade para que o menor ponto vá à origem; a "
      "igualdade vira comparação direta de listas (ou de hashes).",
      "invariância por rotação/translação; figura descrita como união de pedaços possivelmente sobrepostos",
      ["simetria rotacional de polígono via sequência (lado, ângulo) e busca cíclica",
       "isomorfismo de árvores por forma canônica",
       "contar figuras distintas a menos de rotação usando a menor rotação"]),
    N("estrutura/algoritmo", "Coordenadas exatas: rastrear a componente diagonal separadamente para rotacionar "
      "45° sem irracionais."),
]))

P.append(K("nerc2024-H", [
    C("estrutura/algoritmo", "Manter segmentos candidatos com probabilidade a posteriori e bloquear meios dos "
      "segmentos em ordem decrescente de probabilidade.",
      "Bisseção pela massa de probabilidade",
      "Quando as respostas são ruidosas ou o alvo se move aleatoriamente, mantenha a distribuição a posteriori "
      "dos candidatos (atualização bayesiana) e consulte onde a massa de probabilidade se divide ao meio — não "
      "onde o tamanho se divide. Isso supera a bisseção comum em número esperado de consultas.",
      "interativo com alvo que se move aleatoriamente ou respostas que erram com probabilidade conhecida",
      ["busca binária com respostas erradas com probabilidade p (noisy binary search)",
       "adivinhar número com distribuição não uniforme (árvore de Huffman)",
       "localizar falha com testes imperfeitos"]),
]))

P.append(K("nerc2024-I", [
    A("estrutura/algoritmo", "Distâncias até o alvo no grafo reverso; vértices sem caminho são tipo −1.",
      "Dijkstra"),
    C("reformulação", "Tipo de um vértice = maior k de desvios que ele tolera; calcular tipos em camadas "
      "k = 0, 1, 2… a partir dos de nível k−1.",
      "Calcular por níveis de tolerância k = −1, 0, 1, …",
      "Se a resposta é 'o maior número k de falhas/desvios tolerados', defina o tipo de cada estado = maior k "
      "que ele aguenta e calcule os tipos em camadas: os de nível k são obtidos dos de nível k−1 por uma "
      "propagação O(m), e cada vértice é fixado uma vez.",
      "adversário/acaso pode desviar até d vezes; pede o d máximo garantido",
      ["menor caminho com até k arestas que podem falhar (DP em camadas de k)",
       "jogos em que o adversário pode fazer k movimentos especiais",
       "caminho mínimo com até k atalhos (grafo em camadas)"]),
    A("estrutura/algoritmo", "Contagem de arestas boas restantes no DAG de caminhos mínimos para achar os "
      "vértices de cada nível.", "Análise retrógrada (jogos em grafo)"),
]))

P.append(K("nerc2024-J", [
    C("estrutura/algoritmo", "Ordenar tarefas por prazo e calcular de trás para frente o último instante de "
      "início de cada uma; para t, as de início tardio ≥ t vão depois de t e sobra um bloco livre.",
      "Último instante de início por passada reversa",
      "Com tarefas com duração e prazo, ordene por prazo (prazo mais cedo primeiro é ótimo para viabilidade) e "
      "calcule de trás para frente o último instante em que cada tarefa pode começar sem estourar as "
      "seguintes: ls_i = min(d_i, ls_{i+1}) − t_i. Isso diz, para qualquer instante t, o que pode ser adiado e "
      "qual folga contínua existe.",
      "tarefas com duração e prazo + perguntas sobre tempo livre ou ponto de inserção",
      ["caminho crítico de projeto (latest start / folga)",
       "quanto posso atrasar o início mantendo todos os prazos",
       "inserir uma tarefa extra o mais tarde possível"]),
    A("otimização", "Somas de prefixos das durações dos episódios + busca binária.", "Soma de prefixos"),
], keep_reason="Fácil (40/40), mas a passada reversa de 'último início' é um insight C de escalonamento."))

P.append(K("nerc2024-K", [
    A("redução", "Rede: fonte → blocos do professor 1 (capacidade = tamanho), aresta unitária por aluno "
      "candidato nos dois, blocos do professor 2 → sorvedouro.", "Fluxo máximo (Dinic)"),
    B("observação-chave", "Aluno é Y/N forçado se sua aresta está em todo / em nenhum fluxo máximo; checar por "
      "ciclos no residual.",
      "Fluxo máximo (Dinic)", "Aresta em todo / em nenhum fluxo máximo",
      "Com um fluxo máximo F, uma aresta saturada está em todo fluxo máximo sse não existe ciclo no grafo "
      "residual passando por ela (extremos em SCCs diferentes do residual); uma aresta com fluxo 0 está em "
      "algum fluxo máximo sse existe ciclo residual que a contém.",
      "Dois fluxos máximos diferem por uma circulação no residual; o fluxo de uma aresta pode mudar sem mudar o "
      "valor total sse ela está num ciclo residual.",
      "classificar cada elemento como obrigatório / proibido / opcional em todas as soluções de um matching ou "
      "fluxo",
      ["arestas que estão em todo matching máximo",
       "decidir Y/N/? para cada atribuição em problemas de alocação",
       "arestas que podem ser removidas sem diminuir o fluxo"]),
    A("estrutura/algoritmo", "SCC do grafo residual.", "SCC (Tarjan/Kosaraju)"),
]))

P.append(K("nerc2024-L", [
    C("reformulação", "As projeções em x e em y evoluem independentemente, cada uma periódica "
      "(período lcm(2(W−w1), 2(W−w2))).",
      "Separar eixos em movimentos com reflexão",
      "Em movimentos diagonais com reflexão nas paredes (bilhar, logo de DVD), cada coordenada evolui "
      "independentemente e é periódica com período 2·(espaço livre); analise cada eixo sozinho e combine no "
      "fim.",
      "objeto que quica nas paredes movendo-se na diagonal; pergunta sobre longo prazo",
      ["bilhar: desdobrar reflexões numa reta no plano espelhado",
       "logo de DVD: quando bate num canto (CRT nas duas coordenadas)",
       "robôs com movimentos independentes em x e y"]),
    C("estrutura/algoritmo", "Instante τ casa (i, j) sse i ≡ j (mod g = gcd(tx, ty)), e cada par compatível "
      "ocorre igualmente: resposta = Σ_r c_r·d_r / lcm.",
      "Combinar duas sequências periódicas por resíduo mod gcd",
      "Para contar instantes τ em que a[τ mod p] e b[τ mod q] são ambos 1, use o CRT: o par (i, j) ocorre sse "
      "i ≡ j (mod g), g = gcd(p, q), e cada par compatível ocorre exatamente uma vez por lcm(p, q). Agrupe por "
      "resíduo r mod g: fração = Σ_r c_r·d_r / lcm(p, q).",
      "duas propriedades periódicas com períodos diferentes e pergunta sobre a fração/contagem de coincidências",
      ["dois semáforos periódicos: fração do tempo em que ambos estão verdes",
       "calendários cíclicos de períodos diferentes",
       "rodas de dados/engrenagens que coincidem"]),
    A("estrutura/algoritmo", "Correspondência entre (τ mod p, τ mod q) e τ mod lcm.", "CRT"),
]))

P.append(K("nerc2024-M", [
    A("observação-chave", "A resposta é o tamanho do matching máximo da árvore (limite superior atingível).",
      "Matching máximo em árvore"),
    C("redução", "Grafo nos serviços com uma aresta por aresta do matching: grau ≤ 2, logo caminhos e ciclos; "
      "cada ciclo de c arestas se resolve com c−1 trocas espelhadas.",
      "Cada item aparece duas vezes ⇒ grafo de caminhos e ciclos",
      "Quando cada elemento aparece em exatamente (ou no máximo) duas posições/restrições, o grafo que liga as "
      "duas ocorrências tem grau ≤ 2 e se decompõe em caminhos e ciclos; resolva cada caminho/ciclo com um "
      "padrão fixo e some.",
      "cada valor/serviço/carta aparece exatamente duas vezes (duas réplicas, dois lados, pares)",
      ["permutação como união de ciclos: ordenar com n − #ciclos trocas",
       "cartas com dois números: grafo de valores e escolha de um lado por carta",
       "array em que cada valor aparece duas vezes: emparelhar ocorrências por ciclos"]),
]))

# ---------------------------------------------------------------- NERC 2025
P.append(D("nerc2025-A", "Fácil (40/40): reescrever a condição como desigualdade por letra e tomar o máximo de "
           "tetos é direto."))
P.append(D("nerc2025-B", "Fácil (40/40, 7 min): atacar sempre com o máximo + simulação com heaps."))

P.append(K("nerc2025-C", [
    N("observação-chave", "Remover duas arestas do mesmo ciclo desconecta o cacto."),
    C("estrutura/algoritmo", "Baldes 0..15 em que o balde i guarda arestas com i arestas anteriores no ciclo: "
      "G_i = E − balde i é sempre conexo e o predicado Ask(G_i − e) é monótono em i.",
      "Baldes com no máximo um elemento por grupo oculto",
      "Para descobrir grupos ocultos com consultas de conectividade, mantenha baldes com no máximo um elemento "
      "de cada grupo; o predicado 'remover o novo elemento junto com o balde i mantém conectado' é monótono em "
      "i, então a posição do elemento no seu grupo sai por busca binária.",
      "interativo com consultas de conectividade sobre subconjuntos de arestas de um cacto",
      ["classificação de arestas de cacto por consultas"], specific=True),
    A("estrutura/algoritmo", "Busca binária sobre os baldes (4 consultas por aresta, duas passadas).",
      "Busca interativa (bisseção)"),
]))

P.append(D("nerc2025-D", "Fácil (40/40): uma única abertura basta e uma varredura com multiset resolve; ideia "
           "específica do enunciado."))

P.append(K("nerc2025-E", [
    C("reformulação", "Escrever o tempo como Σ|x_{i+1} − x_i| com sinais: 2n sinais + e 2n−1 sinais −, dados "
      "aos maiores e aos menores andares.",
      "Maximizar soma de |diferenças| atribuindo sinais",
      "Uma soma Σ|x_{i+1} − x_i| ao longo de uma ordem é no máximo a melhor atribuição de sinais ± a cada "
      "ocorrência, respeitando quantos + e − existem (cada elemento interno aparece duas vezes, as pontas uma): "
      "dê + aos maiores e − aos menores, e então construa uma ordem que alterne entre o grupo alto e o baixo "
      "para atingir o limite.",
      "maximizar distância total percorrida / soma de diferenças absolutas sobre uma ordem a escolher",
      ["permutação maximizando Σ|p_{i+1} − p_i| (alternar grandes e pequenos)",
       "maximizar Σ|a_i − b_{π(i)}| num pareamento",
       "rota mais longa visitando pontos numa reta"]),
    N("otimização", "Enumerar o andar final entre os destinos e avaliar com somas de prefixos; tratar à parte o "
      "caso em que todas as origens estão abaixo de todos os destinos."),
]))

P.append(K("nerc2025-F", [
    C("observação-chave", "Entregar ao adversário uma pilha > 1 perde: ele escolhe tirar tudo ou deixar 1 e fixa "
      "a paridade; resposta pela paridade de (#pilhas 1 + [max > 1]).",
      "Quem decide entre deixar 0 ou 1 controla a paridade",
      "Em jogos de remoção em que pilhas de tamanho 1 são jogadas forçadas, o jogador que pega a primeira pilha "
      "> 1 pode escolher entre esvaziá-la ou deixar 1 e assim fixar a paridade do restante — ele vence. O "
      "resultado depende só da paridade das jogadas forçadas antes desse momento.",
      "Nim com ordem ou escolha restrita de pilhas; pilhas de tamanho 1 com papel especial",
      ["Nim em que se tira sempre da primeira pilha não vazia",
       "Nim misère (decidido pelas pilhas de 1)",
       "jogos de escada com pilhas unitárias"]),
], keep_reason="Fácil (40/40), mas o controle de paridade por 'deixar 0 ou 1' é um insight C recorrente em jogos."))

P.append(K("nerc2025-G", [
    C("reformulação", "Com b_i = rodadas em que i venceu i+1, a_i = b_i + b_{i−1} num ciclo: n ímpar determina b; "
      "n par deixa um parâmetro δ livre.",
      "Sistema cíclico de somas de vizinhos: paridade de n decide",
      "Num sistema a_i = b_i + b_{i−1} num ciclo, para n ímpar a soma alternada determina b unicamente; para n "
      "par há uma família b + δ·(+1, −1, +1, …) (e a soma alternada de a deve ser 0). Otimize o parâmetro livre "
      "δ dentro do intervalo que mantém b ≥ 0.",
      "valores em ciclo onde cada observação é a soma (ou diferença) de dois vizinhos",
      ["operações '+1 em dois vizinhos' num ciclo",
       "recuperar valores de vértices a partir de somas nas arestas de um ciclo",
       "lâmpadas que afetam vizinhos num anel"]),
    C("observação-chave", "Para b conhecido, mínimo de rodadas = max(max b_i, ⌈Σb/(n−1)⌉).",
      "Limite duplo atingível: max(maior item, ⌈total/capacidade⌉)",
      "Quando em cada rodada cada item pode avançar no máximo uma unidade e há capacidade c por rodada, o "
      "mínimo de rodadas é max(maior demanda individual, ⌈total/c⌉), e esse limite costuma ser atingível "
      "(regra de McNaughton para escalonamento preemptivo).",
      "itens com demandas, cada um servido no máximo uma vez por rodada, capacidade por rodada",
      ["McNaughton: tempo ótimo com preempção = max(max p_j, Σp/m)",
       "dias para consumir pilhas tirando de no máximo c pilhas distintas por dia",
       "jogos em pares em que cada pessoa joga no máximo uma vez por rodada"]),
], keep_reason="Fácil (92%), mas traz dois insights C gerais (sistemas cíclicos e limite duplo de "
   "escalonamento)."))

P.append(D("nerc2025-H", "Fácil (40/40, 4 min): gcd sucessivo por dimensão é direto."))

P.append(K("nerc2025-I", [
    A("estrutura/algoritmo", "Fecho convexo de um conjunto.", "Convex hull"),
    A("estrutura/algoritmo", "Classificar pontos do outro conjunto como dentro/fora do fecho.",
      "Ponto em polígono convexo (O(log n))"),
    N("observação-chave", "Se um conjunto tem pontos dentro e fora do fecho do outro, um cruzamento é garantido."),
    C("redução", "Com todos os pontos de A fora de conv(B), pq cruza conv(B) sse p e q não se 'veem': mapear "
      "cada ponto ao arco angular entre suas tangentes e buscar dois arcos disjuntos.",
      "Visibilidade em torno de convexo vira intervalos angulares",
      "Para pontos fora de um polígono convexo, o que cada um 'vê' (ou bloqueia) é delimitado pelas duas "
      "tangentes ao polígono; mapeie cada ponto a um arco de ângulos e reduza a pergunta geométrica a "
      "interseção/disjunção de intervalos circulares, resolvida por ordenação e varredura.",
      "pontos fora de um obstáculo convexo e perguntas sobre segmentos que o atravessam ou se enxergam",
      ["contar pares de pontos que se veem com um obstáculo convexo entre eles",
       "câmeras/guardas que vigiam um polígono convexo: cobertura de arcos",
       "sombra de um convexo vista de um ponto"]),
    A("estrutura/algoritmo", "Ordenar os arcos e varrer.", "Ordenação angular"),
]))

P.append(K("nerc2025-J", [
    C("reformulação", "Depois de a vitórias e b derrotas, a probabilidade da próxima vitória depende só de "
      "(a, b): p(a,b) = Σp^{a+1}(1−p)^b / Σp^a(1−p)^b.",
      "Estado bayesiano suficiente: contagens de sucessos e fracassos",
      "Com parâmetro desconhecido sorteado de um prior conhecido e observações independentes, a posteriori "
      "depende só das contagens de sucessos e fracassos (não da ordem); use (a, b) como estado da DP e "
      "pré-compute p(a, b) agrupando parâmetros iguais.",
      "máquina/moeda com probabilidade desconhecida escolhida de uma lista, decisões adaptativas",
      ["bandit bayesiano Beta-Bernoulli",
       "moeda viciada escolhida aleatoriamente de um conjunto",
       "probabilidade de sucesso no próximo teste após k sucessos"]),
    C("observação-chave", "O valor é linear no dinheiro: dp(a,b,x) = C[a][b]·x, então a aposta ótima é tudo ou "
      "nada.",
      "Valor linear no recurso ⇒ decisão extremal",
      "Se todos os ganhos são proporcionais ao recurso investido e se maximiza a esperança, a função valor é "
      "linear/homogênea no recurso: V(estado, x) = C(estado)·x. A dimensão x some da DP e a decisão ótima "
      "é sempre um extremo (apostar tudo ou nada), como o ótimo de uma função linear num intervalo.",
      "apostas/investimentos com retorno proporcional ao valor apostado e objetivo = esperança",
      ["maximizar esperança em apostas repetidas: all-in se a vantagem é positiva (diferente de Kelly)",
       "LP: ótimo de função linear está num vértice",
       "DP em que escalar a entrada escala a saída — fatorar o escalar"]),
], keep_reason="Fácil no limite (75%); a linearidade do valor (decisão extremal) é um insight C forte."))

P.append(K("nerc2025-K", [
    C("reformulação", "Rotular cada célula pela paridade de ciclos que a envolvem; um segmento é tricotado sse as "
      "células vizinhas diferem, e cada sapo dá o XOR de seus 4 vizinhos.",
      "Curvas fechadas como paridade dentro/fora nas células",
      "Curvas fechadas disjuntas numa grade são descritas pelas células: rotule cada uma com a paridade de "
      "quantas curvas a envolvem (fora = 0); uma aresta da grade pertence a alguma curva sse as duas células "
      "vizinhas têm rótulos diferentes. Restrições sobre curvas viram restrições XOR locais.",
      "ciclos/curvas sem cruzamento numa grade; perguntas sobre dentro/fora ou arestas usadas",
      ["Slitherlink: decidir dentro/fora de cada célula",
       "ponto dentro de polígono por paridade de cruzamentos",
       "contar regiões delimitadas por fronteiras na grade"]),
    C("redução", "Tudo é determinado pela primeira linha; restrições de quadrados 2×2 viram cláusulas sobre no "
      "máximo duas variáveis da primeira linha.",
      "Fixar a primeira linha e propagar",
      "Se cada célula é determinada por XOR de vizinhas já conhecidas (regra tipo Lights Out), fixe a primeira "
      "linha como variáveis: o resto vira x_j, ¬x_j ou XOR de poucas variáveis, e as restrições restantes viram "
      "equações/cláusulas sobre a primeira linha.",
      "grade com regra local XOR/paridade entre vizinhos e pedido de reconstrução",
      ["Lights Out: escolher a primeira linha determina os demais toques",
       "matriz com XOR prescrito de vizinhos",
       "inverter autômato celular linear (regra 90)"]),
    A("estrutura/algoritmo", "Cláusulas de até duas variáveis resolvidas em O(rc).", "2-SAT"),
]))

P.append(K("nerc2025-L", [
    C("reformulação", "Para k fixo o modelo ótimo é a distribuição empírica: perda = Σ_ctx N log N − "
      "Σ cnt log cnt.",
      "Perda logarítmica ótima é a entropia empírica",
      "Minimizar a log-loss de um modelo de probabilidade condicional livre dá a distribuição empírica; a perda "
      "ótima vira uma soma de termos x·log x sobre contagens, mantida incrementalmente quando grupos se "
      "fundem.",
      "minimizar perda logarítmica/verossimilhança de modelo com parâmetros livres por contexto",
      ["tamanho ótimo de compressão de ordem k (entropia empírica)",
       "máxima verossimilhança de distribuição categórica"]),
    B("estrutura/algoritmo", "Processar k decrescente unindo sufixos adjacentes com DSU quando LCP_i = k, "
      "mantendo contagens de próximos tokens com small-to-large.",
      "Suffix array + LCP", "Classes de k-mers para todo k = DSU sobre o LCP",
      "Os sufixos que compartilham um prefixo de tamanho ≥ k formam intervalos contíguos no suffix array; ao "
      "diminuir k, intervalos vizinhos se fundem exatamente quando LCP_i = k. Processar k decrescente unindo "
      "com DSU percorre todas as classes de equivalência de substrings para todo k (equivale à árvore de "
      "sufixos).",
      "O LCP de dois sufixos é o mínimo do array LCP entre eles; logo 'compartilham ≥ k' particiona o suffix "
      "array em blocos contíguos que só engrossam quando k diminui.",
      "para todo comprimento k, agregar sobre classes de substrings iguais de tamanho k",
      ["contar substrings distintas de cada comprimento",
       "para cada k, quantos pares de sufixos têm LCP ≥ k",
       "substring mais frequente de cada comprimento"]),
    A("estrutura/algoritmo", "Fundir contagens por token ao unir grupos.", "Small-to-large"),
    A("estrutura/algoritmo", "Contextos mais curtos que k são prefixos de texto: trie.", "Trie"),
]))

P.append(D("nerc2025-M", "Fácil (40/40, 7 min): DP linear direta com estado = paridade do prefixo."))


# ---------------------------------------------------------------- validation + output
def validate(problems):
    raw_ids = [p["id"] for p in json.loads(RAW.read_text(encoding="utf-8"))["problems"]]
    ids = [p["id"] for p in problems]
    errs = []
    if sorted(ids) != sorted(raw_ids) or len(ids) != len(set(ids)):
        errs.append(f"ids mismatch: missing {set(raw_ids) - set(ids)}, extra {set(ids) - set(raw_ids)}, "
                    f"dups {len(ids) - len(set(ids))}")
    kinds = {"reformulação", "observação-chave", "redução", "estrutura/algoritmo", "otimização"}
    req = {"A": {"technique"}, "B": {"base", "name", "property", "why", "signal", "contexts", "specific"},
           "C": {"name", "statement", "signal", "contexts", "known_problems", "specific"}, None: set()}
    forb = re.compile(r"\b(" + "|".join(re.escape(w) for w in FORBIDDEN) + r")\b", re.IGNORECASE)
    new_used = set()
    for p in problems:
        if not p["keep"]:
            if not p.get("discard_reason"):
                errs.append(f"{p['id']}: no discard_reason")
            continue
        if not p["steps"]:
            errs.append(f"{p['id']}: kept without steps")
        for s in p["steps"]:
            if s["kind"] not in kinds:
                errs.append(f"{p['id']}: bad kind {s['kind']}")
            if s["cat"] not in req:
                errs.append(f"{p['id']}: bad cat {s['cat']}")
                continue
            missing = req[s["cat"]] - set(s)
            if missing:
                errs.append(f"{p['id']}: missing {missing}")
            if s["cat"] == "A":
                t = s["technique"]
                if t not in CANON_A:
                    if t in NEW_A:
                        new_used.add(t)
                    else:
                        errs.append(f"{p['id']}: unknown A {t}")
            if s["cat"] == "B" and s["base"] not in CANON_A | NEW_A:
                errs.append(f"{p['id']}: unknown B base {s['base']}")
            if s["cat"] in ("B", "C"):
                if not s["specific"] and len(s["contexts"]) < 2:
                    errs.append(f"{p['id']}: <2 contexts on non-specific {s['name']}")
                for fld in ("name",):
                    if forb.search(s[fld]):
                        errs.append(f"{p['id']}: forbidden label in {fld}: {s[fld]}")
            if s["cat"] == "A" and forb.search(s["technique"]):
                errs.append(f"{p['id']}: forbidden label in technique")
    return errs, new_used


def main():
    errs, new_used = validate(P)
    for e in errs:
        print("ERROR", e)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"group": "nerc", "problems": P}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    kept = [p for p in P if p["keep"]]
    cats = {"A": 0, "B": 0, "C": 0, None: 0}
    spec = 0
    for p in kept:
        for s in p["steps"]:
            cats[s["cat"]] += 1
            spec += bool(s.get("specific"))
    print(f"problems {len(P)}  kept {len(kept)}  discarded {len(P) - len(kept)}")
    print(f"steps A {cats['A']}  B {cats['B']}  C {cats['C']}  null {cats[None]}  specific {spec}")
    print("new A names used:", sorted(new_used))
    print("wrote", OUT)
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
