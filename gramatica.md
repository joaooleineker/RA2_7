# Gramática da Linguagem RPN — Análise LL(1)

## Regras de Produção (EBNF)

Convenção: **MAIÚSCULAS** = terminais | **minúsculas** = não-terminais | **ε** = vazio

```
programa         ::= comando_lista
comando_lista    ::= comando comando_lista | ε
comando          ::= ABRE_PAREN conteudo_comando FECHA_PAREN

conteudo_comando ::= KEYWORD_START
                   | KEYWORD_END
                   | NUMERO sufixo_numero
                   | MEMORIA sufixo_memoria
                   | comando sufixo_comando

sufixo_numero    ::= KEYWORD_RES
                   | NUMERO operador_final
                   | MEMORIA apos_mem
                   | comando operador_final

sufixo_memoria   ::= NUMERO operador_final
                   | MEMORIA apos_mem
                   | comando operador_final
                   | ε

sufixo_comando   ::= NUMERO operador_final
                   | MEMORIA apos_mem
                   | comando apos_cmd
                   | ε

operador_final   ::= OPERADOR
                   | OPERADOR_REL

apos_mem         ::= OPERADOR
                   | OPERADOR_REL
                   | ε

apos_cmd         ::= OPERADOR
                   | OPERADOR_REL
                   | KEYWORD_WHILE
                   | comando KEYWORD_IF
```

### Terminais da linguagem:
| Token | Exemplo |
|---|---|
| ABRE_PAREN | `(` |
| FECHA_PAREN | `)` |
| NUMERO | `3.14`, `10`, `2.0` |
| OPERADOR | `+`, `-`, `*`, `/`, `%`, `^`, `\|` |
| OPERADOR_REL | `<`, `>`, `==`, `!=`, `<=`, `>=` |
| MEMORIA | `VAR`, `RESULTADO`, `CONT` |
| KEYWORD_START | `START` |
| KEYWORD_END | `END` |
| KEYWORD_RES | `RES` |
| KEYWORD_IF | `IF` |
| KEYWORD_WHILE | `WHILE` |
| $ | fim da entrada |

---

## Exemplos de Derivação

### `(3.14 2.0 +)` — Expressão aritmética
```
comando → ( conteudo_comando )
        → ( NUMERO sufixo_numero )
        → ( 3.14 NUMERO operador_final )
        → ( 3.14 2.0 OPERADOR )
        → ( 3.14 2.0 + )
```

### `(1 RES)` — Comando RES
```
comando → ( conteudo_comando )
        → ( NUMERO sufixo_numero )
        → ( 1 KEYWORD_RES )
        → ( 1 RES )
```

### `((VAR 10.0 <) ((VAR 1.0 +) VAR) WHILE)` — Laço WHILE
```
comando → ( conteudo_comando )
        → ( comando sufixo_comando )
        → ( (VAR 10.0 <) comando apos_cmd )
        → ( (VAR 10.0 <) ((VAR 1.0 +) VAR) KEYWORD_WHILE )
```