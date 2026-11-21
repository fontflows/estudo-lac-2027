# -*- coding: utf-8 -*-
"""Consolidação do currículo v2 (SPEC.md, "Curriculum (v2)", seção 2–3).

Lê pipeline/curriculum/steps_*.json e escreve pipeline/curriculum/curriculum.json.
Todas as decisões editoriais estão como dados abaixo:
  - GROUPS:      grupos de afinidade dos insights C
  - INSIGHTS:    insights C canônicos; `steps` = chaves "<problema>#<índice do passo>" fundidas
  - DEEPENINGS:  aprofundamentos B canônicos
  - C_TO_A / C_TO_B / B_TO_C: passos reclassificados
  - SPECIFIC:    passos marcados specific (viram cat null)
  - TECH_ALIASES: normalização de nomes de técnicas A
Campos omitidos (name/statement/signal/contexts) vêm do passo `primary` (o primeiro de `steps`).
Rodar:  python -I pipeline/scripts/curriculum_consolidate.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CUR_DIR = os.path.join(ROOT, "pipeline", "curriculum")
OUT = os.path.join(CUR_DIR, "curriculum.json")
DATASET = os.path.join(ROOT, "data", "dataset.js")

FORBIDDEN = ["construtivo", "ad hoc", "análise de casos", "observação", "greedy", "matemática", "implementação"]

# ---------------------------------------------------------------------------
# Grupos de afinidade
# ---------------------------------------------------------------------------
GROUPS = [
    ("order-time", "Ordem e tempo de processamento"),
    ("exchange", "Argumentos de troca e forma do ótimo"),
    ("monotone-critical", "Parâmetros: monotonicidade e pontos críticos"),
    ("counting", "Contagem por contribuição e decomposição"),
    ("sequences", "Prefixos, intervalos e ciclos"),
    ("invariants", "Invariantes, paridade e aritmética"),
    ("graph-modeling", "Modelagem em grafos e árvores"),
    ("state", "Estado e representação"),
    ("bounds", "Limites de tamanho e amortização"),
    ("geometry", "Reformulações geométricas"),
    ("constructions", "Construções e limites atingíveis"),
    ("probability", "Probabilidade e esperança"),
    ("games", "Jogos"),
    ("interactive", "Interativos e identificação"),
]


def I(id, group, gen, steps, **kw):
    d = dict(id=id, group=group, generality=gen, steps=steps)
    d.update(kw)
    return d


# ---------------------------------------------------------------------------
# Insights C canônicos
# ---------------------------------------------------------------------------
INSIGHTS = [
    # ---- Ordem e tempo ----
    I("monotone-potential-order", "order-time", 2, ["latam2019-H#0"]),
    I("backward-deadlines", "order-time", 2, ["lac2026-D#0", "nerc2024-J#0"],
      name="Prazos: percorra de trás para frente",
      statement="Se cada item tem prazo (posição ou instante máximo), percorra o tempo do fim para o início: o conjunto de elegíveis só cresce e cada decisão vira 'qual elegível ocupa esta posição' (heap/multiset), justificada por troca. A mesma passada reversa dá o último instante em que cada tarefa pode começar: ls_i = min(d_i, ls_{i+1}) − t_i.",
      signal="tarefas/itens com prazo ou 'deve estar entre as primeiras i+K posições'; perguntas sobre folga ou adiamento",
      contexts=["tarefas com prazo e lucro, uma por dia (dias de trás para frente com heap)",
                "caminho crítico de projeto: último início e folga",
                "inserir uma tarefa extra o mais tarde possível sem estourar prazos"]),
    I("stack-of-versions", "order-time", 2, ["latam2021-M#1"]),
    I("threshold-sweep-dsu", "order-time", 3, ["lac2025-D#1", "nerc2022apr-G#0"],
      name="Varrer o limiar unindo com DSU",
      statement="Se a pergunta depende de um limiar (peso máximo no caminho, nível de água, tempo) e 'conectado com limiar h' é monótono em h, ordene elementos e consultas pelo limiar, ative em ordem e una com DSU: cada consulta é respondida no instante certo da varredura, e na união de A e B com valor w exatamente |A|·|B| pares novos passam a ter gargalo w.",
      signal="consultas de conectividade com limiar; soma sobre todos os pares de 'maior aresta no caminho' ou gargalo",
      contexts=["ilhas acima da água para vários níveis",
                "soma do maior peso de aresta sobre todos os caminhos de uma árvore",
                "pares cujo caminho minimax é ≤ k (árvore de Kruskal)"]),
    I("skip-between-events", "order-time", 3, ["nerc2019-A#1", "nac2025-M#1"],
      name="Entre eventos, pule em bloco",
      statement="Se a regra de uma simulação só muda quando ocorre um evento (chegada, troca de líder, mudança de ordem), o trecho entre dois eventos é uma transformação de forma fechada (linear, mod, polinomial em k): calcule quantos passos cabem até o próximo evento e aplique todos de uma vez. O custo passa a ser O(#eventos) — como no Euclides, em que subtrações repetidas viram um mod.",
      signal="tempos ou repetições até 1e18 numa simulação passo a passo cuja regra depende só de quem está ativo",
      contexts=["Euclides: subtrair b de a muitas vezes = a mod b",
                "partículas: pular direto até a próxima colisão",
                "recurso que enche/esvazia com taxa constante entre eventos"]),

    # ---- Trocas e forma do ótimo ----
    I("adjacent-swap-order", "exchange", 3, ["lac2025-K#0", "nac2023-D#0"],
      name="Troca de vizinhos dá o comparador",
      statement="Se a ordem dos itens é livre e o custo é sequencial (composição de operações, soma ponderada de términos, esperança até falhar), compare só o efeito de trocar dois itens adjacentes: se 'ij não é pior que ji' se escreve como f(i) ≤ f(j), ordenar por f é ótimo, e o que resta é escolher quais itens usar.",
      signal="'em que ordem executar/aplicar'; operações x → a·x + b em ordem livre; custo ponderado ou esperado que depende da ordem",
      contexts=["regra de Smith: ordenar por tempo/peso",
                "ordenar funções lineares para maximizar a composição (ABC366 F)",
                "concatenar strings para a menor lexicográfica (a+b < b+a)"]),
    I("merge-block-into-parent", "exchange", 2, ["latam2023b-E#0", "nac2023-D#1", "nerc2022apr-H#1"],
      name="Precedência em árvore: funda o melhor bloco ao pai",
      statement="Com regra de troca por razão (soma/tamanho, peso/tempo) e precedências 'pai antes do filho', o bloco de melhor razão deve vir imediatamente depois do pai: funda-o ao pai (somando os parâmetros) e repita com heap + DSU. Para cadeias de ordem fixa, quebre cada cadeia em blocos pelo envelope convexo das somas de prefixo e ordene os blocos por razão.",
      signal="ordem de execução com 'X antes de Y' em árvore ou cadeias e custo Σ peso × tempo de conclusão",
      contexts=["Color a Tree (POJ 2054)",
                "minimizar inversões com precedência em árvore (AGC023 F)",
                "intercalar cadeias de tarefas minimizando o dano/tempo ponderado"]),
    I("ratio-split-prefix-suffix", "exchange", 2, ["lac2024-J#0"]),
    I("incremental-local-swaps", "exchange", 1, ["lac2025-H#0"]),
    I("cheaper-chain", "exchange", 2, ["apac2025-F#0"]),
    I("rearrangement-pairing", "exchange", 2, ["latam2022-B#0"]),
    I("uncross-optimal-matching", "exchange", 2, ["nac2024-E#0"]),
    I("extremes-at-block-ends", "exchange", 1, ["nac2026-J#0"]),
    I("ends-moves-value-interval", "exchange", 2, ["apac2025-K#0"]),
    I("changed-to-extremes", "exchange", 2, ["nerc2022dec-L#0"]),
    I("requirement-gain-order", "exchange", 2, ["nerc2023-A#0"]),
    I("equalize-marginals", "exchange", 3, ["nerc2022apr-B#1", "nerc2023-B#0"],
      name="Custo convexo: iguale os custos marginais",
      statement="Para minimizar Σ f_i(x_i) com Σ x_i fixo e f_i convexas, no ótimo todos os itens que recebem algo têm o mesmo custo marginal λ (tirar uma unidade de um e pôr noutro nunca melhora). Com f_i iguais isso dá partes balanceadas ⌊N/k⌋/⌈N/k⌉; com f_i diferentes, busque λ por busca binária ou distribua unidade a unidade num heap de ganho marginal.",
      signal="dividir uma quantidade entre itens/grupos com custo quadrático, C(x, 2) ou ganhos decrescentes; muitas consultas de X",
      contexts=["minimizar pares de mesma cor: grupos balanceados (Turán)",
                "alocar k unidades com ganhos marginais decrescentes (heap)",
                "Aliens trick / relaxação lagrangiana: penalizar λ por unidade"]),
    I("greedy-longest-piece", "exchange", 2, ["latam2019-G#0", "latam2023a-L#0", "nac2022-C#0"],
      statement="Se é preciso cortar uma sequência no menor número de pedaços válidos e todo trecho contíguo de um pedaço válido também é válido, pegar a cada passo o maior prefixo válido é ótimo: por troca, o k-ésimo corte do método nunca fica antes do k-ésimo corte de uma solução ótima. Na linguagem de DP: se o custo do restante é monótono na posição, a transição mais longa domina todas as curtas. Resta calcular rápido o maior prefixo válido a partir de cada posição.",
      signal="minimizar o número de partes que formam uma string/array, quando cada parte deve ser substring de X, ter período ≤ D, soma ≤ S etc.; transições 'avance até L posições pelo mesmo custo'",
      contexts=["cortar array no menor número de blocos com soma ≤ S",
                "formar uma string com o menor número de substrings de um texto",
                "fatoração LZ77 com custo fixo por referência"]),
    I("sign-assignment-abs", "exchange", 2, ["nerc2025-E#0"]),
    I("extreme-solutions-intersection", "exchange", 2, ["nerc2021-J#0"]),

    # ---- Parâmetros: monotonicidade e pontos críticos ----
    I("guess-fixed-point", "monotone-critical", 3, ["lac2024-B#1", "latam2019-H#1", "nerc2023-F#1"],
      name="Ponto fixo: chute o valor circular",
      statement="Se a resposta aparece dentro da própria definição (reiniciar custa a esperança E; A = f(B) e B = g(A); x = F(x)), trate-a como parâmetro: com o chute fixo o cálculo fica acíclico, e a resposta é o ponto fixo — por busca binária quando f(E) − E é monótona, ou por iteração x ← F(x) quando o sistema é contrativo (cada volta tem probabilidade positiva de terminar).",
      signal="valor esperado com opção de reiniciar/desistir; probabilidades definidas circularmente entre poucos estados; equações implícitas com resposta real e tolerância",
      contexts=["speedrun com reset (CF 865C — Gotta Go Fast)",
                "probabilidade de vitória em jogos alternados com passe de turno",
                "value iteration em MDP / jogo estocástico",
                "Dinkelbach: chutar a razão λ e testar o sinal de custo − λ·peso"]),
    I("threshold-binarize", "monotone-critical", 3, ["apac2026-B#0"]),
    I("min-of-linear-concave", "monotone-critical", 2, ["latam_regional2025-G#0"]),
    I("monotone-crossing", "monotone-critical", 3, ["latam_regional2024-C#1", "latam2022-E#1", "nerc2023-G#3"],
      name="Monótonas opostas trocam uma vez",
      statement="Se f é não decrescente e g não crescente num índice m, então {m : f(m) < g(m)} é um prefixo: max(f, g), min(f, g) ou termos max(·, 0) monótonos mudam de expressão em um único ponto, achado por busca binária ou ponteiro monótono. De cada lado do cruzamento só um termo conta, e o resto vira soma de prefixo ou RMQ.",
      signal="min_m max(f(m), g(m)) numa DP minimax; Σ min(p_i, q_i) com p crescente e q decrescente; expressões com max(…, 0) sobre um ponto de corte",
      contexts=["queda de ovos: min sobre o andar de max(quebra, não quebra)",
                "água retida = Σ min(prefmax, sufmax)",
                "minimizar Σ|x − a_i| por trechos entre os a_i ordenados"]),
    I("first-capturing-prefix", "monotone-critical", 2, ["latam2023a-B#0"]),
    I("ratio-binary-search", "monotone-critical", 3, ["nac2026-F#2"]),
    I("range-split-extremes", "monotone-critical", 1, ["nerc2022apr-E#1"]),
    I("breakpoint-optimum", "monotone-critical", 3, ["lac2024-A#1", "latam_regional2025-C#1", "apac2024-I#0"],
      name="Ótimo num ponto de quebra: só os eventos importam",
      statement="Se o espaço de um parâmetro (um real, ou um ponto no plano) se divide por O(n) eventos/retas em pedaços onde a combinatória da solução é fixa e o objetivo é monótono, linear ou côncavo (para mínimo) dentro de cada pedaço, então o ótimo está num ponto de quebra ou vértice do arranjo: enumere os candidatos (O(n) em 1D, O(n²) interseções em 2D) e avalie cada um. Não use busca ternária quando a função não é unimodal.",
      signal="preço/taxa/instante comum a escolher; pontos em movimento linear; objetivo que é max/min/produto de funções lineares; escolher um ponto no plano com n pequeno",
      contexts=["programação linear em 1–2 variáveis: ótimo num vértice",
                "minimizar Σ|x − a_i|·w_i: ótimo num a_i",
                "preço único que maximiza a receita com faixas de aceitação",
                "minimizar perímetro/diâmetro de pontos que se movem linearmente"]),
    I("integer-near-continuous", "monotone-critical", 2, ["nac2025-L#0"]),

    # ---- Contagem ----
    I("prefix-state-pairs", "counting", 3, ["lac2024-H#0", "latam2023b-C#0"],
      name="Intervalo = par de prefixos com a mesma chave",
      statement="Se a propriedade de um intervalo [i..j] é uma relação entre os estados de prefixo P_{i−1} e P_j (diferença múltipla de (1,…,1), composição P_{i−1}⁻¹·P_j num conjunto pequeno, máscara de paridade igual), normalize cada estado numa chave e conte/ache pares de prefixos com chave compatível num hashmap — a generalização de 'subarrays de soma zero'.",
      signal="contar subarrays/intervalos 'neutros' ou com a mesma quantidade de cada tipo; operações invertíveis compostas em intervalos",
      contexts=["subarrays de soma 0 ou XOR 0",
                "substrings em que toda letra aparece um número par de vezes (máscara de prefixo)",
                "substrings com a mesma quantidade de a, b, c (chave (a − b, a − c))",
                "intervalos de permutações cuja composição é a identidade"]),
    I("swap-summation-contribution", "counting", 3, ["latam2021-E#0", "nerc2022apr-J#1"],
      name="Contribuição: troque a ordem da soma",
      statement="Se a resposta soma, para cada i, quantos j satisfazem P(i, j) (ou um custo sobre todos os pares), inverta os papéis: para cada j (ou cada aresta, cada elemento) descubra o conjunto de i que ele afeta. Muitas vezes é um intervalo (array de diferenças) ou um produto local (tamanho da subárvore × resto), e a soma sai em O(n).",
      signal="'para cada i, conte os j tais que…'; soma de distâncias ou custos sobre todos os pares numa árvore",
      contexts=["soma das distâncias entre todos os pares: Σ size·(n − size) por aresta",
                "quantos intervalos contêm cada ponto",
                "contribuição de cada elemento a todos os subarrays em que ele é o máximo"]),
    I("fix-intersection", "counting", 2, ["lac2026-H#0"]),
    I("first-divergence", "counting", 3, ["nac2022-K#0"]),
    I("linear-influence", "counting", 2, ["latam_regional2024-H#0"]),
    I("ie-flip-inequalities", "counting", 2, ["apac2024-M#0"]),
    I("shape-times-translations", "counting", 1, ["apac2025-I#1"]),
    I("kth-by-counting", "counting", 3, ["latam_regional2024-I#0", "nac2021-G#1"],
      name="k-ésimo por contagem de completamentos",
      statement="Para achar o k-ésimo objeto numa ordem (lexicográfica, ou a k-ésima posição de uma sequência gerada recursivamente), não gere tudo: decida posição a posição (ou filho a filho) contando quantos objetos ou símbolos cabem em cada escolha; se k ≤ contagem, desça nela, senão subtraia e siga. Sature as contagens em K+1 para não estourar.",
      signal="'imprima o k-ésimo' com k até 1e18; string definida recursivamente com tamanho exponencial e consulta por posição",
      contexts=["k-ésima sequência de parênteses balanceada",
                "k-ésimo caractere de palavras de Fibonacci",
                "k-ésimo número com soma de dígitos s"]),
    I("saturate-count-uniqueness", "counting", 2, ["nac2021-L#2"]),
    I("peel-a-layer", "counting", 2, ["latam2019-F#0", "nac2022-D#0"],
      name="Descascar uma camada",
      statement="Para contar formas feitas de alturas/partes ≥ 1 (histogramas, partições, gaps), remova a camada de baixo (subtraia 1 de todos): o que continua positivo é uma instância menor do mesmo tipo — apoiada num subintervalo contíguo ou com menos partes — e o que zera tem contagem simples. Recorra sobre (largura ou quantidade, total).",
      signal="contar sequências de alturas ou partições com soma fixa e restrição de forma (unimodal, sem reter água, partes distintas); gaps entre pontos ordenados",
      contexts=["partições em partes distintas removendo a primeira coluna do diagrama de Ferrers",
                "contar polígonos de colunas convexos com área fixa",
                "esperança do k-ésimo menor gap entre pontos aleatórios"]),
    I("insert-in-value-order", "counting", 2, ["latam_regional2024-E#0", "nerc2022apr-F#0", "nerc2019-K#1"],
      name="Inserir em ordem de valor: as opções não dependem do passado",
      statement="Para contar ou construir arranjos com restrições de comparação, insira os elementos em ordem de valor (ou do mais restrito ao menos restrito): o número de lugares válidos para o próximo depende só de contadores (quantos já colocados, quantas pontas livres), não de onde os anteriores foram. A contagem vira produto ou DP pequena (unimodais: 2^{n−1}; p_i ≤ b_i: Π (b_(i) − (i−1))).",
      signal="permutações unimodais/zigue-zague, picos e descidas, restrições 'a_i ≤ b_posição'; n ≤ 5000",
      contexts=["contar permutações unimodais (2^{n−1})",
                "contar permutações com p_i ≤ b_i ordenando b",
                "contar permutações com exatamente k descidas (números eulerianos)"]),
    I("polynomial-coefficients-sweep", "counting", 2, ["nerc2022apr-G#2"]),

    # ---- Prefixos, intervalos e ciclos ----
    I("prefix-min-condition", "sequences", 3, ["latam2022-D#0", "latam2023b-L#1", "nac2024-K#0"],
      contexts=["contar substrings de parênteses balanceadas",
                "dias consecutivos em que o saldo nunca fica negativo",
                "união de intervalos é conexa sse o saldo aberturas − fechamentos nunca zera antes do fim"]),
    I("crossing-interleave", "sequences", 3, ["lac2024-E#0", "latam2022-J#0", "latam_regional2025-L#1"],
      name="Cruzar = extremos intercalados (sem cruzamento = parênteses)",
      statement="Duas cordas/intervalos com extremos numa ordem linear ou cíclica (reta, perímetro de região convexa, linha do tempo de uma pilha) se cruzam sse os extremos se intercalam (a < c < b < d). Logo 'nenhum par se cruza' = família laminar = sequência de parênteses bem aninhada (teste com pilha), e contar cruzamentos = contar pares de intervalos intercalados (ordenar por l + BIT sobre r).",
      signal="ligar pares de pontos na borda de um polígono/círculo sem cruzar; validar uso de uma pilha/LIFO; contar pares de cordas ou retas que se cruzam dentro de uma região",
      contexts=["emparelhar pontos num círculo sem cruzamentos (Catalan)",
                "ordenar com duas pilhas (Twin Stack Sorting)",
                "pares de retas que se cruzam na faixa x1 < x < x2 = inversões entre as duas ordens"]),
    I("laminar-forest", "sequences", 2, ["nerc2021-H#0"]),
    I("grammar-to-balance", "sequences", 2, ["apac2026-M#0", "latam2023b-L#0"],
      name="Gramática vira restrições locais + contadores de balanço",
      statement="Para validar, contar ou completar substrings de uma gramática (expressões, parênteses incomuns), recodifique os símbolos em classes — mudando o significado conforme paridade/contexto se preciso — até que ser válido vire: nenhum par adjacente proibido, extremos permitidos e um ou dois contadores de prefixo que nunca ficam negativos e terminam num estado fixo. As restrições locais cortam a string em trechos; o balanço vira somas de prefixo.",
      signal="contar substrings que são expressões bem formadas; gramática recursiva com parênteses 'invertidos' ou de vários tipos",
      contexts=["completar parênteses com o mínimo de inserções nas pontas (−min prefixo e saldo final)",
                "validar expressões aritméticas sem parser recursivo",
                "subarrays com tags abre/fecha bem formadas"]),
    I("pairs-as-plane-regions", "sequences", 2, ["lac2025-E#1"]),
    I("reachable-interval", "sequences", 2, ["nac2025-D#0", "nerc2022apr-E#2"],
      name="Conjunto viável continua um intervalo",
      statement="Se cada passo permite mover para uma faixa contínua (y ± 1, diferença em [lo, hi]) e as restrições de cada passo são intervalos, o conjunto de valores viáveis em cada passo é sempre um intervalo (às vezes com paridade fixa): propague [lo, hi] para frente em O(1) por passo e, para construir, reconstrua de trás para frente escolhendo em cada intervalo um valor compatível com o próximo já escolhido.",
      signal="passos ±1 ou diferenças limitadas entre vizinhos, com faixa permitida por posição/tempo; 'menor e maior posição final' ou pedido de construção",
      contexts=["agenda com velocidade limitada e janelas de tempo",
                "alturas com diferença limitada entre vizinhos e faixa por posição",
                "passeio ±1 que deve ficar dentro de um corredor"]),
    I("unroll-duplicate", "sequences", 3, ["lac2026-A#1"]),
    I("cut-at-canonical-element", "sequences", 2, ["nac2026-J#2"]),
    I("rotate-removed-cycle-edge", "sequences", 1, ["nac2026-C#0"]),
    I("cycle-parametrize", "sequences", 2, ["latam2021-C#0", "nerc2025-G#0"],
      name="Ciclo: fixe uma aresta e tudo vira função de uma variável",
      statement="Em sistemas ao redor de um ciclo (fluxo entre vizinhos, a_i = b_i + b_{i−1}), fixe a incógnita de uma aresta/posição: por conservação todas as outras ficam determinadas como x + p_i (ou ±x alternado). O custo vira função de uma variável (Σ|x + p_i| ⇒ mediana; sentido único ⇒ x = −min p_i), e a paridade de n decide se a solução é única ou uma família de um parâmetro.",
      signal="itens em círculo equalizados movendo unidades entre vizinhos; observações que são somas de dois vizinhos num anel",
      contexts=["equalizar moedas numa mesa redonda (UVa 11300)",
                "posto de gasolina circular: comece logo após o prefixo mínimo",
                "recuperar valores de vértices a partir de somas nas arestas de um ciclo"]),
    I("cycle-lemma", "sequences", 2, ["nac2026-D#0"]),

    # ---- Invariantes, paridade e aritmética ----
    I("only-gcd-matters", "invariants", 2, ["lac2024-F#0"]),
    I("parity-bit", "invariants", 2, ["lac2025-B#1", "apac2024-L#0"]),
    I("orbits-constant", "invariants", 2, ["latam_regional2024-L#0"]),
    I("normal-form-reversible", "invariants", 3, ["apac2024-A#0", "nerc2023-C#1"],
      name="Operações reversíveis: leve os dois à forma canônica",
      statement="Se todas as operações podem ser desfeitas, alcançabilidade é relação de equivalência: defina um procedimento que leva qualquer objeto a uma forma normal canônica (não precisa ser ótima, só alcançável dentro do limite). A resposta é N(S) = N(E), e a construção é S → N(S) seguido do inverso de E → N(E).",
      signal="transformar S em E por operações reversíveis (rotações, inserir/remover padrões, trocas) com limite folgado de passos",
      contexts=["transformar uma árvore binária em outra por rotações passando pela árvore-caminho",
                "puzzles de permutação: resolver os dois estados até a identidade",
                "strings com 'remover AA/BB': forma reduzida por pilha"]),
    I("canonical-form-symmetry", "invariants", 2, ["nerc2024-G#0"]),
    I("equal-windows-periodic", "invariants", 2, ["apac2024-D#0"]),
    I("no-overtaking-order", "invariants", 2, ["lac2026-A#0"]),
    I("transposition-cycles", "invariants", 2, ["nac2026-L#0"]),
    I("two-involutions", "invariants", 1, ["nerc2021-K#0"]),
    I("inside-outside-parity", "invariants", 2, ["nerc2025-K#0"]),
    I("double-counting", "invariants", 3, ["nac2025-I#0", "nerc2024-C#0"],
      name="Contar a mesma coisa de dois jeitos",
      statement="Se uma grandeza (soma de graus, área, número de pares) se escreve como soma sobre duas famílias diferentes (por vértice e por aresta, por linhas e por colunas), igualar as duas expressões dá uma condição necessária de paridade/divisibilidade — que frequentemente também é suficiente — ou uma identidade que prova que a resposta de existência é 'sempre'.",
      signal="restrições locais em cada vértice/célula com pedido de construção ou 'impossível'; pergunta de existência que parece difícil",
      contexts=["lema do aperto de mãos: o número de vértices de grau ímpar é par",
                "torneio: soma das vitórias = C(n, 2)",
                "dominós cobrem uma casa de cada cor do tabuleiro",
                "teorema de Pick / área por cruzamentos com a grade"]),
    I("enumerate-residues", "invariants", 2, ["nerc2023-J#0"]),
    I("periodic-coincidence-gcd", "invariants", 2, ["nerc2024-L#1"]),
    I("only-prime-divisors", "invariants", 2, ["apac2024-F#0"]),
    I("modular-line-sqrt-ap", "invariants", 1, ["apac2026-L#0"]),
    I("trailing-nines", "invariants", 1, ["nac2024-B#1"]),

    # ---- Modelagem em grafos e árvores ----
    I("two-bins-bipartite", "graph-modeling", 3, ["lac2024-E#1"]),
    I("two-attributes-edge", "graph-modeling", 3, ["latam_regional2024-D#0"]),
    I("transitions-as-euler", "graph-modeling", 2, ["latam_regional2025-A#0", "nac2026-B#1"],
      contexts=["sequência de De Bruijn (todas as substrings de tamanho k uma vez)",
                "encadear todos os dominós",
                "agenda cíclica mod d com ações de salto fixo usadas um número dado de vezes (multigrafo de resíduos)"]),
    I("in-out-perfect-matching", "graph-modeling", 2, ["nac2023-M#0"]),
    I("twice-appearing-paths-cycles", "graph-modeling", 2, ["nerc2024-M#1"]),
    I("alternate-fixed-decouple", "graph-modeling", 1, ["latam2022-H#0"]),
    I("phases-to-precedence", "graph-modeling", 2, ["nerc2024-D#0"]),
    I("functional-graph", "graph-modeling", 2, ["nac2022-G#0"]),
    I("reversible-transition-permutation", "graph-modeling", 2, ["lac2026-K#1"]),
    I("tree-plus-k-edges", "graph-modeling", 2, ["nac2023-B#0"]),
    I("branches-of-vertex", "graph-modeling", 2, ["lac2025-E#0", "nerc2022apr-L#0"],
      name="Ramos distintos ⇒ o caminho passa pelo vértice",
      statement="Rotule cada vértice pelo ramo (componente de T − v, ou filho de s na árvore de busca) que o contém: v está entre dois vértices de um conjunto sse o conjunto toca ≥ 2 ramos, e uma aresta entre ramos diferentes de s fecha um ciclo por s / dá dois caminhos internamente disjuntos. Com Euler tour, cada ramo é a subárvore de um filho ou o complemento da subárvore de v.",
      signal="'o vértice fica entre membros do conjunto?'; dois caminhos disjuntos a partir de s; menor ciclo passando por um vértice",
      contexts=["vértices da árvore de Steiner/árvore virtual de um conjunto",
                "menor ciclo por um vértice: BFS rotulada pelo primeiro vizinho",
                "centroid decomposition: combinar só vértices de subárvores-filhas distintas"]),
    I("odd-degree-pairing", "graph-modeling", 2, ["nerc2019-C#1", "nerc2019-C#2", "nerc2021-C#3"],
      name="Vértices ímpares são pontas abertas: emparelhe-os",
      statement="Todo vértice de grau ímpar é extremidade de alguma trilha/caminho aberto, logo #peças abertas ≥ #ímpares/2. Ligando os ímpares em pares por arestas fictícias o grafo vira todo-par (euleriano), e cortar o circuito nas fictícias atinge exatamente esse limite; a cota vira a fórmula da resposta ou a condição de existência.",
      signal="cobrir arestas com o mínimo de caminhos/traços; restrições sobre graus; ciclos ou trilhas que não compartilham arestas",
      contexts=["desenhar uma figura com o mínimo de traços sem levantar a caneta",
                "carteiro chinês: as arestas duplicadas emparelham os vértices ímpares",
                "orientar arestas com |in − out| ≤ 1 (vértice fictício ligado aos ímpares)"]),
    I("tree-walk-2e-minus-path", "graph-modeling", 2, ["nerc2021-G#0"]),
    I("tree-split-divisible", "graph-modeling", 1, ["latam2022-G#0"]),
    I("local-reductions-queue", "graph-modeling", 2, ["apac2026-G#1", "nac2025-G#0"],
      name="Reduções locais com fila até a forma mínima",
      statement="Muitas classes de grafos se reconhecem — e muitos problemas nelas se resolvem — aplicando repetidamente reduções locais que preservam a resposta (podar folha, contrair vértice de grau 2 somando arestas, fundir arestas paralelas guardando o melhor candidato, remover vértice de grau < k) com uma fila de candidatos. A classe vale sse o processo termina na configuração mínima; a ordem não importa quando o sistema é confluente, e tudo roda em O(V + E).",
      signal="grafos série-paralelos, cactos, 'planar com dual árvore', k-core; maior/menor ciclo ou caminho nessas classes",
      contexts=["reconhecer árvore podando folhas",
                "k-core/degeneração removendo vértices de grau < k",
                "resistência equivalente ou melhor caminho entre dois terminais em série-paralelo"]),
    I("hall-two-consumers", "graph-modeling", 1, ["nac2026-M#1"]),

    # ---- Estado e representação ----
    I("product-graph-pairs", "state", 3, ["lac2025-A#0", "nac2022-K#1"],
      name="Grafo produto: estado = par de posições",
      statement="Para raciocinar sobre duas execuções ao mesmo tempo (as duas pontas de um palíndromo, duas strings no mesmo autômato, dois robôs), use estados pares (u, v): transições sincronizadas movem os dois, livres movem um, e BFS/caminho mínimo no grafo produto (O(s²) estados) resolve. Para palíndromos, parta dos centros (u, u) e das arestas únicas.",
      signal="palíndromo sobre caminhos de grafo; dois agentes/strings com condição conjunta; poucos estados (s ≤ 300) ou M² cabendo",
      contexts=["menor caminho palíndromo (ABC197 F)",
                "dois robôs num labirinto recebendo os mesmos comandos",
                "equivalência/interseção de DFAs por BFS em pares de estados"]),
    I("advance-lagging-path", "state", 2, ["latam_regional2025-I#1"]),
    I("time-expanded-state", "state", 2, ["latam2022-C#0"]),
    I("window-bitmask-state", "state", 2, ["nac2023-H#0"]),
    I("drop-determined-dimension", "state", 2, ["nac2024-M#0"]),
    I("drop-dominated", "state", 3, ["nerc2022dec-L#2", "nac2024-C#0"],
      name="Descarte o que é dominado",
      statement="Se dois estados, regras ou candidatos são comparáveis e um é sempre pelo menos tão bom (menos custo e menos recurso; uma regra anterior com a mesma condição), o dominado nunca decide a resposta: descarte-o. Guardar só o melhor por chave pequena reduz o tamanho efetivo de n ao número de chaves distintas.",
      signal="DP com várias coordenadas em que 'menor é sempre melhor'; listas enormes de regras/ifs com poucas condições distintas",
      contexts=["caminho mínimo com recurso guardando só rótulos não dominados",
                "mochila com fronteira de Pareto (custo, peso)",
                "tabela de roteamento com primeira correspondência: só a primeira regra por condição importa"]),
    I("dedupe-by-features", "state", 2, ["nerc2021-E#1"]),
    I("checker-to-dp", "state", 3, ["nerc2022dec-L#1"]),
    I("enumerate-type-counts", "state", 2, ["nac2022-H#0"]),
    I("closed-under-composition", "state", 3, ["latam2019-C#0"]),
    I("spread-to-subobjects", "state", 2, ["latam2021-J#0"]),
    I("distinct-successor", "state", 2, ["lac2025-I#0"]),
    I("log-of-product", "state", 2, ["nerc2021-D#1"]),
    I("aggregate-moments", "state", 2, ["nerc2021-E#0"]),
    I("powers-of-two-lex", "state", 2, ["latam2022-F#0"]),
    I("reciprocals-parallel", "state", 1, ["latam2021-A#0"]),
    I("interleave-ends-palindrome", "state", 1, ["nac2021-E#0"]),

    # ---- Limites de tamanho e amortização ----
    I("harmonic-blocks", "bounds", 3, ["latam2021-B#1"]),
    I("bounded-by-smallest-group", "bounds", 2, ["nerc2019-J#1"]),
    I("distinct-parts-sqrt", "bounds", 2, ["apac2024-M#1"]),
    I("halving-log-changes", "bounds", 3, ["apac2026-I#1", "nac2025-M#0"],
      name="Cada mudança ao menos dobra ⇒ só log mudanças",
      statement="Se cada mudança efetiva de um valor o divide por ≥ 2 (cadeia de divisibilidade, gcd/AND/OR de prefixo, a mod x efetivo, queda de faixa de potência de 2), cada elemento muda O(log V) vezes: comprima a sequência em 'valores distintos + pontos de mudança' ou simule ingenuamente só os elementos ainda ativos.",
      signal="gcd/AND/OR de prefixos ou subarrays; divisibilidade em cadeia; mod/divisão/subtração repetidas com valores até 1e18",
      contexts=["gcd de todos os subarrays: O(log M) valores distintos por fim (CF 475D)",
                "a_i mod x em intervalo (segtree beats)",
                "OR de subarrays: ≤ 30 valores distintos por fim"]),
    I("sqrt-split-parameter", "bounds", 3, ["latam2023b-F#0"]),
    I("large-forced-small-brute", "bounds", 3, ["latam2023b-K#0", "nac2022-L#0", "nerc2022dec-D#1"],
      name="Grande é garantido, pequeno é força bruta",
      statement="Quando a propriedade buscada só pode falhar em instâncias pequenas (pombos, Erdős–Szekeres, crescimento tipo Fibonacci: sem triângulo ⇒ no máximo ~log_φ V elementos) ou a saída tem teto (min(resposta, LIMITE)), resolva todos os casos grandes de uma vez com uma regra simples ou resposta garantida e reserve a busca exponencial ou quadrática para o que sobra abaixo do limiar.",
      signal="valores até 1e9/1e18 com 'existem 3 que…'; saída 'min(resposta, 10^6)'; N, K ≤ 300 com pergunta sobre todas as permutações/subconjuntos",
      contexts=["triângulo em subarray por consulta (CF 1991F)",
                "n > 2^k números garantem dois subconjuntos de mesma soma",
                "Erdős–Szekeres: n > (a − 1)(b − 1) garante subsequência monótona longa"]),
    I("stop-at-first-success", "bounds", 2, ["apac2024-G#0"]),
    I("explosive-count-small-tail", "bounds", 2, ["latam_regional2024-I#1"]),
    I("dominant-penalty", "bounds", 1, ["apac2024-B#0"]),
    I("trivial-solution-bounds", "bounds", 2, ["nac2022-E#0"]),

    # ---- Geometria ----
    I("angular-arcs", "geometry", 2, ["latam2019-B#1", "latam2019-D#0", "latam2023b-H#1", "lac2026-C#1", "nerc2025-I#3"],
      contexts=["direção de projeção que ordena pontos como exigido (cada par dá um semicírculo)",
                "círculo coberto pela união de discos: cada disco cobre um arco",
                "visibilidade em torno de um convexo: cada ponto vira o arco entre as duas tangentes",
                "holofote de abertura fixa que ilumina o máximo de pontos"]),
    I("few-active-constraints", "geometry", 2, ["lac2025-J#2", "lac2026-C#0", "nac2022-B#0", "nac2026-G#2"],
      name="Ótimo geométrico tocado por 2–3 restrições",
      statement="Em otimização sobre círculos, retas ou pontos livres no plano, pegue uma solução ótima e empurre/gire/encolha sem piorar até ela encostar em 2–3 objetos da entrada (pontos, bordas, fronteiras de discos). Isso troca um espaço contínuo por O(n²)–O(n³) candidatos definidos por duplas/triplas de objetos (mais o extremo de cada objeto), que se enumeram e verificam.",
      signal="maior/menor círculo ou calota com condição de vazio/cobertura; melhor reta/semiplano; 'ponto mais alto/fundo' numa região de discos; n ≤ 50–2000",
      contexts=["menor círculo envolvente (determinado por 2–3 pontos)",
                "reta que passa pelo maior número de pontos / separador linear",
                "maior círculo vazio dentro de um polígono",
                "ponto mais baixo na interseção de discos"]),
    I("integrate-between-events", "geometry", 2, ["nerc2021-F#3", "nerc2023-I#1"]),
    I("star-shaped-angular", "geometry", 2, ["latam2021-I#0"]),
    I("fix-segment-split-sides", "geometry", 2, ["latam2022-A#0"]),
    I("minkowski-existential", "geometry", 2, ["latam2023a-G#0"]),
    I("separate-axes", "geometry", 2, ["nerc2024-L#0"]),

    # ---- Construções ----
    I("extremal-choice", "constructions", 3, ["latam_regional2024-B#0"]),
    I("independent-gadgets", "constructions", 2, ["lac2026-G#0", "nerc2023-E#0"],
      name="Peças independentes que somam",
      statement="Para construir um objeto com valores exatos prescritos (exatamente X ocorrências; dois valores dados sob duas leituras), projete peças cujas contribuições são conhecidas e não interferem (cada uma afeta só uma exigência, ou soma sem contagem cruzada), com valores que crescem rápido (triangulares, tetraédricos, potências). Escreva o alvo como soma delas, maior primeiro, e ajuste o resto/paridade à parte.",
      signal="construir string/grafo/número com exatamente k padrões, ou com dois valores prescritos sob duas medidas, com tamanho limitado",
      contexts=["string com exatamente k subsequências 'ab'",
                "CRT: e_i ≡ 1 (mod m_i) e ≡ 0 nos outros módulos",
                "grafo com exatamente k triângulos"]),
    I("comb-spine", "constructions", 1, ["latam2023a-K#1"]),
    I("read-the-bound", "constructions", 3, ["nerc2019-D#1", "nerc2019-H#2"]),
    I("lex-min-feasibility", "constructions", 3, ["latam2022-M#1"]),
    I("induction-on-params", "constructions", 2, ["nerc2022dec-K#1"]),
    I("representatives-recursion", "constructions", 2, ["nerc2019-H#1"]),
    I("bit-recursion", "constructions", 2, ["nac2021-A#1"]),
    I("component-lower-bound", "constructions", 2, ["nerc2023-H#0"]),
    I("per-pair-upper-bound", "constructions", 2, ["nerc2024-A#0"]),
    I("max-of-two-bounds", "constructions", 2, ["nerc2025-G#1"]),
    I("randomize-and-retry", "constructions", 2, ["nerc2022dec-A#1"]),
    I("independent-unknowns", "constructions", 2, ["nac2026-G#1"]),
    I("fix-seed-propagate", "constructions", 2, ["nac2026-A#1", "nerc2025-K#1"],
      name="Fixe a semente e propague",
      statement="Se restrições locais determinam cada valor a partir de vizinhos já conhecidos (x_v = x_u + c numa árvore; regra XOR tipo Lights Out na grade), fixe o mínimo que determina o resto — a raiz, a primeira linha — como variáveis: tudo o mais vira função delas, e as restrições restantes (faixa permitida, última linha) viram condições sobre poucas variáveis (translação, sistema linear, 2-SAT).",
      signal="valores em árvore com diferença fixa por aresta e faixa [L, R]; grade com regra local XOR entre vizinhos e pedido de reconstrução",
      contexts=["Lights Out: a primeira linha determina os demais toques",
                "potenciais em grafo: diferenças por aresta, consistência checada nos ciclos",
                "inverter autômato celular linear (regra 90)"]),
    I("edge-coloring-rounds", "constructions", 2, ["apac2025-B#0"]),
    I("commutator-local-op", "constructions", 2, ["nac2024-F#0", "nerc2022dec-J#2"],
      name="Combine operações grandes numa operação local",
      statement="Se as operações permitidas afetam muitos elementos de uma vez, combine duas que diferem minimamente (somar numa linha e subtrair na vizinha; comutador A·B·A⁻¹·B⁻¹, que só mexe na interseção dos suportes) para obter uma primitiva que move só 2–3 peças. Com ela, fixe uma peça por vez sem desfazer as anteriores e resolva o resto por um invariante global.",
      signal="'imprima no máximo K operações que levam ao alvo' com operações que mexem em linhas, anéis ou conjuntos inteiros",
      contexts=["cubo de Rubik e quebra-cabeças de anéis",
                "ordenar com rotações de 3 elementos (paridade)",
                "trocas entre bases vizinhas de um matroide"]),

    # ---- Probabilidade ----
    I("condition-on-statistic", "probability", 2, ["latam2022-L#0", "nac2023-H#1"],
      name="Condicione no que torna o resto determinístico",
      statement="Em processos aleatórios, procure uma estatística pequena (quantos pares cheios, as partes inteiras de uniformes deslocadas, o número de ciclos) que, fixada, torna o restante determinístico ou simétrico (todas as ordens equiprováveis). Então E[X] = Σ_k P(K = k)·f(k), com P(K = k) por contagem combinatória.",
      signal="processo em fases em que só a primeira tem regra aleatória complicada; uniformes contínuas com suportes inteiros deslocados; resposta mod primo",
      contexts=["probabilidades em permutações aleatórias condicionando no número de pontos fixos/ciclos",
                "probabilidade de uma ordem entre uniformes de intervalos diferentes",
                "número esperado de componentes após um sorteio inicial seguido de regra fixa"]),
    I("uniform-subset-by-size", "probability", 2, ["nerc2019-G#1", "nac2025-J#1"],
      name="Ordem aleatória: o que resta é subconjunto uniforme",
      statement="Remover (ou escolher) elementos uniformemente ao acaso, um a um, equivale a uma permutação aleatória: após j passos o conjunto restante é uniforme entre os de tamanho n − j. Se a escolha livre não afeta o custo, troque-a por escolha aleatória sem mudar a esperança. A esperança vira soma por (tamanho, soma) de subconjuntos — contada por mochila — dividida por C(n, k).",
      signal="'remova um elemento aleatório até…'; esperança sobre coleção de itens (n ≤ 100) cujo estado natural seria o subconjunto",
      contexts=["apagar arestas aleatórias até desconectar",
                "coupon collector com itens que também podem ser comprados",
                "probabilidade de o conjunto restante ser independente/ordenado"]),
    I("merge-random-samples-order", "probability", 2, ["latam2021-G#2"]),
    I("skip-noop-steps", "probability", 2, ["nerc2022dec-G#0"]),
    I("simulate-mass", "probability", 2, ["nac2022-F#0"]),
    I("sufficient-statistic-counts", "probability", 1, ["nerc2025-J#0"]),
    I("linear-in-resource-extreme", "probability", 2, ["nerc2025-J#1"]),
    I("log-loss-entropy", "probability", 1, ["nerc2025-L#0"]),

    # ---- Jogos ----
    I("mirror-pairs-cancel", "games", 2, ["lac2026-I#0", "nac2023-E#1"],
      name="Espelho: pares iguais se anulam",
      statement="Em jogos de dois jogadores, se movimentos vêm em pares tais que responder com o par neutraliza o lance do oponente sem mudar o resto (cópias de mesmo valor, arestas opostas, pilhas iguais), remova os pares: o vencedor não muda. Analise só o núcleo sem par (multiplicidade ímpar) e confirme por força bruta em instâncias pequenas.",
      signal="jogo com multiconjunto, pilhas ou arestas repetidas/simétricas; resultado por paridade ou soma",
      contexts=["Nim: pilhas iguais se anulam no XOR",
                "estratégia simétrica pelo centro do tabuleiro",
                "jogo de divisores com estratégia de pareamento"]),
    I("solve-last-mover-first", "games", 2, ["latam2021-G#1"]),
    I("one-loser-per-line", "games", 2, ["nac2021-K#0"]),
    I("brute-force-pattern", "games", 2, ["nac2023-L#0"]),
    I("control-parity-game", "games", 2, ["nerc2025-F#0"]),
    I("tolerance-layers", "games", 2, ["nerc2024-I#1"]),

    # ---- Interativos ----
    I("neutralize-known", "interactive", 2, ["apac2025-E#0"]),
    I("signatures-count", "interactive", 2, ["latam2023a-K#0", "nac2023-A#0"],
      name="Assinaturas distintas: capacidade = número de códigos",
      statement="Para identificar ou distinguir um entre K itens com testes, associe a cada item a assinatura de resultados que ele produziria: uma estratégia funciona sse as assinaturas são distintas. Conte quantas assinaturas t recursos geram (2^t em sim/não, 3^t em balança, (d+1)^t com d rodadas) para o limite inferior, e atinja-o dando ao k-ésimo item o código de k nessa base.",
      signal="'mínimo de testes/ratos/rótulos para identificar ou distinguir K coisas', K até 1e18 e resposta pequena",
      contexts=["garrafa envenenada com ratos (base 2; com d dias, base d+1)",
                "pesagem de moedas falsas (base 3)",
                "perguntas por conjuntos para descobrir um elemento bit a bit"]),
    I("incremental-group-bsearch", "interactive", 2, ["nac2026-L#1"]),
    I("unit-step-comparison", "interactive", 1, ["nerc2022dec-H#1"]),
    I("minimax-decision-tree", "interactive", 2, ["nerc2022dec-I#1"]),
    I("probability-mass-bisection", "interactive", 2, ["nerc2024-H#0"]),
    I("statistic-identifies-target", "interactive", 2, ["nerc2022dec-B#0"]),
]

# ---------------------------------------------------------------------------
# Aprofundamentos B canônicos
# ---------------------------------------------------------------------------
def B(id, gen, steps, **kw):
    d = dict(id=id, generality=gen, steps=steps)
    d.update(kw)
    return d


DEEPENINGS = [
    B("geography-matching", 2, ["lac2024-C#0"]),
    B("matching-alternating-flex", 2, ["lac2024-C#1", "nerc2022dec-D#2"],
      name="Caminhos alternantes dizem o que é obrigatório num emparelhamento",
      property="Dado um emparelhamento máximo M, v fica fora de algum emparelhamento máximo sse é livre ou alcançável de um livre do mesmo lado por caminho alternante par; e remover u e v de um emparelhamento perfeito mantém um perfeito sse uv ∈ M ou há caminho M-alternante entre os parceiros u' e v'. Tudo sai de buscas de alcançabilidade no grafo dirigido por M.",
      why="Deslizar M ao longo de um caminho alternante troca qual vértice fica livre sem mudar |M|; reciprocamente, a diferença simétrica entre M e outro emparelhamento ótimo é formada exatamente por esses caminhos.",
      signal="quais vértices/arestas são obrigatórios, opcionais ou proibidos em emparelhamentos máximos; 'e se removermos estes vértices'",
      contexts=["decomposição de Dulmage–Mendelsohn",
                "casas cuja remoção mantém um tabuleiro ladrilhável por dominós",
                "verificar unicidade do emparelhamento máximo"]),
    B("subset-sum-sqrt", 2, ["lac2024-F#1"]),
    B("divisor-zeta-lcm", 2, ["lac2024-G#1"]),
    B("kmp-periods", 2, ["lac2024-H#1", "latam2023a-L#1"],
      name="Períodos pela função prefixo",
      property="O menor período de s[0..i] é (i + 1) − π[i], e ele não diminui quando o prefixo cresce; se o menor período p divide n, as rotações que fixam a string são exatamente os múltiplos de p, e uma rotação de T igual a S existe sse S ocorre em T+T.",
      why="p é período sse há borda de tamanho n − p, e a maior borda dá o menor período; se k e n são períodos, pelo lema de Fine–Wilf gcd(k, n) também é.",
      signal="strings sob rotação (colares); 'menor bloco que gera o prefixo'; repetições de um bloco de tamanho ≤ D",
      contexts=["decidir se S é potência de outra string",
                "contar rotações distintas de uma string (Burnside)",
                "quantas vezes cada prefixo é uma potência"]),
    B("integer-hull-size", 1, ["lac2024-I#0"]),
    B("xor-basis-certificate", 2, ["lac2025-B#2"]),
    B("kruskal-reconstruction-tree", 2, ["lac2025-D#2"]),
    B("segtree-on-time", 3, ["lac2025-F#1"]),
    B("sphere-hull-delaunay", 1, ["lac2025-J#1"]),
    B("centroid-fft-distances", 1, ["lac2026-H#1"]),
    B("kinetic-order", 2, ["lac2026-L#0", "latam2023a-J#0", "nac2024-K#1"],
      base="Sweep line",
      name="Ordem cinética: só trocas de vizinhos",
      property="Se n objetos estão ordenados por uma chave que depende de um parâmetro (tempo, ângulo) e cada par troca de ordem no máximo uma vez, a ordem muda em O(n²) eventos, cada um uma troca de adjacentes: mantenha num heap (ou ordene) os próximos cruzamentos e, a cada troca, atualize só os pares e somas de prefixo afetados.",
      why="Entre eventos a ordem é constante; duas funções lineares se cruzam no máximo uma vez e, no instante do cruzamento, os dois objetos são adjacentes, então só as adjacências deles mudam.",
      signal="pontos com velocidade constante ou direção que gira, com consultas sobre a ordem/gaps em vários instantes",
      contexts=["ranking de corredores ao longo de uma corrida",
                "girar uma direção mantendo a ordem das projeções (rotating sweep line)",
                "k-ésimo nível de um arranjo de retas"]),
    B("dfs-deepest-back-edge", 2, ["latam_regional2024-B#1"]),
    B("rerooting-offline", 2, ["latam_regional2024-G#1"]),
    B("periodic-rebuild", 3, ["latam_regional2024-H#1"]),
    B("bit-descent", 2, ["latam_regional2025-C#2"]),
    B("multiplicative-order", 1, ["latam_regional2025-D#1"]),
    B("planar-mincut-dual", 2, ["latam_regional2025-G#1"]),
    B("persistent-kth-diff", 2, ["apac2024-K#1"]),
    B("series-inverse-blocks", 2, ["apac2024-M#2"]),
    B("segtree-function-composition", 3, ["apac2025-D#1"]),
    B("suffix-order-incremental", 1, ["apac2026-A#0"]),
    B("hld-dynamic-dp", 2, ["apac2026-D#1"]),
    B("iterated-prefix-binomial", 2, ["nac2021-G#0", "apac2026-I#2"],
      base="Soma de prefixos",
      name="Soma de prefixos iterada = binomiais",
      property="Aplicar soma de prefixos k vezes é convoluir com C(i + k − 1, k − 1); em particular Σ_{j<l} C(j, k) = C(l, k + 1) (taco de hóquei). Escrevendo funções de contagem na base binomial C(l, k), somas de prefixo só deslocam índices e se manipulam pelos coeficientes.",
      why="k aplicações contam sequências não crescentes de k índices, isto é, multiconjuntos (estrelas e barras); a identidade de Pascal C(j, k) = C(j + 1, k + 1) − C(j, k + 1) telescopa.",
      signal="operação 'substitua pelo acumulado' repetida k vezes; contagem de sequências não decrescentes de comprimento grande",
      contexts=["aplicar soma de prefixos k vezes mod p em O(n)",
                "número de sequências não decrescentes de tamanho l",
                "tamanho de expansões recursivas que crescem como polinômio de grau k"]),
    B("dilworth-matching", 2, ["latam2019-A#1"]),
    B("half-plane-angular-gap", 2, ["latam2019-D#1"]),
    B("affine-weight-prefix", 2, ["latam2019-F#1"]),
    B("segtree-descent", 3, ["latam2019-J#1", "nerc2023-G#2"],
      property="Numa segment tree de máximos (ou somas), o primeiro índice ≥ l com valor > x (ou o primeiro prefixo com soma ≥ k) é encontrado em O(log n) descendo pela árvore, em vez de busca binária + consulta em O(log² n), com atualizações pontuais."),
    B("monostack-best-dp", 2, ["latam2021-F#1"]),
    B("flow-walk-edge-limits", 2, ["latam2021-H#0"]),
    B("convex-polygon-dp-last-two", 2, ["latam2021-I#1"]),
    B("sam-append-suffixes", 1, ["latam2021-M#0"]),
    B("correlation-convolution", 2, ["latam2022-B#2"]),
    B("li-chao-single-crossing", 2, ["latam2023b-A#0"]),
    B("linear-multiset-hash", 3, ["latam2023b-C#1", "nerc2022dec-B#1"],
      name="Hash linear de multiconjunto (atualização O(1))",
      property="Dê a cada valor um peso aleatório (ou b^i) e faça o hash de um multiconjunto/vetor de contagens ser a soma (ou XOR) dos pesos: é comutativo e linear, então incrementar uma contagem, somar uma constante a todas ou tirar a diferença de dois prefixos atualiza o hash em O(1).",
      why="Pela linearidade a variação do hash depende só da variação do vetor; com pesos aleatórios de 64 bits, dois multiconjuntos distintos colidem com probabilidade ~2^-64.",
      signal="comparar conjuntos/multiconjuntos de subarrays ou subárvores ignorando a ordem; vetores de contagem grandes que mudam uma coordenada por passo",
      contexts=["checar se um subarray é permutação de 1..k",
                "subarrays em que cada valor aparece múltiplo de 3 vezes",
                "igualdade de multiconjuntos de filhos em árvores"]),
    B("centroid-nearest-marked", 2, ["latam2023b-J#0"]),
    B("bitmask-greedy-embedding", 1, ["latam2023b-K#1"]),
    B("vertex-on-all-shortest", 2, ["latam2023b-M#1"]),
    B("power-diagram", 1, ["nac2021-B#0"]),
    B("tutte-gadget", 2, ["nac2021-H#1"]),
    B("matching-in-tree-dp", 2, ["latam2023a-F#1"]),
    B("matroid-kruskal-oracle", 2, ["nac2021-I#0"]),
    B("shortest-path-dag", 3, ["nac2021-L#1"]),
    B("previous-factor-sa", 1, ["nac2022-C#1"]),
    B("harmonic-multiples-aggregate", 2, ["nac2022-E#2"]),
    B("dfs-enter-exit-state", 3, ["nac2022-G#1"]),
    B("path-intersection-lca", 2, ["nac2023-B#1"]),
    B("kruskal-tiebreak-closest", 1, ["nac2023-C#0"]),
    B("bitset-triples", 2, ["nac2024-C#2"]),
    B("segtree-coverage", 2, ["nac2024-H#1", "nac2026-C#2"],
      base="Segment tree",
      name="Comprimento coberto pela união de intervalos",
      property="Para manter o comprimento (ou peso) coberto por ≥ 1 intervalo sob inserções/remoções ou add em intervalo, guarde em cada nó (a) cnt de intervalos que o cobrem inteiro, sem propagar, e len = tamanho do nó se cnt > 0, senão a soma dos filhos; ou (b) com lazy de soma, o mínimo da cobertura e o peso que atinge esse mínimo: coberto = total − peso do mínimo, se o mínimo é 0.",
      why="(a) Cada remoção desfaz uma inserção que se decompôs nos mesmos O(log n) nós, então cnt nunca precisa descer nem fica negativo; (b) a cobertura nunca é negativa, logo 0 só aparece como mínimo, e (mínimo, contagem) se combina com lazy.",
      signal="área/perímetro da união de retângulos; comprimento coberto sob toggles de intervalos; quantos zeros há sob add em intervalo",
      contexts=["área da união de retângulos (sweep line)",
                "contar subarrays com max − min = r − l",
                "perímetro da união de retângulos"]),
    B("product-except-one", 2, ["nac2025-B#1"]),
    B("small-to-large-cartesian", 2, ["nac2025-E#2"]),
    B("expectation-by-tail", 3, ["nac2025-J#0"]),
    B("dc-polynomials-border", 1, ["nac2025-J#2"]),
    B("prufer-bipartite", 1, ["nerc2019-F#1"]),
    B("kuhn-vertex-weights", 2, ["nerc2021-B#2"]),
    B("green-area-arcs", 2, ["nerc2021-F#2"]),
    B("tree-knapsack-n2", 3, ["nerc2021-H#2"]),
    B("mw-calibrate-beta", 1, ["nerc2021-I#1"]),
    B("floor-sum-continued-fractions", 2, ["nerc2022apr-H#2"]),
    B("mincut-vertex-copies", 2, ["nerc2022apr-K#0"]),
    B("ternary-sos", 2, ["nerc2022dec-G#2"]),
    B("spanning-tree-per-block", 1, ["nerc2022dec-J#0"]),
    B("cauchy-perimeter", 1, ["nerc2023-I#0"]),
    B("flow-edge-mandatory", 2, ["nerc2024-K#1"]),
    B("sa-lcp-dsu-classes", 2, ["nerc2025-L#1"]),
    # vindo de um passo C (é propriedade de uma estrutura, não insight solto)
    B("prefix-max-range-update", 1, ["nerc2023-G#1"],
      base="Segment tree com lazy",
      name="Range add muda os máximos de prefixo num único intervalo",
      property="Se a[l..r] += 1, o array de máximos de prefixo muda (+1) num único intervalo contíguo: do primeiro índice em [l, r] que supera max(a[0..l−1]) até antes do primeiro índice à direita de r que já era grande o bastante. Assim prefmax/sufmax podem ser mantidos com lazy sob atualizações de intervalo.",
      why="Antes de l nada muda; prefmax é monótono, então os índices de [l, r] cujo prefmax passa a vir de dentro da faixa formam um sufixo dela, e à direita de r o efeito some a partir do primeiro elemento ≥ novo máximo.",
      signal="atualizações de intervalo e consultas que dependem de máximos de prefixo/sufixo (recordes, visibilidade, água retida)",
      contexts=["contar recordes (elementos visíveis da esquerda) sob atualizações",
                "manter Σ prefmax sob incrementos de intervalo",
                "água retida sob atualizações"]),
]

# ---------------------------------------------------------------------------
# Reclassificações
# ---------------------------------------------------------------------------
# Passos C que são, na verdade, técnicas com nome (viram A)
C_TO_A = {
    "lac2025-G#1": "Map de intervalos (Chtholly/ODT)",
    "apac2024-B#1": "Ordem de degeneração",
}
# Passos B fundidos num insight C (listados em INSIGHTS.steps): nac2026-B#1, nerc2021-C#3
# Passo C movido para B (listado em DEEPENINGS.steps): nerc2023-G#1

# Nomes de técnica A: sinônimos -> canônico
TECH_ALIASES = {
    "Ponto em polígono convexo (O(log n))": "Ponto em polígono convexo",
}


# ---------------------------------------------------------------------------
# Revisão crítica (pipeline/curriculum/review.json), etapa 3 do SPEC.
# As seções estruturadas (merges, rewrites, drops, regroup, generality) são lidas
# do arquivo e aplicadas; o que foi rejeitado ou ajustado está abaixo, com o motivo.
# A seção "steps" (texto livre) está transcrita em STEP_* abaixo.
# ---------------------------------------------------------------------------
REVIEW = os.path.join(CUR_DIR, "review.json")

# (seção, id, campo) -> texto que substitui a proposta do revisor
REVIEW_OVERRIDE = {
    # A proposta dizia "o mínimo ou a soma ... basta usar d primo": para somas isso conta duas vezes
    # os y que compartilham vários primos com x. Mantida a ideia (só primos), restrita a min/max/existência.
    ("rewrites", "harmonic-multiples-aggregate", "property"):
        "Para calcular, para todo x, o mínimo (ou máximo, ou existência) de h(y) sobre os y que compartilham "
        "um divisor d ≥ 2 com x, basta usar d primo (ω(x) ≤ 7 para x ≤ 1e6): faça g[d] = agregado de h sobre "
        "os múltiplos de d e depois agregue g[d] sobre os divisores primos de x — o primeiro passo custa "
        "Σ V/p = O(V log log V). Para somas, os primos contariam duas vezes quem compartilha vários fatores: "
        "use todos os divisores com Möbius, em O(V log V).",
}
REVIEW_REJECT = set()  # (seção, id) rejeitados por inteiro — nenhum

# Campos que faltam nos itens que mudam de categoria
REVIEW_EXTRA = {
    "matroid-kruskal-oracle": dict(generality=3),  # MST, emparelhamento, base XOR, escalonamento
    "periodic-coincidence-gcd": dict(
        base="CRT", name="CRT não coprimo: coincidências por resíduo mod gcd",
        why="O sistema τ ≡ i (mod p), τ ≡ j (mod q) tem solução sse i ≡ j (mod g), g = gcd(p, q), e então ela é "
            "única módulo lcm(p, q) (CRT generalizado); por isso cada par compatível ocorre exatamente uma vez por "
            "período lcm, e basta agrupar as posições de cada sequência pelo resíduo mod g."),
    "ie-flip-inequalities": dict(
        base="Inclusão-exclusão",
        why="Para cada conjunto S de relações '>' trocadas, o termo com sinal (−1)^{|S|} conta sequências em que as "
            "relações de S valem na forma oposta não estrita e as demais ficam livres; cortando nas relações livres, "
            "cada termo é uma concatenação de blocos monótonos, contada por produto ou pela série 1/(1 − A)."),
}

# Notas internas que não podem chegar ao site
NOTE_PATTERNS = [r"\s*\(ideia de raciocínio próprio[^)]*\)", r";\s*dúvida:[^.;]*"]
FORBIDDEN_TEXT = ["não verificad", "dúvida"]

# Correções de passos (chaves 0-based; o revisor numera a partir de 1)
STEP_TEXT = {
    "latam_regional2025-A#1": "Arestas não usadas devem formar trilha do fim do prefixo ao começo do sufixo: paridade de "
                              "graus + conectividade (BFS no complemento, O(N²)); o número de arestas restantes já fixa "
                              "o tamanho do trecho oculto.",
    "latam_regional2025-G#0": "Fluxo máximo = corte mínimo = mínimo de funções lineares em t, logo côncavo em t: busca "
                              "ternária sobre t inteiro (cuidado com platôs: compare f(m) com f(m+1)).",
    "latam_regional2025-L#0": "Cada reta corta a região y > Ax² + B numa corda aberta entre as raízes x1 < x2 de "
                              "Ax² − Mx + (B − C) = 0; a região é convexa (A > 0), condição para o critério de cordas "
                              "intercaladas valer.",
    "lac2024-I#1": "Empurrar o ponto novo para fora só aumenta a área, então ele fica na circunferência; para cada par "
                   "(i, j) de futuros vizinhos, o ápice ótimo é o ponto do círculo mais distante da corda ij.",
    "latam2022-F#0": "O vértice N pesa mais que todos os outros juntos: Ana fica com N, e Bob, com N − 1, leva tudo o que "
                     "consegue — a componente de N − 1 em G − N; o resto fica com Ana, ligado por N.",
    "lac2025-K#0": "Nos ciclos completos a ordem ótima é fixa — atacar, multiplicar, somar —, o que se verifica comparando "
                   "duas cartas vizinhas de tipos diferentes; só o ciclo final parcial pede enumerar quantas de cada "
                   "tipo usar.",
}
# Passo substituído por inteiro (antes da atribuição): {campos do passo}
STEP_REPLACE = {
    # dois passos A 'Bipartição' repetidos após two-bins-bipartite → A viram um só
    "lac2024-E#1": {"kind": "estrutura/algoritmo", "cat": "A", "technique": "Bipartição (2-coloração)",
                    "text": "Grafo de conflitos (pares que se cruzam) 2-colorido por BFS/DFS em O(N²); as cores são as filas."},
    # product-except-one descartado: o passo vira uso de soma (produto) de prefixos
    "nac2025-B#1": {"cat": "A", "technique": "Soma de prefixos"},
    # passo sem categoria que escondia o insight de configuração crítica
    "lac2024-I#1": {"cat": "C"},
}
STEP_DELETE = {"lac2024-E#2"}
# Passos acrescentados a itens existentes (depois das fusões)
STEP_ADD = {"breakpoint-optimum": ["lac2024-I#1"]}

# Grupos: renomear, dividir state e acrescentar 'representation' logo depois dele
GROUP_RENAME = {"order-time": "Ordem de processamento e eventos", "state": "Estado de DP e de busca"}
GROUP_INSERT_AFTER = {"state": ("representation", "Mudar a representação")}


def apply_review(probs):
    """Aplica review.json sobre INSIGHTS/DEEPENINGS (em memória) e corrige passos. Retorna um log."""
    with open(REVIEW, encoding="utf-8") as fh:
        rv = json.load(fh)
    log = {"merges": 0, "rewrites": 0, "drops": 0, "regroup": 0, "generality": 0, "rejected": []}
    items = {}  # id -> (cat, spec)
    for x in INSIGHTS:
        items[x["id"]] = ("C", x)
    for x in DEEPENINGS:
        items[x["id"]] = ("B", x)

    def ov(sec, iid, field, val):
        return REVIEW_OVERRIDE.get((sec, iid, field), val)

    # --- passos
    for key, rep in STEP_REPLACE.items():
        pid, idx = key.rsplit("#", 1)
        s = probs[pid]["steps"][int(idx)]
        for f in ("name", "statement", "signal", "contexts", "known_problems", "base", "property", "why", "specific"):
            if rep.get("cat") == "A":
                s.pop(f, None)
        s.update(rep)
    for key, txt in STEP_TEXT.items():
        pid, idx = key.rsplit("#", 1)
        probs[pid]["steps"][int(idx)]["text"] = txt
    for p in probs.values():
        for s in p.get("steps", []):
            for pat in NOTE_PATTERNS:
                s["text"] = re.sub(pat, "", s["text"])

    def text_of(spec):  # campos do passo primário, para itens que mudam de categoria
        pid, idx = spec["steps"][0].rsplit("#", 1)
        return probs[pid]["steps"][int(idx)]

    # --- merges
    for m in rv["merges"]:
        if ("merges", m["keep"]) in REVIEW_REJECT:
            log["rejected"].append(("merges", m["keep"]))
            continue
        cat, keep = items[m["keep"]]
        prim = text_of(keep)
        merged_ctx, merged_sig, merged_kp = list(keep.get("contexts") or prim.get("contexts") or []), \
            [keep.get("signal") or prim.get("signal")], []
        for a in m["absorb"]:
            _, sa = items.pop(a)
            pa = text_of(sa)
            keep["steps"] = keep["steps"] + [k for k in sa["steps"] if k not in keep["steps"]]
            merged_ctx.append((sa.get("contexts") or pa.get("contexts") or [None])[0])
            merged_sig.append(sa.get("signal") or pa.get("signal"))
            merged_kp += sa.get("known_problems") or []
            for k in sa["steps"]:
                p2, i2 = k.rsplit("#", 1)
                merged_kp += probs[p2]["steps"][int(i2)].get("known_problems") or []
        keep.setdefault("contexts", dedup(merged_ctx)[:5])
        keep.setdefault("signal", "; ".join(dedup(merged_sig)))
        if merged_kp:
            base_kp = keep.get("known_problems")
            if base_kp is None:
                base_kp = dedup(x for k in keep["steps"] for x in (text_of({"steps": [k]}).get("known_problems") or []))
            keep["known_problems"] = dedup(base_kp + merged_kp)
        for f in ("name", "statement", "property", "why"):
            if m.get(f):
                keep[f] = ov("merges", m["keep"], f, m[f])
        if m.get("category") == "C" and cat == "B":
            keep["statement"] = keep.pop("property", None) or keep.get("statement")
            keep.pop("why", None)
            keep.pop("base", None)
            keep["group"] = m["group"]
            cat = "C"
        items[m["keep"]] = (cat, keep)
        log["merges"] += 1

    # --- drops / mudanças de categoria
    drop_assign = {}
    for d in rv["drops"]:
        if ("drops", d["id"]) in REVIEW_REJECT:
            log["rejected"].append(("drops", d["id"]))
            continue
        cat, spec = items.pop(d["id"])
        if d["action"] == "to_A":
            for k in spec["steps"]:
                drop_assign[k] = ("A", d["target"])
        elif d["action"] == "drop":
            for k in spec["steps"]:
                drop_assign[k] = ("null", "dropped")
        elif d["action"] == "to_B":
            prim = text_of(spec)
            extra = REVIEW_EXTRA.get(d["id"], {})
            nb = dict(id=spec["id"], generality=spec["generality"], steps=spec["steps"],
                      base=extra.get("base", d["target"]),
                      name=extra.get("name") or spec.get("name") or prim.get("name"),
                      property=spec.get("statement") or prim.get("statement"),
                      why=extra["why"],
                      signal=spec.get("signal") or prim.get("signal"),
                      contexts=spec.get("contexts") or prim.get("contexts"))
            items[d["id"]] = ("B", nb)
        log["drops"] += 1

    # --- rewrites, regroup, generality
    for r in rv["rewrites"]:
        if ("rewrites", r["id"]) in REVIEW_REJECT:
            log["rejected"].append(("rewrites", r["id"]))
            continue
        items[r["id"]][1][r["field"]] = ov("rewrites", r["id"], r["field"], r["proposed"])
        log["rewrites"] += 1
    for r in rv["regroup"]:
        items[r["id"]][1]["group"] = r["group"]
        log["regroup"] += 1
    for g in rv["generality"]:
        spec = items[g["id"]][1]
        if spec["generality"] != g["from"]:
            sys.exit(f"review generality: {g['id']} esperava {g['from']}, tem {spec['generality']}")
        spec["generality"] = g["to"]
        log["generality"] += 1
    for iid, extra in REVIEW_EXTRA.items():
        if iid in items:
            for f, v in extra.items():
                items[iid][1].setdefault(f, v)
            if "generality" in extra:
                items[iid][1]["generality"] = extra["generality"]
    for iid, keys in STEP_ADD.items():
        items[iid][1]["steps"] = items[iid][1]["steps"] + keys

    # --- grupos
    new_groups = []
    for g, n in GROUPS:
        new_groups.append((g, GROUP_RENAME.get(g, n)))
        if g in GROUP_INSERT_AFTER:
            new_groups.append(GROUP_INSERT_AFTER[g])
    GROUPS[:] = new_groups

    INSIGHTS[:] = [s for c, s in items.values() if c == "C"]
    DEEPENINGS[:] = [s for c, s in items.values() if c == "B"]
    for k, v in drop_assign.items():
        p2, i2 = k.rsplit("#", 1)
        if v[0] == "A" and probs[p2]["steps"][int(i2)].get("cat") in ("B", "C"):
            C_TO_A[k] = v[1]
    return log, {k for k, v in drop_assign.items() if v[0] == "null"}


def load_steps():
    probs = {}
    order = []
    for f in sorted(glob.glob(os.path.join(CUR_DIR, "steps_*.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        for p in d["problems"]:
            if p["id"] in probs:
                sys.exit(f"problema duplicado: {p['id']}")
            probs[p["id"]] = p
            order.append(p["id"])
    return probs, order


def load_unverified():
    """Problemas cuja solução é raciocínio próprio (raw solution_source == 'own')."""
    out = set()
    for f in glob.glob(os.path.join(ROOT, "pipeline", "raw", "*.json")):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        for p in (d["problems"] if isinstance(d, dict) else d):
            if p.get("solution_source") == "own":
                out.add(p["id"])
    return out


def load_dataset_ids():
    with open(DATASET, encoding="utf-8") as fh:
        s = fh.read()
    s = s[s.index("=") + 1:].strip().rstrip(";")
    return {p["id"] for p in json.loads(s)["problems"]}


def step_of(probs, key):
    pid, idx = key.rsplit("#", 1)
    return pid, probs[pid]["steps"][int(idx)]


def dedup(seq):
    out, seen = [], set()
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def build():
    probs, order = load_steps()
    review_log, review_nulls = apply_review(probs)
    known_ids = load_dataset_ids()
    unverified = load_unverified()
    errors = []

    # assignment map: key -> ("C", id) | ("B", id) | ("A", tech) | ("null", reason)
    assign = {}

    def claim(key, target):
        if key in assign:
            errors.append(f"passo {key} atribuído duas vezes: {assign[key]} e {target}")
        assign[key] = target

    for ins in INSIGHTS:
        for k in ins["steps"]:
            claim(k, ("C", ins["id"]))
    for dp in DEEPENINGS:
        for k in dp["steps"]:
            claim(k, ("B", dp["id"]))
    for k, t in C_TO_A.items():
        claim(k, ("A", t))
    for k in review_nulls:
        p2, i2 = k.rsplit("#", 1)
        if probs[p2]["steps"][int(i2)].get("cat") in ("B", "C"):
            claim(k, ("null", "dropped"))
    for k in STEP_DELETE:
        if k in assign:
            errors.append(f"passo apagado {k} ainda é referenciado")

    # every C/B step must be assigned (or specific -> null)
    stats = {"C_total": 0, "B_total": 0, "C_specific": 0, "B_specific": 0}
    for pid in order:
        p = probs[pid]
        if not p.get("keep"):
            continue
        for i, s in enumerate(p["steps"]):
            key = f"{pid}#{i}"
            if s.get("cat") not in ("B", "C"):
                if key in assign:
                    errors.append(f"passo {key} (cat {s.get('cat')}) não é B/C mas foi atribuído")
                continue
            stats[s["cat"] + "_total"] += 1
            if s.get("specific"):
                stats[s["cat"] + "_specific"] += 1
                if key in assign:
                    errors.append(f"passo específico {key} foi atribuído a {assign[key]}")
                assign[key] = ("null", "specific")
            elif key not in assign:
                errors.append(f"passo {s['cat']} {key} ({s.get('name')}) sem destino")

    # ---- insights
    group_ids = {g for g, _ in GROUPS}
    insights = []
    for ins in INSIGHTS:
        prim_pid, prim = step_of(probs, ins["steps"][0])
        for k in ins["steps"]:
            pid, s = step_of(probs, k)
            if s.get("cat") not in ("C", "B"):
                errors.append(f"insight {ins['id']}: passo {k} tem cat {s.get('cat')}")
        if ins["group"] not in group_ids:
            errors.append(f"insight {ins['id']}: grupo desconhecido {ins['group']}")
        steps = [step_of(probs, k) for k in ins["steps"]]
        problems, hows = [], {}
        for pid, s in steps:
            if pid not in hows:
                problems.append(pid)
                hows[pid] = []
            hows[pid].append(s["text"])
        kp = ins.get("known_problems")
        if kp is None:
            kp = dedup(x for _, s in steps for x in (s.get("known_problems") or []))
        insights.append({
            "id": ins["id"], "group": ins["group"],
            "name": ins.get("name") or prim.get("name"),
            "statement": ins.get("statement") or prim.get("statement") or prim.get("property"),
            "signal": ins.get("signal") or prim.get("signal"),
            "contexts": ins.get("contexts") or prim.get("contexts") or [],
            "known_problems": kp,
            "generality": ins["generality"],
            "problems": [{"id": pid, "how": " ".join(hows[pid])} for pid in problems],
        })

    # ---- deepenings
    deepenings = []
    for dp in DEEPENINGS:
        prim_pid, prim = step_of(probs, dp["steps"][0])
        steps = [step_of(probs, k) for k in dp["steps"]]
        problems, hows = [], {}
        for pid, s in steps:
            if pid not in hows:
                problems.append(pid)
                hows[pid] = []
            hows[pid].append(s["text"])
        base = dp.get("base") or prim.get("base")
        base = TECH_ALIASES.get(base, base)
        deepenings.append({
            "id": dp["id"], "base": base,
            "name": dp.get("name") or prim.get("name"),
            "property": dp.get("property") or prim.get("property") or prim.get("statement"),
            "why": dp.get("why") or prim.get("why"),
            "signal": dp.get("signal") or prim.get("signal"),
            "contexts": dp.get("contexts") or prim.get("contexts") or [],
            "generality": dp["generality"],
            "problems": [{"id": pid, "how": " ".join(hows[pid])} for pid in problems],
        })
    deepenings.sort(key=lambda d: (d["base"], d["id"]))

    # ---- problem_steps + techniques
    tech_probs = {}
    problem_steps = {}
    moved = {"C->A": 0, "C->B": 0, "B->C": 0}
    for pid in order:
        p = probs[pid]
        if not p.get("keep"):
            problem_steps[pid] = {"keep": False, "discard_reason": p.get("discard_reason")}
            if pid in unverified:
                problem_steps[pid]["unverified"] = True
            continue
        out = []
        for i, s in enumerate(p["steps"]):
            key = f"{pid}#{i}"
            if key in STEP_DELETE:
                continue
            cat, ref = s.get("cat"), None
            if cat == "A":
                ref = TECH_ALIASES.get(s.get("technique"), s.get("technique"))
            elif cat in ("B", "C"):
                kind, target = assign.get(key, ("null", None))
                if kind == "null":
                    cat, ref = None, None
                else:
                    if kind != cat:
                        moved[f"{cat}->{kind}"] += 1
                    cat, ref = kind, target
            if cat == "A":
                if not ref:
                    errors.append(f"passo A sem técnica: {key}")
                tech_probs.setdefault(ref, [])
                if pid not in tech_probs[ref]:
                    tech_probs[ref].append(pid)
            out.append({"kind": s["kind"], "text": s["text"], "cat": cat, "ref": ref})
        entry = {"keep": True, "steps": out}
        if p.get("keep_reason"):
            entry["keep_reason"] = p["keep_reason"]
        if pid in unverified:
            entry["unverified"] = True
        problem_steps[pid] = entry

    # um aprofundamento de X também é uso de X
    for d in deepenings:
        lst = tech_probs.setdefault(d["base"], [])
        for pr in d["problems"]:
            if pr["id"] not in lst:
                lst.append(pr["id"])
    techniques = [{"name": n, "problems": ps} for n, ps in tech_probs.items()]
    techniques.sort(key=lambda t: (-len(t["problems"]), t["name"]))

    cur = {
        "techniques": techniques,
        "deepenings": deepenings,
        "insight_groups": [{"id": g, "name": n, "order": i + 1} for i, (g, n) in enumerate(GROUPS)],
        "insights": insights,
        "problem_steps": problem_steps,
    }

    # ---- validation
    kebab = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    ids = [x["id"] for x in insights] + [x["id"] for x in deepenings] + [g for g, _ in GROUPS]
    for x in ids:
        if not kebab.match(x):
            errors.append(f"id não kebab-case ASCII: {x}")
    if len(set(x["id"] for x in insights)) != len(insights):
        errors.append("ids de insight duplicados")
    if len(set(x["id"] for x in deepenings)) != len(deepenings):
        errors.append("ids de deepening duplicados")
    used_groups = {x["group"] for x in insights}
    for g, _ in GROUPS:
        if g not in used_groups:
            errors.append(f"grupo vazio: {g}")

    def forbidden_in(txt):
        t = (txt or "").lower()
        return [w for w in FORBIDDEN if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", t)]

    for x in insights:
        for f in ("name", "statement", "signal"):
            if not x.get(f):
                errors.append(f"insight {x['id']} sem {f}")
        if len(x["contexts"]) < 2:
            errors.append(f"insight {x['id']} com < 2 contextos")
        if x["generality"] not in (1, 2, 3):
            errors.append(f"insight {x['id']} generality inválida")
        if forbidden_in(x["name"]):
            errors.append(f"insight {x['id']} usa rótulo proibido no nome: {forbidden_in(x['name'])}")
    for x in deepenings:
        for f in ("base", "name", "property", "why", "signal"):
            if not x.get(f):
                errors.append(f"deepening {x['id']} sem {f}")
        if len(x["contexts"]) < 2:
            errors.append(f"deepening {x['id']} com < 2 contextos")
        if forbidden_in(x["name"]):
            errors.append(f"deepening {x['id']} usa rótulo proibido: {x['name']}")
    for g, n in GROUPS:
        if forbidden_in(n):
            errors.append(f"grupo {g} usa rótulo proibido: {n}")
    for t in techniques:
        if forbidden_in(t["name"]):
            errors.append(f"técnica usa rótulo proibido: {t['name']}")

    ins_ids = {x["id"] for x in insights}
    dp_ids = {x["id"] for x in deepenings}
    tech_names = {t["name"] for t in techniques}
    for pid, e in problem_steps.items():
        if pid not in known_ids:
            errors.append(f"problema desconhecido no dataset: {pid}")
        for s in e.get("steps", []):
            c, r = s["cat"], s["ref"]
            ok = (c is None and r is None) or (c == "A" and r in tech_names) or \
                 (c == "B" and r in dp_ids) or (c == "C" and r in ins_ids)
            if not ok:
                errors.append(f"{pid}: ref não resolve ({c}, {r})")
    for coll in (insights, deepenings):
        for x in coll:
            if not x["problems"]:
                errors.append(f"{x['id']} sem problemas")
            for pr in x["problems"]:
                if pr["id"] not in known_ids or pr["id"] not in problem_steps:
                    errors.append(f"{x['id']}: problema desconhecido {pr['id']}")
                if not pr["how"]:
                    errors.append(f"{x['id']}: 'how' vazio em {pr['id']}")
    for t in techniques:
        if not t["problems"]:
            errors.append(f"técnica {t['name']} sem problemas")
    if len(problem_steps) != len(order):
        errors.append("problem_steps não cobre todos os problemas")

    dumped = json.dumps(cur, ensure_ascii=False).lower()
    for w in FORBIDDEN_TEXT:
        if w in dumped:
            errors.append(f"texto interno '{w}' no currículo")
    if errors:
        print("ERROS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(cur, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # ---- report
    kept = sum(1 for e in problem_steps.values() if e["keep"])
    c_assigned = sum(1 for k, v in assign.items() if v[0] == "C")
    print(f"problemas: {len(problem_steps)} (mantidos {kept}, descartados {len(problem_steps) - kept})")
    print(f"passos C: {stats['C_total']} (específicos {stats['C_specific']}), "
          f"B: {stats['B_total']} (específicos {stats['B_specific']}); movidos {moved}")
    print(f"revisão: {review_log}; unverified: {sorted(k for k, e in problem_steps.items() if e.get('unverified'))}")
    print(f"insights: {len(insights)} (de {c_assigned} passos), grupos: {len(GROUPS)}, "
          f"deepenings: {len(deepenings)}, técnicas: {len(techniques)}")
    for g, n in GROUPS:
        print(f"  {g:18s} {sum(1 for x in insights if x['group'] == g):3d}  {n}")
    print("top técnicas:", [(t["name"], len(t["problems"])) for t in techniques[:12]])
    top = sorted(insights, key=lambda x: (-x["generality"] * len(x["problems"]), x["id"]))[:12]
    print("top (generality × #problemas):")
    for x in top:
        print(f"  {x['generality']}×{len(x['problems'])}  {x['id']:30s} {x['name']}")


if __name__ == "__main__":
    build()
