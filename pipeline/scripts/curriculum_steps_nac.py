"""Curriculum v2 — decomposição dos problemas da NAC (2021–2026) em passos A/B/C.

Gera pipeline/curriculum/steps_nac.json (grupo "nac") seguindo SPEC.md, seção "Curriculum (v2)".
Os dados (passos, nomes, enunciados) estão escritos à mão abaixo; o script só monta o JSON,
preenche as contagens dos top-40 nos motivos de descarte e valida o resultado.

Uso: python -I pipeline/scripts/curriculum_steps_nac.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "pipeline", "raw", "nac.json")
DATASET = os.path.join(ROOT, "data", "dataset.js")
OUT = os.path.join(ROOT, "pipeline", "curriculum", "steps_nac.json")

CANON_A = [
    "BFS", "BFS 0-1", "DFS", "Dijkstra", "Bellman-Ford", "Floyd-Warshall", "Ordenação topológica",
    "SCC (Tarjan/Kosaraju)", "Pontes e articulações", "Componentes biconexas", "Caminho euleriano", "2-SAT",
    "MST (Kruskal/Prim)", "DSU", "DSU com rollback", "LCA (binary lifting)", "HLD", "Centroid decomposition",
    "Small-to-large", "Euler tour em árvore", "Matching bipartido (Kuhn/Hopcroft-Karp)", "Blossom",
    "Fluxo máximo (Dinic)", "Corte mínimo", "Fluxo de custo mínimo", "Segment tree", "Segment tree com lazy",
    "Segment tree persistente", "BIT", "BIT 2D", "Sparse table", "Sqrt decomposition", "Mo's algorithm", "Treap",
    "Soma de prefixos", "Array de diferenças", "Pilha monotônica", "Deque monotônico", "Dois ponteiros",
    "Busca binária na resposta", "Busca ternária", "Meet in the middle", "Backtracking com poda", "DP com bitmask",
    "SOS DP", "DP em dígitos", "DP em árvore", "Rerooting", "DP de intervalos", "Mochila", "LIS",
    "Convex hull trick / Li Chao", "Divide and conquer DP", "Knuth", "Slope trick", "Matrix exponentiation",
    "KMP", "Função Z", "Manacher", "Hashing de strings", "Suffix array + LCP", "Suffix automaton", "Aho-Corasick",
    "Trie", "Crivo de Eratóstenes", "Fatoração", "Euclides estendido", "Inverso modular", "CRT",
    "Exponenciação rápida", "Binomiais mod p", "Inclusão-exclusão", "Möbius", "Burnside", "Eliminação gaussiana",
    "Base XOR", "FFT/NTT", "Valor esperado por linearidade", "Sprague-Grundy", "Produto vetorial / orientação",
    "Convex hull", "Interseção de segmentos", "Sweep line", "Ordenação angular", "Rotating calipers",
    "Shoelace (área)", "Rotação 45° (Manhattan → Chebyshev)", "Busca interativa (bisseção)",
]
# Nomes A novos introduzidos por este grupo (mesmo estilo do vocabulário canônico).
NEW_A = [
    "Interseção de semiplanos",
    "Área de interseção círculo-polígono",
    "Bitset",
    "Minimax com memoização",
    "Merge sort tree",
    "LCP de todos os pares (DP O(n²))",
]
FORBIDDEN = ["construtivo", "ad hoc", "análise de casos", "observação", "greedy", "matemática", "implementação"]
KINDS = {"reformulação", "observação-chave", "redução", "estrutura/algoritmo", "otimização"}


# ----------------------------------------------------------------------------- helpers
def A(kind, text, technique):
    return {"kind": kind, "text": text, "cat": "A", "technique": technique}


def B(kind, text, base, name, prop, why, signal, contexts, specific=False, known=None):
    d = {"kind": kind, "text": text, "cat": "B", "base": base, "name": name, "property": prop, "why": why,
         "signal": signal, "contexts": contexts, "specific": specific}
    if known:
        d["known_problems"] = known
    return d


def C(kind, text, name, statement, signal, contexts, specific=False, known=None):
    return {"kind": kind, "text": text, "cat": "C", "name": name, "statement": statement, "signal": signal,
            "contexts": contexts, "known_problems": known or [], "specific": specific}


def N(kind, text):
    return {"kind": kind, "text": text, "cat": None}


def KEEP(steps, reason=None):
    return {"keep": True, "keep_reason": reason, "steps": steps}


def DROP(reason):
    return {"keep": False, "discard_reason": reason}


R, O, D, E, OT = "reformulação", "observação-chave", "redução", "estrutura/algoritmo", "otimização"

P = {}

# ============================================================================= NAC 2021
P["nac2021-A"] = KEEP([
    N(O, "O conjunto é fechado por submáscaras: separando pelo bit i, a parte X (com o bit) é exatamente a parte Y (sem o bit) deslocada de 2^i, restrita a X−2^i ⊆ Y."),
    C(D, "Resolve-se recursivamente {x−2^i : x ∈ X} e Y, e a solução da metade sem o bit é levantada para a metade com o bit, corrigindo os parceiros de Y.",
      "Recursão no bit: tire o bit e resolva a cópia menor",
      "Se um conjunto de máscaras é fechado por submáscaras (ou tem estrutura de hipercubo), escolher um bit i o divide em duas metades em que uma é a outra somada de 2^i; resolva recursivamente a metade sem o bit e 'levante' a resposta para a outra, gastando O(n) por nível e O(n log C) no total.",
      "conjunto de máscaras fechado por submáscaras/supermáscaras; condições como a_i & b_i = 0 ou a_i xor b_i fixo; n até 2^18–2^20",
      ["permutação de 0..2^k−1 maximizando Σ (i xor p_i)", "SOS DP vista como recursão bit a bit sobre o hipercubo",
       "construir caminhos/códigos de Gray no hipercubo"],
      known=["Codeforces 288C — Polo the Penguin and XOR operation"]),
])

P["nac2021-B"] = KEEP([
    B(R, "Em vez de lidar com a união de 3000 círculos, divide-se o plano no diagrama de potência; em cada célula a união coincide com o círculo dono da célula.",
      "Interseção de semiplanos", "Diagrama de potência (Laguerre) para união de círculos",
      "Atribuindo a cada ponto p o círculo de menor potência |p−c|² − r², as células são polígonos convexos e, dentro da célula de um círculo, p está na união de todos os círculos sse está nesse círculo.",
      "Se p está em algum círculo, sua potência em relação a ele é ≤ 0, então a potência mínima (a do dono da célula) também é ≤ 0. Os bissetores de potência são retas porque os termos |p|² se cancelam, logo cada célula é uma interseção de semiplanos.",
      "área/medida da união de muitos discos (n até alguns milhares), consultas sobre a região coberta por círculos",
      ["área da união de círculos", "consultas 'qual disco domina este ponto' (Voronoi ponderado)",
       "decompor a união de discos em pedaços disjuntos para integrar ou amostrar"]),
    A(E, "Cada célula é construída por interseção de O(n) semiplanos, O(n² log n) no total.", "Interseção de semiplanos"),
    A(E, "Cada consulta soma área(célula ∩ círculo ∩ retângulo) com rotina de área polígono convexo ∩ círculo.", "Área de interseção círculo-polígono"),
])

P["nac2021-C"] = DROP("busca binária na resposta + somas de prefixo 2D + BFS + array de diferenças, todos no uso padrão; {top}")
P["nac2021-D"] = DROP("DP de contagem direta indexada pelos dois últimos elementos escolhidos; {top}")

P["nac2021-E"] = KEEP([
    C(R, "Intercalando s1, sn, s2, s(n−1), …, uma divisão em palavras simétrica vira uma decomposição de um prefixo da nova string em palíndromos de tamanho par.",
      "Intercalar extremos: blocos espelhados viram palíndromos pares",
      "Se a condição é que a sequência de blocos s = b1 b2 … bk satisfaça b_i = b_(k+1−i), reescreva t = s1 sn s2 s(n−1) …: cada par de blocos espelhados vira um palíndromo de comprimento par em t, e o problema vira particionar (um prefixo de) t em palíndromos pares — uma DP de partição padrão.",
      "string cortada em pedaços em que o i-ésimo pedaço deve ser igual ao i-ésimo a partir do fim; 'palíndromo de palavras/blocos'",
      ["contar partições s = p1…pk com p_i = p_(k+1−i)", "maior número de blocos numa decomposição em 'palíndromo de blocos'",
       "verificar se s é concatenação simétrica de pedaços com hashing"],
      known=["Codeforces 932G — Palindrome Partition"]),
    N(E, "DP sobre prefixos de t com transições por palíndromos pares, enumerados expandindo a partir de cada centro (O(n²)), com '?' casando com qualquer letra (fator 26 por par livre)."),
])

P["nac2021-F"] = DROP("varredura linear expandindo a partir de cada pico; {top}")

P["nac2021-G"] = KEEP([
    B(O, "O comprimento f(x, s) da expansão do símbolo x após s passos é uma soma de prefixos iterada, logo dado por binomiais.",
      "Soma de prefixos", "Soma de prefixos iterada k vezes = binomiais",
      "Aplicar a operação 'trocar cada valor pela soma do prefixo' k vezes equivale a convoluir com C(i+k−1, k−1); em particular, partindo de um vetor de uns, o x-ésimo valor após k aplicações é C(x+k−1, k).",
      "Cada aplicação de soma de prefixos escolhe um índice ≤ o anterior; k aplicações contam sequências não crescentes de k índices, isto é, multiconjuntos (estrelas e barras).",
      "operação 'substitua pelo prefixo/acumulado' repetida k vezes; tamanhos de expansões recursivas que crescem como polinômio de grau k",
      ["aplicar soma de prefixos k vezes com k grande (mod p)", "contar sequências não decrescentes limitadas",
       "tamanho de expansões em gramáticas/árvores recursivas"],
      known=["Codeforces 223C — Partial Sums"]),
    C(E, "Para localizar a posição a, desce-se nível a nível pela árvore de expansão, percorrendo os filhos e subtraindo os comprimentos f já conhecidos.",
      "Descer na árvore de expansão por tamanhos",
      "Para achar o a-ésimo símbolo (ou contar algo até a posição a) de uma sequência gerada recursivamente, não gere a sequência: calcule o comprimento expandido de cada símbolo e, em cada nível, percorra os filhos subtraindo comprimentos até achar o filho que contém a posição. A profundidade é pequena e o custo por nível é só o de achar esse filho.",
      "string/sequência definida recursivamente com tamanho exponencial e consultas por posição k",
      ["k-ésimo caractere de strings definidas por recorrência (palavras de Fibonacci)",
       "k-ésimo objeto em ordem lexicográfica contando completamentos", "consulta de posição numa rope/árvore implícita"],
      known=["Codeforces 896A — Nephren gives a riddle"]),
    A(E, "Os níveis rasos (s ≤ 2) viram contagem de dominância 2D offline.", "BIT"),
])

P["nac2021-H"] = KEEP([
    N(D, "Componentes de arestas especiais: um ciclo especial já é a resposta, vértices com grau especial ≥ 3 ficam fora, e cada caminho especial é comprimido numa aresta obrigatória."),
    B(D, "Escolher um ciclo em que cada vértice tem grau 0 ou 2, com arestas forçadas, vira emparelhamento perfeito num grafo auxiliar com cópias dos vértices e um par de nós por aresta.",
      "Blossom", "Gadget de Tutte: subgrafo com graus prescritos via emparelhamento geral",
      "Escolher um subgrafo em que cada vértice v tem grau exatamente b(v) (ou grau num conjunto pequeno, como {0, 2}) reduz-se a emparelhamento perfeito num grafo auxiliar: b(v) cópias de v, e cada aresta uv vira um caminho cópia_u – e_u – e_v – cópia_v.",
      "Num emparelhamento perfeito, ou e_u–e_v se emparelham (aresta não usada) ou ambos se ligam a cópias (aresta usada); assim cada cópia de v consumida é uma aresta escolhida incidente a v. Vértices extras ligados às cópias permitem 'ficar fora' (grau 0).",
      "escolher arestas com grau exato por vértice em grafo NÃO bipartido; 'cada vértice no ciclo ou fora dele'; cobertura por ciclos disjuntos; n ≤ algumas centenas",
      ["f-fator / b-matching em grafo geral", "cobrir vértices de grafo não direcionado por ciclos disjuntos",
       "escolher arestas para que cada grau tenha valor prescrito"]),
    A(E, "Emparelhamento perfeito em grafo geral no grafo auxiliar.", "Blossom"),
])

P["nac2021-I"] = KEEP([
    B(E, "Processam-se as arestas (da MST) em ordem crescente e cada uma é aceita se, após a fusão, ainda existe atribuição de guardas distintos a todas as componentes.",
      "MST (Kruskal/Prim)", "Kruskal com oráculo de viabilidade (matroide)",
      "Se as escolhas viáveis formam uma estrutura com propriedade de troca (matroide), percorrer os elementos em ordem de custo e aceitar cada um sse a solução parcial continua completável dá o ótimo — o teste de 'completável' pode ser qualquer oráculo, como um emparelhamento.",
      "A prova do Kruskal só usa a troca de bases: se o ótimo não contém o elemento aceito, ele pode trocar por um elemento mais caro do ótimo sem perder viabilidade. Com o oráculo garantindo que a solução parcial é extensível, nenhum passo fecha o caminho até um ótimo.",
      "minimizar a soma de elementos escolhidos sob uma restrição extra verificável (cada componente com exatamente um X, conjunto independente); n pequeno (≤ 300–500)",
      ["base de peso mínimo de matroide linear (Base XOR com pesos)", "escalonamento de tarefas com prazos (matroide de escalonamento)",
       "MST com restrição verificável por fluxo/emparelhamento"]),
    A(E, "Oráculo: emparelhamento bipartido componentes × guardas.", "Matching bipartido (Kuhn/Hopcroft-Karp)"),
    A(E, "Fusões de componentes.", "DSU"),
])

P["nac2021-J"] = DROP("DP simples sobre a primeira metade do palíndromo; {top}")

P["nac2021-K"] = KEEP([
    C(O, "Para cada (x1, x2, y1) existe exatamente um y2 perdedor, então os estados perdedores são gerados em ordem em vez de avaliar 300^4 estados.",
      "No máximo um perdedor por linha em jogos de diminuir coordenada",
      "Se uma jogada pode reduzir uma coordenada a qualquer valor menor, dois estados perdedores nunca diferem só nessa coordenada (o maior alcançaria o menor). Fixadas as demais coordenadas existe no máximo um valor perdedor — e exatamente um se a linha é 'completa' —, então gere os perdedores em ordem crescente e marque o que eles já cobrem.",
      "jogo imparcial em que cada jogada reduz uma coordenada de um estado multidimensional; tabela de estados grande demais para DP direta",
      ["Nim de 2 pilhas e jogo de Wythoff (P-posições únicas por linha)", "rainha/torre que só anda para esquerda/baixo numa grade",
       "calcular Grundy por linha com mex usando bitset"],
      known=["Jogo de Wythoff"]),
    A(E, "Bitsets por tripla (x1, x2, y1) e _Find_first para achar o y2 perdedor; O(n⁴/64).", "Bitset"),
])

P["nac2021-L"] = KEEP([
    A(E, "Distâncias a partir da cidade 1.", "Dijkstra"),
    B(D, "Mantêm-se só as arestas com dist[v] = dist[u] + w; os caminhos de Bob são caminhos nesse DAG, filtrados pelos tempos registrados.",
      "Dijkstra", "DAG de caminhos mínimos",
      "As arestas apertadas (dist[v] = dist[u] + w) formam um DAG cujos caminhos a partir da origem são exatamente os caminhos mínimos; qualquer pergunta sobre 'algum/todo/quantos caminhos mínimos' vira pergunta sobre caminhos nesse DAG, ordenado por dist.",
      "Com pesos positivos, dist cresce estritamente ao longo de arestas apertadas (sem ciclos), e um caminho é mínimo sse cada uma de suas arestas é apertada.",
      "perguntas sobre todos os caminhos mínimos: unicidade, contagem, arestas/vértices em algum ou em todo caminho mínimo",
      ["contar caminhos mínimos", "arestas que pertencem a todo caminho mínimo", "caminho mínimo lexicograficamente menor"]),
    C(E, "Contam-se os caminhos 1→n no DAG filtrado com saturação em 2 e reconstrói-se só quando a contagem é 1.",
      "Contar saturando em 2 para decidir unicidade",
      "Para responder 'nenhuma / única / várias soluções', conte soluções com min(contagem, 2) numa DP de contagem: evita números gigantes e overflow, e a reconstrução só é feita quando a contagem é exatamente 1.",
      "saída pede 0 se impossível, 1 se ambíguo, ou a própria solução se única; 'a resposta é única?'",
      ["unicidade da ordenação topológica / do caminho num DAG", "unicidade da solução de quebra-cabeça via DP de contagem",
       "decidir se um emparelhamento ou uma decomposição ótima é única"]),
], reason="fácil, mas ensina o DAG de caminhos mínimos (B) e a contagem saturada para unicidade (C)")

P["nac2021-M"] = DROP("verificação direta da cobertura por L-triminós; o difícil é só codificar; {top}")

# ============================================================================= NAC 2022
P["nac2022-A"] = DROP("simulação dia a dia do conjunto de possíveis infectados; {top}")

P["nac2022-B"] = KEEP([
    C(R, "Uma reta ótima pode ser girada/transladada sem piorar até passar por dois chips, ou por um chip que seja ponto médio da corda que corta um canto.",
      "Empurrar a reta ótima até tocar pontos",
      "Em otimização sobre todas as retas/cortes do plano, pegue uma solução ótima e mova ou gire a reta sem piorar até que ela encoste em dois pontos da entrada (ou pare num extremo local do termo contínuo). Isso troca um espaço contínuo por O(n²) candidatos, que se enumeram com um pivô + ordenação angular.",
      "escolher uma reta/semiplano livre no plano; objetivo com contagem de pontos de um lado; n até alguns milhares",
      ["reta que passa pelo maior número de pontos / separador linear de duas cores", "maior faixa vazia entre pontos",
       "círculos ótimos determinados por 2–3 pontos"]),
    A(E, "Para cada chip como pivô, os demais são ordenados por ângulo.", "Ordenação angular"),
    A(E, "Varredura com dois ponteiros contando os chips de cada lado.", "Dois ponteiros"),
])

P["nac2022-C"] = KEEP([
    C(OT, "Como o custo ótimo do restante não cresce ao avançar, de cada posição basta usar a referência mais longa possível L em vez de todos os comprimentos ≤ L.",
      "DP monótona: só o salto mais longo importa",
      "Se g(i) = custo ótimo do restante a partir de i é não crescente em i (um sufixo menor nunca custa mais) e de i é possível saltar qualquer comprimento até L pelo mesmo custo, basta a transição de comprimento L: ela domina todas as mais curtas e a DP cai para O(1) transições por posição.",
      "transições 'avance até L posições pelo custo fixo' com L dependendo de i; compressão, cobertura de string por pedaços que já apareceram",
      ["mínimo de pedaços que são substrings de T para formar S", "jump game: menor número de saltos com alcance variável",
       "fatoração LZ77 com custo fixo por referência"]),
    B(E, "L (maior casamento começando antes de i, podendo sobrepor) sai dos vizinhos mais próximos de i no suffix array entre os sufixos que começam antes de i.",
      "Suffix array + LCP", "Maior fator anterior via vizinhos no suffix array",
      "O maior casamento de s[i..] com uma ocorrência que começa antes de i é o maior LCP entre i e o vizinho mais próximo no SA, à esquerda e à direita, dentre os sufixos que começam antes de i. Processando i em ordem decrescente e removendo i de uma lista duplamente ligada sobre o SA, os vizinhos na lista são exatamente esses candidatos.",
      "O LCP entre dois sufixos é o mínimo do array LCP no intervalo entre eles no SA, que só diminui ao se afastar; então, de cada lado, o candidato mais próximo é o melhor.",
      "'o trecho já apareceu antes?', fatoração Lempel-Ziv, casamento com ocorrência anterior (possivelmente sobreposta)",
      ["fatoração Lempel-Ziv", "para cada i, maior prefixo de s[i..] que ocorre começando antes de i",
       "consultas de maior casamento restritas a um conjunto que só perde elementos"]),
    A(E, "LCP entre vizinhos por RMQ.", "Sparse table"),
])

P["nac2022-D"] = KEEP([
    C(R, "Subtraindo 1 de todos os gaps, os que continuam positivos formam uma instância menor (menos elementos, alcance m − n), e quantos sobram segue uma distribuição combinatória.",
      "Descascar uma camada: subtrair 1 de todos",
      "Quando os objetos são vetores de inteiros ≥ 1 (gaps, partes, alturas), subtraia 1 de todos: os que continuam positivos formam uma instância menor do mesmo problema (menos elementos e menor total), e a quantidade dos que zeram tem contagem combinatória simples. Recorra sobre (quantidade, total).",
      "gaps entre números escolhidos/ordenados, partições de inteiros, estatísticas de ordem; n pequeno e soma moderada",
      ["contar partições em partes distintas removendo uma camada (primeira coluna do diagrama de Ferrers)",
       "esperança do k-ésimo menor gap entre pontos aleatórios", "histogramas: quantas colunas continuam ativas ao subir um nível"]),
    A(E, "DP dp[cnt][range] de prefixos esperados, deslocando índices ao recorrer.", "Valor esperado por linearidade"),
])

P["nac2022-E"] = KEEP([
    C(O, "Pôr 2 em todos os nós custa 2n, então nenhum valor acima de ~2n aparece num ótimo e a DP pode ser indexada pelo valor.",
      "Solução trivial limita o domínio dos valores",
      "Se existe uma solução trivial de custo C e o custo de um elemento cresce com o valor escolhido, nenhum valor maior que C aparece num ótimo; use esse limite para tornar viável uma DP indexada pelo valor atribuído (dp[u][x] com x ≤ C em vez de valores arbitrários).",
      "valores atribuídos livres (inteiros sem limite explícito) com custo crescente no valor",
      ["DP em árvore sobre o valor de cada nó quando o custo é o próprio valor", "limitar alturas/tamanhos numa construção por uma solução de referência",
       "teto para busca binária ou enumeração a partir de uma solução viável"]),
    A(E, "dp[u][x] = custo mínimo da subárvore com u valendo x.", "DP em árvore"),
    B(OT, "Para combinar com o filho sob 'gcd > 1', projeta-se o dp do filho para o mínimo sobre múltiplos de cada d e volta-se por d | x.",
      "Crivo de Eratóstenes", "Agregar por múltiplos/divisores em O(V log V)",
      "Para calcular, para todo x, min/soma de h(y) sobre y que compartilham um divisor d ≥ 2 com x, faça g[d] = agregado de h sobre os múltiplos de d e depois agregue g[d] sobre os divisores d de x; ambos os passos custam Σ V/d = O(V log V).",
      "O número total de pares (d, múltiplo de d) até V é a série harmônica V·(1 + 1/2 + … + 1/V).",
      "condição gcd > 1, divisibilidade ou fator comum entre valores ≤ 1e5–1e6",
      ["contar pares com gcd = g (agregando sobre múltiplos e Möbius)", "DP em árvore com condição de gcd entre vizinhos",
       "somas de Dirichlet / soma sobre divisores para todo x"]),
], reason="fácil, mas o limite do domínio pela solução trivial (C) e a agregação por múltiplos (B) são reutilizáveis")

P["nac2022-F"] = KEEP([
    C(R, "No limite de infinitos times o placar é determinístico: propaga-se a massa de times por (minuto, problemas lidos) e as frações resolvidas viram parâmetros das próximas escolhas.",
      "Infinitos agentes: simule a massa, não os indivíduos",
      "Com uma população infinita (limite n → ∞) de agentes independentes, a fração em cada estado é determinística; trate a população como distribuição e propague a massa no tempo (DP sobre (tempo, estado)), usando os agregados já acumulados como parâmetros das transições seguintes.",
      "'infinitos times/jogadores', 'fração esperada no limite', escolhas que dependem do que os outros fizeram (placar, popularidade)",
      ["propagar a distribuição de uma cadeia de Markov passo a passo", "modelos de população/infecção por frações (campo médio)",
       "DP de probabilidade em tempo discreto dependente do agregado"]),
    A(E, "Estado (minuto, máscara de problemas lidos) com transições por problema escolhido.", "DP com bitmask"),
])

P["nac2022-G"] = KEEP([
    C(R, "As células de rio formam um grafo funcional: ciclos (todos visitados) e sumidouros são raízes de árvores invertidas.",
      "Grafo funcional = ciclos com árvores penduradas",
      "Se cada nó tem no máximo uma saída, cada componente é um ciclo (ou um sumidouro) com árvores apontando para ele; contraia o ciclo numa raiz e resolva o resto com DFS nas arestas invertidas a partir dela — o trajeto seguido a partir de um nó é o caminho de volta até a raiz nessa árvore.",
      "'siga a seta até sair ou repetir', cada célula/nó com exatamente um sucessor, n até 1e5–1e6",
      ["k-ésimo sucessor e entrada no ciclo em grafo funcional", "comprimento da trajetória até repetir para cada nó",
       "mapeamentos f: [n] → [n] e permutações"]),
    B(E, "DFS nas arestas invertidas mantendo contador de pontos turísticos vizinhos: adiciona ao entrar, registra o número de distintos, remove ao sair.",
      "DFS", "Estado do caminho com entra/sai na DFS",
      "Uma quantidade sobre o caminho raiz → v (número de distintos, multiconjunto, prefixo de palavra) pode ser mantida por uma estrutura que adiciona a contribuição de v ao entrar e desfaz ao sair; a cada momento ela representa exatamente o caminho atual.",
      "A DFS percorre cada aresta duas vezes, ida e volta, e as operações de ida e volta são inversas, então são O(n) atualizações no total e nenhuma estrutura persistente é necessária.",
      "a resposta de cada nó depende do multiconjunto de valores no caminho da raiz até ele",
      ["número de cores distintas no caminho raiz–nó", "contar ancestrais com valor em faixa (BIT com entra/sai)",
       "backtracking com estado desfazível (DSU com rollback)"]),
])

P["nac2022-H"] = KEEP([
    C(D, "Inserir Z no meio de uma cédula é dominado por colocá-lo no topo ou no fim, e cédulas com a mesma ordem são intercambiáveis: basta enumerar quantas cédulas de cada tipo recebem Z no topo.",
      "Agrupar itens por tipo e enumerar quantos de cada",
      "Quando cada item tem poucas opções úteis (depois de descartar as dominadas — muitas vezes só os extremos importam) e itens do mesmo tipo são intercambiáveis, o espaço de decisões vira um vetor de contagens por tipo; enumere essas contagens (O(n) ou O(n²) combinações) e verifique cada uma com uma simulação.",
      "n itens grandes, mas só 2–3 'tipos' distintos (ordens de 3 candidatos, poucas cores), decisão individual por item",
      ["cédulas/votos com poucos candidatos", "distribuir n objetos de k tipos com k pequeno iterando sobre a composição",
       "jogos com pilhas agrupadas por valor"]),
    N(E, "Para k = 3, cada divisão é verificada simulando as rodadas de eliminação; para k = 2 há uma desigualdade fechada."),
])

P["nac2022-I"] = KEEP([
    A(D, "Busca binária no número de reinícios R.", "Busca binária na resposta"),
    N(O, "Com R fixo, cada tarefa é 'eliminável só com pesquisas' (consome só segundos de pesquisa) ou é pesquisada em toda tentativa e sobra na última; a viabilidade é uma conta de orçamento."),
])

P["nac2022-J"] = DROP("enumerar toda a árvore do jogo da velha com memoização; {top}")

P["nac2022-K"] = KEEP([
    C(R, "Fixa-se o ponto em que as duas strings divergem: antes há um prefixo comum (custo 2·dist), depois as duas execuções do DFA seguem acopladas.",
      "Fixe o primeiro ponto de divergência",
      "Para otimizar ou contar pares de objetos que precisam ser diferentes (strings, caminhos, sequências), fixe onde eles se separam pela primeira vez: antes são idênticos (um só objeto, custo dobrado), no ponto há uma diferença explícita e depois seguem independentes ou só sincronizados — cada parte vira um subproblema padrão.",
      "'duas strings/caminhos distintos com propriedade X', pares x ≠ y com custo somado, 'segundo melhor diferente'",
      ["contar números ≤ N em DP de dígitos (fixar o primeiro dígito menor)", "detectar ambiguidade de autômato/gramática (duas derivações da mesma palavra)",
       "segundo menor caminho distinto"]),
    C(E, "Depois da divergência roda-se Dijkstra em pares de estados: maiúsculas avançam os dois ao mesmo tempo (custo 2), minúsculas avançam um só (custo 1).",
      "Grafo produto para duas execuções simultâneas",
      "Para raciocinar sobre duas execuções ao mesmo tempo (duas strings no mesmo autômato, dois robôs, duas pessoas), use estados pares (q1, q2): transições sincronizadas movem os dois, transições livres movem um; um caminho mínimo no grafo produto (s² estados) resolve.",
      "dois agentes/strings que precisam satisfazer uma condição conjunta; poucos estados (s ≤ 50–300)",
      ["dois robôs num labirinto recebendo os mesmos comandos", "interseção/equivalência de DFAs",
       "duas pessoas que precisam se encontrar num grafo (BFS em pares)"]),
    A(E, "Caminho mínimo no grafo de pares de estados.", "Dijkstra"),
    A(E, "Distâncias só com letras minúsculas entre todos os pares de estados.", "Floyd-Warshall"),
])

P["nac2022-L"] = KEEP([
    C(O, "Com alturas ≤ 1e9, uma sequência ordenada sem triângulo cresce como Fibonacci, então qualquer retângulo com ≥ 45 árvores responde 'sim'.",
      "Limite de Fibonacci: conjunto grande sempre tem triângulo",
      "Se os valores são ≤ V e a propriedade buscada só falha quando a sequência ordenada cresce como Fibonacci/geometricamente (sem trio que forme triângulo, cada elemento ≥ soma ou dobro dos anteriores), todo conjunto com mais de ~log_φ V elementos já a satisfaz: responda 'sim' para conjuntos grandes e faça força bruta ordenada nos pequenos.",
      "valores até 1e9/1e18 e consulta 'existem 3 que formam triângulo', ou cadeia em que cada elemento supera a soma/o dobro dos anteriores",
      ["triângulo em subarray por consulta", "subconjunto 'livre de somas' com valores limitados",
       "cadeias de divisores/gcd: no máximo log V mudanças distintas"],
      known=["Codeforces 1991F — Triangle Formation"]),
    A(E, "Estrutura de faixa 2D para listar até 45 pontos dentro do retângulo.", "Merge sort tree"),
])

P["nac2022-M"] = DROP("construção de caminho induzido no grafo de Hamming por busca com pré-cálculo; truque pontual; {top}")

# ============================================================================= NAC 2023
P["nac2023-A"] = KEEP([
    C(R, "Cada composto corresponde a uma assinatura (em que dia cada local reage, ou nunca); k locais e d dias geram (d+1)^k assinaturas, então a resposta é o menor k com (d+1)^k ≥ n.",
      "Cada item recebe um código: capacidade = número de códigos",
      "Em problemas de identificar um item oculto com testes, associe a cada item a 'assinatura' de resultados que ele produziria; uma estratégia identifica n itens sse gera ≥ n assinaturas distintas. Conte as assinaturas que k recursos produzem (base d+1 com d rodadas, base 3 em balanças, base 2 em sim/não) e inverta para achar o mínimo de recursos.",
      "'mínimo de testes/locais/ratos para identificar o único defeituoso', n até 1e18 e resposta pequena",
      ["garrafa envenenada com ratos (código binário; com d dias, base d+1)", "pesagem de moedas falsas (base 3)",
       "limite inferior de perguntas sim/não: ⌈log2 n⌉"]),
], reason="fácil, mas a contagem de assinaturas (C) é um argumento reutilizável de limite/construção")

P["nac2023-B"] = KEEP([
    C(D, "Fixada uma árvore geradora, todo caminho simples usa cada aresta extra no máximo uma vez: enumeram-se os poucos casos (nenhuma, uma em cada direção, as duas em cada ordem/direção) como concatenações de caminhos na árvore.",
      "Árvore + k arestas: enumere quais extras usar",
      "Num grafo com n − 1 + k arestas e k pequeno, fixe uma árvore geradora; todo caminho ou ciclo simples usa cada aresta extra no máximo uma vez, então enumere o subconjunto, a ordem e a direção das extras usadas e trate cada caso como concatenação de caminhos na árvore, verificando as condições com LCA.",
      "m = n + c com c pequeno (≤ 2–20 arestas extras); consultas de caminhos/distâncias",
      ["distâncias em grafo quase-árvore: mínimo entre caminho na árvore e caminhos via extremos das extras",
       "contar ciclos simples com poucas arestas extras", "pseudoárvores (n arestas, um único ciclo)"],
      known=["Codeforces 1051F — The Shortest Statement"]),
    B(E, "Cada caso exige que os segmentos de árvore sejam disjuntos dois a dois, o que se testa partindo-os nos LCAs em caminhos ascendentes.",
      "LCA (binary lifting)", "Interseção de caminhos em árvore via LCA",
      "Dois caminhos u1–v1 e u2–v2 de uma árvore se intersectam sse o LCA de um deles está no outro caminho; e x está no caminho u–v sse dist(u, x) + dist(x, v) = dist(u, v).",
      "Se a interseção é não vazia, seu ponto mais alto é o mais profundo dos dois LCAs, e esse ponto pertence aos dois caminhos.",
      "verificar se caminhos de árvore são disjuntos/se cruzam; consultas 'x está no caminho u–v?'",
      ["checar se duas rotas numa árvore se cruzam por consulta", "decidir se um vértice bloqueado está na rota",
       "contar pares de caminhos disjuntos"]),
])

P["nac2023-C"] = KEEP([
    B(E, "Kruskal com empates desfeitos a favor das arestas da árvore dada dá a MST mais parecida com ela; a resposta é o número de arestas dadas fora dela.",
      "MST (Kruskal/Prim)", "Kruskal com desempate: MST mais próxima de uma árvore dada",
      "Ordenando por (peso, não pertence a T), o Kruskal devolve, entre todas as MSTs, a que compartilha mais arestas com T; e de qualquer árvore geradora chega-se a essa MST com exatamente |T \\ MST| trocas, cada uma adicionando uma aresta da MST e removendo do ciclo formado uma aresta fora dela.",
      "O desempate equivale a pesos perturbados w − ε·[e ∈ T]. Árvores geradoras são bases de um matroide: pela troca de bases, o ciclo criado por uma aresta da MST sempre contém uma aresta de T fora da MST.",
      "transformar uma árvore/base dada na ótima com o mínimo de trocas; 'MST que mais/menos usa arestas de um tipo'",
      ["MST com o máximo/mínimo de arestas de uma cor (desempate ou penalidade λ)", "decidir se uma aresta está em alguma MST",
       "distância em trocas entre bases de um matroide"]),
    A(E, "Para cada troca, DFS no caminho da árvore entre os extremos da nova aresta.", "DFS"),
], reason="fácil, mas o desempate do Kruskal e a troca de bases (B) não são conhecidos por quem só sabe MST")

P["nac2023-D"] = KEEP([
    C(O, "Sem dependências, trocar dois testes adjacentes compara c_i/(1−p_i) com c_j/(1−p_j): ordena-se pela razão.",
      "Ordem ótima por razão via troca adjacente",
      "Para escolher a ordem que minimiza um custo sequencial (custo esperado até falhar, soma ponderada de términos), compare só dois itens adjacentes i, j: se a condição 'ij não é pior que ji' se separa em f(i) ≤ f(j), a ordem ótima é ordenar por f.",
      "minimizar soma ponderada ou esperança que depende da ordem dos itens; 'em que ordem executar os testes/tarefas'",
      ["regra de Smith: ordenar por tempo/peso", "concatenar strings para a menor lexicográfica (a+b < b+a)",
       "ordem de itens com probabilidade de interromper o processo"]),
    C(E, "Com prerequisitos em floresta, o bloco de melhor razão é agendado se o pai já foi; senão é fundido ao bloco do pai (custo c1 + p1·c2, prob. p1·p2) e reinserido.",
      "Fundir com o pai o melhor bloco (precedência em árvore)",
      "Com uma regra de troca por razão e precedências em floresta, pegue o bloco de melhor razão: se o pai já foi agendado, agende-o; senão ele deve vir imediatamente depois do pai, então funda os dois num bloco (parâmetros combinados) e reinsira. Heap + DSU + listas ligadas dão O(n log n).",
      "ordenação ótima por razão com restrições 'X antes de Y' formando árvore/floresta",
      ["colorir/visitar árvore minimizando soma de tempo × peso", "minimizar inversões numa sequência com precedência de árvore",
       "escalonamento com precedência em árvore minimizando soma ponderada"],
      known=["POJ 2054 — Color a Tree", "AtCoder AGC023 F — 01 on Tree"]),
    A(E, "Fusão de blocos com o pai.", "DSU"),
])

P["nac2023-E"] = KEEP([
    N(R, "Letras viram vértices e palavras viram arestas dirigidas: é um jogo de geografia em arestas num multigrafo de ≤ 3 vértices."),
    C(D, "Dois laços no mesmo vértice se cancelam, e arestas opostas u→v e v→u também (o oponente espelha); o grafo reduzido tem poucas arestas.",
      "Pares espelháveis se cancelam",
      "Em jogos de dois jogadores, se alguns movimentos vêm em pares tais que, sempre que um jogador usa um, o outro pode responder com o par sem mudar o resto do estado, remova o par: o vencedor não muda. Aplique repetidamente até sobrar um núcleo pequeno e então faça minimax.",
      "jogo com muitos objetos repetidos ou simétricos (arestas paralelas/opostas, pilhas iguais) e espaço de estados grande demais",
      ["Nim: duas pilhas iguais se cancelam (XOR 0)", "estratégia de espelho pelo centro em tabuleiro simétrico",
       "jogos de remover arestas em multigrafos"]),
    A(E, "Minimax memoizado sobre as contagens de arestas restantes.", "Minimax com memoização"),
])

P["nac2023-F"] = DROP("força bruta sobre permutações e orientações de 4 retângulos; {top}")
P["nac2023-G"] = DROP("escolha local (pagar os voos mais recentes) com janela deslizante; {top}")

P["nac2023-H"] = KEEP([
    C(R, "O concorrente i − k nunca supera i, então só os k concorrentes logo abaixo do segundo colocado podem ser eliminados: estado = bitmask dessa janela.",
      "Interação limitada a uma janela ⇒ estado = bitmask da janela",
      "Se só elementos a distância ≤ k podem interagir (ordem garantida fora da janela), a parte relevante do estado é uma fronteira de k posições: guarde por bitmask quais delas ainda estão vivas e comprima o resto em poucos números, dando O(n·2^k).",
      "parâmetro pequeno k (≤ 10–20) que limita o alcance da interação, com n grande",
      ["DP de perfil (broken profile) em tabuleiros n × k", "permutações com |p_i − i| ≤ k",
       "escalonamento em que cada tarefa só pode mudar ±k posições"]),
    C(OT, "As probabilidades de quem é o segundo são calculadas agrupando notas pela parte inteira: dentro da mesma unidade todas as ordens são igualmente prováveis.",
      "Uniformes deslocadas: condicione na parte inteira",
      "Para comparar variáveis uniformes em intervalos [a_i, a_i + k] com extremos inteiros, condicione na parte inteira de cada uma: as partes fracionárias são i.i.d. em [0,1), então dentro da mesma unidade toda ordem relativa é equiprovável e a probabilidade de uma ordem vira contagem combinatória.",
      "variáveis uniformes contínuas com suportes inteiros deslocados; probabilidade de ranking/ordem",
      ["probabilidade de ordem entre uniformes de intervalos diferentes", "esperança do máximo/segundo maior de uniformes com suportes distintos"]),
    A(E, "DP sobre (abaixo, máscara, acima) com 'acima' limitado a k.", "DP com bitmask"),
    A(E, "Postos esperados somando probabilidades de eliminação.", "Valor esperado por linearidade"),
])

P["nac2023-I"] = DROP("raiz e-ésima por busca binária + contagem de divisores por divisão; {top}")

P["nac2023-J"] = KEEP([
    C(O, "A concatenação é um quadrado TT sse as duas partes são iguais ou a maior é ABA e a menor é B.",
      "Quadrado de duas partes: iguais ou ABA + B",
      "Se a concatenação de duas substrings deve ser um quadrado TT, ou elas são iguais, ou a maior tem a forma ABA e a menor é B (em alguma ordem); conte cada forma separadamente.",
      "contar pares de substrings cuja concatenação é um quadrado",
      ["contar pares (x, y) com xy quadrado"], specific=True),
    A(E, "lcp[i][j] para todos os pares de posições.", "LCP de todos os pares (DP O(n²))"),
    A(OT, "Contagem das posições compatíveis e não sobrepostas por prefixos.", "Soma de prefixos"),
])

P["nac2023-K"] = DROP("força bruta no tamanho do tab (≤ 1000); {top}")

P["nac2023-L"] = KEEP([
    C(O, "O padrão das posições perdedoras (paridade / valuação 2-ádica comum) foi achado por força bruta em casos pequenos e provado por espelhamento.",
      "Tabelar casos pequenos para achar o padrão das posições perdedoras",
      "Em jogos imparciais com regras estranhas e valores enormes, escreva um brute force memoizado para estados pequenos, imprima as posições perdedoras e procure um padrão (paridade, mod, potência de 2 comum); depois valide: de uma posição perdedora toda jogada leva a uma vencedora e de toda vencedora existe jogada para uma perdedora (muitas vezes por espelhamento).",
      "jogo com valores até 1e12/1e18 e regra complicada, muitos testes — DP direta impossível",
      ["variações de Nim (subtrair potências, dividir pilhas)", "jogos em grafos pequenos com padrão periódico em n",
       "sequências de Grundy periódicas"]),
    N(E, "n par: perde sse todas as pilhas são ímpares; n ímpar: divida pela maior potência de 2 comum e aplique o mesmo teste."),
])

P["nac2023-M"] = KEEP([
    C(R, "Cada sentinela vê exatamente uma e é vista por exatamente uma: é escolher uma permutação, isto é, um emparelhamento perfeito vigia × vigiado.",
      "Uma entrada e uma saída por nó ⇒ emparelhamento perfeito",
      "Exigir que cada elemento aponte para exatamente um e seja apontado por exatamente um é escolher uma permutação (cobertura por ciclos dirigidos); modele como emparelhamento perfeito bipartido entre cópias 'saída' e 'entrada' de cada nó — com custos, vira problema de atribuição.",
      "'cada um vê/segue/aponta exatamente um outro e é visto por exatamente um'; cobrir grafo dirigido por ciclos",
      ["cobertura de grafo dirigido por ciclos disjuntos de custo mínimo", "cobertura mínima de DAG por caminhos (emparelhamento saída/entrada)",
       "reatribuir sucessores com custo mínimo para formar uma permutação"]),
    A(E, "Atribuição de custo mínimo (custo 0 se já vê, 1 se o segmento está livre).", "Fluxo de custo mínimo"),
    N(O, "Com n ímpar e todos colineares é preciso mover exatamente uma sentinela: força bruta em qual, com testes de raio 3D e prefixos."),
])

# ============================================================================= NAC 2024
P["nac2024-A"] = DROP("mochila padrão de duas máquinas (makespan); {top}")

P["nac2024-B"] = KEEP([
    N(D, "Enumera-se o número de dígitos do primeiro número que toca o padrão e quantos dígitos dele ficam antes do padrão."),
    C(O, "Restrições com coringas sobre x e x+1 consecutivos ficam independentes ao fixar quantos 9s terminam x.",
      "x e x+1 diferem só no bloco final de 9s",
      "Ao impor restrições de dígitos simultâneas sobre x e x+1 (números consecutivos escritos lado a lado), fixe a quantidade t de 9s no final de x: então x = P d 9…9 e x+1 = P (d+1) 0…0, e as restrições viram restrições independentes sobre P e d. Enumere t.",
      "padrão que atravessa números consecutivos escritos em sequência; DP de dígitos envolvendo x e x+1 (vai-um)",
      ["contar x tal que x e x+1 têm alguma propriedade de dígitos (soma de dígitos de x+1)", "posição de uma substring na sequência 123456789101112…",
       "DP de dígitos sobre x + c com estado de carry"]),
])

P["nac2024-C"] = KEEP([
    C(OT, "Só a primeira instrução de cada (a, b, tabela-verdade) pode decidir; isso limita o programa a 16k² instruções úteis.",
      "Só a primeira regra por condição importa",
      "Se uma lista de regras é avaliada em ordem e a primeira que dispara decide, qualquer regra com a mesma condição de uma anterior nunca decide — deduplique por condição. O número de regras úteis fica limitado pelo número de condições distintas, não por n.",
      "n enorme de if/regras com poucos valores possíveis por campo; 'a primeira regra aplicável vence'",
      ["tabelas de roteamento/firewall com primeira correspondência", "atribuições sobrescritas: só a última por posição importa (processe ao contrário)",
       "cadeias de if-else sobre domínio pequeno: tabelar a resposta por entrada"]),
    N(E, "Cada expressão booleana vira sua tabela de 4 entradas sobre (x_a, y_b); avalia-se o comparador em todos os 4^k pares."),
    B(E, "Violações de transitividade: para cada (x, y) com f(x, y) = 1, soma-se popcount(linha_y & ~linha_x).",
      "Bitset", "Contar triplas de uma relação com AND de linhas",
      "Para contar triplas (x, y, z) com f(x, y) ∧ f(y, z) ∧ ¬f(x, z), guarde cada linha da relação como bitset; para cada par (x, y) com f(x, y) = 1, o número de z é popcount(linha_y & ~linha_x), em O(N³/64) total.",
      "Cada operação de palavra processa 64 valores de z de uma vez, e a condição sobre z é um AND/NOT de duas linhas fixas.",
      "contar triângulos/triplas numa relação binária densa com N ≤ alguns milhares",
      ["contar triângulos em grafo denso", "fecho transitivo com bitset", "contar pares a distância exatamente 2"]),
])

P["nac2024-D"] = DROP("a primeira posição fixa a rotação; checar as duas direções diretamente; {top}")

P["nac2024-E"] = KEEP([
    C(O, "Num emparelhamento ótimo pessoas–casas no círculo, os arcos não se cruzam, nenhuma casa livre fica sob um arco e arcos aninhados vão no mesmo sentido; assim cada pessoa tem só duas casas candidatas, achadas com pilha.",
      "Emparelhamento de custo mínimo na reta: arcos não se cruzam",
      "Em emparelhamento de custo mínimo entre pontos de dois tipos numa reta/círculo com custo = distância, sempre existe ótimo em que os arcos não se cruzam (descruzar não aumenta a soma), nenhum ponto opcional livre fica sob um arco e arcos aninhados têm o mesmo sentido. O emparelhamento vira estrutura de parênteses calculável com pilha, e cada elemento tem pouquíssimos parceiros candidatos.",
      "pontos de dois tipos numa linha/círculo, emparelhar minimizando Σ |a − b|, com sobra de pontos opcionais (m > n)",
      ["emparelhar pontos vermelhos e azuis numa reta", "pessoas e abrigos/casas numa linha com capacidade 1",
       "transporte 1D: custo mínimo = Σ |saldo do prefixo|"]),
    N(E, "O grafo de candidatos se quebra em componentes caminho; custo e número de escolhas ótimas por componente saem de somas de prefixo/sufixo."),
    A(E, "Somas de prefixo/sufixo sobre cada componente.", "Soma de prefixos"),
])

P["nac2024-F"] = KEEP([
    C(E, "Comutador (gira anel colorido, gira anel central, desfaz o colorido, desfaz o central) troca duas contas entre anéis mexendo pouco no resto; com ele fixa-se uma conta por vez.",
      "Comutador: A B A⁻¹ B⁻¹ só mexe na interseção",
      "Em quebra-cabeças de permutação (anéis, cubos), o comutador A·B·A⁻¹·B⁻¹ só afeta peças na interseção dos suportes de A e B; use-o como primitiva de poucos movimentos que troca 2–3 peças e resolva fixando uma peça por vez sem desfazer as já colocadas.",
      "'imprima no máximo K rotações que resolvem o estado', grupos de rotação que se sobrepõem",
      ["cubo de Rubik e quebra-cabeças de anéis", "ordenar com rotações de 3 elementos (paridade)",
       "gerar uma transposição/3-ciclo a partir dos geradores de um grupo de permutações"]),
])

P["nac2024-G"] = DROP("DP de esperança na grade com fórmula fechada específica para E[min(T + a, b)]; {top}")

P["nac2024-H"] = KEEP([
    N(R, "Projetando as arestas de 45° no eixo x, o comprimento visível é constante × comprimento da união das bases [x − y, x + y] recortadas a [0, w]."),
    B(E, "A união sob inserções/remoções de intervalos é mantida por segment tree com contador de cobertura por nó, sem propagação.",
      "Segment tree", "Segment tree de cobertura (união de intervalos sem lazy)",
      "Para manter o comprimento da união de intervalos sob inserção/remoção, cada nó guarda cnt (quantos intervalos o cobrem inteiro, sem empurrar para os filhos) e len (comprimento coberto): len = tamanho do nó se cnt > 0, senão soma dos filhos.",
      "Toda remoção desfaz uma inserção anterior do mesmo intervalo, que se decompõe nos mesmos O(log n) nós; então cnt nunca precisa ser propagado e nunca fica negativo.",
      "área/perímetro da união de retângulos, comprimento coberto sob toggles de intervalos",
      ["área da união de retângulos (sweep line)", "perímetro da união de retângulos",
       "quantos pontos estão cobertos por ≥ 1 intervalo sob inserções/remoções"]),
], reason="fácil, mas a segment tree de cobertura sem lazy (B) é uma variação que muitos não conhecem")

P["nac2024-I"] = DROP("DP/backtracking sobre (contagem de N, de NA, de NAC) com memoização e poda; {top}")
P["nac2024-J"] = DROP("casa dos pombos: o adversário fragmenta em k blocos, checagem direta por prefixo; {top}")

P["nac2024-K"] = KEEP([
    C(R, "A sombra é conexa sse, ordenando os extremos por ângulo a partir da luz, o saldo de extremos inferiores menos superiores nunca zera antes do último segmento fechar.",
      "Conexidade de intervalos = saldo de parênteses",
      "Um conjunto de intervalos (ou sombras angulares) forma uma única peça sse, percorrendo todos os extremos em ordem, o saldo aberturas − fechamentos nunca chega a 0 antes do último extremo; vira checar o mínimo das somas de prefixo.",
      "'a união é conexa / um único intervalo?', intervalos cujos extremos mudam com um parâmetro",
      ["união de intervalos sem buracos", "sequência de parênteses balanceada via mínimo de prefixo",
       "cobertura de um círculo por arcos"]),
    B(OT, "A ordem angular de dois extremos só muda quando a reta por eles cruza o eixo x: O(n²) eventos, cada um uma troca de adjacentes que altera um prefixo em ±2.",
      "Ordenação angular", "Varredura de eventos de troca (ordem cinética)",
      "Se n objetos estão ordenados por uma chave que depende de um parâmetro t e cada par troca de ordem no máximo uma vez, a ordem muda só em O(n²) eventos e cada evento é uma troca de vizinhos; ordene os eventos e mantenha a ordem e as somas de prefixo atualizadas em O(1) por evento.",
      "Entre eventos consecutivos a ordem é constante; numa troca de adjacentes só a soma de prefixo entre os dois muda.",
      "ponto/direção que se move continuamente e uma propriedade da ordem dos objetos; n ≤ 2000–5000",
      ["girar uma direção por todos os ângulos mantendo a ordem das projeções (rotating sweep line)",
       "maior/menor área de triângulo com a ordem por direção", "k-ésimo nível de arranjo de retas"]),
    A(E, "Eventos ordenados e processados em ordem.", "Sweep line"),
])

P["nac2024-L"] = DROP("busca exaustiva de arranjos de 4 triângulos com aritmética inteira; o difícil é só a quantidade de casos e codificar ({top})")

P["nac2024-M"] = KEEP([
    C(R, "Como s + t = inicial + resolvidos, o estado (problema, s, t) vira (problema, resolvidos, incremento de s), guardado como bitset.",
      "Invariante elimina uma dimensão do estado",
      "Se duas variáveis do estado têm soma (ou outra combinação) determinada pelo progresso — cada passo incrementa exatamente uma delas —, guarde só uma: o estado cai de (passo, s, t) para (passo, s), e os estados alcançáveis podem ser guardados como bitset por passo.",
      "estado com vários contadores que crescem juntos; cada passo incrementa exatamente um deles",
      ["DP em grade com passos direita/baixo: (passo, linha) determina a coluna", "DP de parênteses: (posição, abertos) determina os fechados",
       "jogos com dois recursos de soma conhecida"]),
    N(OT, "Iterar só sobre bits ligados e removê-los após processar dá O(n²) no total."),
], reason="fácil, mas a eliminação de dimensão por invariante (C) é reutilizável")

# ============================================================================= NAC 2025
P["nac2025-A"] = DROP("fatoração e ajuste primo a primo, do maior para o menor; {top}")

P["nac2025-B"] = KEEP([
    N(R, "dp[v][j]: maneiras na subárvore de v com j ∈ {0, 1} caminhos-folha ativos até a raiz; dois ativos fechariam um ciclo."),
    B(OT, "dp[v][1] = Σ_c dp[c][1] · ∏_{outros} (…) é calculado com produtos de prefixo e sufixo, porque fatores zero mod p impedem usar inverso.",
      "DP em árvore", "Produto de todos menos um sem divisão",
      "Para obter ∏_{j ≠ i} a_j para todo i (o filho 'especial' e o produto dos outros), use produtos de prefixo e sufixo: pre[i−1]·suf[i+1]. Funciona mesmo quando algum a_j ≡ 0 mod p, caso em que dividir pelo inverso falha.",
      "Zero não tem inverso modular, e prefixo/sufixo nunca dividem; o custo continua O(grau).",
      "DP com 'exatamente um filho/item especial': Σ_c x_c · ∏_{d ≠ c} y_d, módulo primo com fatores possivelmente 0",
      ["rerooting com o produto dos outros filhos", "contar escolhas 'exatamente um' num produto de opções",
       "produto do array exceto a própria posição"]),
], reason="fácil, mas o produto-exceto-um sem inverso (B) evita um bug comum com zeros mod p")

P["nac2025-C"] = DROP("minimax completo sobre bitboards 3×3; o difícil é só codificar o jogo interativo ({top})")

P["nac2025-D"] = KEEP([
    C(O, "O conjunto de y alcançáveis a cada x continua um intervalo de paridade fixa: mantém-se [ymin, ymax], expande-se ±1 e intersecta-se com a faixa livre.",
      "Conjunto alcançável continua um intervalo: guarde só os extremos",
      "Se de cada estado y dá para ir a y ± 1 (ou a uma faixa contínua) e as restrições de cada passo são intervalos, o conjunto de valores alcançáveis (com paridade fixa) é sempre um intervalo — mantenha [lo, hi], expanda e intersecte a cada passo em O(1).",
      "passos ±1 com faixas permitidas por coluna/tempo; 'menor e maior posição final alcançável'",
      ["viabilidade de agenda com velocidade limitada e janelas de tempo", "passeio ±1 que deve ficar dentro de um corredor",
       "valores possíveis de uma soma com ajustes ±1 por passo"]),
    A(E, "Dois ponteiros sobre os segmentos do teto e do chão enquanto x avança.", "Dois ponteiros"),
], reason="fácil, mas 'o alcançável é um intervalo' (C) é um atalho geral")

P["nac2025-E"] = KEEP([
    A(R, "Sem adversário, c_i = h_i − a_i ou k(h_i − a_i) e conta-se pares de prefixos P_i ≤ P_j.", "Soma de prefixos"),
    N(O, "O adversário sempre troca o elemento de maior h_i − a_i do subarray (se houver), o que subtrai um valor fixo."),
    B(E, "Fixa-se o elemento máximo s (o mais à esquerda), acha-se seu intervalo de domínio e itera-se só sobre o lado menor, contando o outro extremo com estrutura de contagem.",
      "Small-to-large", "Fixar o máximo e iterar pelo lado menor",
      "Para contar subarrays cuja condição depende do máximo (ou mínimo), para cada i ache o intervalo [L, R] em que ele é o máximo (pilha monotônica) e enumere o lado mais curto, consultando o outro lado com uma estrutura; o total é O(n log n) enumerações.",
      "É small-to-large na árvore cartesiana: uma posição só é enumerada quando está no lado menor, e o segmento que a contém ao menos dobra a cada vez.",
      "contar subarrays com condição envolvendo max/min junto com soma ou extremos",
      ["pares (l, r) com p_l + p_r = max(l..r) em permutação", "contar subarrays em que o máximo divide a soma",
       "subarrays com soma ≥ k·max"],
      known=["Codeforces 1156E — Special Segments of Permutation"]),
    A(E, "Intervalo de domínio de cada máximo.", "Pilha monotônica"),
    A(E, "Contagem offline de prefixos ≥ valor.", "BIT"),
])

P["nac2025-F"] = DROP("construção por caminho em escada preenchendo as duas regiões; {top}")

P["nac2025-G"] = KEEP([
    C(D, "Contraem-se vértices de grau 2 (somando pesos) e fundem-se arestas paralelas (registrando a + b como ciclo candidato e mantendo a maior); como o dual é árvore, os ciclos-folha somem um a um.",
      "Redução série-paralela",
      "Em grafos formados por ciclos colados em árvore (série-paralelo, cactos generalizados, treewidth 2), repita: contraia vértice de grau 2 somando suas arestas e funda arestas paralelas registrando a resposta candidata que elas formam e mantendo a melhor. Cada operação preserva a resposta e tudo roda em O(V + E) com filas.",
      "'grafo planar cujo dual é uma árvore', cactos, grafos série-paralelos; maior/menor ciclo ou caminho",
      ["resistência equivalente / melhor caminho entre dois terminais em série-paralelo", "maior ciclo em cacto",
       "otimização em grafos de treewidth 2"]),
])

P["nac2025-H"] = DROP("pós-ordem atribuindo a cada nó o máximo permitido; {top}")

P["nac2025-I"] = KEEP([
    C(O, "A área do polígono se escreve somando cruzamentos com retas verticais inteiras e também com horizontais; igualar as duas expressões já define a partição.",
      "Contar a mesma quantidade de duas formas",
      "Se uma grandeza (área, número de pares) se escreve como soma sobre duas famílias diferentes de eventos (cruzamentos com retas verticais × horizontais, linhas × colunas), igualar as duas expressões dá uma identidade: os termos com sinal + de um lado e − do outro se dividem em dois grupos de mesma soma. Útil quando a resposta de existência é 'sempre'.",
      "pergunta de existência que parece difícil mas sempre tem resposta; somas de pisos de coordenadas; cruzamentos com a grade",
      ["provas por dupla contagem (Σ graus = 2|E|)", "teorema de Pick / área por cruzamentos com a grade",
       "particionar em dois grupos de soma igual via invariante"]),
])

P["nac2025-J"] = KEEP([
    B(R, "A resposta é n − E[X] com E[X] = Σ_k P(X ≥ k).",
      "Valor esperado por linearidade", "Esperança pela cauda: E[X] = Σ P(X ≥ k)",
      "Para X inteiro ≥ 0, E[X] = Σ_{k ≥ 1} P(X ≥ k); quando P(X ≥ k) é uma contagem fácil e P(X = k) não, calcule a esperança pela cauda.",
      "X = Σ_{k ≥ 1} [X ≥ k] e aplica-se linearidade às indicadoras.",
      "esperança de um tempo de parada ou de um tamanho; P(X ≥ k) tem forma de contagem",
      ["número esperado de passos até um evento", "esperança do máximo/mínimo de variáveis discretas",
       "tempo esperado de remoções aleatórias até uma propriedade valer"]),
    C(R, "Remover balões uniformemente equivale a uma ordem aleatória; os k restantes formam um subconjunto uniforme, logo P(X ≥ k) = (# subsequências não decrescentes de tamanho k)/C(n, k).",
      "Remoção aleatória = subconjunto restante uniforme",
      "Remover elementos uniformemente ao acaso, um a um, equivale a uma permutação aleatória: após j remoções o que resta é um subconjunto uniforme de tamanho n − j. Se a condição de parada é monótona (uma vez satisfeita, continua), P(ainda restam ≥ k quando para) vira (# subconjuntos bons de tamanho k)/C(n, k) — o problema vira contagem por tamanho.",
      "'remova um elemento aleatório até a sequência/grafo ficar X'; esperança mod primo",
      ["apagar arestas aleatórias até desconectar", "sortear itens até aparecer uma propriedade monótona",
       "probabilidade de o conjunto restante ser ordenado/independente"]),
    B(E, "Subsequências não decrescentes de cada comprimento: divide-se ao meio, guarda-se um polinômio por (cor inicial, cor final) e junta-se por multiplicação.",
      "FFT/NTT", "Divisão e conquista com polinômios por estado de borda",
      "Para contar subsequências de todos os comprimentos com restrição só entre elementos consecutivos (cores não decrescentes), divida o array ao meio e guarde, para cada par (estado inicial, estado final), o polinômio gerador por comprimento; juntar as metades é multiplicar polinômios compatíveis, O(c²·n log² n).",
      "O comprimento é aditivo entre as metades e a restrição só afeta o par (último da esquerda, primeiro da direita), então a junção é um produto de 'matrizes de polinômios'.",
      "contar subsequências/subconjuntos por tamanho para TODOS os tamanhos, n ~ 1e5–2e5, poucos estados locais",
      ["produto ∏ (1 + a_i x) por divisão e conquista", "contar subsequências crescentes por tamanho com poucos valores",
       "DP linear com matriz de transição de polinômios"]),
    A(E, "Multiplicação de polinômios mod 998244353.", "FFT/NTT"),
])

P["nac2025-K"] = DROP("simulação incremental mantendo um único poço; {top}")

P["nac2025-L"] = KEEP([
    C(O, "f(i) = ⌊maior j para i colunas⌋ não é unimodal, mas sua relaxação real é; o ótimo inteiro fica a O(√r) do ótimo real, então busca-se só nessa vizinhança.",
      "Ótimo inteiro perto do ótimo da relaxação contínua",
      "Quando a função inteira (com pisos) não é unimodal mas a versão real F é, e f difere de F por uma folga controlada, o ótimo inteiro está numa vizinhança limitada do ótimo real: quantifique a folga, enumere só essa vizinhança e use raiz/aritmética inteira exata.",
      "maximizar i·⌊g(i)⌋ ou produto com pisos; valores até 1e9; muitos testes",
      ["maximizar funções com piso como i·⌊n/i⌋", "maior retângulo de lados inteiros inscrito em círculo/elipse",
       "programação inteira em 2 variáveis com uma restrição"]),
], reason="fácil, mas 'buscar perto do ótimo contínuo' (C) é reutilizável")

P["nac2025-M"] = KEEP([
    C(O, "Em cada faixa de potência de 2 ao menos metade dos elementos cai por rodada, então após poucas rodadas simuladas restam ≤ 3 não nulos.",
      "Potencial: elementos zeram rápido — simule só os ativos",
      "Se cada rodada faz uma fração constante dos elementos de cada escala (faixa de potência de 2) cair de faixa ou zerar, o número de rodadas efetivas é O(log V) por elemento; simule ingenuamente enquanto há muitos elementos ativos e trate o caso pequeno restante à parte.",
      "K até 1e18 repetições de uma operação de subtração/redução; valores até 1e18",
      ["a_i mod x em intervalos: cada mod efetivo ao menos divide pela metade (segtree beats)", "raiz/divisão em intervalo que estabiliza rápido",
       "Euclides iterado sobre arrays"]),
    C(OT, "Com 3 elementos e ordem estável, k rodadas têm forma fechada [a, b − ka, c − kb + k(k+1)/2·a]; pula-se até a ordem mudar, num número logarítmico de saltos.",
      "Forma fechada entre eventos: pule rodadas em bloco",
      "Enquanto a ordem/estrutura não muda, k rodadas aplicam uma transformação de forma fechada (linear ou polinomial em k); calcule quantas rodadas cabem até a estrutura mudar e pule todas de uma vez — o número de mudanças costuma ser pequeno, como no Euclides.",
      "simulação com K enorme, poucos elementos e transformação fixa entre eventos",
      ["Euclides: subtrações repetidas viram mod", "simular partículas pulando direto até a próxima colisão",
       "floor_sum / caminhada sob uma reta com saltos"]),
])

# ============================================================================= NAC 2026
P["nac2026-A"] = KEEP([
    C(R, "Escolhem-se valores para que, quando u rouba, todos os vizinhos estejam empatados em T_u; o processo fica previsível e cada aresta dá relações lineares.",
      "Construa forçando empates",
      "Para controlar um processo que escolhe 'o máximo' com empates, projete os valores para que todos os candidatos estejam empatados no momento da escolha: o processo passa a agir sobre todos e as condições viram igualdades lineares.",
      "processo com regra de máximo/empate e liberdade para escolher os valores iniciais",
      ["construir entrada em que uma regra de escolha atinge todos os candidatos"], specific=True),
    C(E, "Com d_1 = T_1 = 0, propagam-se as relações por DFS e no fim desloca-se tudo para [N, 2N−1].",
      "Restrições de diferença em árvore: fixe a raiz e propague",
      "Se cada aresta impõe uma relação x_v = x_u + c com c conhecido, numa árvore todos os valores ficam determinados a partir da raiz: fixe a raiz em 0, propague por DFS e no final translade tudo para caber na faixa pedida (é possível sse max − min cabe na faixa).",
      "construir valores em árvore com faixa permitida [L, R]; condições locais por aresta que fixam diferenças",
      ["potenciais em grafo: diferenças por aresta, consistência checada nos ciclos", "atribuir alturas/pesos com diferença fixa por aresta",
       "sistemas de restrições de diferença com igualdades"]),
])

P["nac2026-B"] = KEEP([
    A(D, "Busca binária no tempo final t.", "Busca binária na resposta"),
    B(R, "Linha do tempo mod d: arestas de chefe f_i → f_i + w e de espera j → j + 1 com multiplicidades dadas por t; uma agenda válida é uma trilha euleriana de 0 até t mod d.",
      "Caminho euleriano", "Agenda como trilha euleriana com multiplicidades",
      "Se uma agenda é uma sequência de ações que avançam um 'relógio mod d' por saltos fixos, cada ação deve ser usada um número dado de vezes e só importa o encadeamento, então existe agenda sse o multigrafo (vértices = resíduos, arestas = ações com multiplicidade) tem trilha euleriana do início ao fim: balanço de graus + conectividade.",
      "Pelo teorema de Euler, um multigrafo dirigido conexo com entrada = saída exceto no início/fim tem trilha que usa cada aresta exatamente uma vez — a ordem é livre, só contam as multiplicidades.",
      "eventos periódicos mod d, ações com recarga/salto fixo, 'usar cada coisa exatamente uma vez' encadeando estados",
      ["sequência de De Bruijn", "reconstruir string a partir de todos os seus k-mers", "agendas cíclicas com transições fixas"]),
    N(OT, "O ciclo de d resíduos é comprimido em O(n) pontos de evento."),
    A(E, "Conectividade das arestas usadas.", "DSU"),
])

P["nac2026-C"] = KEEP([
    C(D, "Sempre há ótimo que não usa alguma aresta do ciclo; ao girar a aresta removida pelo ciclo, cada par troca de arco uma vez.",
      "Grafo unicíclico: gire a aresta removida do ciclo",
      "Num grafo com exatamente um ciclo, remover uma aresta do ciclo dá uma árvore e costuma haver ótimo que não usa alguma delas. Em vez de recalcular para cada aresta removida, ande pelo ciclo: ao passar a aresta removida adiante, só os itens cujo caminho a usava trocam para o outro arco, e cada item troca O(1) vezes.",
      "n vértices e n arestas (pseudoárvore); cada demanda escolhe um dos dois arcos do ciclo",
      ["distâncias/caminhos em grafo unicíclico", "conectar pares num anel escolhendo um dos dois arcos",
       "array circular: girar o ponto de corte mantendo estrutura"]),
    A(E, "União dos caminhos nas árvores penduradas marcada com HLD + atribuição em intervalo.", "HLD"),
    B(E, "Segment tree com add em intervalo que soma os pesos das arestas de cobertura positiva usando (mínimo, peso do mínimo).",
      "Segment tree com lazy", "Cobertura positiva via (mínimo, contagem do mínimo)",
      "Com add em intervalo (cobertura sobe e desce arbitrariamente) e consulta 'peso total com cobertura > 0', guarde em cada nó o mínimo da cobertura e o peso dos elementos que atingem esse mínimo; coberto = total − (peso do mínimo, se o mínimo é 0).",
      "A cobertura nunca é negativa, então o valor 0 só pode aparecer como mínimo; (mínimo, contagem) se combina e se atualiza com lazy de soma.",
      "contar posições/comprimento cobertos por ≥ 1 intervalo, ou quantos zeros há, sob add em intervalo",
      ["área da união de retângulos", "contar subarrays com max − min = r − l", "número de zeros num array com add em intervalo"],
      known=["Codeforces 526F — Pudding Monsters"]),
])

P["nac2026-D"] = KEEP([
    C(O, "Se a soma é exatamente N − 1, só uma rotação cíclica da ordem nunca trava (lema do ciclo), então a resposta é 1/N.",
      "Lema do ciclo: exatamente uma rotação funciona",
      "Se uma sequência de passos inteiros ≥ −1 soma −1, exatamente uma de suas n rotações cíclicas tem todas as somas de prefixo próprias ≥ 0 (o processo nunca trava antes do fim). Para uma ordem aleatória com orçamento justo, a probabilidade de sucesso é 1/n; para contar, divida por n.",
      "processo de saldo (ganha − gasta) que não pode zerar antes do fim, ordem aleatória, total exatamente o mínimo necessário",
      ["contar sequências de parênteses/Catalan pelo lema do ciclo", "contar árvores via sequências de Łukasiewicz",
       "problema do escrutínio (ballot): passeio que fica sempre positivo"]),
    N(E, "Com folga, cartas de valor 1 são neutras e a ordem de jogo é fixa; DP sobre (zeros, dois, três) já sacados, parando quando os saques zeram ou cobrem o resto."),
])

P["nac2026-E"] = DROP("contar inversões (A antes de C/K); cada troca adjacente remove exatamente uma; {top}")

P["nac2026-F"] = KEEP([
    A(R, "a = x + y, b = x − y: Manhattan vira max(|Δa|, |Δb|).", "Rotação 45° (Manhattan → Chebyshev)"),
    A(D, "Busca binária no tempo t.", "Busca binária na resposta"),
    C(D, "(a_i − a_j) ≤ t(v_i + v_j) para todos os pares ⇔ max_i(a_i − t·v_i) ≤ min_j(a_j + t·v_j): checagem O(n).",
      "Busca binária na razão separa a condição par a par",
      "Para max sobre pares de (a_i − a_j)/(v_i + v_j) — razão cujo numerador e denominador somam termos de cada elemento —, fixe t: a desigualdade se separa em (a_i − t v_i) ≤ (a_j + t v_j), e 'vale para todos os pares' vira max_i(…) ≤ min_j(…), em O(n) em vez de O(n²).",
      "maximizar/minimizar razão de somas sobre pares ou subconjuntos",
      ["subconjunto de melhor razão Σa/Σb (Dinkelbach / busca binária)", "ciclo de média mínima (busca binária + Bellman-Ford)",
       "maior tempo de encontro entre pares com velocidades"]),
], reason="fácil, mas separar a razão por busca binária (C) é uma técnica geral")

P["nac2026-G"] = KEEP([
    N(R, "Cada leitura define um semicírculo (raio = distância à gema conhecida mais próxima) que deve conter sua gema, e as gemas seguem a ordem das leituras em x."),
    C(O, "Se as gemas conhecidas respeitam a ordem, as desconhecidas sempre podem ser completadas; logo cada desconhecida é otimizada sozinha, só com as leituras conhecidas vizinhas.",
      "Completação sempre existe ⇒ otimize cada incógnita isoladamente",
      "Quando se prova que, respeitadas restrições globais simples (ordem, por exemplo), as demais incógnitas sempre admitem uma completação canônica, o ótimo de cada incógnita depende só das restrições locais (vizinhos conhecidos mais próximos): calcule cada uma independentemente.",
      "'para cada desconhecido, o maior/menor valor possível, independentemente dos outros'; garantia de consistência no enunciado",
      ["preencher '?' com restrições entre vizinhos maximizando cada posição", "faixa possível de cada variável em restrições de diferença",
       "reconstrução de permutação parcial com valores extremos por posição"]),
    C(E, "Testa-se o ponto mais baixo do semicírculo e suas interseções com os semicírculos conhecidos vizinhos.",
      "Ótimo em região de discos: extremos e interseções",
      "Para otimizar uma coordenada numa região dada por interseção/diferença de discos, os candidatos são o ponto extremo de cada disco nessa direção e os pontos de interseção entre pares de fronteiras; teste a viabilidade de cada candidato.",
      "região descrita por vários círculos/semicírculos e 'ponto mais fundo/alto/distante possível'",
      ["ponto mais baixo na interseção de discos", "círculo mínimo determinado por 2–3 pontos", "local de antena que maximiza uma coordenada sob alcances"]),
])

P["nac2026-H"] = DROP("interativo direto: valores extremos decodificam cada posição; {top}")
P["nac2026-I"] = DROP("só o resto mod 5 importa; pareamento direto 3+4, 3+3, 4+4+4; {top}")

P["nac2026-J"] = KEEP([
    C(O, "Em cada bloco fundido ótimo, as peças de largura máxima e de altura máxima ficam nas extremidades, então as transições só dependem de dp_j + w_i·h_j ou dp_j + w_j·h_i.",
      "Blocos com custo por máximos: os máximos ficam nas pontas",
      "Se o valor de um bloco é f(max a, max b) e os blocos podem ser recortados livremente, existe ótimo em que os elementos que realizam os máximos estão nas extremidades de cada bloco (senão, separar as sobras não piora); assim a transição da DP de partição depende só dos extremos j e i.",
      "particionar array em segmentos com custo dependente de máximos de duas grandezas",
      ["partição em segmentos com custo max·comprimento", "fundir retângulos/caixas adjacentes com custo por máximos"]),
    A(OT, "Transições dp_j + w_i·h_j otimizadas com Li Chao (retas de j, intercepto dp_j).", "Convex hull trick / Li Chao"),
    C(R, "No círculo, a primeira jelly de largura máxima está numa ponta do seu bloco: basta testar as duas rotações que a colocam numa borda.",
      "Tirar a circularidade cortando num elemento que fica na borda",
      "Para linearizar uma partição circular em blocos, prove que algum elemento distinguido (o máximo, o primeiro máximo) está sempre na ponta do seu bloco; então basta abrir o círculo começando/terminando nele (1–2 rotações) em vez de testar n cortes.",
      "array circular particionado em segmentos contíguos",
      ["partição circular de custo ótimo cortando no elemento máximo", "DP de intervalos circular",
       "rotas circulares: escolher um ponto de corte canônico"]),
])

P["nac2026-K"] = DROP("a resposta é sempre N − 1 ou impossível; enumerar retas candidatas por pares de vértices; {top}")

P["nac2026-L"] = KEEP([
    C(O, "Compor com a transposição (a b) muda o número de ciclos em ±1 conforme a e b estejam no mesmo ciclo; com elementos em ciclos distintos, várias transposições somam.",
      "Transposição muda o número de ciclos em ±1",
      "Compor uma permutação com a transposição (a b) une os ciclos de a e b se estão em ciclos diferentes (−1 ciclo) e divide o ciclo se estão no mesmo (+1). Assim 'número de ciclos' responde 'a e b estão no mesmo ciclo?', e várias transposições entre ciclos distintos mudam a contagem pela quantidade de uniões.",
      "consultas que devolvem número de ciclos/componentes de uma permutação; mínimo de trocas para ordenar",
      ["mínimo de trocas para ordenar uma permutação = n − #ciclos", "paridade de permutação pelo número de ciclos",
       "manter ciclos sob swaps com DSU"]),
    C(E, "Insere-se um elemento por vez, fazendo busca binária sobre os ciclos atuais (uma consulta com trocas em lote por metade) para achar a qual ele se junta.",
      "Inserção incremental com busca binária sobre grupos",
      "Para reconstruir uma estrutura oculta com ~n log n consultas, insira os elementos um a um e, para cada novo, faça busca binária sobre os grupos já identificados usando uma consulta que testa 'ele pertence a algum grupo deste subconjunto?' (perguntas em lote).",
      "interativo com orçamento ≈ Σ log2 i consultas e consultas sobre conjuntos",
      ["descobrir componentes de grafo oculto com consultas de conjunto", "ordenar com consultas de comparação (inserção binária)",
       "achar classes de equivalência interativamente"]),
    A(E, "Busca binária sobre os grupos com uma consulta por metade.", "Busca interativa (bisseção)"),
])

P["nac2026-M"] = KEEP([
    A(D, "Viabilidade monótona no número de voltas r: busca binária.", "Busca binária na resposta"),
    C(O, "Para r fixo, o tipo i é atendível sse min(a_i, só-Alice) + min(b_i, só-Bob) + compartilhados ≥ a_i + b_i.",
      "Dois consumidores com exclusivos e compartilhados (Hall para 2)",
      "Com dois consumidores, cada um com recursos exclusivos e um pool compartilhado, a demanda é atendível sse min(a, A_excl) + min(b, B_excl) + compartilhado ≥ a + b: use primeiro os exclusivos, e o que falta sai do compartilhado (a condição de Hall reduzida a 3 desigualdades).",
      "dois agentes e itens que só um alcança ou que ambos alcançam",
      ["dois trabalhadores com tarefas exclusivas e compartilhadas", "fluxo bipartido com 2 nós de um lado (corte mínimo em fórmula fechada)",
       "dividir recursos entre duas filas com parte flexível"]),
    N(E, "Custo mínimo: ordenar pratos por preço e preencher primeiro a demanda exclusiva, depois a compartilhada."),
])


# ----------------------------------------------------------------------------- build + validate
def _parse_dataset(s):
    s = s[s.index("{"): s.rstrip().rstrip(";").rindex("}") + 1]
    return json.loads(s)


def load_dataset():
    """Real dataset for difficulty data; if the working copy is a mock, use the committed one."""
    d = _parse_dataset(open(DATASET, encoding="utf-8").read())
    if d.get("mock"):
        import subprocess
        s = subprocess.run(["git", "-C", ROOT, "show", "HEAD:data/dataset.js"], capture_output=True,
                           check=True).stdout.decode("utf-8")
        d = _parse_dataset(s)
        if d.get("mock"):
            sys.exit("data/dataset.js (working copy e HEAD) é mock; rode build_dataset.py antes")
        print("aviso: data/dataset.js é mock; usando a versão de HEAD para os dados de dificuldade")
    return {p["id"]: p for p in d["problems"]}


def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    ids = [p["id"] for p in raw["problems"]]
    ds = load_dataset()
    errors = []

    missing = [i for i in ids if i not in P]
    extra = [i for i in P if i not in ids]
    if missing:
        errors.append(f"ids faltando: {missing}")
    if extra:
        errors.append(f"ids desconhecidos: {extra}")

    allowed_a = set(CANON_A) | set(NEW_A)
    used_new = set()
    out = []
    cnt = {"A": 0, "B": 0, "C": 0, None: 0}
    spec_cnt = 0
    for pid in ids:
        e = dict(P[pid])
        if not e["keep"]:
            q = ds.get(pid, {})
            top = f"{q.get('solved_top')}/{q.get('k_used')} dos top-40 resolveram"
            out.append({"id": pid, "keep": False, "discard_reason": e["discard_reason"].replace("{top}", top)})
            continue
        if ds.get(pid, {}).get("difficulty") == "easy" and not e.get("keep_reason"):
            errors.append(f"{pid}: fácil mantido sem keep_reason")
        if not e["steps"]:
            errors.append(f"{pid}: sem passos")
        for st in e["steps"]:
            if st["kind"] not in KINDS:
                errors.append(f"{pid}: kind inválido {st['kind']}")
            cat = st["cat"]
            if cat not in ("A", "B", "C", None):
                errors.append(f"{pid}: cat inválido {cat}")
            cnt[cat] += 1
            if cat == "A":
                if st["technique"] not in allowed_a:
                    errors.append(f"{pid}: técnica não canônica {st['technique']}")
                if st["technique"] in NEW_A:
                    used_new.add(st["technique"])
            if cat == "B":
                need = ["base", "name", "property", "why", "signal", "contexts", "specific"]
                if st["base"] not in allowed_a:
                    errors.append(f"{pid}: base não canônica {st['base']}")
            if cat == "C":
                need = ["name", "statement", "signal", "contexts", "known_problems", "specific"]
            if cat in ("B", "C"):
                for k in need:
                    if k not in st:
                        errors.append(f"{pid}: falta {k}")
                if st["specific"]:
                    spec_cnt += 1
                elif len(st["contexts"]) < 2:
                    errors.append(f"{pid}: {st['name']} com < 2 contextos e specific=false")
                for w in FORBIDDEN:
                    if re.search(r"\b" + re.escape(w) + r"\b", st["name"], re.I):
                        errors.append(f"{pid}: rótulo proibido '{w}' em {st['name']}")
        out.append({"id": pid, **e})

    if errors:
        print("ERROS:")
        for x in errors:
            print(" -", x)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"group": "nac", "problems": out}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    kept = sum(1 for x in out if x["keep"])
    print(f"ok: {len(out)} problemas, {kept} mantidos, {len(out) - kept} descartados")
    print(f"passos: A={cnt['A']} B={cnt['B']} C={cnt['C']} sem categoria={cnt[None]}; specific={spec_cnt}")
    print(f"novos nomes A usados: {sorted(used_new)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
