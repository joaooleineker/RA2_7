# Gramática da Linguagem RPN — Análise LL(1)

Convenção: **MAIÚSCULAS** = terminais | **minúsculas** = não-terminais | **ε** = vazio

## Tabela de Análise LL(1)

| Não-terminal | ABRE_PAREN | FECHA_PAREN | NUMERO | MEMORIA | OPERADOR | OPERADOR_REL | KW_START | KW_END | KW_RES | KW_IF | KW_WHILE | $ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| programa | comando_lista | — | — | — | — | — | — | — | — | — | — | comando_lista |
| comando_lista | cmd cmd_lista | — | — | — | — | — | — | — | — | — | — | ε |
| comando | ( cont_cmd ) | — | — | — | — | — | — | — | — | — | — | — |
| conteudo_cmd | cmd sfx_cmd | — | NUM sfx_num | MEM sfx_mem | — | — | KW_START | KW_END | — | — | — | — |
| sufixo_num | cmd op_final | — | NUM op_final | MEM apos_mem | — | — | — | — | KW_RES | — | — | — |
| sufixo_mem | cmd op_final | ε | NUM op_final | MEM apos_mem | — | — | — | — | — | — | — | — |
| sufixo_cmd | cmd apos_cmd | ε | NUM op_final | MEM apos_mem | — | — | — | — | — | — | — | — |
| operador_final | — | — | — | — | OPERADOR | OP_REL | — | — | — | — | — | — |
| apos_mem | — | ε | — | — | OPERADOR | OP_REL | — | — | — | — | — | — |
| apos_cmd | cmd KW_IF | — | — | — | OPERADOR | OP_REL | — | — | — | — | KW_WHILE | — |

> **Observação:** Nenhuma célula possui mais de uma produção → gramática é LL(1) ✓