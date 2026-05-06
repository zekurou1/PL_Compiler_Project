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

expression     ::= logical_or
logical_or     ::= logical_and ("||" logical_and)*
logical_and    ::= equality ("&&" equality)*
equality       ::= comparison (("==" | "!=") comparison)*
comparison     ::= term ((">" | "<" | ">=" | "<=") term)*
term           ::= factor (("+" | "-") factor)*
factor         ::= unary (("*" | "/" | "%") unary)*
unary          ::= ("-" | "!") unary | power
power          ::= primary ("**" power)?
primary        ::= NUMBER | STRING | IDENTIFIER | "(" expression ")"
```

## Operator Precedence (lowest → highest)

| Level | Operators       | Associativity |
|-------|-----------------|---------------|
| 1     | `\|\|`            | left          |
| 2     | `&&`            | left          |
| 3     | `==` `!=`       | left          |
| 4     | `>` `<` `>=` `<=` | left        |
| 5     | `+` `-`         | left          |
| 6     | `*` `/` `%`     | left          |
| 7     | `**`            | right         |
| 8     | `-` (unary) `!` | right         |
| 9     | literals, `()`  | —             |

## Special Features

**Compound Assignments** (syntactic sugar):
- `x += e` desugars to `x = x + e`
- `x -= e` desugars to `x = x - e`
- `x *= e` desugars to `x = x * e`
- `x /= e` desugars to `x = x / e`
- `x %= e` desugars to `x = x % e`

## Keywords

`let`, `if`, `else`, `while`, `print`, `true`, `false`, `null`
