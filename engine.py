"""
engine.py — recursive backtracking evaluator over the AST.

Strategy:
  - Walk the AST recursively against (string, position).
  - Each node returns a generator of (end_pos, groups) pairs —
    all the ways that node can match starting at pos.
  - Quantifiers drive backtracking: greedy tries longest first,
    lazy tries shortest first.
  - Groups record (start, end) spans; unmatched groups store None.

Public API:
  match(pattern, string)            -> Match | None
  search(pattern, string)           -> Match | None
  findall(pattern, string)          -> list[tuple[str, ...]]
  replace(pattern, repl, string)    -> str
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterator

from lexer import tokenize, LexError
from parser import (
    parse, ParseError,
    Node, Literal, Wildcard, CharClass, Anchor, Quantified,
    Group, Sequence, Alternation, AnchorKind,
)


# ---------------------------------------------------------------------------
# Match result
# ---------------------------------------------------------------------------

@dataclass
class Match:
    """Holds the result of a successful match."""
    string:  str
    start:   int
    end:     int
    _groups: dict[int, Optional[tuple[int, int]]]  # group index → (start, end) | None

    @property
    def matched(self) -> str:
        return self.string[self.start:self.end]

    def group(self, index: int = 0) -> Optional[str]:
        """Return captured text for group index (0 = whole match)."""
        if index == 0:
            return self.matched
        span = self._groups.get(index)
        if span is None:
            return None
        return self.string[span[0]:span[1]]

    def groups(self) -> tuple[Optional[str], ...]:
        """Return all capture groups as a tuple (1-indexed)."""
        if not self._groups:
            return ()
        max_idx = max(self._groups.keys())
        return tuple(self.group(i) for i in range(1, max_idx + 1))

    def __repr__(self):
        return f"Match(matched={self.matched!r}, start={self.start}, end={self.end}, groups={self.groups()})"


# ---------------------------------------------------------------------------
# Engine errors
# ---------------------------------------------------------------------------

class EngineError(Exception):
    pass

class ReplaceError(Exception):
    pass


# ---------------------------------------------------------------------------
# Groups state — immutable dict wrapper for backtracking safety
# ---------------------------------------------------------------------------

Groups = dict  # int → (int, int) | None


def _set_group(groups: Groups, index: int, span: Optional[tuple[int, int]]) -> Groups:
    """Return a new groups dict with one entry updated."""
    g = dict(groups)
    g[index] = span
    return g


# ---------------------------------------------------------------------------
# Core evaluator — yields (pos, groups) for every way node can match
# ---------------------------------------------------------------------------

def _eval(node: Node, s: str, pos: int, groups: Groups) -> Iterator[tuple[int, Groups]]:
    """
    Yield every (end_pos, groups) that node can produce starting at pos.
    Greedy quantifiers yield longer matches first; lazy yield shorter first.
    """

    # ── Literal ──────────────────────────────────────────────────────────
    if isinstance(node, Literal):
        if pos < len(s) and s[pos] == node.char:
            yield pos + 1, groups
        return

    # ── Wildcard ─────────────────────────────────────────────────────────
    if isinstance(node, Wildcard):
        if pos < len(s):
            yield pos + 1, groups
        return

    # ── CharClass ────────────────────────────────────────────────────────
    if isinstance(node, CharClass):
        if pos < len(s):
            hit = s[pos] in node.chars
            if (hit and not node.negated) or (not hit and node.negated):
                yield pos + 1, groups
        return

    # ── Anchor ───────────────────────────────────────────────────────────
    if isinstance(node, Anchor):
        if _anchor_matches(node.kind, s, pos):
            yield pos, groups
        return

    # ── Sequence ─────────────────────────────────────────────────────────
    if isinstance(node, Sequence):
        yield from _eval_sequence(node.children, s, pos, groups)
        return

    # ── Alternation ──────────────────────────────────────────────────────
    if isinstance(node, Alternation):
        for branch in node.branches:
            yield from _eval(branch, s, pos, groups)
        return

    # ── Group ────────────────────────────────────────────────────────────
    if isinstance(node, Group):
        for end, g2 in _eval(node.child, s, pos, groups):
            yield end, _set_group(g2, node.index, (pos, end))
        return

    # ── Quantified ───────────────────────────────────────────────────────
    if isinstance(node, Quantified):
        yield from _eval_quantified(node, s, pos, groups)
        return

    raise EngineError(f"unknown AST node type: {type(node).__name__}")


def _eval_sequence(children: list, s: str, pos: int, groups: Groups) -> Iterator[tuple[int, Groups]]:
    """Evaluate a list of nodes in order — thread pos and groups through each."""
    if not children:
        yield pos, groups
        return
    head, *tail = children
    for mid, g2 in _eval(head, s, pos, groups):
        yield from _eval_sequence(tail, s, mid, g2)


def _eval_quantified(node: Quantified, s: str, pos: int, groups: Groups) -> Iterator[tuple[int, Groups]]:
    """
    Expand quantifier by collecting all valid repetition counts,
    then yield end positions in greedy (high→low) or lazy (low→high) order.
    """
    min_, max_, lazy = node.min, node.max, node.lazy

    # Each entry: (end_pos, groups_state) after exactly k repetitions
    # We build up counts[k] = list of (pos, groups) reachable after k reps
    counts: list[list[tuple[int, Groups]]] = []
    current = [(pos, groups)]  # starting state (0 repetitions)

    k = 0
    while True:
        if max_ is not None and k >= max_:
            break
        next_states: list[tuple[int, Groups]] = []
        seen_positions: set[int] = set()
        for cur_pos, cur_groups in current:
            for end, g2 in _eval(node.child, s, cur_pos, cur_groups):
                # avoid infinite loops on zero-width matches
                if end == cur_pos and k >= min_:
                    continue
                if end not in seen_positions:
                    seen_positions.add(end)
                    next_states.append((end, g2))
        if not next_states:
            break
        counts.append(next_states)
        current = next_states
        k += 1

    # Build list of (rep_count, states) for valid counts (>= min_)
    valid: list[tuple[int, list]] = []
    for rep, states in enumerate(counts, start=1):
        if rep >= min_:
            valid.append((rep, states))
    # Also include 0 repetitions if min_ == 0
    if min_ == 0:
        valid.insert(0, (0, [(pos, groups)]))

    if not lazy:
        valid = list(reversed(valid))  # greedy: try most repetitions first

    for _rep, states in valid:
        for end_pos, g in states:
            yield end_pos, g


# ---------------------------------------------------------------------------
# Anchor matching logic
# ---------------------------------------------------------------------------

def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def _anchor_matches(kind: AnchorKind, s: str, pos: int) -> bool:
    if kind == AnchorKind.BEG:
        return pos == 0
    if kind == AnchorKind.END:
        return pos == len(s)
    if kind in (AnchorKind.WDBEG, AnchorKind.WDEND,
                AnchorKind.WDBEG_NEG, AnchorKind.WDEND_NEG):
        before = _is_word_char(s[pos - 1]) if pos > 0 else False
        after  = _is_word_char(s[pos])     if pos < len(s) else False
        if kind == AnchorKind.WDBEG:
            return (not before) and after
        if kind == AnchorKind.WDEND:
            return before and (not after)
        if kind == AnchorKind.WDBEG_NEG:
            return not ((not before) and after)
        if kind == AnchorKind.WDEND_NEG:
            return not (before and (not after))
    return False


# ---------------------------------------------------------------------------
# Count groups in AST (to initialise all group slots to None)
# ---------------------------------------------------------------------------

def _count_groups(node: Node) -> int:
    if isinstance(node, Group):
        return max(node.index, _count_groups(node.child))
    if isinstance(node, Sequence):
        return max((_count_groups(c) for c in node.children), default=0)
    if isinstance(node, Alternation):
        return max((_count_groups(b) for b in node.branches), default=0)
    if isinstance(node, Quantified):
        return _count_groups(node.child)
    return 0


# ---------------------------------------------------------------------------
# Internal match driver
# ---------------------------------------------------------------------------

def _run(ast: Node, s: str, start: int) -> Optional[tuple[int, Groups]]:
    """Try to match ast at position start. Return (end, groups) or None."""
    n_groups = _count_groups(ast)
    groups: Groups = {i: None for i in range(1, n_groups + 1)}
    for end, g in _eval(ast, s, start, groups):
        return end, g
    return None


def _compile(pattern: str) -> Node:
    """Lex + parse a pattern, wrapping errors with context."""
    try:
        return parse(pattern)
    except LexError as e:
        raise EngineError(f"Invalid pattern (lex error): {e}") from e
    except ParseError as e:
        raise EngineError(f"Invalid pattern (parse error): {e}") from e


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def match(pattern: str, string: str) -> Optional[Match]:
    """
    Match pattern at the BEGINNING of string only.
    Returns a Match object or None.
    """
    ast = _compile(pattern)
    result = _run(ast, string, 0)
    if result is None:
        return None
    end, groups = result
    return Match(string=string, start=0, end=end, _groups=groups)


def search(pattern: str, string: str) -> Optional[Match]:
    """
    Find the FIRST match of pattern anywhere in string.
    Returns a Match object or None.
    """
    ast = _compile(pattern)
    for start in range(len(string) + 1):
        result = _run(ast, string, start)
        if result is not None:
            end, groups = result
            return Match(string=string, start=start, end=end, _groups=groups)
    return None


def findall(pattern: str, string: str) -> list[tuple[str, ...]]:
    """
    Find all non-overlapping matches of pattern in string.
    Always returns a list of tuples of captured groups.
    If there are no groups, each tuple contains the full match.
    """
    ast     = _compile(pattern)
    results = []
    pos     = 0
    while pos <= len(string):
        result = _run(ast, string, pos)
        if result is None:
            pos += 1
            continue
        end, groups = result
        m = Match(string=string, start=pos, end=end, _groups=groups)
        if groups:
            results.append(m.groups())
        else:
            results.append((m.matched,))
        # advance past this match; step 1 if zero-length to avoid infinite loop
        pos = end if end > pos else pos + 1
    return results


def replace(pattern: str, repl: str, string: str) -> str:
    """
    Replace all non-overlapping matches of pattern in string.
    Use {1}, {2}, ... in repl to refer to captured groups.
    Raises ReplaceError if a backreference refers to an unmatched group.
    """
    ast    = _compile(pattern)
    result = []
    pos    = 0
    while pos <= len(string):
        run = _run(ast, string, pos)
        if run is None:
            if pos < len(string):
                result.append(string[pos])
            pos += 1
            continue
        end, groups = run
        m = Match(string=string, start=pos, end=end, _groups=groups)
        result.append(_apply_repl(repl, m))
        pos = end if end > pos else pos + 1
    return "".join(result)


def _apply_repl(repl: str, m: Match) -> str:
    """Expand backreferences in a replacement string."""
    out = []
    i   = 0
    while i < len(repl):
        if repl[i] == "{":
            j = repl.find("}", i)
            if j == -1:
                raise ReplaceError(f"unclosed '{{' in replacement string at position {i}")
            ref = repl[i+1:j]
            if not ref.isdigit():
                raise ReplaceError(f"invalid backreference '{{{ref}}}' — must be a number")
            idx = int(ref)
            val = m.group(idx)
            if val is None:
                raise ReplaceError(
                    f"backreference {{{idx}}} refers to an unmatched group"
                )
            out.append(val)
            i = j + 1
        else:
            out.append(repl[i])
            i += 1
    return "".join(out)