"""
parser.py — builds an AST from the token list produced by lexer.py.

Grammar (informal):
    pattern     := sequence ( '|' sequence )*        # top level
    sequence    := quantified*
    quantified  := atom quantifier?
    atom        := LITERAL | WILDCARD | CHARCLASS | ANCHOR | group
    group       := '(' pattern ')'
    quantifier  := QUANT_STAR | QUANT_PLUS | QUANT_OPT
                 | QUANT_EXACT | QUANT_RANGE
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from lexer import Token, TT, tokenize


# ---------------------------------------------------------------------------
# AST node types
# ---------------------------------------------------------------------------

class AnchorKind(Enum):
    BEG       = auto()
    END       = auto()
    WDBEG     = auto()
    WDEND     = auto()
    WDBEG_NEG = auto()
    WDEND_NEG = auto()


# base class (just for type hints)
class Node:
    pass


@dataclass
class Literal(Node):
    char: str


@dataclass
class Wildcard(Node):
    pass


@dataclass
class CharClass(Node):
    chars: frozenset
    negated: bool


@dataclass
class Anchor(Node):
    kind: AnchorKind


@dataclass
class Quantified(Node):
    child: Node
    min: int
    max: Optional[int]   # None = unbounded
    lazy: bool


@dataclass
class Group(Node):
    index: int
    child: "Sequence | Alternation"


@dataclass
class Sequence(Node):
    children: list[Node] = field(default_factory=list)


@dataclass
class Alternation(Node):
    branches: list[Sequence] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parse errors
# ---------------------------------------------------------------------------

class ParseError(Exception):
    def __init__(self, msg: str, pos: int, pattern: str):
        snippet = pattern[max(0, pos - 5):pos + 10]
        arrow   = " " * min(5, pos) + "^"
        super().__init__(f"\nParse error at position {pos}: {msg}\n  ...{snippet}...\n  ...{arrow}")
        self.pos     = pos
        self.pattern = pattern


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

_ANCHOR_MAP = {
    TT.ANCHOR_BEG:       AnchorKind.BEG,
    TT.ANCHOR_END:       AnchorKind.END,
    TT.ANCHOR_WDBEG:     AnchorKind.WDBEG,
    TT.ANCHOR_WDEND:     AnchorKind.WDEND,
    TT.ANCHOR_WDBEG_NEG: AnchorKind.WDBEG_NEG,
    TT.ANCHOR_WDEND_NEG: AnchorKind.WDEND_NEG,
}

_ANCHOR_TOKENS = set(_ANCHOR_MAP.keys())

_QUANT_TOKENS = {
    TT.QUANT_STAR, TT.QUANT_PLUS, TT.QUANT_OPT,
    TT.QUANT_EXACT, TT.QUANT_RANGE,
}


class Parser:
    def __init__(self, tokens: list[Token], pattern: str):
        self.tokens  = tokens
        self.pattern = pattern
        self.pos     = 0
        self._group_counter = 0  # increments each time we open a group

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse(self) -> Node:
        node = self._parse_pattern()
        if self._peek() is not None:
            tok = self._peek()
            raise ParseError(
                f"unexpected token '{tok.type.name}' — possibly unmatched ')'",
                tok.pos, self.pattern
            )
        # unwrap trivial single-branch alternation at top level
        if isinstance(node, Alternation) and len(node.branches) == 1:
            return node.branches[0]
        return node

    # ------------------------------------------------------------------
    # pattern := sequence ('|' sequence)*
    # ------------------------------------------------------------------

    def _parse_pattern(self) -> Node:
        branches: list[Sequence] = []
        branches.append(self._parse_sequence())

        while self._peek() and self._peek().type == TT.PIPE:
            self._consume()  # eat '|'
            branches.append(self._parse_sequence())

        if len(branches) == 1:
            return branches[0]
        return Alternation(branches=branches)

    # ------------------------------------------------------------------
    # sequence := quantified*
    # ------------------------------------------------------------------

    def _parse_sequence(self) -> Sequence:
        seq = Sequence()
        while True:
            tok = self._peek()
            # stop at end-of-tokens, ')', or '|'
            if tok is None or tok.type in (TT.RPAREN, TT.PIPE):
                break
            node = self._parse_quantified()
            seq.children.append(node)
        return seq

    # ------------------------------------------------------------------
    # quantified := atom quantifier?
    # ------------------------------------------------------------------

    def _parse_quantified(self) -> Node:
        atom = self._parse_atom()

        tok = self._peek()
        if tok is None or tok.type not in _QUANT_TOKENS:
            return atom

        # anchors cannot be quantified
        if isinstance(atom, Anchor):
            raise ParseError(
                f"anchors cannot be quantified",
                tok.pos, self.pattern
            )

        self._consume()
        min_, max_, lazy = self._quant_bounds(tok)
        return Quantified(child=atom, min=min_, max=max_, lazy=lazy)

    def _quant_bounds(self, tok: Token):
        """Return (min, max, lazy) for a quantifier token."""
        if tok.type == TT.QUANT_STAR:
            return 0, None, tok.lazy
        if tok.type == TT.QUANT_PLUS:
            return 1, None, tok.lazy
        if tok.type == TT.QUANT_OPT:
            return 0, 1, False
        if tok.type == TT.QUANT_EXACT:
            return tok.exact, tok.exact, tok.lazy
        if tok.type == TT.QUANT_RANGE:
            return tok.min, tok.max, tok.lazy
        raise ParseError(f"unknown quantifier token {tok.type}", tok.pos, self.pattern)

    # ------------------------------------------------------------------
    # atom := LITERAL | WILDCARD | CHARCLASS | ANCHOR | group
    # ------------------------------------------------------------------

    def _parse_atom(self) -> Node:
        tok = self._peek()

        if tok is None:
            raise ParseError(
                "unexpected end of pattern — expected an atom",
                len(self.pattern), self.pattern
            )

        # quantifier with no preceding atom
        if tok.type in _QUANT_TOKENS:
            raise ParseError(
                f"quantifier '{tok.type.name}' has nothing to quantify",
                tok.pos, self.pattern
            )

        if tok.type == TT.LITERAL:
            self._consume()
            return Literal(char=tok.char)

        if tok.type == TT.WILDCARD:
            self._consume()
            return Wildcard()

        if tok.type == TT.CHARCLASS:
            self._consume()
            return CharClass(chars=tok.chars, negated=tok.negated)

        if tok.type in _ANCHOR_TOKENS:
            self._consume()
            return Anchor(kind=_ANCHOR_MAP[tok.type])

        if tok.type == TT.LPAREN:
            return self._parse_group()

        if tok.type == TT.RPAREN:
            raise ParseError(
                "unmatched ')'",
                tok.pos, self.pattern
            )

        raise ParseError(
            f"unexpected token '{tok.type.name}'",
            tok.pos, self.pattern
        )

    # ------------------------------------------------------------------
    # group := '(' pattern ')'
    # ------------------------------------------------------------------

    def _parse_group(self) -> Group:
        lparen = self._consume()  # eat '('
        self._group_counter += 1
        index = self._group_counter

        inner = self._parse_pattern()

        if self._peek() is None or self._peek().type != TT.RPAREN:
            raise ParseError(
                f"unclosed group — missing ')'",
                lparen.pos, self.pattern
            )
        self._consume()  # eat ')'

        return Group(index=index, child=inner)

    # ------------------------------------------------------------------
    # Token stream helpers
    # ------------------------------------------------------------------

    def _peek(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def parse(pattern: str) -> Node:
    """Lex and parse a pattern string, returning the AST root."""
    from lexer import LexError
    tokens = tokenize(pattern)
    return Parser(tokens, pattern).parse()


# ---------------------------------------------------------------------------
# Pretty printer (useful for debugging)
# ---------------------------------------------------------------------------

def dump(node: Node, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(node, Literal):
        return f"{pad}Literal({node.char!r})"
    if isinstance(node, Wildcard):
        return f"{pad}Wildcard"
    if isinstance(node, CharClass):
        neg = "!" if node.negated else ""
        return f"{pad}CharClass({neg}{{{', '.join(sorted(node.chars)[:6])}{'...' if len(node.chars) > 6 else ''}}})"
    if isinstance(node, Anchor):
        return f"{pad}Anchor({node.kind.name})"
    if isinstance(node, Quantified):
        hi  = "∞" if node.max is None else str(node.max)
        lz  = " lazy" if node.lazy else ""
        hdr = f"{pad}Quantified({node.min}..{hi}{lz})"
        return hdr + "\n" + dump(node.child, indent + 1)
    if isinstance(node, Group):
        hdr = f"{pad}Group(#{node.index})"
        return hdr + "\n" + dump(node.child, indent + 1)
    if isinstance(node, Sequence):
        if not node.children:
            return f"{pad}Sequence(empty)"
        lines = [f"{pad}Sequence"] + [dump(c, indent + 1) for c in node.children]
        return "\n".join(lines)
    if isinstance(node, Alternation):
        lines = [f"{pad}Alternation"]
        for i, branch in enumerate(node.branches):
            lines.append(f"{pad}  branch {i}")
            lines.append(dump(branch, indent + 2))
        return "\n".join(lines)
    return f"{pad}Unknown({type(node).__name__})"