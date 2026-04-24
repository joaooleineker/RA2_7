# Fase 2 - Analisador Sintático *LL(1)*

- **Instituição:** PUCPR
- **Disciplina:** Linguagens Formais e Compiladores  
- **Professor:** Frank Coelho de Alcantara  
- **Grupo:** RA2 7  

## Integrantes do Grupo
- Daniel de Almeida Santos Bina (GitHub: @danielbina) 
- Eduardo Ferreira de Melo (GitHub: @edufmelo) 
- João Eduardo Faccin Leineker (GitHub: @joaooleineker) 

*(Nota: O repositório está organizado com commits claros e as contribuições de cada integrante foram registradas na forma de Pull Requests, conforme a especificação).*

---

## Instruções para Compilar, Executar e Depurar

### Pré-requisitos
O projeto foi desenvolvido em Python. Certifique-se de ter o **Python 3.x** instalado em sua máquina. Nenhuma biblioteca externa é necessária.

### Execução
O programa deve ser executado diretamente via linha de comando, passando o arquivo de teste desejado como argumento.

No terminal, navegue até a raiz do repositório e execute:
```bash
python sintatico.py teste1.txt
```

### Depuração (Debugging)

Para facilitar a depuração, o sistema gera automaticamente os seguintes arquivos a cada execução:

1. Log do Terminal: Exibe o rastreamento do parser e a recuperação de erros (caso encontre algum problema na "fita").
2. arvore_sintatica.md: Representação visual da árvore gerada.
3. arvore_sintatica.json: A árvore sintática salva no formato JSON.
4. Arquivo .s: O código Assembly gerado para o ambiente Cpulator-ARMv7 (ex: teste1.s).

## Arquivos da Gramática LL(1)

Conforme a especificação, a estrutura teórica do analisador é exportada para os seguintes arquivos .md na raiz do repositório:

- **gramatica.md**: Contém as regras de produção da linguagem em formato EBNF e os terminais utilizados.

- **first_follow.md**: Contém os conjuntos FIRST e FOLLOW calculados para cada não-terminal.

- **tabela_LL1.md**: A tabela de análise preditiva gerada (validada internamente para garantir que não existam conflitos de produção).

## Sintaxe e Exemplos das Estruturas de Controle 

As novas estruturas seguem a notação pós-fixada da linguagem original e devem ser delimitadas por parênteses.

### 1. Tomada de Decisão (IF)
Avalia uma condição. Se for verdadeira, executa o primeiro bloco; se for falsa, executa o segundo bloco.

- Sintaxe: ( (condição) (bloco_verdadeiro) (bloco_falso) IF )
- Exemplo: ( (VAR 5.0 >) (1.0 RESULTADO) (0.0 RESULTADO) IF )

### 2. Laços de Repetição (WHILE)
Executa o bloco de repetição continuamente enquanto a condição resultar em um valor verdadeiro.

- Sintaxe: ( (condição) (bloco_de_repeticao) WHILE )
- Exemplo: ( (VAR 10.0 <) ((VAR 1.0 +) VAR) WHILE )


## Testes Automatizados
Para garantir a robustez do analisador, foi desenvolvida uma bateria de testes unitários e de integração (presentes no arquivo `funcoesTesteSintatico.py`).

Os testes automatizados validam:

- testarConstruirGramatica(): Verifica se todas as regras foram inseridas e se a gramática é validada como LL(1) sem conflitos.

- testarCalcularFirst() e testarCalcularFollow(): Validam se os conjuntos foram calculados com os resultados corretos esperados.

- testarTabelaLL1(): Checa se a tabela de análise foi construída corretamente com as posições certas.

- testarParsear(): Injeta expressões válidas e inválidas para garantir que o parser funciona corretamente e que a recuperação básica de erros atua quando a "fita" de tokens está malformada.