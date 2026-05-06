"""
parser.py — Recursive-descent parser that strictly follows the EBNF grammar.

Each grammar rule maps 1-to-1 to a method.  The parser consumes Tokens
produced by the Lexer and emits an AST (ast_nodes.py).
"""

from __future__ import annotations
from typing import List

from tokens import Token, TokenType
from ast_nodes import (
    ASTNode, Program, VarDecl, Assignment, PrintStmt,
    IfStmt, WhileStmt, Block, BinaryOp, UnaryOp,
    NumberLiteral, StringLiteral, BoolLiteral, NullLiteral, Identifier,
)
from error import SyntaxError as LangSyntaxError


class Parser:
    """
    Recursive-descent parser.

    Usage::

        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
    """

    def __init__(self, tokens: List[Token]):
        self._tokens: List[Token] = tokens
        self._pos: int = 0

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def parse(self) -> Program:
        stmts: list[ASTNode] = []
        while not self._at_end():
            stmts.append(self._statement())
        return Program(statements=stmts)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _previous(self) -> Token:
        return self._tokens[self._pos - 1]

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        if tok.type != TokenType.EOF:
            self._pos += 1
        return tok

    def _check(self, ttype: TokenType, value: str | None = None) -> bool:
        tok = self._peek()
        if tok.type != ttype:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def _match(self, ttype: TokenType, value: str | None = None) -> bool:
        if self._check(ttype, value):
            self._advance()
            return True
        return False

    def _expect(self, ttype: TokenType, value: str | None = None, msg: str | None = None) -> Token:
        """Consume the next token if it matches, else raise SyntaxError."""
        tok = self._peek()
        if tok.type == ttype and (value is None or tok.value == value):
            return self._advance()
        expected = repr(value) if value else ttype.name
        actual   = repr(tok.value)
        error_msg = msg or f"Expected {expected} but got {actual}"
        raise LangSyntaxError(error_msg, tok.line, tok.column)

    # ------------------------------------------------------------------
    # Grammar: Statements
    # ------------------------------------------------------------------

    def _statement(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.KEYWORD:
            if tok.value == "let":
                return self._var_decl()
            if tok.value == "print":
                return self._print_stmt()
            if tok.value == "if":
                return self._if_stmt()
            if tok.value == "while":
                return self._while_stmt()

        if tok.type == TokenType.IDENTIFIER:
            # Lookahead: identifier followed by assignment operator (=, +=, -=, *=, /=, %=)
            nxt = self._tokens[self._pos + 1] if self._pos + 1 < len(self._tokens) else None
            if nxt and nxt.type == TokenType.OPERATOR and nxt.value in ("=", "+=", "-=", "*=", "/=", "%="):
                return self._assignment()

        raise LangSyntaxError(
            f"Unexpected token {tok.value!r} — cannot start a statement",
            tok.line, tok.column,
        )

    # var_decl ::= "let" IDENTIFIER "=" expression ";"
    def _var_decl(self) -> VarDecl:
        kw = self._expect(TokenType.KEYWORD, "let")
        name_tok = self._expect(TokenType.IDENTIFIER, msg="Expected variable name after 'let'")
        self._expect(TokenType.OPERATOR, "=", msg="Expected '=' after variable name")
        value = self._expression()
        self._expect(TokenType.DELIMITER, ";", msg="Missing ';' after variable declaration")
        return VarDecl(name=name_tok.value, value=value, line=kw.line, col=kw.column)

    # assignment ::= IDENTIFIER ("=" | "+=" | "-=" | "*=" | "/=" | "%=") expression ";"
    def _assignment(self) -> Assignment:
        name_tok = self._expect(TokenType.IDENTIFIER)
        op_tok = self._peek()
        
        # Check for assignment operator (=, +=, -=, *=, /=, %=)
        if op_tok.type == TokenType.OPERATOR and op_tok.value in ("=", "+=", "-=", "*=", "/=", "%="):
            op = self._advance().value
        else:
            raise LangSyntaxError(
                f"Expected assignment operator, got {op_tok.value!r}",
                op_tok.line, op_tok.column,
            )
        
        value = self._expression()
        
        # Desugar compound assignments: x += y → x = x + y
        if op != "=":
            op_map = {
                "+=": "+",
                "-=": "-",
                "*=": "*",
                "/=": "/",
                "%=": "%",
            }
            arithmetic_op = op_map[op]
            value = BinaryOp(
                op=arithmetic_op,
                left=Identifier(name=name_tok.value, line=name_tok.line, col=name_tok.column),
                right=value,
                line=name_tok.line,
                col=name_tok.column,
            )
        
        self._expect(TokenType.DELIMITER, ";", msg="Missing ';' after assignment")
        return Assignment(name=name_tok.value, value=value, line=name_tok.line, col=name_tok.column)

    # print_stmt ::= "print" "(" expression ")" ";"
    def _print_stmt(self) -> PrintStmt:
        kw = self._expect(TokenType.KEYWORD, "print")
        self._expect(TokenType.DELIMITER, "(", msg="Expected '(' after 'print'")
        expr = self._expression()
        self._expect(TokenType.DELIMITER, ")", msg="Expected ')' after print expression")
        self._expect(TokenType.DELIMITER, ";", msg="Missing ';' after print statement")
        return PrintStmt(expr=expr, line=kw.line)

    # if_stmt ::= "if" "(" expression ")" block ("else" block)?
    def _if_stmt(self) -> IfStmt:
        kw = self._expect(TokenType.KEYWORD, "if")
        self._expect(TokenType.DELIMITER, "(", msg="Expected '(' after 'if'")
        cond = self._expression()
        self._expect(TokenType.DELIMITER, ")", msg="Expected ')' after if condition")
        then_block = self._block()
        else_block = None
        if self._match(TokenType.KEYWORD, "else"):
            else_block = self._block()
        return IfStmt(condition=cond, then_block=then_block, else_block=else_block, line=kw.line)

    # while_stmt ::= "while" "(" expression ")" block
    def _while_stmt(self) -> WhileStmt:
        kw = self._expect(TokenType.KEYWORD, "while")
        self._expect(TokenType.DELIMITER, "(", msg="Expected '(' after 'while'")
        cond = self._expression()
        self._expect(TokenType.DELIMITER, ")", msg="Expected ')' after while condition")
        body = self._block()
        return WhileStmt(condition=cond, body=body, line=kw.line)

    # block ::= "{" statement* "}"
    def _block(self) -> Block:
        open_tok = self._expect(TokenType.DELIMITER, "{", msg="Expected '{' to open block")
        stmts: list[ASTNode] = []
        while not self._check(TokenType.DELIMITER, "}") and not self._at_end():
            stmts.append(self._statement())
        self._expect(TokenType.DELIMITER, "}", msg="Unclosed block — missing '}'")
        return Block(statements=stmts)

    # ------------------------------------------------------------------
    # Grammar: Expressions (ordered by precedence, lowest first)
    # ------------------------------------------------------------------

    def _expression(self) -> ASTNode:
        return self._logical_or()

    # logical_or ::= logical_and ("||" logical_and)*
    def _logical_or(self) -> ASTNode:
        left = self._logical_and()
        while self._check(TokenType.OPERATOR, "||"):
            op = self._advance()
            right = self._logical_and()
            left = BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # logical_and ::= equality ("&&" equality)*
    def _logical_and(self) -> ASTNode:
        left = self._equality()
        while self._check(TokenType.OPERATOR, "&&"):
            op = self._advance()
            right = self._equality()
            left = BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # equality ::= comparison (("==" | "!=") comparison)*
    def _equality(self) -> ASTNode:
        left = self._comparison()
        while self._check(TokenType.OPERATOR, "==") or self._check(TokenType.OPERATOR, "!="):
            op = self._advance()
            right = self._comparison()
            left = BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # comparison ::= term ((">" | "<" | ">=" | "<=") term)*
    def _comparison(self) -> ASTNode:
        left = self._term()
        cmp_ops = {">", "<", ">=", "<="}
        while self._peek().type == TokenType.OPERATOR and self._peek().value in cmp_ops:
            op = self._advance()
            right = self._term()
            left = BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # term ::= factor (("+" | "-") factor)*
    def _term(self) -> ASTNode:
        left = self._factor()
        while self._check(TokenType.OPERATOR, "+") or self._check(TokenType.OPERATOR, "-"):
            op = self._advance()
            right = self._factor()
            left = BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # factor ::= unary (("*" | "/" | "%") unary)*
    def _factor(self) -> ASTNode:
        left = self._unary()
        while self._check(TokenType.OPERATOR, "*") or self._check(TokenType.OPERATOR, "/") or self._check(TokenType.OPERATOR, "%"):
            op = self._advance()
            right = self._unary()
            left = BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # unary ::= ("-" | "!") unary | power
    def _unary(self) -> ASTNode:
        if self._check(TokenType.OPERATOR, "-") or self._check(TokenType.OPERATOR, "!"):
            op = self._advance()
            operand = self._unary()
            return UnaryOp(op=op.value, operand=operand, line=op.line, col=op.column)
        return self._power()

    # power ::= primary ("**" power)?  (right-associative)
    def _power(self) -> ASTNode:
        left = self._primary()
        if self._check(TokenType.OPERATOR, "**"):
            op = self._advance()
            # Right-associative: call _power again, not _primary
            right = self._power()
            return BinaryOp(op=op.value, left=left, right=right, line=op.line, col=op.column)
        return left

    # primary ::= NUMBER | STRING | IDENTIFIER | "(" expression ")"
    def _primary(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.INTEGER:
            self._advance()
            return NumberLiteral(value=int(tok.value), line=tok.line, col=tok.column)

        if tok.type == TokenType.FLOAT:
            self._advance()
            return NumberLiteral(value=float(tok.value), line=tok.line, col=tok.column)

        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(value=tok.value, line=tok.line, col=tok.column)

        if tok.type == TokenType.KEYWORD and tok.value == "true":
            self._advance()
            return BoolLiteral(value=True, line=tok.line, col=tok.column)

        if tok.type == TokenType.KEYWORD and tok.value == "false":
            self._advance()
            return BoolLiteral(value=False, line=tok.line, col=tok.column)

        if tok.type == TokenType.KEYWORD and tok.value == "null":
            self._advance()
            return NullLiteral(line=tok.line, col=tok.column)

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Identifier(name=tok.value, line=tok.line, col=tok.column)

        if tok.type == TokenType.DELIMITER and tok.value == "(":
            self._advance()
            expr = self._expression()
            self._expect(TokenType.DELIMITER, ")", msg="Expected ')' after grouped expression")
            return expr

        raise LangSyntaxError(
            f"Unexpected token {tok.value!r} in expression",
            tok.line, tok.column,
        )
