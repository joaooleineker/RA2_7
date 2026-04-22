"""
Integrantes do grupo (ordem alfabética):
- Daniel de Almeida Santos Bina - @danielbina
- Eduardo Ferreira de Melo - @edufmelo
- João Eduardo Faccin Leineker - @joaooleineker

- Nome do grupo no Canvas: RA2 7
"""
import sys
import io

# Força saída UTF-8 no console do Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Importamos o analisador da Fase 1 para ler o arquivo e extrair os tokens.
# Renomeamos de "analisador.py" para "lexico.py" para evitar confusão com o de análise sintática.
from lexico import Token, lerArquivo, parseExpressao, salvarArquivo

def construirGramatica():
    """
    Define as regras de produção da linguagem RPN em formato LL(1).
    Retorna um dicionário com gramática, FIRST, FOLLOW e tabela LL(1).
    """

    # Regras de produção: { nao_terminal: [[producao1], [producao2], ...] }
    regras_producao = {
        "programa": [
            ["comando_lista"]
        ],
        "comando_lista": [
            ["comando", "comando_lista"],
            ["ε"]
        ],
        "comando": [
            ["ABRE_PAREN", "conteudo_comando", "FECHA_PAREN"]
        ],
        "conteudo_comando": [
            ["KEYWORD_START"],
            ["KEYWORD_END"],
            ["NUMERO", "sufixo_numero"],
            ["MEMORIA", "sufixo_memoria"],
            ["comando", "sufixo_comando"]
        ],
        "sufixo_numero": [
            ["KEYWORD_RES"],
            ["NUMERO", "operador_final"],
            ["MEMORIA", "apos_mem"],
            ["comando", "operador_final"]
        ],
        "sufixo_memoria": [
            ["NUMERO", "operador_final"],
            ["MEMORIA", "apos_mem"],
            ["comando", "operador_final"],
            ["ε"]
        ],
        "sufixo_comando": [
            ["NUMERO", "operador_final"],
            ["MEMORIA", "apos_mem"],
            ["comando", "apos_cmd"],
            ["ε"]
        ],
        "operador_final": [
            ["OPERADOR"],
            ["OPERADOR_REL"]
        ],
        "apos_mem": [
            ["OPERADOR"],
            ["OPERADOR_REL"],
            ["ε"]
        ],
        "apos_cmd": [
            ["OPERADOR"],
            ["OPERADOR_REL"],
            ["KEYWORD_WHILE"],
            ["comando", "KEYWORD_IF"]
        ]
    }

    # Lista de todos os terminais reconhecidos pelo léxico
    lista_terminais = [
        "ABRE_PAREN", "FECHA_PAREN", "NUMERO", "OPERADOR",
        "OPERADOR_REL", "MEMORIA", "KEYWORD_START", "KEYWORD_END",
        "KEYWORD_RES", "KEYWORD_IF", "KEYWORD_WHILE", "$"
    ]

    # Calcula FIRST, FOLLOW e tabela LL(1)
    conjuntos_first = calcularFirst(regras_producao, lista_terminais)
    conjuntos_follow = calcularFollow(regras_producao, conjuntos_first, lista_terminais)
    tabela_ll1 = construirTabelaLL1(regras_producao, conjuntos_first, conjuntos_follow, lista_terminais)

    # Valida ausência de conflitos
    eh_valida = validarGramaticaLL1(tabela_ll1)

    resultado_gramatica = {
        "gramatica": regras_producao,
        "terminais": lista_terminais,
        "first": conjuntos_first,
        "follow": conjuntos_follow,
        "tabela_ll1": tabela_ll1,
        "eh_valida": eh_valida
    }

    return resultado_gramatica

def calcularFirst(regras_producao, lista_terminais):
    """
    Calcula os conjuntos FIRST para cada não-terminal usando algoritmo de ponto fixo.
    """
    conjuntos_first = {}

    # Inicializa conjuntos FIRST vazios para cada não-terminal
    for nao_terminal in regras_producao:
        conjuntos_first[nao_terminal] = set()

    # Algoritmo de ponto fixo: repete até não haver mudanças
    houve_mudanca = True
    while houve_mudanca:
        houve_mudanca = False

        for nao_terminal in regras_producao:
            for producao in regras_producao[nao_terminal]:
                # Calcula FIRST da produção e adiciona ao não-terminal
                first_da_producao = calcularFirstDeProducao(producao, conjuntos_first, lista_terminais)

                tamanho_anterior = len(conjuntos_first[nao_terminal])
                conjuntos_first[nao_terminal] = conjuntos_first[nao_terminal].union(first_da_producao)

                if len(conjuntos_first[nao_terminal]) > tamanho_anterior:
                    houve_mudanca = True

    return conjuntos_first

def calcularFirstDeProducao(producao, conjuntos_first, lista_terminais):
    """
    Calcula o conjunto FIRST de uma sequência de símbolos (produção).
    """
    resultado_first = set()

    # Produção vazia
    if producao == ["ε"]:
        resultado_first.add("ε")
        return resultado_first

    for simbolo in producao:
        # Se é terminal, adiciona e para
        if simbolo in lista_terminais or simbolo == "ε":
            resultado_first.add(simbolo)
            break

        # Se é não-terminal, adiciona FIRST dele (sem ε)
        if simbolo in conjuntos_first:
            resultado_first = resultado_first.union(conjuntos_first[simbolo] - {"ε"})

            # Se ε não está em FIRST do símbolo, para aqui
            if "ε" not in conjuntos_first[simbolo]:
                break
        else:
            # Símbolo desconhecido tratado como terminal
            resultado_first.add(simbolo)
            break
    else:
        # Todos os símbolos podem derivar ε
        resultado_first.add("ε")

    return resultado_first

def calcularFollow(regras_producao, conjuntos_first, lista_terminais):
    """
    Calcula os conjuntos FOLLOW para cada não-terminal.
    O símbolo inicial 'programa' inclui $ no FOLLOW.
    """
    conjuntos_follow = {}

    # Inicializa conjuntos FOLLOW vazios
    for nao_terminal in regras_producao:
        conjuntos_follow[nao_terminal] = set()

    # Regra 1: $ pertence a FOLLOW do símbolo inicial
    conjuntos_follow["programa"].add("$")

    # Algoritmo de ponto fixo
    houve_mudanca = True
    while houve_mudanca:
        houve_mudanca = False

        for nao_terminal in regras_producao:
            for producao in regras_producao[nao_terminal]:
                if producao == ["ε"]:
                    continue

                for indice_simbolo, simbolo in enumerate(producao):
                    # Só calcula FOLLOW para não-terminais na produção
                    if simbolo not in regras_producao:
                        continue

                    # Pega o resto da produção após o símbolo atual
                    resto_producao = producao[indice_simbolo + 1:]

                    if resto_producao:
                        # Regra 2: FIRST(resto) - {ε} vai para FOLLOW(simbolo)
                        first_do_resto = calcularFirstDeProducao(resto_producao, conjuntos_first, lista_terminais)

                        tamanho_anterior = len(conjuntos_follow[simbolo])
                        conjuntos_follow[simbolo] = conjuntos_follow[simbolo].union(first_do_resto - {"ε"})

                        # Regra 3: Se ε ∈ FIRST(resto), FOLLOW(nao_terminal) vai para FOLLOW(simbolo)
                        if "ε" in first_do_resto:
                            conjuntos_follow[simbolo] = conjuntos_follow[simbolo].union(conjuntos_follow[nao_terminal])

                        if len(conjuntos_follow[simbolo]) > tamanho_anterior:
                            houve_mudanca = True
                    else:
                        # Regra 3: Símbolo está no final da produção
                        tamanho_anterior = len(conjuntos_follow[simbolo])
                        conjuntos_follow[simbolo] = conjuntos_follow[simbolo].union(conjuntos_follow[nao_terminal])

                        if len(conjuntos_follow[simbolo]) > tamanho_anterior:
                            houve_mudanca = True

    return conjuntos_follow

def construirTabelaLL1(regras_producao, conjuntos_first, conjuntos_follow, lista_terminais):
    """
    Constrói a tabela de análise LL(1).
    Retorna dicionário { (nao_terminal, terminal): producao }.
    Se houver conflito, armazena lista de produções.
    """
    tabela_ll1 = {}

    for nao_terminal in regras_producao:
        for producao in regras_producao[nao_terminal]:
            # Calcula FIRST da produção
            first_da_producao = calcularFirstDeProducao(producao, conjuntos_first, lista_terminais)

            # Para cada terminal em FIRST(produção), adiciona na tabela
            for terminal in first_da_producao:
                if terminal == "ε":
                    continue

                chave_tabela = (nao_terminal, terminal)

                if chave_tabela in tabela_ll1:
                    # Conflito detectado: armazena ambas as produções
                    entrada_existente = tabela_ll1[chave_tabela]
                    if isinstance(entrada_existente[0], list):
                        entrada_existente.append(producao)
                    else:
                        tabela_ll1[chave_tabela] = [entrada_existente, producao]
                else:
                    tabela_ll1[chave_tabela] = producao

            # Se ε ∈ FIRST(produção), para cada terminal em FOLLOW(nao_terminal)
            if "ε" in first_da_producao:
                for terminal_follow in conjuntos_follow.get(nao_terminal, set()):
                    chave_tabela = (nao_terminal, terminal_follow)

                    if chave_tabela in tabela_ll1:
                        entrada_existente = tabela_ll1[chave_tabela]
                        if isinstance(entrada_existente[0], list):
                            entrada_existente.append(producao)
                        else:
                            tabela_ll1[chave_tabela] = [entrada_existente, producao]
                    else:
                        tabela_ll1[chave_tabela] = producao

    return tabela_ll1

def validarGramaticaLL1(tabela_ll1):
    """
    Verifica se a tabela LL(1) possui conflitos.
    Retorna True se a gramática é LL(1) válida, False caso contrário.
    """
    conflitos_encontrados = []

    for chave_tabela, producao in tabela_ll1.items():
        # Conflito = célula com lista de listas (múltiplas produções)
        if isinstance(producao[0], list):
            nao_terminal, terminal = chave_tabela
            conflito_texto = f"Conflito em M[{nao_terminal}, {terminal}]: {producao}"
            conflitos_encontrados.append(conflito_texto)

    if conflitos_encontrados:
        print("ERRO: A gramática NÃO é LL(1). Conflitos encontrados:")
        for conflito in conflitos_encontrados:
            print(f"  - {conflito}")
        return False

    print("Gramática validada: é LL(1) sem conflitos.")
    return True

def exibirGramatica(resultado_gramatica):
    """
    Imprime a gramática, FIRST, FOLLOW e tabela LL(1) formatados.
    """
    regras_producao = resultado_gramatica["gramatica"]
    conjuntos_first = resultado_gramatica["first"]
    conjuntos_follow = resultado_gramatica["follow"]
    tabela_ll1 = resultado_gramatica["tabela_ll1"]

    # Exibe regras de produção
    print("=" * 60)
    print("REGRAS DE PRODUÇÃO")
    print("=" * 60)
    for nao_terminal, producoes in regras_producao.items():
        for indice_producao, producao in enumerate(producoes):
            separador = "::=" if indice_producao == 0 else "  |"
            texto_producao = " ".join(producao)
            print(f"  {nao_terminal:<20} {separador} {texto_producao}")
    print()

    # Exibe conjuntos FIRST
    print("=" * 60)
    print("CONJUNTOS FIRST")
    print("=" * 60)
    for nao_terminal in regras_producao:
        elementos_ordenados = sorted(conjuntos_first[nao_terminal])
        texto_first = "{ " + ", ".join(elementos_ordenados) + " }"
        print(f"  FIRST({nao_terminal:<20}) = {texto_first}")
    print()

    # Exibe conjuntos FOLLOW
    print("=" * 60)
    print("CONJUNTOS FOLLOW")
    print("=" * 60)
    for nao_terminal in regras_producao:
        elementos_ordenados = sorted(conjuntos_follow[nao_terminal])
        texto_follow = "{ " + ", ".join(elementos_ordenados) + " }"
        print(f"  FOLLOW({nao_terminal:<20}) = {texto_follow}")
    print()

    # Exibe tabela LL(1)
    print("=" * 60)
    print("TABELA DE ANÁLISE LL(1)")
    print("=" * 60)
    # Agrupa por não-terminal para exibir organizado
    nao_terminais_unicos = list(regras_producao.keys())
    for nao_terminal in nao_terminais_unicos:
        entradas_deste_nt = []
        for (nt_chave, terminal), producao in tabela_ll1.items():
            if nt_chave == nao_terminal:
                texto_producao = " ".join(producao)
                entradas_deste_nt.append((terminal, texto_producao))

        if entradas_deste_nt:
            entradas_deste_nt.sort(key=lambda entrada: entrada[0])
            for terminal, texto_producao in entradas_deste_nt:
                print(f"  M[{nao_terminal:<20}, {terminal:<15}] = {texto_producao}")
    print()

def gerarTokens(linhas_brutas):
    """
    Gera tokens a partir das linhas brutas usando o léxico e salva em tokens.txt.
    """
    linhas_tokens = []

    for linha in linhas_brutas:
        vetor_tokens = []

        # Gera os tokens usando léxico -> armazena em vetor_tokens
        parseExpressao(linha, vetor_tokens)

        if vetor_tokens:
            # Formata -> TIPO:VALOR
            tokens_formatados = []
            for token in vetor_tokens:
                tokens_formatados.append(f"{token.tipo}:{token.valor}")

            # Junta com espaços e adiciona a lista de linhas de tokens
            linha_completa = " ".join(tokens_formatados)
            linhas_tokens.append(linha_completa)

    # Utiliza função do léxico para salvar o arquivo tokens.txt
    salvarArquivo('tokens.txt', linhas_tokens)

def lerTokens(nome_arquivo):
    """
    Lê o arquivo tokens.txt e retorna lista de listas de Token.
    """
    lista_de_linhas = []

    try:
        with open(nome_arquivo, 'r') as arquivo_texto:
            for linha_bruta in arquivo_texto:
                # Validação extra (analisar necessidade depois)
                linha_limpa = linha_bruta.strip() # remove espaços em branco (como implementado no léxico)
                if not linha_limpa:
                    continue # pula linhas vazias

                tokens_da_linha = []

                # Divide a linha pelos espaços para pegar cada "TIPO:VALOR"
                pedacos_de_texto = linha_limpa.split(' ')

                for pedaco in pedacos_de_texto:
                    # Divide entre tipo e valor usando o separador ":"
                    if ':' in pedaco:
                        tipo_extraido, valor_extraido = pedaco.split(':', 1)
                        # Cria o objeto Token (usando a classe importada do lexico.py)
                        novo_token = Token(tipo_extraido, valor_extraido)
                        tokens_da_linha.append(novo_token)

                if tokens_da_linha:
                    lista_de_linhas.append(tokens_da_linha)

        return lista_de_linhas

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        sys.exit(1)

def parsear(linhas_de_tokens, tabela_ll1):
    """
    Inicia a análise sintática descendente recursiva usando a tabela LL(1).
    """
    # Juntar a lista de listas em uma única lista
    lista_tokens = []
    
    for tokens_da_linha in linhas_de_tokens:
        for token_extraido in tokens_da_linha:
            lista_tokens.append(token_extraido)
            
    # Adiciona o token de fim de arquivo ($) na última posição
    token_fim = Token("$", "$")
    lista_tokens.append(token_fim)

    indice_atual = 0

    def consumirToken(tipo_esperado):
        nonlocal indice_atual
        
        # Se o indice extrapolou, nao podemos consumir 
        if indice_atual >= len(lista_tokens):
            return False
            
        token_analisado = lista_tokens[indice_atual]
        
        # Valida se é TIPO (NUMERO) ou o VALOR exato ($)
        if token_analisado.tipo == tipo_esperado or token_analisado.valor == tipo_esperado or token_analisado.tipo == f"KEYWORD_{tipo_esperado}":
            print(f"  [Match] Casou limite de token: {token_analisado.valor} (referência: {tipo_esperado})")
            indice_atual += 1
            return True
            
        print(f"  [Erro] Esperava '{tipo_esperado}', mas obteve token '{token_analisado.valor}'.")
        return False

    print("parsing\n")
    print(f"-> Quantidade de tokens inseridos na fita de leitura: {len(lista_tokens)}")
    
    # (Bloco informativo, pode ser removido)
    textos_dos_tokens = []
    tipos_literais = ["OPERADOR", "OPERADOR_REL", "ABRE_PAREN", "FECHA_PAREN", "$"]
    
    for token in lista_tokens:
        if token.tipo in tipos_literais:
            textos_dos_tokens.append(token.valor) 
        else:
            textos_dos_tokens.append(token.tipo)  
            
    fita_formatada = " ".join(textos_dos_tokens)
    print(f"-> Fita pronta: {fita_formatada}\n")
    def acionarModoPanico(nao_terminal_afetado):
        nonlocal indice_atual
        if indice_atual < len(lista_tokens):
            token_com_erro = lista_tokens[indice_atual]
            print(f"  [Recuperação] Sincronizando... Descartando token inesperado '{token_com_erro.valor}' no escopo de '{nao_terminal_afetado}'.")
            indice_atual += 1

    def derivarNaoTerminal(nome_nao_terminal):
        nonlocal indice_atual
        
        # Previne acesso fora dos limites caso a fita termine inesperadamente
        if indice_atual >= len(lista_tokens):
            return {"nodo_pai": nome_nao_terminal, "erro": "Fim inesperado da fita de tokens"}
            
        token_analisado = lista_tokens[indice_atual]
        chave_de_busca = (nome_nao_terminal, token_analisado.tipo)
        
        if chave_de_busca in tabela_ll1:
            producao_encontrada = tabela_ll1[chave_de_busca]
            
            nodo_arvore = {"nodo_pai": nome_nao_terminal, "producao_acionada": " ".join(producao_encontrada), "nodos_filhos": []}
            print(f"  [Derivação] {nome_nao_terminal} -> {nodo_arvore['producao_acionada']}")
            
            for simbolo_producao in producao_encontrada:
                if simbolo_producao == "ε":
                    nodo_arvore["nodos_filhos"].append({"terminal_folha": "ε"})
                    continue
                    
                # Se for um não terminal, temos uma função especifica mapeada para ele
                if simbolo_producao in mapa_funcoes_recursivas: 
                    funcao_recursiva_filho = mapa_funcoes_recursivas[simbolo_producao]
                    filho_gerado_na_arvore = funcao_recursiva_filho()
                    
                    if filho_gerado_na_arvore:
                        nodo_arvore["nodos_filhos"].append(filho_gerado_na_arvore)
                else: 
                    # Se não é terminal, usamos a função consumirToken para validar e extrair o token
                    casou_sucesso = consumirToken(simbolo_producao)
                    if casou_sucesso:
                        # Extrai posição - 1 pois o token acabou de ser validado e somou na fita
                        nodo_arvore["nodos_filhos"].append({
                            "terminal_folha": simbolo_producao, 
                            "valor_extraido": lista_tokens[indice_atual - 1].valor
                        })
                    else:
                        nodo_arvore["nodos_filhos"].append({"erro_sintatico": f"Faltou terminal esperado {simbolo_producao}"})
                        acionarModoPanico(nome_nao_terminal)
                        
            return nodo_arvore
        else:
            print(f"  [Erro Sintático] Fluxo de regras quebrado em '{nome_nao_terminal}', elemento não aguardava o token '{token_analisado.valor}' (de perfil {token_analisado.tipo}).")
            acionarModoPanico(nome_nao_terminal)
            return {"erro_nodo_pai": nome_nao_terminal, "falha_registro": token_analisado.valor}

    # Funções de Não-Terminais
    def parsePrograma(): 
        return derivarNaoTerminal("programa")
    def parseComandoLista(): 
        return derivarNaoTerminal("comando_lista")
    def parseComando(): 
        return derivarNaoTerminal("comando")
    def parseConteudoComando(): 
        return derivarNaoTerminal("conteudo_comando")
    def parseSufixoNumero(): 
        return derivarNaoTerminal("sufixo_numero")
    def parseSufixoMemoria(): 
        return derivarNaoTerminal("sufixo_memoria")
    def parseSufixoComando(): 
        return derivarNaoTerminal("sufixo_comando")
    def parseOperadorFinal(): 
        return derivarNaoTerminal("operador_final")
    def parseAposMem(): 
        return derivarNaoTerminal("apos_mem")
    def parseAposCmd(): 
        return derivarNaoTerminal("apos_cmd")
    
    # Dicionário dinâmico conectando texto as funções 
    mapa_funcoes_recursivas = {
        "programa": parsePrograma,
        "comando_lista": parseComandoLista,
        "comando": parseComando,
        "conteudo_comando": parseConteudoComando,
        "sufixo_numero": parseSufixoNumero,
        "sufixo_memoria": parseSufixoMemoria,
        "sufixo_comando": parseSufixoComando,
        "operador_final": parseOperadorFinal,
        "apos_mem": parseAposMem,
        "apos_cmd": parseAposCmd
    }

    # Inicialização central do parser
    arvore_sintatica_ast = parsePrograma()
    
    if indice_atual < len(lista_tokens) and lista_tokens[indice_atual].tipo != "$":
        print(f"\n  [Aviso Analítico] O parsing finalizou através da raiz mas sobraram tokens estáticos não processados na fita, a partir domedidor: {lista_tokens[indice_atual].valor}")
    
    print("\n=> Parsing e rastreamento recursivo concluídos com sucesso!")
    return arvore_sintatica_ast # retorna a AST

def construirTextoArvore(no, prefixo="", eh_ultimo=True, eh_raiz=True):
    """
    Percorre a Árvore Sintática de forma recursiva e constrói uma representação
    visual em texto usando caracteres de ramificação (para depois salvar no arquivo .md).
    """
    linhas = []

    # Define o texto do nó lendo as chaves do parser
    if "terminal_folha" in no:
        # Como é um nó folha (terminal) -> extraí o valor com "valor_extraido" e caso não exista, deixa vazio (para evitar None)
        valor = no.get("valor_extraido", "")
        # Exibe o tipo do terminal e o valor correspondente -> como NUMERO (3.14)
        texto_no = f"{no['terminal_folha']} ({valor})"
    elif "nodo_pai" in no:
        # É um nó interno (não-terminal) -> exemplo: comando, sufixo_numero, conteudo_comando, etc
        texto_no = no["nodo_pai"]
    elif "erro_sintatico" in no:
        # Nó folha com erro capturado pelo "Panic Mode"
        texto_no = f"ERRO SINTÁTICO: {no['erro_sintatico']}"
    elif "erro_nodo_pai" in no:
        # Nó pai que falhou na derivação -> nenhuma regra válida na tabela LL(1) para o token
        texto_no = f"FALHA NO NÓ: {no['erro_nodo_pai']} (Token inesperado: {no.get('falha_registro', '')})"
    else:
        # Segurança extra para caso nó venha mal formado
        texto_no = "Nó Desconhecido"

    # Desenha os galhos
    if eh_raiz:
        # A raiz é o ponto de partida, não tenho nenhum galho
        linhas.append(texto_no)
        # Não há linha vertical antes da raiz, então o prefixo para os filhos começa vazio
        novo_prefixo = ""
    else:
        # Caso seja uma folha/último filho
        if eh_ultimo:
            marcador = "└── "
            # Não tem mais irmãos depois -> espaço em branco
            novo_prefixo = prefixo + "    "
        else:
            # Caso ainda tenha irmãos abaixo
            marcador = "├── "
            # Ainda tem irmãos depois -> mantém a linha vertical para conectar
            novo_prefixo = prefixo + "│   "
            

        # Junta o que veio dos anteriores, galho atual, e nome do nó atual
        linhas.append(f"{prefixo}{marcador}{texto_no}")

    # Prepara a lista de filhos para recursão
    if "nodos_filhos" in no: # exemplo: comando -> ABRE_PAREN, conteudo_comando, FECHA_PAREN 
        filhos = no["nodos_filhos"]
    else:
        filhos = []

    # Para o exemplo, temos total_filhos = 3. 
    total_filhos = len(filhos) # contudo, terminal não tem filhos, logo, total_filhos = 0

    # Loop de recursão -> terminais apenas retornam linha do próprio nó, enquanto não-terminais continuam gerando filhos
    for i in range(total_filhos):
        filho = filhos[i]
        
        # Define explicitamente se é o último filho da lista
        if i == (total_filhos - 1):
            ultimo_filho = True
        else:
            ultimo_filho = False
            
        # A recursão passa o novo_prefixo para o nível de baixo e obviamente não é mais raiz
        linhas_filho = construirTextoArvore(filho, novo_prefixo, ultimo_filho, False)

        # Armazena as linhas geradas pelos filhos na lista de linhas do nível atual
        linhas.extend(linhas_filho)

    # Roda para cada nó
    # - Se for um terminal -> for não executou. O return apenas devolve a linha para o pai
    # - Se for um não-terminal -> devolve a lista completa com todos os galhos dos filhos já agrupados
    return linhas

def gerarArvore(derivacao, nome_teste):
    """
    Chama a função construir_texto_arvore para gerar a árvore em formato de string
    e exporta o resultado para o arquivo 'arvore_sintatica.md'.
    """
    nome_arquivo = "arvore_sintatica.md"

    try:
        # Passa a derivação para a função que desenha os galhos
        linhas_arvore = construirTextoArvore(derivacao)
        # Junta as linhas da lista em um único texto pulando as linhas
        texto_final = "\n".join(linhas_arvore)

        # Grava no arquivo
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("# Árvore Sintática (Derivação)\n\n")
            f.write(f"## Resultado do {nome_teste}:\n\n")
            f.write("```text\n")
            f.write(texto_final + "\n")
            f.write("```\n")

        print(f"Sucesso: A árvore sintática foi estruturada e salva em '{nome_arquivo}'.")

    except Exception as e:
        print(f"Erro ao gerar o arquivo da árvore sintática: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python sintatico.py <arquivo_teste>")
        return

    # Arquivo teste passado via terminal
    arquivo_codigo_fonte = sys.argv[1]

    linhas_brutas = []
    lerArquivo(arquivo_codigo_fonte, linhas_brutas)

    # Temos que gerar os tokens.txt a partir do arquivo teste passado via terminal do sintático
    gerarTokens(linhas_brutas) # gera o tokens.txt usando parseExpressao do léxico

    arquivo_tokens = 'tokens.txt' # nome fixo do arquivo de tokens gerado pela função acima
    tokens = lerTokens(arquivo_tokens)

    # Testes para debug dos tokens lidos
    print(f"Foram lidas {len(tokens)} linhas de código válidas.\n")

    resultado_gramatica = construirGramatica()

    exibirGramatica(resultado_gramatica)
    print("\n        INÍCIO DO PROCESSADOR SINTÁTICO DA FITA        \n")
       
    # Aciona o analisador repassando o buffer extraído e a tabela formatada
    derivacao = parsear(tokens, resultado_gramatica["tabela_ll1"])

    # Gera o arquivo arvore_sintatica.md com o resultado referente ao teste passado via terminal
    gerarArvore(derivacao, arquivo_codigo_fonte)

if __name__ == "__main__":
    main()