"""test_lexer.py — tests for every token type the lexer can produce."""

import traceback
from lexer import tokenize, TT, LexError

PASS = 0
FAIL = 0

def check(label, tokens, expected):
    global PASS, FAIL
    types = [t.type for t in tokens]
    if types == expected:
        print(f"  PASS  {label}")
        PASS += 1
    else:
        print(f"  FAIL  {label}")
        print(f"        expected: {[e.name for e in expected]}")
        print(f"        got:      {[t.name for t in types]}")
        FAIL += 1

def check_attr(label, token, **attrs):
    global PASS, FAIL
    mismatches = []
    for k, v in attrs.items():
        actual = getattr(token, k)
        if actual != v:
            mismatches.append(f"{k}: expected {v!r}, got {actual!r}")
    if not mismatches:
        print(f"  PASS  {label}")
        PASS += 1
    else:
        print(f"  FAIL  {label}")
        for m in mismatches:
            print(f"        {m}")
        FAIL += 1

def check_error(label, pattern, fragment):
    global PASS, FAIL
    try:
        tokenize(pattern)
        print(f"  FAIL  {label} — expected LexError, got no error")
        FAIL += 1
    except LexError as e:
        if fragment in str(e):
            print(f"  PASS  {label}")
            PASS += 1
        else:
            print(f"  FAIL  {label} — wrong error message")
            print(f"        expected fragment: {fragment!r}")
            print(f"        got: {e}")
            FAIL += 1
    except Exception as e:
        print(f"  FAIL  {label} — unexpected exception: {e}")
        FAIL += 1


# ---------------------------------------------------------------------------
print("\n── Literals & wildcard ──")
# ---------------------------------------------------------------------------

toks = tokenize("abc")
check("plain literals", toks, [TT.LITERAL, TT.LITERAL, TT.LITERAL])
check_attr("literal char a", toks[0], char="a")
check_attr("literal char b", toks[1], char="b")

toks = tokenize("_")
check("wildcard token", toks, [TT.WILDCARD])

toks = tokenize(r"\<")
check("escaped <", toks, [TT.LITERAL])
check_attr("escaped < resolves to <", toks[0], char="<")

toks = tokenize(r"\*")
check("escaped *", toks, [TT.LITERAL])
check_attr("escaped * resolves to *", toks[0], char="*")

toks = tokenize(r"h\_llo")
check("escaped _ is literal", toks, [TT.LITERAL]*5)
check_attr("escaped _ char", toks[1], char="_")


# ---------------------------------------------------------------------------
print("\n── Anchors ──")
# ---------------------------------------------------------------------------

check("<beg>",           tokenize("<beg>"),           [TT.ANCHOR_BEG])
check("<end>",           tokenize("<end>"),           [TT.ANCHOR_END])
check("<wdbeg>",         tokenize("<wdbeg>"),         [TT.ANCHOR_WDBEG])
check("<wdend>",         tokenize("<wdend>"),         [TT.ANCHOR_WDEND])
check("!<wdbeg>",        tokenize("!<wdbeg>"),        [TT.ANCHOR_WDBEG_NEG])
check("!<wdend>",        tokenize("!<wdend>"),        [TT.ANCHOR_WDEND_NEG])
check("<beg>...<end>",   tokenize("<beg>hi<end>"),    [TT.ANCHOR_BEG, TT.LITERAL, TT.LITERAL, TT.ANCHOR_END])


# ---------------------------------------------------------------------------
print("\n── Character classes ──")
# ---------------------------------------------------------------------------

toks = tokenize("<0-9>")
check("digit class token", toks, [TT.CHARCLASS])
check_attr("digit class not negated", toks[0], negated=False)
check_attr("digit class chars", toks[0], chars=frozenset("0123456789"))

toks = tokenize("!<0-9>")
check("negated digit class", toks, [TT.CHARCLASS])
check_attr("negated flag set", toks[0], negated=True)

toks = tokenize("<a-c>")
check("alpha range a-c", toks, [TT.CHARCLASS])
check_attr("a-c chars", toks[0], chars=frozenset("abc"))

toks = tokenize("<5|b-d>")
check("union class <5|b-d>", toks, [TT.CHARCLASS])
check_attr("union chars", toks[0], chars=frozenset("5bcd"))

toks = tokenize("<a-b|0-9>")
check("literal a-b|0-9 class", toks, [TT.CHARCLASS])
check_attr("literal a-b|0-9 chars", toks[0], chars=frozenset("ab0123456789"))

toks = tokenize("!<a-c|6>")
check("negated union class", toks, [TT.CHARCLASS])
check_attr("negated union chars", toks[0], negated=True, chars=frozenset("abc6"))

toks = tokenize("<a|z>")
check("non-contiguous single chars", toks, [TT.CHARCLASS])
check_attr("a|z chars", toks[0], chars=frozenset("az"))

toks = tokenize(r"<\<|\>>")
check("escaped chars inside class", toks, [TT.CHARCLASS])
check_attr("escaped bracket chars", toks[0], chars=frozenset("<>"))

# named classes
toks = tokenize("<digit>")
check("<digit> token", toks, [TT.CHARCLASS])
check_attr("<digit> chars", toks[0], negated=False, chars=frozenset("0123456789"))

toks = tokenize("!<digit>")
check("!<digit> token", toks, [TT.CHARCLASS])
check_attr("!<digit> negated", toks[0], negated=True, chars=frozenset("0123456789"))

toks = tokenize("<alpha>")
check("<alpha> token", toks, [TT.CHARCLASS])
check_attr("<alpha> chars", toks[0], chars=frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))

toks = tokenize("<upper>")
check("<upper> token", toks, [TT.CHARCLASS])
check_attr("<upper> chars", toks[0], chars=frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

toks = tokenize("<lower>")
check("<lower> token", toks, [TT.CHARCLASS])
check_attr("<lower> chars", toks[0], chars=frozenset("abcdefghijklmnopqrstuvwxyz"))

toks = tokenize("<alnum>")
check("<alnum> token", toks, [TT.CHARCLASS])
check_attr("<alnum> chars", toks[0], chars=frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))

toks = tokenize("<space>")
check("<space> token", toks, [TT.CHARCLASS])
check_attr("<space> chars", toks[0], chars=frozenset(" \t\n\r\f\v"))

toks = tokenize("!<space>")
check("!<space> token", toks, [TT.CHARCLASS])
check_attr("!<space> negated", toks[0], negated=True, chars=frozenset(" \t\n\r\f\v"))

toks = tokenize("!<alnum>")
check("!<alnum> token", toks, [TT.CHARCLASS])
check_attr("!<alnum> negated", toks[0], negated=True)


# ---------------------------------------------------------------------------
print("\n── Quantifiers ──")
# ---------------------------------------------------------------------------

toks = tokenize("a*")
check("greedy star", toks, [TT.LITERAL, TT.QUANT_STAR])
check_attr("star not lazy", toks[1], lazy=False)

toks = tokenize("a*?")
check("lazy star", toks, [TT.LITERAL, TT.QUANT_STAR])
check_attr("star lazy", toks[1], lazy=True)

toks = tokenize("a+")
check("greedy plus", toks, [TT.LITERAL, TT.QUANT_PLUS])
check_attr("plus not lazy", toks[1], lazy=False)

toks = tokenize("a+?")
check("lazy plus", toks, [TT.LITERAL, TT.QUANT_PLUS])
check_attr("plus lazy", toks[1], lazy=True)

toks = tokenize("a?")
check("optional", toks, [TT.LITERAL, TT.QUANT_OPT])

toks = tokenize("a*<3>")
check("exact quantifier", toks, [TT.LITERAL, TT.QUANT_EXACT])
check_attr("exact n=3", toks[1], exact=3, lazy=False)

toks = tokenize("a*<3>?")
check("exact quantifier lazy", toks, [TT.LITERAL, TT.QUANT_EXACT])
check_attr("exact n=3 lazy", toks[1], exact=3, lazy=True)

toks = tokenize("a*<2,4>")
check("range quantifier", toks, [TT.LITERAL, TT.QUANT_RANGE])
check_attr("range 2-4", toks[1], min=2, max=4, lazy=False)

toks = tokenize("a*<2,4>?")
check("range quantifier lazy", toks, [TT.LITERAL, TT.QUANT_RANGE])
check_attr("range 2-4 lazy", toks[1], min=2, max=4, lazy=True)

toks = tokenize("a*<0,0>")
check("zero range quantifier", toks, [TT.LITERAL, TT.QUANT_RANGE])
check_attr("range 0-0", toks[1], min=0, max=0)


# ---------------------------------------------------------------------------
print("\n── Grouping & alternation ──")
# ---------------------------------------------------------------------------

toks = tokenize("(ab)")
check("capture group", toks, [TT.LPAREN, TT.LITERAL, TT.LITERAL, TT.RPAREN])

toks = tokenize("(a|b)")
check("alternation in group", toks, [TT.LPAREN, TT.LITERAL, TT.PIPE, TT.LITERAL, TT.RPAREN])

toks = tokenize("(cat|dog)")
check("word alternation", toks, [
    TT.LPAREN,
    TT.LITERAL, TT.LITERAL, TT.LITERAL,
    TT.PIPE,
    TT.LITERAL, TT.LITERAL, TT.LITERAL,
    TT.RPAREN,
])

toks = tokenize("(<0-9>+|abc)")
check("mixed alternation", toks, [TT.LPAREN, TT.CHARCLASS, TT.QUANT_PLUS, TT.PIPE, TT.LITERAL, TT.LITERAL, TT.LITERAL, TT.RPAREN])


# ---------------------------------------------------------------------------
print("\n── Complex patterns ──")
# ---------------------------------------------------------------------------

toks = tokenize("<beg>(<a-z>+)<end>")
check("full anchored word", toks, [
    TT.ANCHOR_BEG, TT.LPAREN, TT.CHARCLASS, TT.QUANT_PLUS, TT.RPAREN, TT.ANCHOR_END
])

toks = tokenize("<wdbeg>!<0-9>+<wdend>")
check("word boundary + negated class", toks, [
    TT.ANCHOR_WDBEG, TT.CHARCLASS, TT.QUANT_PLUS, TT.ANCHOR_WDEND
])
check_attr("negated class in complex", toks[1], negated=True)

toks = tokenize("(<0-9>*<3>)-(<0-9>*<2>)")
check("date-like pattern", toks, [
    TT.LPAREN, TT.CHARCLASS, TT.QUANT_EXACT, TT.RPAREN,
    TT.LITERAL,
    TT.LPAREN, TT.CHARCLASS, TT.QUANT_EXACT, TT.RPAREN,
])


# ---------------------------------------------------------------------------
print("\n── Error cases ──")
# ---------------------------------------------------------------------------

check_error("trailing backslash",        "abc\\",       "trailing backslash")
check_error("unterminated class",         "<a-z",        "unterminated")
check_error("empty class",                "<>",          "empty")
check_error("invalid range z-a",         "<z-a>",       "invalid range")
check_error("bad quantifier content",    "*<x>",        "integers")
check_error("invalid range in quant",    "*<4,2>",      "0 <= m <= n")
check_error("bare ! not followed by <",  "!abc",        "'!'")
check_error("unterminated quantifier",   "*<3",         "unterminated quantifier")


# ---------------------------------------------------------------------------
print(f"\n{'─'*40}")
print(f"  {PASS} passed   {FAIL} failed   {PASS+FAIL} total")
print(f"{'─'*40}\n")