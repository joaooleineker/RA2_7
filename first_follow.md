# Gramática da Linguagem RPN — Análise LL(1)

## Conjuntos FIRST

| Não-terminal | FIRST |
|---|---|
| programa | { ABRE_PAREN, ε } |
| comando_lista | { ABRE_PAREN, ε } |
| comando | { ABRE_PAREN } |
| conteudo_comando | { KEYWORD_START, KEYWORD_END, NUMERO, MEMORIA, ABRE_PAREN } |
| sufixo_numero | { KEYWORD_RES, NUMERO, MEMORIA, ABRE_PAREN } |
| sufixo_memoria | { NUMERO, MEMORIA, ABRE_PAREN, ε } |
| sufixo_comando | { NUMERO, MEMORIA, ABRE_PAREN, ε } |
| operador_final | { OPERADOR, OPERADOR_REL } |
| apos_mem | { OPERADOR, OPERADOR_REL, ε } |
| apos_cmd | { OPERADOR, OPERADOR_REL, KEYWORD_WHILE, ABRE_PAREN } |

---

## Conjuntos FOLLOW

| Não-terminal | FOLLOW |
|---|---|
| programa | { $ } |
| comando_lista | { $ } |
| comando | { ABRE_PAREN, $, NUMERO, MEMORIA, FECHA_PAREN, OPERADOR, OPERADOR_REL, KEYWORD_WHILE, KEYWORD_IF } |
| conteudo_comando | { FECHA_PAREN } |
| sufixo_numero | { FECHA_PAREN } |
| sufixo_memoria | { FECHA_PAREN } |
| sufixo_comando | { FECHA_PAREN } |
| operador_final | { FECHA_PAREN } |
| apos_mem | { FECHA_PAREN } |
| apos_cmd | { FECHA_PAREN } |

---
