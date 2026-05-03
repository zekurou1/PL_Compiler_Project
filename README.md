# Mini Compiler / Interpreter

A complete, modular compiler pipeline for a custom toy language — built in Python.

Inspired by the Java lexer architecture of [JetJustineEspanola/Tokenizer-](https://github.com/JetJustineEspanola/Tokenizer-), redesigned and extended into a full five-stage compiler.

---

## Project Structure

```
compiler_project/
├── main.py                   ← Pipeline orchestrator & CLI
├── lexer/
│   ├── __init__.py
│   ├── lexer.py              ← Hand-written tokenizer
│   ├── token.py              ← Token types & Token dataclass
│   ├── keyword_manager.py    ← Data-driven keyword loader
│   └── keywords.txt          ← Keyword definitions (no hardcoding)
├── parser/
│   ├── __init__.py
│   ├── parser.py             ← Recursive-descent parser
│   └── grammar.md            ← Formal EBNF grammar reference
├── ast_module/
│   ├── __init__.py
│   └── ast_nodes.py          ← AST node class hierarchy
├── semantic/
│   ├── __init__.py
│   └── analyzer.py           ← Semantic checks + scoped symbol table
├── interpreter/
│   ├── __init__.py
│   └── interpreter.py        ← Tree-walking interpreter
├── utils/
│   ├── __init__.py
│   └── error.py              ← Structured error hierarchy
├── tests/
│   ├── sample_program.txt    ← Valid demo program
│   └── error_test.txt        ← Error demonstration programs
└── README.md
```

---

## Language Grammar (EBNF)

```ebnf
program        ::= statement*
statement      ::= var_decl | assignment | print_stmt | if_stmt | while_stmt
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

---

## Usage

```bash
# Normal run
python main.py tests/sample_program.txt

# Debug mode (prints tokens + AST + semantic confirmation)
python main.py --debug tests/sample_program.txt
```

---

## Pipeline Stages

| # | Stage             | Input          | Output              |
|---|-------------------|----------------|---------------------|
| 1 | **Lexer**         | Source text    | `List[Token]`       |
| 2 | **Parser**        | Tokens         | `Program` AST       |
| 3 | **Semantic Analysis** | AST        | Validated AST       |
| 4 | **Interpreter**   | Validated AST  | Printed output      |

---

## Token Types

| Type         | Examples                        |
|--------------|---------------------------------|
| `KEYWORD`    | `let`, `if`, `else`, `while`, `print`, `true`, `false`, `null` |
| `IDENTIFIER` | `x`, `counter`, `greeting`     |
| `INTEGER`    | `42`, `0`, `100`               |
| `FLOAT`      | `3.14`, `0.5`                  |
| `STRING`     | `"hello"`, `"world"`           |
| `OPERATOR`   | `+`, `-`, `*`, `/`, `==`, `!=`, `<=`, `>=`, `>`, `<`, `!`, `&&`, `\|\|` |
| `DELIMITER`  | `(`, `)`, `{`, `}`, `;`, `,`   |
| `EOF`        | (end of file sentinel)          |
| `UNKNOWN`    | any unrecognised character      |

---

## Error Handling

All errors carry **message**, **line**, and **column**:

```
[LexicalError]  (line 1, col 11) Unexpected character '@'
[SyntaxError]   (line 2, col 1)  Missing ';' after variable declaration
[SemanticError] (line 2, col 1)  Duplicate declaration of 'x'
[SemanticError] (line 5, col 7)  Use of undeclared variable 'unknownVar'
[RuntimeError]  (line 8, col 9)  Division by zero
```

---

## Extending the Language

To add new keywords: edit `lexer/keywords.txt` — no code changes needed.

To add new operators: add them to `_MULTI_OPS` / `_SINGLE_OPS` in `lexer.py`, then handle them in the interpreter's `_eval_BinaryOp`.

---

## Design Principles

- **No monolithic files** — each stage is an isolated module
- **No hardcoded keywords** — loaded from `keywords.txt` at runtime
- **No skipped stages** — all five stages run on every execution
- **No mixing of concerns** — UI calls backend only
- **Structured errors** — every error includes stage, line, and column
