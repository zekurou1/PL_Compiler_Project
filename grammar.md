# Grammar Reference

## Formal EBNF Grammar

```ebnf
program        ::= statement*

statement      ::= var_decl
                 | assignment
                 | print_stmt
                 | if_stmt
                 | while_stmt

var_decl       ::= "let" IDENTIFIER "=" expression ";"
assignment     ::= IDENTIFIER "=" expression ";"

print_stmt     ::= "print" "(" expression ")" ";"

if_stmt        ::= "if" "(" expression ")" block ("else" block)?
while_stmt     ::= "while" "(" expression ")" block

block          ::= "{" statement* "}"

expression     ::= equality
equality       ::= comparison (("==" | "!=") comparison)*
comparison     ::= term ((">" | "<" | ">=" | "<=") term)*
term           ::= factor (("+" | "-") factor)*
factor         ::= unary (("*" | "/") unary)*
unary          ::= ("-" | "!") unary | primary
primary        ::= NUMBER | STRING | IDENTIFIER | "(" expression ")"
```

## Operator Precedence (lowest → highest)

| Level | Operators       | Associativity |
|-------|-----------------|---------------|
| 1     | `==` `!=`       | left          |
| 2     | `>` `<` `>=` `<=` | left        |
| 3     | `+` `-`         | left          |
| 4     | `*` `/`         | left          |
| 5     | `-` (unary) `!` | right         |
| 6     | literals, `()`  | —             |

## Keywords

`let`, `if`, `else`, `while`, `print`, `true`, `false`, `null`
