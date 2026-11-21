# -*- coding: utf-8 -*-
"""Curriculum v2 - decomposition for group "lac_apac" (LAC 2024-2026, Regional LATAM 2024-2025,
APAC 2024-2026). Holds the data by hand (reviewable) and writes
pipeline/curriculum/steps_lac_apac.json, then validates it.

Run: python -I pipeline/scripts/curriculum_steps_lac_apac.py  (from the repo root)
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "pipeline", "curriculum", "steps_lac_apac.json")

CANONICAL_A = """BFS, BFS 0-1, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Ordenação topológica, SCC (Tarjan/Kosaraju),
Pontes e articulações, Componentes biconexas, Caminho euleriano, 2-SAT, MST (Kruskal/Prim), DSU,
DSU com rollback, LCA (binary lifting), HLD, Centroid decomposition, Small-to-large, Euler tour em árvore,
Matching bipartido (Kuhn/Hopcroft-Karp), Blossom, Fluxo máximo (Dinic), Corte mínimo, Fluxo de custo mínimo,
Segment tree, Segment tree com lazy, Segment tree persistente, BIT, BIT 2D, Sparse table, Sqrt decomposition,
Mo's algorithm, Treap, Soma de prefixos, Array de diferenças, Pilha monotônica, Deque monotônico,
Dois ponteiros, Busca binária na resposta, Busca ternária, Meet in the middle, Backtracking com poda,
DP com bitmask, SOS DP, DP em dígitos, DP em árvore, Rerooting, DP de intervalos, Mochila, LIS,
Convex hull trick / Li Chao, Divide and conquer DP, Knuth, Slope trick, Matrix exponentiation,
KMP, Função Z, Manacher, Hashing de strings, Suffix array + LCP, Suffix automaton, Aho-Corasick, Trie,
Crivo de Eratóstenes, Fatoração, Euclides estendido, Inverso modular, CRT, Exponenciação rápida,
Binomiais mod p, Inclusão-exclusão, Möbius, Burnside, Eliminação gaussiana, Base XOR, FFT/NTT,
Valor esperado por linearidade, Sprague-Grundy, Produto vetorial / orientação, Convex hull,
Interseção de segmentos, Sweep line, Ordenação angular, Rotating calipers, Shoelace (área),
Rotação 45° (Manhattan → Chebyshev), Busca interativa (bisseção)"""
CANON = {s.strip() for s in CANONICAL_A.replace("\n", " ").split(", ")}
# New A names added by this group (nothing canonical fit):
NEW_A = {"Bipartição (2-coloração)", "Redução série-paralela"}

FORBIDDEN = ["construtivo", "ad hoc", "análise de casos", "observação", "greedy", "matemática",
             "implementação"]

UNVERIFIED = " (ideia de raciocínio próprio, não verificada contra solução do júri)"


# ---------------------------------------------------------------- helpers
def A(kind, text, technique):
    return {"kind": kind, "text": text, "cat": "A", "technique": technique}


def N(kind, text):
    return {"kind": kind, "text": text, "cat": None}


def B(kind, text, base, name, prop, why, signal, contexts, specific=False):
    return {"kind": kind, "text": text, "cat": "B", "base": base, "name": name, "property": prop,
            "why": why, "signal": signal, "contexts": contexts, "specific": specific}


def C(kind, text, name, statement, signal, contexts, known=None, specific=False):
    return {"kind": kind, "text": text, "cat": "C", "name": name, "statement": statement,
            "signal": signal, "contexts": contexts, "known_problems": known or [],
            "specific": specific}


KEEP = {}      # id -> (keep_reason or None, steps)
DISCARD = {}   # id -> reason (top-40 stats are appended automatically)

# ======================================================================= LAC 2024
KEEP["lac2024-A"] = (None, [
    A("reformulação", "Largura(t) = max(X+VX·t) − min(X+VX·t) é a diferença entre o envelope superior e o "
      "inferior de N retas; idem para a altura.", "Convex hull trick / Li Chao"),
    C("observação-chave", "A área é o produto largura·altura; em cada trecho entre breakpoints dos envelopes é "
      "produto de duas funções lineares positivas, logo monótona ou côncava, e o mínimo está num breakpoint "
      "(ou em t=0).",
      "Ótimo em breakpoint de função linear por partes",
      "Se a função objetivo é montada a partir de peças simples entre O(n) pontos de quebra e em cada peça o "
      "extremo procurado cai na borda (peça monótona ou côncava para mínimo), então o ótimo global está num "
      "ponto de quebra: enumere-os. Não use busca ternária quando a função é produto/combinação não convexa "
      "de convexas — ela não é unimodal.",
      "pontos em movimento linear no tempo; minimizar área/produto de duas grandezas que são max/min de "
      "funções lineares",
      ["minimizar perímetro ou diâmetro de pontos que se movem linearmente",
       "programação linear em 1 variável: ótimo num vértice (ponto de quebra)",
       "minimizar custo total por partes como Σ|x−a_i|·w_i (ótimo num a_i)"]),
    N("estrutura/algoritmo", "Calcular os breakpoints dos 4 envelopes por ordenação de inclinações e avaliar a "
      "área em cada um: O(N log N)."),
])

KEEP["lac2024-B"] = (None, [
    N("reformulação", "Uma estratégia é uma árvore de decisão sobre os resultados das fases (qual estratégia "
      "usar e quando reiniciar)."),
    C("observação-chave", "Como reiniciar custa 'o valor esperado ótimo E' (que é a resposta), chuta-se E, "
      "calcula-se por DP em (fase, tempo gasto) o custo esperado f(E) quando reiniciar vale E, e busca-se o "
      "ponto fixo f(E)=E.",
      "Chutar a resposta como custo do reinício (ponto fixo)",
      "Se o processo ótimo pode 'voltar ao começo' e o custo de voltar é a própria resposta desconhecida E, "
      "trate E como parâmetro: com E fixo a DP fica acíclica (reiniciar = pagar E); f(E) é monótona com "
      "inclinação < 1, então a resposta é o ponto fixo f(E)=E, achado por busca binária.",
      "valor esperado com opção de reiniciar/desistir e recomeçar; estados que voltam ao estado inicial",
      ["jogo de speedrun com reset (CF 865C Gotta Go Fast)",
       "cadeias de Markov em que toda falha volta ao início",
       "otimização de razão (Dinkelbach): chutar a razão λ e testar sinal de custo − λ·peso"],
      ["Codeforces 865C — Gotta Go Fast"]),
    A("otimização", "Busca binária em E com DP sobre (nível, tempo) para cada chute.", "Busca binária na resposta"),
])

KEEP["lac2024-C"] = (None, [
    B("reformulação", "Colocar pedras adjacentes sem repetir casa é geografia não dirigida em vértices; a "
      "grade é bipartida.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)", "Geografia em grafo ⇔ emparelhamento máximo",
      "Com a ficha em v e o jogador X a mover (para vizinho não visitado; quem não pode mover perde), X vence "
      "sse v pertence a TODO emparelhamento máximo.",
      "Se v está em todo M máximo, X responde sempre com o par em M do vértice atual; se o oponente chegasse "
      "a um vértice livre, o caminho percorrido seria alternante e trocá-lo daria um M máximo sem v. Se existe "
      "M máximo sem v, o oponente usa essa estratégia: todo vizinho escolhido por X está emparelhado (senão M "
      "aumentaria) e ele responde com o par.",
      "jogo de dois jogadores que movem uma ficha para casa vizinha nunca visitada; perde quem não pode mover",
      ["jogo de cavalo/rei em tabuleiro sem repetir casas", "geografia em grafo geral (com Blossom)",
       "contar posições iniciais vencedoras em grade com obstáculos"]),
    B("estrutura/algoritmo", "Os vértices perdedores para o segundo jogador são os alcançáveis por caminho "
      "alternante a partir de vértices livres do mesmo lado.",
      "Matching bipartido (Kuhn/Hopcroft-Karp)", "Vértices que estão em todo emparelhamento máximo",
      "Dado um emparelhamento máximo M, v (do lado L) fica de fora de algum emparelhamento máximo sse v é "
      "livre ou é alcançável de um vértice livre de L por caminho alternante de comprimento par; basta uma "
      "BFS no grafo residual a partir da fonte (lado L) e do sorvedouro (lado R).",
      "Deslizar M ao longo de um caminho alternante par que começa num livre troca qual vértice fica livre "
      "sem mudar |M|; reciprocamente, a diferença simétrica entre M e um M' que evita v contém esse caminho.",
      "pergunta sobre quais vértices/arestas são obrigatórios, opcionais ou proibidos em emparelhamentos "
      "máximos",
      ["arestas que pertencem a algum emparelhamento máximo (decomposição de Dulmage–Mendelsohn)",
       "posições vencedoras em jogos de emparelhamento",
       "verificar unicidade do emparelhamento máximo"]),
    A("estrutura/algoritmo", "Emparelhamento máximo na grade (até 2500 vértices).", "Matching bipartido (Kuhn/Hopcroft-Karp)"),
])

DISCARD["lac2024-D"] = "jogo resolvido por fatoração e poucos casos; fácil para o top"

KEEP["lac2024-E"] = (None, [
    C("observação-chave", "Dois clientes podem dividir uma fila LIFO sse seus intervalos [entrada, saída] não se "
      "cruzam (aninhados ou disjuntos).",
      "Pilha (LIFO) ⇔ intervalos aninhados",
      "Uma sequência de entradas/saídas é válida para uma única pilha sse os intervalos (push, pop) formam "
      "uma família laminar — nenhum par se cruza (+a +b −a −b). Conflito em pilha é sempre um par cruzado.",
      "eventos de entrar/sair com regra 'último que entra, primeiro que sai'; arcos/parênteses",
      ["validar sequência de parênteses com vários tipos", "desenhar arcos de um lado de uma reta sem "
       "cruzamento (book embedding)", "ordenar com pilhas (two-stack sorting)"],
      ["NOIP 2008 — Twin Stack Sorting"]),
    C("redução", "Montar o grafo de conflitos (pares que se cruzam) e 2-colori-lo; as cores são as filas.",
      "Dois recipientes + conflitos par a par ⇒ 2-coloração",
      "Se cada item vai para um de dois recipientes e as restrições são só 'i e j não podem ficar juntos', "
      "construa o grafo de conflitos: há solução sse ele é bipartido, e as cores são a atribuição. Se as "
      "restrições forem implicações mais gerais entre pares, use 2-SAT.",
      "exatamente 2 opções por item (duas filas, dois lados, dois turnos) e restrições entre pares",
      ["dividir pessoas em dois grupos sem inimigos juntos", "arcos em duas páginas sem cruzamento",
       "atribuir aulas a duas salas sem sobreposição incompatível"]),
    A("estrutura/algoritmo", "BFS/DFS de 2-coloração no grafo de cruzamentos, O(N²).", "Bipartição (2-coloração)"),
])

KEEP["lac2024-F"] = (None, [
    C("observação-chave", "Os andares residenciais (≥1 por projeto, sem limite superior) compensam qualquer "
      "diferença múltipla de g = gcd(R); sobra só testar se alguma diferença de térreos é ≡ 0 mod g.",
      "Coeficientes ilimitados ⇒ só o gcd importa",
      "Se você pode somar quantidades arbitrariamente grandes de valores r_i (nos dois lados de uma igualdade, "
      "ou com coeficientes grandes o bastante), toda diferença múltipla de gcd(r_i) é alcançável (Bézout com "
      "coeficientes deslocados para positivos); a restrição remanescente é só a classe módulo g.",
      "quantidades repetíveis à vontade (andares, moedas, passos de tamanho fixo) e uma igualdade/alvo a "
      "atingir",
      ["moedas de valores r_i: todo múltiplo grande de gcd é representável (Frobenius)",
       "problema dos jarros de água", "reflexões/translações que deslocam por múltiplos de g (apac2026-H)"]),
    B("otimização", "As somas de térreos alcançáveis são subset sums com soma total ≤ 2e5.",
      "Mochila", "Subset sum com O(√S) valores distintos",
      "Se a soma total dos itens é S, há no máximo ~√(2S) valores distintos; agrupando por valor e quebrando "
      "multiplicidades em potências de 2 (1,2,4,…,resto), o subset sum custa O(S√S), e O(S√S/64) com bitset.",
      "1+2+…+k ≤ S ⇒ k = O(√S); a divisão binária representa qualquer quantidade 0..c de cópias com O(log c) "
      "itens.",
      "pergunta 'quais somas são alcançáveis' com soma total limitada (≤ 1e5–1e6) e muitos itens",
      ["tamanhos de componentes de um grafo (soma = n): quais tamanhos de união são possíveis",
       "dividir em duas metades de soma próxima com soma total ≤ 1e6"]),
    A("estrutura/algoritmo", "Mochila booleana com bitset sobre os térreos.", "Mochila"),
])

KEEP["lac2024-G"] = (None, [
    A("reformulação", "Moedas esperadas = Σ (visitas esperadas a cada casa) − 1; as visitas satisfazem "
      "E = p ⋆lcm E + δ₁.", "Valor esperado por linearidade"),
    B("estrutura/algoritmo", "Aplicar a transformada 'soma sobre divisores' torna a convolução-lcm um produto "
      "ponto a ponto: T(E) = 1/(1−T(p)), depois inverter com Möbius.",
      "Möbius", "Transformada zeta sobre divisores diagonaliza convolução lcm/gcd",
      "Com T(A)_k = Σ_{d|k} A_d, vale T(A ⋆lcm B) = T(A)·T(B); com somas sobre múltiplos, o mesmo vale para "
      "convolução gcd. A inversa de T é a inversão de Möbius; ambas custam O(N log N) por soma harmônica.",
      "lcm(x,y) | k ⇔ x | k e y | k, então os pares contados em T(A⋆B)_k são exatamente produto das contagens "
      "independentes — o mesmo argumento do OR/AND com SOS DP em máscaras.",
      "operações lcm/gcd entre valores ≤ N combinadas com probabilidades ou contagens; 'gcd/lcm de pares'",
      ["contar pares (i,j) com gcd = g para todo g", "convolução OR/AND em bitmasks (SOS DP)",
       "probabilidade de o lcm/gcd de amostras aleatórias valer k"]),
])

KEEP["lac2024-H"] = (None, [
    C("reformulação", "Reverter e rotacionar geram o grupo diedral; a composição das operações i..j é "
      "P(i−1)⁻¹·P(j) com P de prefixo, e contamos pares em que isso fixa S.",
      "Contar intervalos por composição de prefixos num grupo",
      "Se as operações têm inversa (formam um grupo) e se quer contar intervalos [i..j] cuja composição cai "
      "num conjunto pequeno H, guarde as composições de prefixo P_k: comp(i..j) = P_{i−1}⁻¹·P_j ∈ H. Para cada "
      "j conte, num hashmap, os prefixos anteriores P com P = P_j·h⁻¹ para h ∈ H — generalização de "
      "'subarrays de soma zero'.",
      "contar subarrays/intervalos de operações cujo efeito combinado é neutro ou é um elemento dado",
      ["subarrays de soma 0 ou XOR 0", "substrings em que toda letra aparece um número par de vezes "
       "(máscara de paridade de prefixo)", "intervalos de permutações cuja composição é a identidade"]),
    B("observação-chave", "Reduzir S à sua raiz primitiva (menor período via KMP) para que só identidade e no "
      "máximo uma reflexão+rotação fixem S; a reflexão é achada buscando reverse(S) em S+S.",
      "KMP", "Período primitivo e rotações que fixam uma string",
      "O menor período é p = n − π[n−1] se p divide n (senão a string é primitiva); as rotações que fixam S "
      "são exatamente os múltiplos de p; uma rotação de T igual a S existe sse S ocorre em T+T.",
      "Se S = rot_k(S), então k e n são períodos, e pelo lema de Fine–Wilf gcd(k,n) também; o menor período "
      "que divide n gera todos os outros.",
      "strings sob rotação (colares, cíclicos), pergunta 'quantas rotações/reflexões deixam S igual'",
      ["contar rotações distintas de uma string (Burnside com rotações)",
       "decidir se S é potência de outra string", "testar se dois colares são iguais a menos de rotação"]),
])

KEEP["lac2024-I"] = (None, [
    B("observação-chave", "Pontos inteiros num disco de raio 1e4 têm envoltória com ~1600 vértices, o que "
      "permite O(H²) sobre pares do hull.",
      "Convex hull", "Hull de pontos inteiros tem O(C^{2/3}) vértices",
      "Um polígono convexo com vértices inteiros dentro de uma caixa/disco de lado C tem O(C^{2/3}) vértices.",
      "Arestas consecutivas têm direções distintas, e cada vetor de aresta é múltiplo de um vetor primitivo "
      "distinto; os k menores vetores primitivos somam comprimento Θ(k^{3/2}) e o perímetro é O(C), logo "
      "k = O(C^{2/3}).",
      "coordenadas inteiras pequenas (≤ 1e4–1e6) e um algoritmo quadrático/cúbico sobre vértices do hull",
      ["onion peeling/várias camadas de hull com coordenadas pequenas",
       "força bruta sobre pares de vértices do hull para maior triângulo/quadrilátero"]),
    N("observação-chave", "O ponto novo fica na circunferência; para cada par (i,j) de vértices que serão seus "
      "vizinhos, o ápice ótimo é o ponto do círculo mais distante da corda ij."),
    A("estrutura/algoritmo", "Hull + áreas por soma acumulada de trapézios para avaliar cada par em O(1).",
      "Shoelace (área)"),
])

KEEP["lac2024-J"] = (None, [
    C("observação-chave", "Ordenando recursos por B_i/A_i, existe solução ótima em que a vila A produz um "
      "prefixo e B um sufixo, com no máximo um recurso dividido.",
      "Ordenar por razão ⇒ divisão prefixo/sufixo",
      "Em alocação fracionária de itens entre dois agentes (ou recursos) com custos lineares a_i e b_i e "
      "capacidades, uma troca de vizinhos mostra que vale atribuir por ordem de a_i/b_i: um agente pega um "
      "prefixo, o outro um sufixo, e no máximo um item fica dividido (estrutura de vértice de PL com uma "
      "restrição acoplante). Enumere o item de corte.",
      "dois agentes/máquinas com custos diferentes por item, quantidades divisíveis, minimizar custo total",
      ["mochila fracionária (ordenar por valor/peso)",
       "dividir tarefas entre duas máquinas com velocidades diferentes por tarefa",
       "comércio com vantagem comparativa"]),
    A("otimização", "Para cada recurso de corte, somas de prefixo/sufixo dão as capacidades restantes em O(1).",
      "Soma de prefixos"),
])

DISCARD["lac2024-K"] = "DP/caminho curto simples em estados pequenos"
DISCARD["lac2024-L"] = "verificação direta por linha"

# ======================================================================= LAC 2025
KEEP["lac2025-A"] = (None, [
    C("reformulação", "Um passeio palíndromo cresce pelas duas pontas ao mesmo tempo: estado (u,v) = 'existe "
      "passeio palíndromo u→v'; de (u,v) vai-se a (u',v') com arestas u'→u e v→v' de mesma letra.",
      "BFS em pares de pontas para propriedades simétricas",
      "Quando uma propriedade de caminho compara as duas pontas (palíndromo, dois agentes andando juntos, "
      "equivalência de autômatos), faça BFS no grafo-produto de pares (u,v), partindo dos centros (u,u) e "
      "arestas únicas; o custo é Σ indeg(u)·outdeg(v) = O(M²).",
      "palíndromo sobre caminhos/passeios de grafo; dois tokens que precisam se mover em sincronia",
      ["menor caminho palíndromo entre 1 e n (ABC197 F)", "dois robôs que se movem simultaneamente em "
       "labirintos", "equivalência de dois DFAs por BFS em pares de estados"],
      ["AtCoder ABC197 F — Construct a Palindrome"]),
    A("estrutura/algoritmo", "BFS sobre até N² estados de par.", "BFS"),
])

KEEP["lac2025-B"] = (None, [
    N("reformulação", "Dois times disjuntos de mesmo tamanho e mesmo XOR ⇔ um subconjunto não vazio de tamanho "
      "par com XOR 0 (divida-o ao meio)."),
    C("redução", "Anexar um bit 1 a cada vetor: XOR zero nessa coordenada força tamanho par.",
      "Bit constante extra para controlar paridade de tamanho",
      "Para impor 'o subconjunto tem tamanho par' (ou ímpar) num problema de XOR/álgebra linear em GF(2), "
      "acrescente a cada vetor uma coordenada constante 1: a coordenada extra do XOR é a paridade da "
      "cardinalidade, e a restrição vira linear.",
      "XOR de subconjuntos com restrição sobre o número de elementos escolhidos",
      ["subconjunto de tamanho par com XOR 0", "contar vetores alcançáveis por XOR de pares a_i⊕a_j "
       "(apac2024-L usa 2a_i+1)", "combinações com número ímpar de termos"]),
    B("estrutura/algoritmo", "Eliminação gaussiana em GF(2) com bitsets, guardando para cada vetor da base "
      "quais originais o compõem.",
      "Base XOR", "Recuperar o subconjunto que gera a dependência",
      "Além de reduzir os vetores, mantenha para cada vetor da base um bitset de N bits com os índices "
      "originais combinados; quando um novo vetor reduz a 0, o XOR desses bitsets é o subconjunto. Com N > K+1 "
      "a dependência sempre existe.",
      "Cada passo de eliminação é um XOR, e os bitsets de índices sofrem os mesmos XORs, então representam a "
      "combinação exata; N vetores em dimensão K < N são linearmente dependentes.",
      "pedido de exibir explicitamente os elementos cujo XOR dá 0 ou um alvo",
      ["certificado de subconjunto com XOR = x", "resolver sistema GF(2) e mostrar a combinação"]),
    A("estrutura/algoritmo", "Eliminação em O(N·K²/64).", "Eliminação gaussiana"),
])

DISCARD["lac2025-C"] = "testar cada limiar de temperatura com varredura linear"

KEEP["lac2025-D"] = (None, [
    N("reformulação", "Peso em vértice vira peso em aresta: w(u,v) = max(D_u, D_v); f(u,v) é o gargalo minimax."),
    C("observação-chave", "Unindo componentes em ordem crescente de peso, todos os pares que se conectam na "
      "união de A e B com peso w têm f = w.",
      "Gargalo de todos os pares na ordem das uniões",
      "Se o valor de um par é o max (ou min) dos pesos no melhor caminho, processe arestas em ordem de peso "
      "com DSU: na união de componentes A e B com peso w, exatamente os |A|·|B| pares novos recebem valor w. "
      "Somas sobre todos os pares saem direto; somas por vértice pedem a árvore de reconstrução.",
      "soma/contagem sobre todos os pares de 'max da aresta no caminho' ou 'menor gargalo'",
      ["soma do maior peso de aresta sobre todos os caminhos de uma árvore",
       "contar pares cujo caminho minimax ≤ k", "contribuição de cada elemento como mínimo de subarrays"]),
    B("estrutura/algoritmo", "Construir a árvore de reconstrução de Kruskal e somar, ao longo do caminho de cada "
      "folha até a raiz, (folhas(v_i) − folhas(v_{i+1}))·w(v_i).",
      "MST (Kruskal/Prim)", "Árvore de reconstrução de Kruskal",
      "Cada união do Kruskal cria um nó novo com o peso da aresta e os dois componentes como filhos. O gargalo "
      "minimax entre u e v é o peso do LCA; os vértices alcançáveis a partir de u usando pesos ≤ w formam a "
      "subárvore do ancestral mais alto de u com peso ≤ w.",
      "Os pesos crescem da folha para a raiz (uniões em ordem), e u,v ficam conectados exatamente na união "
      "representada pelo LCA.",
      "consultas 'a partir de u, quem é alcançável usando arestas ≤ w' ou gargalo entre pares, muitas vezes "
      "online",
      ["consultas online de alcance com limite de peso (IOI 2018 Werewolf)",
       "k-ésimo maior entre os vértices alcançáveis com peso ≤ w (persistente sobre a ordem de folhas)"],
    ),
    A("estrutura/algoritmo", "DSU para montar a árvore e uma DFS para as somas.", "DSU"),
])

KEEP["lac2025-E"] = (None, [
    C("observação-chave", "Uma empresa em B está num caminho entre dois patrocinadores sse há patrocinadores em "
      "pelo menos duas componentes de T − B (ou em B).",
      "Vértice entre dois pontos ⇔ conjunto toca ≥ 2 ramos",
      "Em árvore, v está no caminho entre dois vértices de um conjunto S (ou em S) sse S intersecta pelo menos "
      "duas componentes de T − v. Testa-se com Euler tour: cada componente é uma subárvore de filho ou o "
      "complemento da subárvore de v.",
      "pergunta se um vértice 'fica entre' membros de um conjunto em árvore, ou pertence à menor subárvore "
      "que os conecta",
      ["vértices da árvore de Steiner/árvore virtual de um conjunto",
       "contar vértices cobertos por caminhos entre pares de marcados"]),
    C("redução", "Para cada empresa, os patrocinadores mais próximos à esquerda/direita na ordem de propostas "
      "definem pares (início, fim) inválidos; varre-se o início mantendo o primeiro fim inválido.",
      "Restrições como regiões no plano (início, fim) + varredura",
      "Para achar, para cada início i, o maior fim válido (ou contar intervalos válidos), transforme cada "
      "'testemunha' de invalidade num retângulo/faixa de pares (L,R) proibidos; varra L e mantenha numa "
      "segment tree com lazy (soma de proibições + primeira posição positiva) quais R estão bloqueados.",
      "'para todo início, maior intervalo válido' com validade que depende de pares de elementos do intervalo",
      ["contar subarrays com todos os elementos distintos/sem par proibido",
       "para cada L, menor R tal que o subarray contém todas as cores"]),
    A("estrutura/algoritmo", "Euler tour para testar subárvores.", "Euler tour em árvore"),
    A("estrutura/algoritmo", "Segment tree com lazy indexada pelo fim do intervalo.", "Segment tree com lazy"),
])

KEEP["lac2025-F"] = (None, [
    A("estrutura/algoritmo", "Sem remoções: range chmax de altura + range min de consulta.", "Segment tree com lazy"),
    B("redução", "Remoções tratadas offline: cada retângulo vive num intervalo de tempo e é inserido em O(log N) "
      "nós de uma segment tree sobre o tempo; DFS com estrutura que desfaz mudanças.",
      "Segment tree", "Segment tree sobre o tempo (remoções offline)",
      "Se a estrutura suporta inserir e desfazer a última inserção (pilha de alterações), ela passa a suportar "
      "remoções arbitrárias offline: cada elemento ativo em [t1,t2) vai para os O(log T) nós canônicos; "
      "uma DFS aplica as inserções ao entrar no nó, responde consultas nas folhas e desfaz ao sair. Custo "
      "extra: fator log.",
      "Todo intervalo de tempo se decompõe em O(log T) nós; na folha t estão aplicados exatamente os elementos "
      "vivos em t, e o desfazer em ordem de pilha restaura o estado do pai.",
      "inserções e remoções intercaladas com consultas, numa estrutura que só sabe inserir (DSU, base XOR, "
      "chmax)",
      ["conectividade dinâmica offline com DSU com rollback (CF 1140F)",
       "base XOR com remoções", "bipartição dinâmica de grafo offline"],
    ),
])

KEEP["lac2025-G"] = (None, [
    N("observação-chave", "Se o tabuleiro nunca tem buracos, ele é descrito só pelas alturas das colunas; peça "
      "horizontal é segura sse as alturas no seu vão são todas iguais."),
    C("estrutura/algoritmo", "Manter as alturas como conjunto de intervalos [l,r,h] num map ordenado, com "
      "atribuição em intervalo.",
      "Map de intervalos constantes (amortizado)",
      "Para um array com 'atribuir valor a um intervalo' e consultas sobre intervalos, guarde-o como intervalos "
      "maximais constantes num map ordenado: cada atribuição corta no máximo 2 intervalos e apaga os do meio, "
      "então o total de intervalos criados é O(operações) e o custo amortizado é O(log n). Funciona com "
      "coordenadas até 1e18 sem compressão.",
      "atribuição/pintura de intervalos com coordenadas enormes, consulta 'tudo igual?' ou 'quantas cores'",
      ["pintar segmentos de uma cerca e contar comprimento por cor",
       "Chtholly tree (atribuições aleatórias)", "manter intervalos livres/ocupados de memória"]),
])

KEEP["lac2025-H"] = (None, [
    C("observação-chave", "De uma solução ótima com k estrelas chega-se a uma ótima com k+1 por uma troca local "
      "de poucos tipos (+1; +2/−1; +3/−2; +3/−1/−1; +2/+2/−3).",
      "Ótimo incremental por trocas locais finitas",
      "Quando se pede o ótimo para todo k e cada item tem poucos níveis (pesos 1..3), prove que ótimo(k+1) "
      "difere de ótimo(k) por um conjunto finito de trocas pequenas; mantenha um heap/set por tipo de "
      "candidato (por estado do item) e aplique sempre a troca mais barata.",
      "'para todo k = 1..n·c, custo mínimo de exatamente k unidades' com itens de poucos níveis e custos não "
      "convexos",
      ["mochila com pesos 1 e 2 para todas as capacidades",
       "escolher k itens com custos que dependem de níveis (comprar 1, 2 ou 3 unidades)"]),
])

KEEP["lac2025-I"] = (None, [
    C("reformulação", "Como os valores de P são distintos, um subarray comum das repetições infinitas é uma "
      "corrida em A (lido duas vezes) em que cada elemento é o sucessor cíclico do anterior em P.",
      "Elementos distintos ⇒ sequência = função sucessor",
      "Se os elementos de uma sequência são distintos, ela é determinada por next[valor] (lista ligada indexada "
      "pelo valor): 'x seguido de y aparece em P' vira next[x]=y em O(1), e inserir antes/apagar em P é O(1). "
      "Comparar com outra sequência vira varrer pares consecutivos.",
      "permutação/sequência de valores distintos com inserções e remoções e consultas de 'aparece "
      "consecutivo'",
      ["maior subarray comum entre duas permutações (pares consecutivos)",
       "verificar se B é subarray de uma permutação dinâmica", "simular fila/roda com remoções por valor"]),
    N("observação-chave", "Se A contém um ciclo completo consistente de P, a resposta é infinita (*)."),
])

KEEP["lac2025-J"] = (None, [
    N("reformulação", "Cone com vértice na origem ⇔ calota esférica após projetar as estrelas na esfera unitária."),
    B("estrutura/algoritmo", "Candidatos ao maior cone vazio são as faces do hull 3D dos pontos projetados.",
      "Convex hull", "Hull 3D de pontos na esfera = Delaunay esférico",
      "Para pontos sobre uma esfera, um plano que deixa todos de um lado corta uma calota vazia; os planos "
      "suporte que tocam 3 pontos são as faces do hull 3D, e a maior calota vazia limitada por 3 pontos é uma "
      "delas (círculos vazios ⇔ faces, como na triangulação de Delaunay).",
      "A interseção esfera ∩ semiespaço é uma calota; 'calota vazia' ⇔ 'plano com todos os pontos do mesmo "
      "lado' ⇔ plano suporte do hull.",
      "pontos em direções 3D, ângulos a partir da origem, maior círculo/calota vazia",
      ["Delaunay 2D por lifting (x,y) → (x,y,x²+y²) e hull 3D", "maior círculo vazio entre pontos"]),
    C("observação-chave", "A calota ótima é tocada por 3 pontos (ou 2 com centro restrito); enumere essas "
      "configurações e verifique o vazio — O(n³)·O(n) como alternativa.",
      "Ótimo geométrico fixado por poucas restrições ativas",
      "Em problemas de maior círculo/esfera vazia, menor círculo envolvente ou maior figura dentro de região, "
      "o ótimo é tocado por 2–3 objetos (pontos/bordas). Enumere as figuras definidas por cada dupla/tripla "
      "de restrições, verifique a validade de cada uma e fique com a melhor; complexidade polinomial pequena "
      "se n ≤ 50–500.",
      "maior/menor círculo, esfera ou cone com condição de vazio/cobertura e n pequeno (≤ 500)",
      ["menor círculo que contém todos os pontos (determinado por 2–3 pontos)",
       "maior círculo cuja borda fica na união de discos (lac2026-C)",
       "maior círculo vazio dentro de um polígono"]),
])

KEEP["lac2025-K"] = (None, [
    C("observação-chave", "Nos ciclos completos a ordem ótima das cartas (ataque/multiplica/soma) é fixa, "
      "derivada comparando duas cartas vizinhas; só o ciclo final parcial pede força bruta sobre quantas de "
      "cada tipo usar.",
      "Ordem canônica por troca de vizinhos",
      "Para ordenar operações heterogêneas (somar a, multiplicar por m, consumir o valor) de modo a maximizar "
      "o resultado, compare o efeito de trocar duas operações adjacentes: isso dá um comparador e a ordem "
      "ótima. Depois disso, a busca restante é só sobre quais/quantos itens usar, não sobre a ordem.",
      "operações que transformam um acumulador (x → x+a, x → m·x, f_i(x)=a_i x + b_i) em ordem livre",
      ["ordenar funções lineares para maximizar a composição (ABC366 F)",
       "regra de Johnson / escalonamento com comparador por troca adjacente",
       "ordem de upgrades em jogos incrementais"],
      ["AtCoder ABC366 F — Maximum Composition"]),
    N("otimização", "O poder cresce a cada ciclo, então bastam O(√H) ciclos simulados; trate cartas ×1 e poder 0."),
])

DISCARD["lac2025-L"] = "força bruta sobre os 10 dígitos por posição"

# ======================================================================= LAC 2026
KEEP["lac2026-A"] = (None, [
    C("observação-chave", "Formigas que não se ultrapassam preservam a ordem cíclica: fixado o destino da "
      "primeira, os demais estão forçados.",
      "Sem ultrapassagem ⇒ ordem preservada ⇒ só um deslocamento",
      "Se agentes numa linha/círculo não podem se cruzar (ou colidem e são indistinguíveis), a ordem relativa "
      "é invariante: a correspondência início→destino é a ordenada (na linha) ou um deslocamento cíclico (no "
      "círculo). Enumere só o deslocamento (o destino do primeiro) em vez de emparelhamentos arbitrários.",
      "agentes que não podem passar uns pelos outros; colisões que invertem direção",
      ["formigas que colidem e invertem direção (POJ 1852 Ants)",
       "casar pontos de dois conjuntos num círculo minimizando custo (deslocamento cíclico)",
       "mover fichas numa linha sem cruzar minimizando o maior deslocamento"],
      ["POJ 1852 — Ants"]),
    C("reformulação", "Desenrolar o anel em reta (posições x e x+L) e exigir destinos estritamente crescentes "
      "dentro de uma volta.",
      "Desenrolar o ciclo duplicando",
      "Problema circular vira linear cortando o círculo num ponto e duplicando (x, x+L) ou o array (a+a): "
      "objetos que cruzam o corte viram objetos que passam de L. Fixe o que acontece no ponto de corte e "
      "resolva linearmente.",
      "array circular, posições num anel, intervalos que podem dar a volta",
      ["maior soma de subarray circular", "cobertura de círculo por arcos",
       "rotação ótima de array circular"]),
    N("observação-chave", "Com ordem preservada numa reta, o tempo ótimo é max_i |início_i − destino_i|; testar "
      "os dois candidatos para o destino da primeira formiga."),
])

DISCARD["lac2026-B"] = "construção de poucas rodadas de médias; quase todo o top resolveu"

KEEP["lac2026-C"] = (None, [
    C("observação-chave", "O círculo ótimo é um dos círculos dos aspersores ou passa por três vértices da "
      "fronteira da união (interseções de pares de círculos não cobertas).",
      "Ótimo geométrico fixado por poucas restrições ativas",
      "Em problemas de maior/menor círculo com condição de cobertura ou vazio, o ótimo é tocado por 2–3 "
      "objetos; enumere as figuras definidas por duplas/triplas de candidatos (vértices, bordas) e verifique "
      "cada uma.",
      "maior/menor círculo com condição de cobertura/vazio e n pequeno (≤ 50)",
      ["menor círculo envolvente", "maior cone/calota vazia (lac2025-J)",
       "maior círculo vazio dentro de polígono"]),
    C("estrutura/algoritmo", "Verificar se a circunferência candidata está coberta: cada disco cobre um arco; "
      "unir os intervalos angulares e checar se cobrem [0, 2π).",
      "Cobertura de circunferência por intervalos angulares",
      "Para saber se uma curva fechada (circunferência) está coberta por regiões, intersecte cada região com a "
      "curva para obter um arco [α,β], quebre arcos que cruzam o ângulo 0 e verifique a união dos intervalos "
      "ordenados; com epsilons cuidadosos.",
      "círculo/curva que precisa ficar inteira dentro de uma união de discos ou regiões",
      ["círculo totalmente coberto pela união de outros círculos",
       "área visível/cobertura angular de radares", "perímetro da união de círculos"]),
])

KEEP["lac2026-D"] = (None, [
    C("reformulação", "Preencher posições de trás para frente: a posição t aceita qualquer pedido com índice "
      "≥ t−K, então o conjunto de elegíveis só ganha um pedido por passo.",
      "Varrer posições ao contrário transforma prazos em liberações",
      "Em escalonamento com prazos (item i deve ocupar posição ≤ d_i), percorra as posições do fim para o "
      "início: o conjunto de itens elegíveis só cresce, e toda posição é obrigada a receber alguém. Mantenha os "
      "elegíveis num multiset/heap e, em cada posição, decida qual sai do conjunto (o melhor numa posição "
      "valiosa, o pior senão), justificando por troca.",
      "cada item tem prazo/limite de posição (dentro das primeiras i+K), posições com valores diferentes",
      ["tarefas com prazo e lucro, uma por dia (processar dias de trás para frente com heap)",
       "atribuir descontos/bonificações a posições específicas de uma ordem com prazos"]),
])

DISCARD["lac2026-E"] = "intersecção de semirretas em 2x"
DISCARD["lac2026-F"] = "estrutura forçada da pilha + backtracking pequeno e flood fill"

KEEP["lac2026-G"] = (None, [
    C("estrutura/algoritmo", "Grupos de G e C seguidos de blocos 'AT': um G antes de j blocos gera C(j+1,3) "
      "GATA, um C gera j(j+1)/2 CAT, sem interferência; decompor G e C em somas de números tetraédricos e "
      "triangulares.",
      "Contagem exata por peças independentes",
      "Para construir um objeto com exatamente X padrões, projete peças cujas contribuições são conhecidas e "
      "independentes (sem contagem cruzada), com valores que crescem polinomialmente (triangulares, "
      "tetraédricos, potências); escreva X como soma dessas contribuições (maior primeiro, resto com DP "
      "pequena) e verifique o limite de tamanho.",
      "construir string/grafo/array com exatamente k ocorrências de algo e tamanho limitado",
      ["string com exatamente k subsequências 'ab'", "permutação com exatamente k inversões",
       "grafo com exatamente k triângulos ou caminhos mínimos"]),
])

KEEP["lac2026-H"] = (None, [
    C("reformulação", "A interseção de dois caminhos em árvore é um caminho u..v; para ele, os pares são "
      "F(u→v)·F(v→u), com F contado pelos ramos em cada ponta.",
      "Fixar a interseção e contar as pontas independentemente",
      "Para contar pares de objetos (caminhos, intervalos) pela forma da sua interseção, fixe a interseção e "
      "conte as extensões em cada extremidade separadamente: a contagem vira produto de fatores locais "
      "(escolhas em cada ponta que não estendem a interseção).",
      "contar pares de caminhos/intervalos cuja sobreposição tem tamanho exato k",
      ["pares de intervalos na reta com interseção exatamente [l,r]",
       "pares de caminhos em árvore que compartilham pelo menos um vértice"]),
    B("estrutura/algoritmo", "Somar F(u→v)F(v→u) sobre todos os pares a distância k com centroid decomposition "
      "e convolução NTT de polinômios de profundidade ponderados.",
      "Centroid decomposition", "Centroid + FFT para contar por distância",
      "Para obter, para todo k, a soma de pesos de pares a distância k, em cada centróide monte o polinômio "
      "P_c(x) = Σ peso·x^prof por subárvore filha; os pares cruzando o centróide são ((ΣP_c)² − ΣP_c²)/2 "
      "(ou o produto ordenado). O grau de cada polinômio é limitado pelo tamanho da subárvore, então cada "
      "nível custa O(n log n) e o total O(n log² n).",
      "O quadrado da soma conta todos os pares e subtrair os quadrados remove pares do mesmo filho, evitando "
      "convolução entre cada par de filhos; a soma dos tamanhos por nível da decomposição é n.",
      "'para cada k = 1..n−1, conte pares de vértices/caminhos a distância k' em árvore",
      ["contar pares a distância prima (CodeChef PRIMEDST)", "histograma de todas as distâncias de uma árvore"],
    ),
    A("estrutura/algoritmo", "Convoluções módulo 998244353.", "FFT/NTT"),
])

KEEP["lac2026-I"] = (None, [
    C("observação-chave", "Pegar x soma (#restantes menores que x); se o oponente pega um valor e você pega uma "
      "cópia igual, as contribuições se cancelam em paridade — só valores de multiplicidade ímpar importam.",
      "Estratégia espelho: pares iguais se anulam",
      "Em jogos em que o efeito de um lance depende só do valor escolhido, um jogador que responde com uma "
      "cópia igual neutraliza o lance do oponente; elimine os pares e analise só o que sobra sem par "
      "(multiplicidade ímpar). Confirme a fórmula por força bruta em instâncias pequenas.",
      "jogo com multiconjunto/pilhas onde há elementos repetidos e resultado por paridade ou soma",
      ["Nim: pilhas iguais se anulam no XOR", "estratégia simétrica em tabuleiro (copiar espelhado)",
       "jogo de divisores com estratégia de pareamento (lac2024-D)"]),
])

DISCARD["lac2026-J"] = "simulação do adversário ordenando contagens"

KEEP["lac2026-K"] = (None, [
    N("reformulação", "Cada passo é reflexão por um gato: para gatos consecutivos b,c,d, 2c.x = b.x + d.x em "
      "passo horizontal (idem y no vertical)."),
    C("observação-chave", "Como as coordenadas são distintas, um par ordenado de gatos consecutivos determina o "
      "próximo (e o anterior): os O(N²) estados de par formam uma permutação; percorrer seus ciclos.",
      "Par de estados determina o próximo ⇒ ciclos de permutação",
      "Quando a regra de transição faz (anterior, atual) determinar unicamente o próximo e também o anterior, "
      "o grafo sobre pares de estados é uma permutação: decomponha em ciclos visitando cada estado uma vez "
      "(O(estados)), em vez de buscar caminhos.",
      "sequência/circuito em que cada passo é determinado pelos dois últimos elementos (reflexão, recorrência "
      "de 2ª ordem)",
      ["período de Fibonacci mod m (Pisano) via pares", "trajetória de bilhar/espelhos em grade",
       "recorrências x_{n+1} = f(x_{n−1}, x_n) invertíveis"]),
    N("estrutura/algoritmo", "Hash (ou array de índices por coordenada) para achar o próximo gato e bitset "
      "para estados visitados; manter só ciclos de comprimento par sem gato repetido."),
])

KEEP["lac2026-L"] = (None, [
    B("estrutura/algoritmo", "Manter a ordem dos pedestres no tempo: eles trocam de ordem em O(N²) instantes; "
      "a cada troca só mudam gaps adjacentes, cujos instantes de cruzar C também viram eventos.",
      "Sweep line", "Ordem cinética (eventos de troca de vizinhos)",
      "Para pontos que se movem linearmente numa reta, a ordem ordenada só muda quando dois vizinhos "
      "adjacentes se cruzam; cada par se cruza no máximo uma vez, então há O(N²) eventos. Guarde num heap o "
      "próximo cruzamento de cada par adjacente e, ao trocar, recalcule só os pares afetados.",
      "Entre eventos a ordem é constante; uma troca só altera as adjacências dos dois elementos envolvidos "
      "(no máximo 3 pares novos); movimentos lineares se cruzam no máximo uma vez.",
      "pontos com velocidade constante e muitas consultas em tempos crescentes sobre a ordem/gaps",
      ["ranking de corredores ao longo de uma corrida", "par mais próximo de pontos que se movem",
       "bounding box cinético (lac2024-A)"]),
    N("otimização", "Comparar tempos como frações exatas e contar pares adjacentes com gap ≥ C ao varrer as "
      "consultas em ordem."),
])

# ======================================================================= Regional LATAM 2024
DISCARD["latam_regional2024-A"] = "contagem de letras distintas"

KEEP["latam_regional2024-B"] = (None, [
    C("observação-chave", "Grau mínimo ≥ 3 garante que a resposta sempre existe; escolhe-se o ciclo por um "
      "critério extremo (aresta de retorno com extremo superior mais profundo) e a prova usa essa "
      "extremalidade.",
      "Garantia forte ⇒ resposta sempre existe; escolha extrema",
      "Quando o enunciado dá uma condição forte (grau mínimo, densidade, tamanho) e pede 'encontre X', "
      "suspeite que X sempre existe e construa-o escolhendo um objeto extremo (mais profundo, mais longo, "
      "mais à esquerda); a prova de correção vem de 'se falhasse, haveria um objeto mais extremo'.",
      "'todo vértice tem grau ≥ k' / 'garante-se que…' com pedido de exibir uma estrutura",
      ["grafo com grau mínimo d tem ciclo de comprimento ≥ d+1 (caminho máximo da DFS)",
       "achar ciclo longo ou conjunto independente grande (√n)",
       "princípio extremal em provas de existência"]),
    B("estrutura/algoritmo", "Na árvore DFS, tomar a aresta de retorno x–y que maximiza a profundidade do "
      "ancestral x; o ciclo é o caminho x..y mais essa aresta.",
      "DFS", "Escolha extrema de aresta de retorno na árvore DFS",
      "Numa DFS não dirigida toda aresta fora da árvore liga ancestral e descendente. Escolhendo a aresta de "
      "retorno cujo extremo superior é o mais profundo possível, nenhum vértice do ciclo (exceto x) tem aresta "
      "de retorno saindo abaixo dele que suba menos que x — logo seus outros vizinhos levam para fora do "
      "ciclo, preservando a conectividade.",
      "Ausência de arestas cruzadas na DFS não dirigida; a maximalidade proíbe arestas de retorno que "
      "fechariam ciclos mais 'baixos'.",
      "achar um ciclo com propriedade extra (removível, longo, curto) num grafo conexo grande",
      ["ciclo de comprimento ≥ k usando a aresta de retorno ao ancestral mais alto",
       "pontes/articulações via low-link", "orientar arestas para tornar o grafo fortemente conexo"]),
])

KEEP["latam_regional2024-C"] = (None, [
    N("observação-chave", "Distância de edição para string unária tem forma fechada: "
      "d(a^x, S) = max(|S|−x, 0) + max(x − cnt_a(S), 0); divide-se S em m entre a parte r e a parte b."),
    C("otimização", "Cada um dos 4 termos max(·,0) liga/desliga monotonicamente em m: busca binária nos pontos "
      "de troca e, em cada trecho, minimizar uma soma linear fixa de contagens de prefixo com RMQ.",
      "Termos max(·,0) monótonos ⇒ poucos trechos sem max",
      "Se f(m) = Σ max(g_i(m), 0) e cada g_i é monótona em m, o conjunto de termos ativos muda em no máximo "
      "k pontos: ache-os por busca binária; em cada trecho f é uma expressão fixa (sem max) e o mínimo vem de "
      "uma RMQ sobre valores pré-calculados — uma estrutura por combinação de termos ativos (2^k).",
      "minimizar expressão com max(…,0) ou |…| sobre um ponto de corte, com muitas consultas em intervalo",
      ["minimizar Σ|x − a_i| por trechos entre os a_i ordenados",
       "consultas de melhor ponto de divisão de um intervalo em duas partes com custos de contagem"]),
    A("estrutura/algoritmo", "Contagens de letras por prefixo.", "Soma de prefixos"),
    A("estrutura/algoritmo", "16 sparse tables para mínimo das expressões lineares em m.", "Sparse table"),
])

KEEP["latam_regional2024-D"] = (None, [
    C("reformulação", "Cada modelo é um par (cor do texto, cor do fundo) = aresta num grafo bipartido de cores; "
      "'compartilham cor' = arestas adjacentes; modelos com cores todas distintas = emparelhamento.",
      "Item com dois atributos = aresta entre valores",
      "Se cada item é definido por um par (a, b) de atributos de dois tipos, modele o item como aresta a–b num "
      "grafo bipartido de valores: conjuntos de itens sem atributo repetido são emparelhamentos, e "
      "'compartilham atributo' é adjacência de arestas (grafo de linha).",
      "itens descritos por dois atributos e restrição de 'não repetir nenhum atributo'",
      ["torres não atacantes em casas permitidas (linha, coluna)", "dominós com faces distintas",
       "escolher pares (aluno, projeto) sem repetir nenhum"]),
    N("redução", "Reconstruir o grafo bipartido a partir da matriz de adjacência do grafo de linha enumerando "
      "cliques maximais (cada cor é uma clique; grafos de linha bipartidos não têm diamante)."),
    A("estrutura/algoritmo", "Emparelhamento máximo no grafo de cores.", "Matching bipartido (Kuhn/Hopcroft-Karp)"),
])

KEEP["latam_regional2024-E"] = (None, [
    C("observação-chave", "Numa permutação montanha o valor 1 está numa ponta e removê-lo deixa uma montanha: "
      "colocar 1, 2, 3, … sempre na ponta esquerda ou direita restante.",
      "Unimodal = inserir do menor ao maior pelas pontas",
      "Sequências 'cresce e depois decresce' se constroem (e se contam) inserindo valores do menor para o "
      "maior em uma das duas pontas livres — ou do maior para o menor ao redor do pico. Cada decisão é binária "
      "(esquerda/direita), o que dá 2^{n−1} permutações unimodais e torna a decisão gulosa/DP local.",
      "permutações/sequências bitônicas, 'estritamente crescente até um pico e depois decrescente'",
      ["contar permutações unimodais (2^{n−1})", "construir com deque inserindo na frente ou atrás",
       "completar sequência bitônica parcialmente conhecida"]),
    N("otimização", "Quando as duas pontas são desconhecidas, compara-se o vizinho conhecido mais próximo de "
      "cada lado e põe-se o valor pequeno no lado do menor vizinho (troca)."),
    A("estrutura/algoritmo", "Dois ponteiros nas pontas livres, O(N).", "Dois ponteiros"),
])

DISCARD["latam_regional2024-F"] = "construção direta de conjunto independente maximal no caminho"

KEEP["latam_regional2024-G"] = (None, [
    N("reformulação", "Com raiz no destino T, cada vértice é conquistado pela folha mais próxima da sua "
      "subárvore (desempate por id)."),
    B("estrutura/algoritmo", "Agrupar consultas por T e mover a raiz por uma DFS, atualizando só os dois "
      "vértices cujo dono muda quando a raiz passa a um vizinho (melhor e segundo melhor de filhos distintos).",
      "Rerooting", "Rerooting com estado global e consultas offline por raiz",
      "Se cada consulta usa uma raiz diferente e a resposta depende de um estado global (contagem por folha), "
      "ordene as consultas por raiz e percorra a árvore em DFS movendo a raiz aresta a aresta: mover a raiz de "
      "u para v só altera os valores de u e v (com melhor/segundo melhor guardados), e na volta desfaz-se.",
      "A orientação só muda na aresta u–v; as subárvores dos outros vértices são as mesmas, então só os "
      "agregados de u e v precisam ser recalculados.",
      "muitas consultas com raiz/destino variável e resposta global que não é uma simples soma por vértice",
      ["consultas de tamanho de subárvore com raiz variável",
       "contar vértices mais próximos de x que da raiz para todas as raízes"]),
])

KEEP["latam_regional2024-H"] = (None, [
    C("observação-chave", "T(x) = Σ_y C(x,y)·B_y com C(x,y) = número de caminhos x→y: uma atualização de B_y "
      "altera T(x) em C(x,y)·Δ.",
      "Resposta linear nas entradas ⇒ matriz de influência",
      "Quando cada resposta é combinação linear fixa das entradas atualizáveis, pré-calcule a influência "
      "C(x,y) de cada entrada em cada resposta (em DAG, número de caminhos por DP topológica); uma "
      "atualização vira um delta multiplicado por C.",
      "DP linear (somas) sobre DAG/árvore com atualizações pontuais nos valores-base",
      ["soma de subárvore com updates (influência = ser ancestral)",
       "expressões lineares com variáveis atualizadas"]),
    B("otimização", "A cada k atualizações recalcula-se tudo em O(M) por ordem topológica; consultas corrigem o "
      "valor com as ≤ k atualizações pendentes; k ≈ √M.",
      "Sqrt decomposition", "Reconstrução periódica + correção pelas pendentes",
      "Em vez de blocos de array, faça blocos na sequência de eventos: mantenha uma foto estática recalculada a "
      "cada k atualizações (custo R) e responda cada consulta como foto + correção pelas ≤ k pendentes (custo "
      "k·c). Total O(E/k·R + E·k·c), ótimo em k = √(R/c).",
      "O erro da foto é só a soma das atualizações posteriores a ela, que são no máximo k e cada uma é "
      "corrigível isoladamente.",
      "estrutura cara de recalcular mas cuja correção por uma atualização é barata; ~1e5–1e6 eventos",
      ["distância ao vértice especial mais próximo com inserções (BFS multi-fonte a cada √q)",
       "consultas em grafo com arestas adicionadas em lote"]),
    A("estrutura/algoritmo", "DP em ordem topológica para recalcular T e contar caminhos.", "Ordenação topológica"),
])

KEEP["latam_regional2024-I"] = (None, [
    C("estrutura/algoritmo", "Achar o número de inversões x e depois montar a permutação posição a posição, "
      "escolhendo cada elemento pela contagem de completamentos f(n−1, x−i), com contagens saturadas em K+1.",
      "k-ésimo objeto por contagem de completamentos (saturada)",
      "Para gerar o k-ésimo objeto numa ordem (lexicográfica, por chave), decida posição a posição: para cada "
      "candidato conte quantos objetos completam o prefixo; se k ≤ contagem, fixe-o, senão subtraia. Sature as "
      "contagens em K+1 (min) para não estourar.",
      "'imprima o k-ésimo' com k até 1e18 numa ordem lexicográfica ou composta",
      ["k-ésima sequência de parênteses balanceada", "k-ésima permutação com restrições",
       "k-ésimo número com soma de dígitos s"]),
    C("observação-chave", "f(n,x) cresce tão rápido que, para n > ~100, x < 15: com K ≤ 4e18 a parte que muda "
      "da permutação é minúscula.",
      "Contagem explosiva ⇒ k-ésimo só mexe numa parte pequena",
      "Se K ≤ 1e18 e a quantidade de objetos cresce fatorial/exponencialmente com um parâmetro, o k-ésimo "
      "objeto só varia num pedaço de tamanho ~log K (os últimos ~20 elementos, poucas inversões); o resto é "
      "fixo. Limite a DP a esse pedaço.",
      "n grande (1e5) com k até 1e18 numa ordem de permutações/strings",
      ["k-ésima permutação lexicográfica de n = 1e5 (só os últimos ~20 se movem)",
       "k-ésima string de tamanho n grande"]),
    A("otimização", "DP f(n,x) com somas de prefixo nas transições.", "Soma de prefixos"),
])

DISCARD["latam_regional2024-J"] = "união de intervalos ordenados"
DISCARD["latam_regional2024-K"] = "cortes por runs com cuidado nas bordas"

KEEP["latam_regional2024-L"] = (None, [
    C("observação-chave", "As trocas induzem permutações r (linhas) e c (colunas); a matriz deve satisfazer "
      "M[i][j] = M[r(i)][c(j)], logo é constante nas órbitas, e todos os ciclos de r e de c precisam ter o "
      "mesmo comprimento.",
      "Invariância sob permutação ⇒ constante nas órbitas (ciclos)",
      "Se o objeto deve ficar igual após aplicar uma permutação de posições (linhas, colunas, índices), as "
      "posições se agrupam em órbitas = ciclos da permutação, e cada órbita tem um único valor. Raciocine "
      "sobre os ciclos (comprimentos, quantidade) em vez das posições.",
      "objeto que deve ser invariante (fixo) sob uma sequência de trocas/rotações",
      ["contar colorações fixas por uma permutação (Burnside: k^{#ciclos})",
       "string que volta a si após aplicar uma permutação de posições", "matriz invariante por rotação"]),
    N("estrutura/algoritmo", "Relabel para ciclos consecutivos e preencher um quadrado latino de blocos "
      "cíclicos S×S, bloco (i,j) com símbolos k·S+1..k·S+S, k = (i+j) mod (N/S)."),
])

# ======================================================================= Regional LATAM 2025
KEEP["latam_regional2025-A"] = (None, [
    C("reformulação", "Lista em que todo par aparece adjacente exatamente uma vez = trilha euleriana do grafo "
      "completo K_N" + UNVERIFIED + ".",
      "Cada transição usada uma vez ⇒ caminho euleriano",
      "Se uma sequência deve usar cada 'transição' (par de elementos consecutivos, aresta, peça) exatamente "
      "uma vez, modele elementos como vértices e transições como arestas: a sequência é um caminho euleriano. "
      "Existência = paridade dos graus + conectividade das arestas.",
      "'cada par aparece exatamente uma vez como vizinhos', 'usar todas as peças/arestas uma vez'",
      ["sequência de De Bruijn (todas as substrings de tamanho k uma vez)",
       "encadear todos os dominós", "reconstruir string a partir de todos os pares consecutivos"],
      ["CSES — De Bruijn Sequence"]),
    A("redução", "Arestas não usadas devem formar trilha do fim do prefixo ao começo do sufixo: paridade de "
      "graus + conectividade (BFS no complemento, O(N²)); dúvida: tratar limites de tamanho do trecho oculto.",
      "Caminho euleriano"),
])

DISCARD["latam_regional2025-B"] = "DP de médias de prefixo; quase todo o top resolveu"

KEEP["latam_regional2025-C"] = (None, [
    N("reformulação", "Com taxa comum r, p_i = r·H_i: o faxineiro i é elegível sse r ∈ [L_i/H_i, U_i/H_i] e o "
      "custo é r·Σ s_i H_i; para r fixo, preencher com os mais rápidos elegíveis" + UNVERIFIED + "."),
    C("observação-chave", "O r ótimo é algum L_i/H_i: varrer os candidatos com entradas/saídas de intervalos.",
      "Parâmetro contínuo ⇒ só os eventos importam",
      "Se a solução depende de um parâmetro real r, cada item está ativo num intervalo de r e, entre eventos, "
      "o custo é monótono em r, o ótimo está num extremo de intervalo: ordene os O(n) eventos, varra r "
      "mantendo os ativos numa estrutura e avalie só nos eventos. Compare frações exatamente.",
      "taxa/preço/limiar comum real a escolher, itens que aceitam só uma faixa do parâmetro",
      ["escolher preço único que maximiza receita com faixas de aceitação",
       "limiar de tempo ótimo com itens ativos em janelas", "breakpoints de função linear por partes (lac2024-A)"]),
    B("estrutura/algoritmo", "BIT indexado por H guardando capacidades; descer no BIT para pegar as S primeiras "
      "unidades dos mais rápidos e somar o custo.",
      "BIT", "Descida no BIT (k-ésima unidade em O(log n))",
      "Num BIT de contagens, ache o menor prefixo com soma ≥ k em O(log n) descendo por potências de 2 (de "
      "cima para baixo, somando enquanto não ultrapassa k), em vez de busca binária + consulta O(log² n). "
      "Guardando também Σ peso, obtém-se o custo dos k primeiros.",
      "O nó i do BIT cobre exatamente (i − lowbit(i), i]; somando blocos de tamanhos decrescentes reconstrói-se "
      "o prefixo bit a bit.",
      "multiset dinâmico com 'k-ésimo menor' ou 'soma dos k menores'",
      ["k-ésimo elemento de multiset com inserções/remoções", "soma dos k menores custos ativos numa varredura"]),
    A("estrutura/algoritmo", "Varredura dos eventos de r.", "Sweep line"),
])

KEEP["latam_regional2025-D"] = (None, [
    N("reformulação", "Para a/b com denominador reduzido b': dígitos = dígitos(⌊a/b⌋) + max(v2(b'), v5(b')) + "
      "ord_m(10), com m = b' sem fatores 2 e 5" + UNVERIFIED + "."),
    B("estrutura/algoritmo", "Pré-calcular a ordem multiplicativa de 10 módulo todo m ≤ 1e5 a partir da "
      "fatoração de φ(m).",
      "Fatoração", "Ordem multiplicativa via divisores de φ(m)",
      "Para gcd(a,m)=1, o menor k com a^k ≡ 1 (mod m) divide φ(m) (ou λ(m)): comece com d = φ(m) e, para cada "
      "primo p de d, divida d por p enquanto a^{d/p} ≡ 1. Custa O(log² m) por m com exponenciação rápida.",
      "Pelo teorema de Lagrange a ordem divide a ordem do grupo (Z/mZ)*, que é φ(m); remover primos enquanto "
      "a potência continua 1 chega ao menor divisor válido.",
      "período de dízimas, ciclos de x → a·x mod m, 'menor k com a^k ≡ 1'",
      ["período da expansão decimal/em base b de 1/m", "ciclo de multiplicação modular",
       "menor k com 10^k ≡ 1 (repunits divisíveis por m)"]),
    A("estrutura/algoritmo", "Contar pares por denominador reduzido com enumeração de divisores e Möbius sobre gcd.",
      "Möbius"),
    A("otimização", "Frequências por faixa de valor para os dígitos inteiros e divisão por N² com inverso.",
      "Inverso modular"),
])

DISCARD["latam_regional2025-E"] = "fórmula min_k(k + a_{k+1}) mantida em segment tree; todo o top resolveu"
DISCARD["latam_regional2025-F"] = "truncar X e fatorar poucos dígitos"

KEEP["latam_regional2025-G"] = (None, [
    C("observação-chave", "Fluxo máximo = corte mínimo = mínimo de funções lineares em t, logo côncavo em t: "
      "busca ternária sobre t inteiro" + UNVERIFIED + ".",
      "Ótimo sobre soluções lineares no parâmetro ⇒ convexo/côncavo",
      "Se o valor ótimo para um parâmetro t é o mínimo (máximo) sobre um conjunto — mesmo exponencial — de "
      "soluções cujo custo é linear em t, então é côncavo (convexo) em t, sem precisar conhecer as soluções: "
      "use busca ternária em t (cuidado com platôs em inteiros) ou procure o ponto de troca.",
      "capacidades/pesos que variam linearmente com t e pergunta 'para qual t o ótimo é máximo/mínimo'",
      ["corte mínimo paramétrico", "caminho mínimo com pesos a_e + t·b_e (min de retas ⇒ côncavo)",
       "MST com pesos lineares em t"]),
    B("estrutura/algoritmo", "Em cada t, o corte mínimo de vértices da grade planar é um caminho mínimo no dual "
      "(Dijkstra de uma borda à oposta pelos blocos e falhas de cabo).",
      "Corte mínimo", "Corte mínimo planar = caminho mínimo no dual",
      "Em grafo planar com s e t na face externa, um corte s–t corresponde a um caminho no grafo dual entre as "
      "duas regiões da face externa separadas por s e t; corte mínimo = caminho mínimo dual (Dijkstra), muito "
      "mais rápido que fluxo.",
      "Remover as arestas de um caminho dual de uma borda à outra 'corta' o plano em duas partes, uma com s e "
      "outra com t, e vice-versa — dualidade de Whitney.",
      "grade/mapa planar grande (≥ 1e5 vértices) com origem e destino na borda e pergunta de corte/bloqueio",
      ["bloquear todos os caminhos de cima para baixo de um mapa com obstáculos (barreira = caminho dual)",
       "lobos e coelhos (BZOJ 1001)", "menor custo para separar duas bordas de uma grade"]),
    A("estrutura/algoritmo", "Dijkstra no dual por avaliação.", "Dijkstra"),
    A("otimização", "Ternária sobre t ∈ [0, K].", "Busca ternária"),
])

DISCARD["latam_regional2025-H"] = "contar máximos de prefixo"

KEEP["latam_regional2025-I"] = (None, [
    N("reformulação", "Rota = caminho crescente na metade baixa, um código cruzado a → b+N, caminho na metade "
      "alta; identificando i+N com i, pedem-se dois caminhos monótonos que não compartilham andar."),
    C("observação-chave", "BFS sobre pares (x,y) das duas frentes avançando sempre a atrasada e nunca pousando "
      "sobre a outra frente: como ambas só avançam, isso garante disjunção sem guardar conjuntos visitados.",
      "Dois caminhos monótonos disjuntos: avance sempre o atrasado",
      "Para dois caminhos que só avançam numa ordem (topológica, índice, coluna) e não podem compartilhar "
      "vértices, faça DP/BFS no estado (x, y) das duas pontas, movendo sempre a de menor índice: o vértice que "
      "a atrasada visita nunca é revisitado pela outra, então basta checar x ≠ y localmente.",
      "dois caminhos/percursos simultâneos em DAG ou grade, ambos monótonos, sem vértices em comum",
      ["TSP bitônico (DP sobre as duas pontas)", "dois caminhantes de canto a canto numa grade coletando "
       "itens (Cherry Pickup)", "dois caminhos disjuntos em DAG pequeno"]),
    A("estrutura/algoritmo", "BFS em O(N²) estados por código cruzado, com ponteiros para reconstruir.", "BFS"),
])

DISCARD["latam_regional2025-J"] = "contar ocorrências de padrões"
DISCARD["latam_regional2025-K"] = "testar um rei extremo em cada direção"

KEEP["latam_regional2025-L"] = (None, [
    N("reformulação", "Cada reta corta a região y > Ax² + B numa corda aberta entre as raízes x1 < x2 de "
      "Ax² − Mx + (B − C) = 0" + UNVERIFIED + "."),
    C("redução", "Duas cordas de região convexa se cruzam dentro dela sse seus extremos se intercalam: contar "
      "pares de intervalos cruzados (l_i < l_j < r_i < r_j).",
      "Cordas de região convexa ⇒ intervalos que se intercalam",
      "Para contar interseções de segmentos/cordas cujos extremos estão na fronteira de uma região convexa (ou "
      "num círculo, ou em duas retas verticais), parametrize a fronteira: duas cordas se cruzam no interior "
      "sse os extremos se intercalam. Vira contar pares de intervalos cruzados — ordenar por l e BIT sobre r.",
      "contar pares de retas/cordas que se cruzam dentro de uma região (faixa, círculo, parábola)",
      ["pares de cordas que se cruzam num círculo",
       "pares de retas que se cruzam na faixa x1 < x < x2 (inversões entre as ordens em x1 e x2)"]),
    A("estrutura/algoritmo", "Contagem de pares intercalados com BIT após ordenar extremos comparados "
      "exatamente (raízes (M ± √D)/2A com aritmética inteira).", "BIT"),
])

# ======================================================================= APAC 2024
KEEP["apac2024-A"] = (None, [
    C("reformulação", "As operações são relações de grupo (A^a = P^p = 1, P = APA, A = PAP); toda palavra "
      "reduz a uma de 8 formas normais e S → E é possível sse ambas reduzem à mesma.",
      "Operações reversíveis ⇒ compare formas normais",
      "Se todas as operações de reescrita são reversíveis (ou suas inversas são deriváveis), alcançabilidade é "
      "uma relação de equivalência: defina um procedimento que leva qualquer objeto a uma forma normal "
      "canônica. Resposta: N(S) = N(E); construção: S → N(S) seguido do inverso de E → N(E).",
      "transformar S em E por operações de inserir/remover/substituir padrões que podem ser desfeitas",
      ["strings com 'remover AA/BB' e trocas reversíveis (forma reduzida por pilha)",
       "puzzles de permutação com movimentos invertíveis (levar ambos à configuração padrão)",
       "transformar um array em outro por operações reversíveis (comparar invariante canônico)"]),
    N("observação-chave", "Movimentos derivados dão A⁴ = P⁴ = 1, então expoentes reduzem a gcd(a,4) e "
      "gcd(p,4); o grupo é quociente do grupo dos quatérnios Q8."),
])

KEEP["apac2024-B"] = (None, [
    C("observação-chave", "A penalidade 1e6·(pares faltantes)² domina, e com planaridade o ótimo é uma "
      "clique (≤ 4 vértices) ou clique menos uma aresta (≤ 5 vértices).",
      "Penalidade dominante ⇒ forma restrita + força bruta",
      "Quando um termo do objetivo é numericamente enorme (big-M), a solução ótima tem quase nada dele: deduza "
      "a forma possível da resposta (poucos defeitos, tamanho limitado) e enumere só essas formas.",
      "objetivo com coeficiente gigante (1e6, 1e9) multiplicando uma quantidade de 'defeitos'",
      ["custos lexicográficos codificados como M·a + b",
       "maximizar mantendo zero violações a não ser que valha a pena só uma"]),
    C("estrutura/algoritmo", "Grafo planar tem vértice de grau ≤ 5: remover repetidamente o de grau mínimo e "
      "força bruta nos subconjuntos da sua vizinhança enumera todas as cliques em O(n).",
      "Ordem de degeneração limita vizinhos 'para frente'",
      "Em grafos esparsos (planares: ≤ 3n−6 arestas, logo grau mínimo ≤ 5; arboricidade baixa), ordene os "
      "vértices removendo sempre o de menor grau: cada vértice tem ≤ d vizinhos posteriores. Estruturas locais "
      "(cliques, triângulos) são enumeradas a partir do seu primeiro vértice nessa ordem, com custo O(n·2^d).",
      "grafo planar/esparso e pergunta sobre cliques, triângulos ou subgrafos densos pequenos",
      ["contar triângulos em O(m√m) orientando arestas por grau", "colorir grafo planar com 6 cores",
       "enumerar K4 em grafo planar"]),
])

DISCARD["apac2024-C"] = "derivar x pelos carries da popcount e verificar"

KEEP["apac2024-D"] = (None, [
    C("observação-chave", "Janelas 6×7 com somas iguais dão g[i][j] + g[i−6][j−7] = g[i−6][j] + g[i][j−7]: cada "
      "classe de resíduo (i mod 6, j mod 7) é constante, listrada na horizontal ou listrada na vertical.",
      "Somas de janelas iguais ⇒ periodicidade por resíduo",
      "Se toda janela de tamanho k tem a mesma soma, subtraindo janelas vizinhas vem a_i = a_{i+k}: o objeto é "
      "determinado pelos resíduos mod k. Em 2D a mesma subtração dá uma equação de 4 termos que força cada "
      "classe de resíduo a ser constante ou listrada; conte por classe.",
      "'toda janela/subgrade de tamanho fixo tem a mesma soma (ou mesma quantidade de 1s)'",
      ["array binário em que toda janela de k tem exatamente s uns (período k)",
       "reconstruir array a partir de somas de janelas (apac2026-E: a_{i+m} − a_i = s_{i+1} − s_i)"]),
    A("estrutura/algoritmo", "Separar 'constante' de 'listrada' com inclusão-exclusão.", "Inclusão-exclusão"),
    A("otimização", "Funções geradoras por linha elevadas à 6ª potência via NTT (ou DP com poda sobre os 2^42 "
      "tipos).", "FFT/NTT"),
])

DISCARD["apac2024-E"] = "cota inferior por linhas/colunas sem repetição atingida diretamente"

KEEP["apac2024-F"] = (None, [
    C("observação-chave", "Juntar dois grupos nunca piora a razão max/min, então basta testar k primo (divisores "
      "primos de n, ≤ 7).",
      "Mesclar não piora ⇒ teste só os divisores primos",
      "Se ao escolher k | n (número de blocos, período) uma divisão mais grossa é sempre no máximo tão boa "
      "quanto uma mais fina que a refina, basta testar os k 'mínimos' na ordem de divisibilidade: os primos "
      "(ou n/p para cada primo p). Reduz de d(n) para ω(n) ≤ ~10 casos.",
      "escolher k que divide n (grupos, período, blocos iguais) otimizando razão/máximo",
      ["menor período de string: testar só n/p para p primo", "dividir array cíclico em k blocos iguais",
       "ordem multiplicativa: remover fatores primos de φ(m)"]),
    N("estrutura/algoritmo", "Para k fixo, deslizar o aluno 1 muda só dois grupos por passo: multiset de somas "
      "dá max/min em O(log n); comparar frações por multiplicação cruzada."),
])

KEEP["apac2024-G"] = ("C: limite amortizado por pombos com parada antecipada — técnica reutilizável que "
                      "transforma O(n²m) em O(nm + k·n²)", [
    C("otimização", "Incrementar contadores por par (só entre alunos com a mesma letra na coluna) e parar no "
      "primeiro par que chega a k: até então cada par contribuiu < k incrementos.",
      "Parar no primeiro sucesso limita o trabalho (pombos)",
      "Se você procura o primeiro par/objeto que acumula ≥ k coincidências, incremente contadores e pare assim "
      "que algum chega a k: antes disso cada contador está < k, então o trabalho total é ≤ (k−1)·#pares + 1, "
      "independentemente do tamanho da entrada que gera as coincidências.",
      "procurar par com pelo menos k (pequeno) coisas em comum entre muitos objetos longos",
      ["retângulo com 4 cantos 1 numa matriz binária (pares de colunas por linha, para na repetição)",
       "dois conjuntos com ≥ 2 elementos em comum", "dois vetores com ≥ k posições iguais"]),
])

DISCARD["apac2024-H"] = "poucos casos sobre a maioria de cada mesa"

KEEP["apac2024-I"] = (None, [
    C("observação-chave", "As n² retas pelos pontos médios dividem o plano em células onde os testes de "
      "orientação são fixos e a área do hull é linear no centro X: o ótimo está num vértice do arranjo.",
      "Linear por célula de arranjo ⇒ ótimo num vértice",
      "Se o espaço de parâmetros (um ponto no plano) é dividido por O(m) retas em células onde a combinatória "
      "da solução é fixa e o objetivo é linear dentro de cada célula, o ótimo está num vértice do arranjo: "
      "enumere as O(m²) interseções de pares de retas, valide e avalie cada uma.",
      "escolher um ponto/centro no plano com n pequeno (≤ 30–100) e objetivo linear por partes",
      ["programação linear em 2 variáveis (ótimo em vértice)", "versão 1D: ótimo em breakpoint (lac2024-A)",
       "posicionar ponto minimizando soma de distâncias L1 (vértices da grade de coordenadas)"]),
    A("estrutura/algoritmo", "Para cada vértice candidato: hull de P ∪ (2X − P) e área.", "Convex hull"),
])

DISCARD["apac2024-J"] = "Dijkstra das duas pontas + melhor aresta fora do caminho"

KEEP["apac2024-K"] = (None, [
    N("reformulação", "x = ⌈k/n⌉; para x fixo os y se agrupam pelo LCA com x: o ancestral a_i 'possui' "
      "S(a_i) \\ S(a_{i−1})."),
    B("estrutura/algoritmo", "Árvores persistentes (por x ao longo de arestas; por subárvore via small-to-large) "
      "e descida pela diferença de duas versões para achar o LCA e depois o y.",
      "Segment tree persistente", "k-ésimo por descida na diferença de duas versões",
      "Com versões persistentes indexadas por valor, a diferença (versão R − versão L) dá as contagens de um "
      "subconjunto; descer as duas árvores juntas comparando k com a contagem do filho esquerdo encontra o "
      "k-ésimo menor do subconjunto em O(log n), sem construir o subconjunto.",
      "Contagens são aditivas e as versões compartilham estrutura; a diferença nó a nó é a contagem do "
      "subconjunto naquele intervalo de valores.",
      "k-ésimo menor num subarray, num caminho ou numa subárvore, com muitas consultas",
      ["k-ésimo menor em subarray (SPOJ MKTHNUM)", "k-ésimo menor no caminho u–v de árvore (SPOJ COT)"]),
    A("estrutura/algoritmo", "Construir as versões de subárvore reaproveitando o filho pesado.", "Small-to-large"),
])

KEEP["apac2024-L"] = (None, [
    C("redução", "Os vetores alcançáveis são o span de vetores com a_i⊕a_j nos blocos i e j; trocar a_i por "
      "2a_i + 1 (bit de paridade) e calcular o posto s dá rank = C(s,2) + (n−s)(s−1).",
      "Bit constante extra para controlar paridade de tamanho",
      "Para impor paridade de cardinalidade (ou distinguir 'somou um número par de termos') num problema "
      "linear em GF(2), acrescente uma coordenada constante 1 a cada vetor: ela passa a registrar a paridade "
      "e a restrição vira linear.",
      "XOR de pares/subconjuntos com restrição implícita sobre quantos termos entram",
      ["subconjunto de tamanho par com XOR 0 (lac2025-B)", "combinações com número ímpar de termos"]),
    A("estrutura/algoritmo", "Base linear dos 2a_i+1; resposta 2^rank.", "Base XOR"),
    A("otimização", "Potência de 2 módulo 998244353.", "Exponenciação rápida"),
])

KEEP["apac2024-M"] = (None, [
    C("reformulação", "Inclusão-exclusão: cada '>' vira 'sem condição' − '≤', sobrando concatenações de "
      "blocos quase crescentes (a1 < a2 ≤ a3 < …), fáceis de contar.",
      "Inclusão-exclusão em desigualdades: zig-zag vira blocos monótonos",
      "Restrições alternadas (subidas/descidas prescritas) são difíceis; escreva cada relação incômoda como "
      "'qualquer' − 'a oposta não estrita': os termos viram sequências de blocos monótonos, contadas por "
      "produto/concatenação (série 1/(1−A)) com sinal.",
      "contar sequências/permutações com padrão de subidas e descidas prescrito",
      ["permutações com string de subidas/descidas dada (DI-string) via inclusão-exclusão",
       "números alternantes/up-down (Euler zigzag)"]),
    C("observação-chave", "Composições quase estritamente crescentes de n têm comprimento O(√n): DP em (soma, "
      "comprimento) custa O(n√n).",
      "Partes distintas ⇒ O(√n) partes",
      "Uma sequência estritamente crescente de inteiros positivos com soma n tem no máximo ~√(2n) termos; "
      "logo DPs sobre (soma, quantidade de termos) custam O(n√n), e conjuntos de valores distintos com soma "
      "total S têm O(√S) elementos.",
      "contar partições/composições em partes distintas (ou crescentes) para n até ~1e5–3e5",
      ["partições em partes distintas para todo n", "subset sum com soma total S tem O(√S) valores distintos "
       "(lac2024-F)"]),
    B("estrutura/algoritmo", "Sequências de blocos: C(x) = 1/(1 − A(x)), uma inversa de série via NTT.",
      "FFT/NTT", "Inversa de série de potências para concatenação de blocos",
      "Se objetos são concatenações livres de blocos com função geradora A(x) (A(0)=0), sua função geradora é "
      "1/(1 − A(x)); a inversa de série até grau N sai por iteração de Newton em O(N log N), respondendo "
      "todos os n ≤ N de uma vez.",
      "Concatenar k blocos é A(x)^k e Σ_k A^k é a série geométrica; Newton dobra a precisão a cada passo com "
      "uma multiplicação.",
      "contagem para todos os n até 1e5–1e6 de objetos formados por sequências de blocos",
      ["composições com partes num conjunto permitido para todo n", "número de ladrilhamentos para todo n"]),
])

# ======================================================================= APAC 2025
DISCARD["apac2025-A"] = "DP de contagem por linha/coluna com inclusão-exclusão pequena"

KEEP["apac2025-B"] = (None, [
    C("estrutura/algoritmo", "Colorir as arestas gulosamente particiona-as em poucos emparelhamentos; cada "
      "emparelhamento é roteado num par de camadas z próprio, sem colisões.",
      "Decompor em emparelhamentos para rotear em paralelo",
      "Para desenhar/agendar muitas conexões sem conflito, decomponha as arestas em emparelhamentos "
      "(coloração de arestas gulosa com ≤ 2Δ−1 cores; Δ+1 por Vizing; Δ em bipartido): dentro de um "
      "emparelhamento nenhuma conexão compartilha extremo, então todas podem ser feitas na mesma "
      "camada/rodada.",
      "grau máximo pequeno e necessidade de dispor conexões em camadas/rodadas sem conflito nos vértices",
      ["agendar partidas em rodadas (cada time joga ≤ 1 por rodada)",
       "comunicação em rodadas entre pares de máquinas", "roteamento de fios em camadas"]),
    N("otimização", "Gadgets numa grade √n/3 × d e coloração de um grafo contraído para caber em 400³ — "
      "engenharia específica da construção."),
])

KEEP["apac2025-C"] = (None, [
    N("reformulação", "Prova-se que o valor de conectividade = corte máximo + 1 (completando com cliques)."),
    C("observação-chave", "No cacto, 2-colorir uma árvore geradora e contar arestas bicoloridas: cada ciclo "
      "ímpar perde exatamente uma aresta, então max-cut = m − #ciclos ímpares.",
      "Max-cut em cacto = m − ciclos ímpares",
      "Corte máximo é NP-difícil em geral, mas em grafos cujos ciclos são disjuntos em arestas (cactos) cada "
      "ciclo ímpar obriga a perder exatamente uma aresta e ciclos pares nenhuma.",
      "grafo cacto com pergunta sobre bipartição/corte máximo",
      ["max-cut de grafo unicíclico", "max-cut de grafo bipartido (= m)"], specific=True),
    A("estrutura/algoritmo", "DFS para árvore geradora e cores.", "DFS"),
])

KEEP["apac2025-D"] = ("B: segment tree de composição de funções de estado pequeno — deepening reutilizável "
                      "além do cálculo do Hanói", [
    N("reformulação", "Pensar do maior disco para o menor: se o disco não está no destino, todos os menores vão "
      "para o terceiro pino (2^x − 1 movimentos) e o destino dos menores fica determinado."),
    B("estrutura/algoritmo", "Para cada bloco de discos e cada um dos 3 pinos-alvo guardar (movimentos, pino "
      "exigido para os menores); blocos compõem associativamente numa segment tree com update pontual.",
      "Segment tree", "Segment tree de composição de funções (estado pequeno)",
      "Se processar um bloco é uma função de um estado de entrada pequeno (k estados) para (estado de saída, "
      "custo), guarde em cada nó a tabela dessa função para os k estados; o pai é a composição dos filhos. "
      "Consultas de intervalo e updates pontuais em O(k log n).",
      "Composição de funções é associativa, que é tudo o que a segment tree exige; o estado pequeno torna a "
      "tabela de cada nó O(k).",
      "processo sequencial com estado pequeno (autômato, DP linear) sobre um intervalo, com atualizações "
      "pontuais",
      ["DP linear com updates via matrizes (max,+) por posição (CF 750E)",
       "verificar se substring é aceita por um autômato", "simular máquina de estados em intervalos"],
    ),
])

KEEP["apac2025-E"] = (None, [
    C("estrutura/algoritmo", "Conhecendo o prefixo da expressão, pôr 1 só nas folhas da cadeia de aninhamento da "
      "folha atual e 0 nas outras reduz a expressão a x−(x−(x−…)) e isola qual parêntese vem a seguir.",
      "Neutralizar o conhecido para isolar a próxima incógnita",
      "Para descobrir uma estrutura oculta pedaço a pedaço, use o que já foi descoberto para montar consultas "
      "em que tudo o que é conhecido ou irrelevante vira elemento neutro/absorvente (0 em AND, 1 em OR), de "
      "modo que a resposta dependa só da próxima incógnita.",
      "interativo para reconstruir fórmula/árvore/sequência oculta com limite apertado de consultas (~2–3n)",
      ["descobrir circuito booleano oculto", "reconstruir árvore oculta consultando distâncias com vértices "
       "conhecidos fixos", "adivinhar string caractere a caractere com consultas que fixam o prefixo"]),
    N("otimização", "Árvore de decisão pequena: 2 consultas para abrir/simples e ~r/2+2 para fechar r "
      "parênteses, total amortizado ≤ 2,5n."),
])

KEEP["apac2025-F"] = (None, [
    C("observação-chave", "No revezamento ótimo, depois do primeiro portador a estrela só passa para personagens "
      "estritamente mais baratos: a cadeia de mínimos de sufixo entre r_m e l_j.",
      "Revezamento só para o mais barato (cadeia de mínimos)",
      "Em transporte com troca de portador/veículo, em que cada agente tem custo por unidade de distância, só "
      "vale passar a carga a um agente mais barato que o atual; o percurso ótimo usa a cadeia de mínimos "
      "prefixo/sufixo na direção do movimento, mantida com pilha monotônica.",
      "carregar algo ao longo de uma reta com agentes/postos de custo por unidade diferentes",
      ["abastecer só até o próximo posto mais barato (problema do posto de gasolina)",
       "trocar de veículo com custo por km ao longo de uma rota"]),
    A("estrutura/algoritmo", "Cadeia de mínimos mantida com pilha ao ordenar os níveis por l_j.", "Pilha monotônica"),
    A("otimização", "O custo de buscar com cada primeiro portador é linear em l_j: mínimo de retas.",
      "Convex hull trick / Li Chao"),
])

DISCARD["apac2025-G"] = "comparação gulosa de runs com dois ponteiros"
DISCARD["apac2025-H"] = "interativo com k = número de rosas e busca binária curta"

KEEP["apac2025-I"] = (None, [
    N("observação-chave", "Quadrados com todos os vértices em cantos de célula dão áreas ilimitadas; os demais "
      "alternam vértices em arestas horizontais/verticais e têm centro em ponto da grade ou centro de célula."),
    C("reformulação", "Fixar o centro numa posição pivô; cada segmento unitário da grade dá um intervalo de "
      "áreas 2d² para o vértice, com peso = número de translações do centro que mantêm o quadrado dentro.",
      "Contar formas módulo translação × número de posições",
      "Para contar figuras numa grade, conte cada forma uma vez com uma posição canônica (centro pivô) e "
      "multiplique pelo número de translações válidas; se a forma varia continuamente com um parâmetro, gere "
      "intervalos de valores com peso e responda consultas offline por varredura.",
      "contar quadrados/retângulos/padrões em grade n×n com n até ~2000",
      ["contar quadrados inclinados em grade de pontos (por vetor lado × posições)",
       "contar ocorrências de uma forma por tipo × posições"]),
    A("estrutura/algoritmo", "Varredura dos O(n²) intervalos de área contra as consultas ordenadas.", "Sweep line"),
])

DISCARD["apac2025-J"] = "DP de intervalos direta"

KEEP["apac2025-K"] = (None, [
    C("observação-chave", "No ótimo, os livros com rótulo < l vão para a frente, os > r para o fim e o intervalo "
      "de rótulos [l,r] é ordenado com trocas adjacentes: custo (l−1) + (n−r) + inv(a_l..a_r).",
      "Mover para as pontas ⇒ o que fica é um intervalo de valores",
      "Com operações 'mandar ao início/fim' (custo 1) e trocas adjacentes, os elementos mandados ao início são "
      "um prefixo de valores e os mandados ao fim um sufixo de valores; o resto é um intervalo contíguo de "
      "valores ordenado por trocas (custo = inversões). Otimize sobre intervalos [l,r] de valores.",
      "ordenar permutação com 'mover para frente/trás' combinados com outra operação",
      ["mínimo de 'mover para frente' para ordenar (n − maior sufixo de valores já em ordem)",
       "ordenar com 'mover para o fim' (maior prefixo de valores consecutivos em ordem)"]),
    N("otimização", "Varrer r mantendo num set os l 'recordes' onde f(l,r) = r − l − inv cresce; cada nova "
      "inversão remove um candidato — remoções amortizadas, O(n log n)."),
    A("estrutura/algoritmo", "Contagem de inversões com BIT.", "BIT"),
])

DISCARD["apac2025-L"] = "deslocamento de índices na fila e contagem direta"

KEEP["apac2025-M"] = (None, [
    C("observação-chave", "Os movimentos são translações por diferenças de pontos marcados (mais reflexões): com "
      "um ponto só um segmento; com direções colineares uma faixa; com três não colineares tudo.",
      "Alcançável = grupo gerado; classifique pela dimensão",
      "Quando os movimentos combinam translações por vetores derivados da entrada, o conjunto alcançável é o "
      "grupo/reticulado gerado: classifique pela quantidade de direções independentes (0, 1 ou 2) e trate os "
      "pontos de borda com testes de múltiplo inteiro.",
      "movimentos do tipo 'somar P − Q' ou refletir por pontos dados, pergunta de alcançabilidade",
      ["saltos (a,b) na grade alcançam o reticulado gerado (gcd)", "reflexões por pontos geram translações"],
      specific=True),
    A("estrutura/algoritmo", "Testes de lado de reta e colinearidade.", "Produto vetorial / orientação"),
])

# ======================================================================= APAC 2026
KEEP["apac2026-A"] = (None, [
    B("reformulação", "Inserir sufixos do fim para o início: S(k) < S(j) ⇔ (s_k, posição de S(k+1)) < (s_j, "
      "posição de S(j+1)), e a ordem dos sucessores já é conhecida.",
      "Suffix array + LCP", "Ordem de sufixos = (primeira letra, ordem do sufixo seguinte)",
      "A comparação de dois sufixos se reduz à primeira letra e, em caso de empate, à ordem dos sufixos que "
      "começam uma posição depois. Construindo de trás para frente, cada novo sufixo é posicionado comparando "
      "só primeiras letras com uma ordem já conhecida.",
      "S(k) = s_k + S(k+1), então comparar S(k) e S(j) é comparar s_k e s_j e, se iguais, S(k+1) e S(j+1).",
      "construir/ordenar sufixos de forma incremental ou com consultas de comparação caras",
      ["prefix doubling do suffix array (pares de ranks)", "classificação L/S do SA-IS",
       "ordenar sufixos em interativo com poucas comparações"]),
    N("otimização", "Alfabeto de 26 letras gera ≤ 25 'posições de divisão'; busca binária só sobre "
      "representantes de bloco + 1 consulta de confirmação, ≈ n(log₂26 + 1) consultas."),
])

KEEP["apac2026-B"] = ("C: binarizar jogo de valor com busca binária no limiar — técnica geral para jogos "
                      "min/max", [
    C("redução", "Para um limiar v, rotular folhas ≤ v como boas para o minimizador e > v como ruins: o jogo "
      "vira ganha/perde; busca binária em v.",
      "Binarizar o valor de um jogo por limiar",
      "Se o resultado de um jogo é um valor (um jogador minimiza, outro maximiza), pergunte para cada limiar "
      "v 'o minimizador garante ≤ v?': vira um jogo ganha/perde, geralmente com DP simples (±1, sinal), e a "
      "resposta é monótona em v — busca binária.",
      "jogo de dois jogadores com resultado numérico (valor final, folha restante), min vs max",
      ["maior mediana com valores ±1 por limiar (CF 1486D)", "jogos minimax sobre árvore com valores nas folhas",
       "minimizar o máximo em jogos de remoção"],
      ["Codeforces 1486D — Max Median"]),
    A("estrutura/algoritmo", "D(x) = sinal da soma dos D dos filhos, calculado de baixo para cima por limiar.",
      "DP em árvore"),
    A("otimização", "Busca binária sobre o rótulo da folha final.", "Busca binária na resposta"),
])

DISCARD["apac2026-C"] = "max-heap Dijkstra = ordem de DFS, validar com pilha"

KEEP["apac2026-D"] = (None, [
    A("reformulação", "Estático: dp(u) = max(a_u, Σ dp(filhos)).", "DP em árvore"),
    B("estrutura/algoritmo", "Com b_u = soma dos dp dos filhos leves, o dp do topo de cada cadeia pesada é max "
      "de termos a_{c_i} + b_{c_1} + … + b_{c_{i−1}}; manter por cadeia numa segment tree com lazy e propagar "
      "mudanças dos topos aos pais.",
      "HLD", "DP dinâmica sobre HLD",
      "Para DP em árvore com updates pontuais, separe a contribuição dos filhos leves (b_u, armazenada no "
      "vértice) da do filho pesado; ao longo de uma cadeia pesada o dp vira composição de funções simples "
      "(max/soma), mantida numa segment tree por cadeia. Um update altera O(log n) cadeias.",
      "Todo caminho até a raiz cruza O(log n) arestas leves; dentro de uma cadeia, a recorrência é linear "
      "em (max,+) e portanto composta numa segment tree.",
      "DP em árvore cujo valor deve ser respondido após cada atualização pontual de peso",
      ["conjunto independente máximo com updates (DDP clássico, Luogu P4719)",
       "cobertura mínima por caminhos raiz→vértice com demandas alteradas"]),
    A("estrutura/algoritmo", "Range add em b + range max por cadeia.", "Segment tree com lazy"),
])

DISCARD["apac2026-E"] = "diferenças telescópicas por resíduo + máximos por resíduo; quase todo o top resolveu"
DISCARD["apac2026-F"] = "contribuições por largura com FFT e divisores; quase todo o top resolveu"

KEEP["apac2026-G"] = (None, [
    N("reformulação", "'Todo vértice em algum caminho 1–n e ordem única dos internos' ⇔ grafo série-paralelo "
      "de dois terminais 1 e n (prova via árvore de dominadores)."),
    C("estrutura/algoritmo", "Reconhecer com reduções série (vértice de grau 2) e paralelas (fundir arestas "
      "múltiplas) aplicadas com uma fila até sobrar uma aresta 1–n.",
      "Reconhecer classe de grafos por reduções locais com fila",
      "Muitas classes de grafos se reconhecem aplicando repetidamente reduções locais (podar folha, contrair "
      "vértice de grau 2, fundir arestas paralelas, remover vértice de grau < k) com uma fila de candidatos: "
      "a classe vale sse o processo termina na configuração mínima. A ordem das reduções não importa quando "
      "o sistema é confluente.",
      "grafo com estrutura 'aninhada' (série/paralelo, árvore, k-core) a ser verificada em O(m log n)",
      ["reconhecer árvore podando folhas", "k-core/degeneração removendo vértices de grau < k",
       "reconhecer grafos série-paralelos"]),
    A("estrutura/algoritmo", "Reduções série/paralelo com fila.", "Redução série-paralela"),
    N("otimização", "Pares (u,v) válidos são os de uma mesma cadeia contraída por uma operação série: somar "
      "w_i·w_j por cadeia com somas de prefixo durante a redução."),
])

DISCARD["apac2026-H"] = "invariante de diferenças absolutas + gcd; todo o top resolveu"

KEEP["apac2026-I"] = (None, [
    N("reformulação", "Trocar a_i por mínimos de sufixo (b é não decrescente)."),
    C("observação-chave", "Ao longo de b_1 | b_2 | …, o valor muda no máximo log₂(M) ≈ 18 vezes, pois cada "
      "troca ao menos dobra.",
      "Cadeias de divisibilidade mudam ≤ log vezes",
      "Em sequências em que cada termo divide o próximo (ou gcd/AND/OR de prefixo), cada mudança de valor "
      "ao menos dobra (ou perde um bit), então há ≤ log₂(M) valores distintos: comprima a sequência em "
      "'valores distintos + pontos de mudança' e indexe a DP por isso.",
      "divisibilidade em cadeia, gcd/AND/OR de prefixos ou subarrays",
      ["gcd de todos os subarrays: O(n log M) valores distintos por fim (CF 475D)",
       "OR de subarrays: ≤ 30 valores distintos por fim"],
      ["Codeforces 475D — CGCDSSQ"]),
    B("estrutura/algoritmo", "f_v(l) é polinômio em l escrito na base binomial C(l,k) com ≤ 18 coeficientes; "
      "transições por divisores próprios usam Σ_{j=L}^{l−1} C(j,k) = C(l,k+1) − C(L,k+1).",
      "Binomiais mod p", "Base binomial + hockey-stick para somas de prefixo",
      "Escrevendo uma função de contagem como combinação de C(l,k), uma soma de prefixo em l só desloca "
      "o índice: Σ_{j<l} C(j,k) = C(l,k+1). Somas de prefixo iteradas d vezes viram polinômios de grau d, "
      "manipulados só pelos coeficientes.",
      "Identidade do taco de hóquei (Pascal): C(j,k) = C(j+1,k+1) − C(j,k+1), soma telescópica.",
      "contagem de sequências não decrescentes / somas de prefixo repetidas com comprimento grande",
      ["número de sequências não decrescentes de tamanho l (C(l+k−1,k))",
       "aplicar soma de prefixo k vezes a um array em O(n) com binomiais"]),
    N("otimização", "Iterar u e seus múltiplos (soma harmônica): O(n + M log² M)."),
])

DISCARD["apac2026-J"] = "manter número de 'voltas' sob trocas em O(1)"
DISCARD["apac2026-K"] = "verificação de viabilidade gulosa com enumeração"

KEEP["apac2026-L"] = (None, [
    C("observação-chave", "Por pombos existe u ≤ ⌈√n⌉ com v ≡ a·u (mod n), |v| < √n: os pontos (x, (ax+b) mod "
      "n) se dividem em O(√n) progressões colineares de passo (u,v).",
      "Sequência a·x mod n = O(√n) progressões aritméticas",
      "Para sequências/pontos da forma (a·x + b) mod n, o pombal garante um passo u ≤ √n com a·u mod n "
      "pequeno (|v| ≤ √n): a sequência se decompõe em O(√n) progressões aritméticas, e só extremidades de "
      "cada progressão importam para hull/mínimos.",
      "pontos ou valores definidos por a·x + b mod n com n até 1e9",
      ["mínimo de (a·x + b) mod n em x ∈ [0, k)", "somas Σ ⌊(a·x+b)/n⌋ e reticulados (floor sum)"]),
    A("estrutura/algoritmo", "Hull de cada camada sobre O(√n) extremidades candidatas.", "Convex hull"),
])

KEEP["apac2026-M"] = (None, [
    C("reformulação", "Reescrever '(' como '{' ou '}' conforme a paridade de ')' anteriores transforma a "
      "gramática em dois contadores de aninhamento (x, y) ≥ 0 terminando em (1, 0).",
      "Recodificar gramática estranha em contadores de balanço",
      "Para reconhecer uma gramática de parênteses incomum, procure uma recodificação dos símbolos (o "
      "significado de um caractere depende de paridade/contexto) que a transforme em sequências de Dyck "
      "clássicas com um ou dois contadores; a validade vira 'contadores de prefixo nunca negativos e estado "
      "final fixo', e completar nas pontas vira fechar déficits.",
      "gramática recursiva com parênteses 'invertidos' ou de vários tipos; validar/completar sequência",
      ["completar sequência de parênteses com mínimo de inserções nas pontas (−min prefixo e saldo final)",
       "sequências com dois tipos de colchetes misturados"]),
    N("otimização", "Os prefixos úteis têm só 3 formas (L^f, L^f R L^g, L^f R L^g R); o custo é 4f + constante, "
      "varrer f."),
])


# ---------------------------------------------------------------- build + validate
def load_dataset():
    s = open(os.path.join(ROOT, "data", "dataset.js"), encoding="utf-8").read()
    return json.loads(s[s.index("{"):s.rstrip().rstrip(";").rindex("}") + 1])


def main():
    ds = load_dataset()
    dp = {p["id"]: p for p in ds["problems"]}
    ids = []
    for f in ["lac.json", "latam_regional_2024_2025.json", "apac.json"]:
        raw = json.load(open(os.path.join(ROOT, "pipeline", "raw", f), encoding="utf-8"))
        ids += [p["id"] for p in raw["problems"]]
    errors = []
    both = set(KEEP) & set(DISCARD)
    if both:
        errors.append(f"in both keep and discard: {sorted(both)}")
    missing = [i for i in ids if i not in KEEP and i not in DISCARD]
    extra = [i for i in list(KEEP) + list(DISCARD) if i not in ids]
    if missing:
        errors.append(f"missing ids: {missing}")
    if extra:
        errors.append(f"unknown ids: {extra}")

    problems = []
    new_a_used = set()
    counts = {"A": 0, "B": 0, "C": 0, None: 0}
    specific = 0
    for pid in ids:
        q = dp.get(pid, {})
        if pid in DISCARD:
            st = q.get("solved_top")
            reason = DISCARD[pid]
            if st is not None:
                reason += f"; {st}/{q.get('k_used')} dos top-40 resolveram"
            problems.append({"id": pid, "keep": False, "discard_reason": reason})
            continue
        if pid not in KEEP:
            continue
        keep_reason, steps = KEEP[pid]
        if q.get("difficulty") == "easy" and not keep_reason:
            errors.append(f"{pid}: easy problem kept without keep_reason")
        for s in steps:
            cat = s["cat"]
            counts[cat] += 1
            if cat == "A":
                t = s["technique"]
                if t not in CANON:
                    if t in NEW_A:
                        new_a_used.add(t)
                    else:
                        errors.append(f"{pid}: non-canonical A '{t}'")
            if cat == "B":
                if s["base"] not in CANON and s["base"] not in NEW_A:
                    errors.append(f"{pid}: non-canonical B base '{s['base']}'")
                for k in ["base", "name", "property", "why", "signal", "contexts", "specific"]:
                    if k not in s:
                        errors.append(f"{pid}: B missing {k}")
            if cat == "C":
                for k in ["name", "statement", "signal", "contexts", "known_problems", "specific"]:
                    if k not in s:
                        errors.append(f"{pid}: C missing {k}")
            if cat in ("B", "C"):
                if len(s["contexts"]) < 2 and not s["specific"]:
                    errors.append(f"{pid}: <2 contexts and not specific")
                specific += bool(s["specific"])
            if s["kind"] not in ("reformulação", "observação-chave", "redução", "estrutura/algoritmo",
                                 "otimização"):
                errors.append(f"{pid}: bad kind {s['kind']}")
            labels = [s.get("name", ""), s.get("technique", ""), s.get("base", "")]
            for lab in labels:
                for bad in FORBIDDEN:
                    if re.search(r"\b" + re.escape(bad) + r"\b", lab.lower()):
                        errors.append(f"{pid}: forbidden label '{bad}' in '{lab}'")
        if not steps:
            errors.append(f"{pid}: kept without steps")
        problems.append({"id": pid, "keep": True, "keep_reason": keep_reason, "steps": steps})

    out = {"group": "lac_apac", "problems": problems}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    kept = sum(p["keep"] for p in problems)
    print(f"problems: {len(problems)} / expected {len(ids)}  kept={kept} discarded={len(problems) - kept}")
    print(f"steps: A={counts['A']} B={counts['B']} C={counts['C']} null={counts[None]}  specific={specific}")
    print(f"new A names used: {sorted(new_a_used)}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
