"""
lexer.py — tokenizer for the custom regex engine.

Converts a pattern string into a flat list of Token objects.
No parser logic here — every decision is purely lexical.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------

class TT(Enum):
    LITERAL          = auto()  # single resolved character
    WILDCARD         = auto()  # _
    ANCHOR_BEG       = auto()  # <beg>
    ANCHOR_END       = auto()  # <end>
    ANCHOR_WDBEG     = auto()  # <wdbeg>
    ANCHOR_WDEND     = auto()  # <wdend>
    ANCHOR_WDBEG_NEG = auto()  # !<wdbeg>
    ANCHOR_WDEND_NEG = auto()  # !<wdend>
    CHARCLASS        = auto()  # <...> — fully resolved
    QUANT_STAR       = auto()  # *
    QUANT_PLUS       = auto()  # +
    QUANT_OPT        = auto()  # ?
    QUANT_EXACT      = auto()  # *<n>
    QUANT_RANGE      = auto()  # *<m,n>
    LPAREN           = auto()  # (
    RPAREN           = auto()  # )
    PIPE             = auto()  # | inside ( )


# ---------------------------------------------------------------------------
# Token dataclass
# ---------------------------------------------------------------------------

@dataclass
class Token:
    type: TT
    pos: int                        # position in original pattern string

    # LITERAL
    char: Optional[str] = None

    # CHARCLASS
    negated: bool = False
    chars: frozenset = field(default_factory=frozenset)

    # QUANT_EXACT
    exact: Optional[int] = None

    # QUANT_RANGE
    min: Optional[int] = None
    max: Optional[int] = None

    # laziness — applies to QUANT_STAR, QUANT_PLUS, QUANT_EXACT, QUANT_RANGE
    lazy: bool = False

    def __repr__(self):
        base = f"Token({self.type.name}, pos={self.pos}"
        if self.char is not None:
            base += f", char={self.char!r}"
        if self.type == TT.CHARCLASS:
            base += f", negated={self.negated}, chars={set(self.chars)!r}"
        if self.exact is not None:
            base += f", exact={self.exact}"
        if self.min is not None:
            base += f", min={self.min}, max={self.max}"
        if self.lazy:
            base += ", lazy=True"
        return base + ")"


# ---------------------------------------------------------------------------
# Lexer errors
# ---------------------------------------------------------------------------

class LexError(Exception):
    def __init__(self, msg: str, pos: int, pattern: str):
        snippet = pattern[max(0, pos-5):pos+10]
        arrow   = " " * min(5, pos) + "^"
        super().__init__(f"\nLex error at position {pos}: {msg}\n  ...{snippet}...\n  ...{arrow}")
        self.pos     = pos
        self.pattern = pattern


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.pos     = 0
        self.tokens: list[Token] = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.pattern):
            self._next()
        return self.tokens

    # ------------------------------------------------------------------
    # Main dispatch
    # ------------------------------------------------------------------

    def _next(self):
        p   = self.pattern
        pos = self.pos
        ch  = p[pos]

        # --- escape sequence ---
        if ch == "\\":
            self._lex_escape()

        # --- wildcard ---
        elif ch == "_":
            self._emit(TT.WILDCARD, pos)
            self.pos += 1

        # --- negation prefix: !<wdbeg>, !<wdend>, or !<charclass> ---
        elif ch == "!":
            self._lex_bang()

        # --- angle-bracket constructs ---
        elif ch == "<":
            self._lex_angle()

        # --- quantifiers ---
        elif ch == "*":
            self._lex_star()
        elif ch == "+":
            self._lex_plus()
        elif ch == "?":
            self._lex_question()

        # --- grouping ---
        elif ch == "(":
            self._emit(TT.LPAREN, pos)
            self.pos += 1
        elif ch == ")":
            self._emit(TT.RPAREN, pos)
            self.pos += 1
        elif ch == "|":
            self._emit(TT.PIPE, pos)
            self.pos += 1

        # --- plain literal ---
        else:
            self._emit(TT.LITERAL, pos, char=ch)
            self.pos += 1

    # ------------------------------------------------------------------
    # Escape sequences
    # ------------------------------------------------------------------

    def _lex_escape(self):
        pos = self.pos
        if self.pos + 1 >= len(self.pattern):
            raise LexError("trailing backslash", pos, self.pattern)
        escaped = self.pattern[self.pos + 1]
        self._emit(TT.LITERAL, pos, char=escaped)
        self.pos += 2

    # ------------------------------------------------------------------
    # Bang (!) prefix
    # ------------------------------------------------------------------

    def _lex_bang(self):
        pos = self.pos
        rest = self.pattern[self.pos + 1:]

        if rest.startswith("<wdbeg>"):
            self._emit(TT.ANCHOR_WDBEG_NEG, pos)
            self.pos += 8   # len("!<wdbeg>")
        elif rest.startswith("<wdend>"):
            self._emit(TT.ANCHOR_WDEND_NEG, pos)
            self.pos += 8
        elif rest.startswith("<"):
            # check for negated named class first: !<digit>, !<alpha>, etc.
            for keyword, chars in self._NAMED_CLASSES.items():
                if rest.startswith(keyword):
                    self.tokens.append(Token(
                        type=TT.CHARCLASS, pos=pos,
                        negated=True, chars=chars,
                    ))
                    self.pos += 1 + len(keyword)  # skip ! + keyword
                    return
            # otherwise negated literal character class: !<...>
            self.pos += 1   # skip the !
            tok = self._lex_angle_charclass(negated=True, start_pos=pos)
            self.tokens.append(tok)
        else:
            raise LexError(
                "'!' must be followed by '<wdbeg>', '<wdend>', or a character class '<...>'",
                pos, self.pattern
            )

    # ------------------------------------------------------------------
    # Angle-bracket constructs: anchors or character classes
    # ------------------------------------------------------------------

    # built-in named character classes
    _NAMED_CLASSES: dict = {
        "<digit>": frozenset("0123456789"),
        "<alpha>": frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        "<upper>": frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        "<lower>": frozenset("abcdefghijklmnopqrstuvwxyz"),
        "<alnum>": frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
        "<space>": frozenset(" \t\n\r\f\v"),
    }

    def _lex_angle(self):
        pos  = self.pos
        rest = self.pattern[pos:]

        # named anchors — check longest first
        for keyword, tt in [
            ("<wdbeg>", TT.ANCHOR_WDBEG),
            ("<wdend>", TT.ANCHOR_WDEND),
            ("<beg>",   TT.ANCHOR_BEG),
            ("<end>",   TT.ANCHOR_END),
        ]:
            if rest.startswith(keyword):
                self._emit(tt, pos)
                self.pos += len(keyword)
                return

        # named character classes
        for keyword, chars in self._NAMED_CLASSES.items():
            if rest.startswith(keyword):
                self.tokens.append(Token(
                    type=TT.CHARCLASS, pos=pos,
                    negated=False, chars=chars,
                ))
                self.pos += len(keyword)
                return

        # otherwise it must be a literal character class <...>
        tok = self._lex_angle_charclass(negated=False, start_pos=pos)
        self.tokens.append(tok)

    # ------------------------------------------------------------------
    # Character class parser: <...>
    # Handles: single chars, ranges (a-z), unions (a|b-d|5)
    # ------------------------------------------------------------------

    def _lex_angle_charclass(self, negated: bool, start_pos: int) -> Token:
        p   = self.pattern
        pos = self.pos  # points at '<'

        if pos >= len(p) or p[pos] != "<":
            raise LexError("expected '<'", pos, p)

        pos += 1  # skip '<'
        chars: set[str] = set()

        while pos < len(p) and p[pos] != ">":
            # escaped character inside class
            if p[pos] == "\\":
                if pos + 1 >= len(p):
                    raise LexError("trailing backslash inside character class", pos, p)
                ch  = p[pos + 1]
                pos += 2
            else:
                ch  = p[pos]
                pos += 1

            # check for range: ch - end_ch
            if pos < len(p) and p[pos] == "-" and (pos + 1) < len(p) and p[pos + 1] != ">":
                pos += 1  # skip '-'
                if p[pos] == "\\":
                    if pos + 1 >= len(p):
                        raise LexError("trailing backslash in range", pos, p)
                    end_ch  = p[pos + 1]
                    pos    += 2
                else:
                    end_ch  = p[pos]
                    pos    += 1

                if ord(ch) > ord(end_ch):
                    raise LexError(
                        f"invalid range '{ch}-{end_ch}': start must be <= end",
                        start_pos, p
                    )
                for code in range(ord(ch), ord(end_ch) + 1):
                    chars.add(chr(code))
            else:
                chars.add(ch)

            # skip '|' separator between items
            if pos < len(p) and p[pos] == "|":
                pos += 1

        if pos >= len(p):
            raise LexError("unterminated character class — missing '>'", start_pos, p)

        pos += 1  # skip '>'
        self.pos = pos

        if not chars:
            raise LexError("empty character class '<>'", start_pos, p)

        return Token(
            type    = TT.CHARCLASS,
            pos     = start_pos,
            negated = negated,
            chars   = frozenset(chars),
        )

    # ------------------------------------------------------------------
    # Quantifiers
    # ------------------------------------------------------------------

    def _lex_star(self):
        """
        *        → QUANT_STAR
        *?       → QUANT_STAR(lazy)
        *<n>     → QUANT_EXACT(n)
        *<m,n>   → QUANT_RANGE(m,n)
        *<m,n>?  → QUANT_RANGE(m,n,lazy)
        *<n>?    → QUANT_EXACT(n,lazy)  — allowed for consistency
        """
        pos = self.pos
        self.pos += 1  # skip '*'

        if self.pos < len(self.pattern) and self.pattern[self.pos] == "<":
            # *<...>
            tok = self._lex_quant_bracket(pos)
        else:
            # plain * or *?
            lazy = self._consume_lazy()
            tok  = Token(TT.QUANT_STAR, pos, lazy=lazy)

        self.tokens.append(tok)

    def _lex_plus(self):
        pos = self.pos
        self.pos += 1
        lazy = self._consume_lazy()
        self._emit(TT.QUANT_PLUS, pos, lazy=lazy)

    def _lex_question(self):
        pos = self.pos
        self.pos += 1
        # bare ? is never lazy (it's already the shortest match)
        self._emit(TT.QUANT_OPT, pos)

    def _lex_quant_bracket(self, start_pos: int) -> Token:
        """Parse *<n> or *<m,n> — self.pos must point at '<'."""
        p   = self.pattern
        pos = self.pos + 1  # skip '<'
        end = p.find(">", pos)

        if end == -1:
            raise LexError("unterminated quantifier — missing '>'", start_pos, p)

        inner = p[pos:end]
        self.pos = end + 1  # move past '>'

        try:
            if "," in inner:
                parts = inner.split(",", 1)
                m, n  = int(parts[0].strip()), int(parts[1].strip())
                if m < 0 or n < m:
                    raise LexError(
                        f"invalid quantifier range <{m},{n}>: need 0 <= m <= n",
                        start_pos, p
                    )
                lazy = self._consume_lazy()
                return Token(TT.QUANT_RANGE, start_pos, min=m, max=n, lazy=lazy)
            else:
                n    = int(inner.strip())
                if n < 0:
                    raise LexError(f"exact quantifier must be >= 0, got {n}", start_pos, p)
                lazy = self._consume_lazy()
                return Token(TT.QUANT_EXACT, start_pos, exact=n, lazy=lazy)
        except ValueError:
            raise LexError(
                f"quantifier content must be integers, got '{inner}'",
                start_pos, p
            )

    def _consume_lazy(self) -> bool:
        """Consume a trailing '?' for laziness and return True if present."""
        if self.pos < len(self.pattern) and self.pattern[self.pos] == "?":
            self.pos += 1
            return True
        return False

    # ------------------------------------------------------------------
    # Emit helper
    # ------------------------------------------------------------------

    def _emit(self, tt: TT, pos: int, **kwargs):
        self.tokens.append(Token(type=tt, pos=pos, **kwargs))


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def tokenize(pattern: str) -> list[Token]:
    """Tokenize a pattern string and return the token list."""
    return Lexer(pattern).tokenize()