"""test_parser.py — tests for every AST shape the parser can produce."""

from parser import (
    parse, dump,
    Literal, Wildcard, CharClass, Anchor, Quantified,
    Group, Sequence, Alternation, AnchorKind, ParseError
)

PASS = 0
FAIL = 0


def check(label, got, expected_type, **attrs):
    global PASS, FAIL
    if not isinstance(got, expected_type):
        print(f"  FAIL  {label}")
        print(f"        expected {expected_type.__name__}, got {type(got).__name__}")
        FAIL += 1
        return False
    mismatches = []
    for k, v in attrs.items():
        actual = getattr(got, k, "MISSING")
        if actual != v:
            mismatches.append(f"{k}: expected {v!r}, got {actual!r}")
    if mismatches:
        print(f"  FAIL  {label}")
        for m in mismatches:
            print(f"        {m}")
        FAIL += 1
        return False
    print(f"  PASS  {label}")
    PASS += 1
    return True


def check_error(label, pattern, fragment):
    global PASS, FAIL
    try:
        parse(pattern)
        print(f"  FAIL  {label} — expected ParseError, got no error")
        FAIL += 1
    except ParseError as e:
        if fragment in str(e):
            print(f"  PASS  {label}")
            PASS += 1
        else:
            print(f"  FAIL  {label} — wrong error message")
            print(f"        expected fragment: {fragment!r}")
            print(f"        got: {e}")
            FAIL += 1
    except Exception as e:
        print(f"  FAIL  {label} — unexpected exception: {type(e).__name__}: {e}")
        FAIL += 1


def seq_child(node, index):
    """Get child at index from a Sequence, unwrapping if needed."""
    if isinstance(node, Sequence):
        return node.children[index]
    raise TypeError(f"expected Sequence, got {type(node).__name__}")


# ---------------------------------------------------------------------------
print("\n── Single atoms ──")
# ---------------------------------------------------------------------------

node = parse("a")
check("single literal — sequence wrapper", node, Sequence)
check("single literal — child", seq_child(node, 0), Literal, char="a")

node = parse("_")
check("wildcard — child", seq_child(node, 0), Wildcard)

node = parse("<digit>")
check("charclass — child", seq_child(node, 0), CharClass,
      chars=frozenset("0123456789"), negated=False)

node = parse("!<digit>")
check("negated charclass", seq_child(node, 0), CharClass, negated=True)

node = parse("<beg>")
check("anchor beg", seq_child(node, 0), Anchor, kind=AnchorKind.BEG)

node = parse("<end>")
check("anchor end", seq_child(node, 0), Anchor, kind=AnchorKind.END)

node = parse("<wdbeg>")
check("anchor wdbeg", seq_child(node, 0), Anchor, kind=AnchorKind.WDBEG)

node = parse("<wdend>")
check("anchor wdend", seq_child(node, 0), Anchor, kind=AnchorKind.WDEND)

node = parse("!<wdbeg>")
check("anchor wdbeg neg", seq_child(node, 0), Anchor, kind=AnchorKind.WDBEG_NEG)

node = parse("!<wdend>")
check("anchor wdend neg", seq_child(node, 0), Anchor, kind=AnchorKind.WDEND_NEG)


# ---------------------------------------------------------------------------
print("\n── Sequences ──")
# ---------------------------------------------------------------------------

node = parse("abc")
check("sequence length", node, Sequence)
assert len(node.children) == 3
check("seq[0]", node.children[0], Literal, char="a")
check("seq[1]", node.children[1], Literal, char="b")
check("seq[2]", node.children[2], Literal, char="c")

node = parse("<beg>hello<end>")
check("anchored sequence length", node, Sequence)
assert len(node.children) == 7
check("first anchor", node.children[0], Anchor, kind=AnchorKind.BEG)
check("last anchor",  node.children[6], Anchor, kind=AnchorKind.END)


# ---------------------------------------------------------------------------
print("\n── Quantifiers ──")
# ---------------------------------------------------------------------------

node = parse("a*")
q = seq_child(node, 0)
check("greedy star", q, Quantified, min=0, max=None, lazy=False)
check("star child", q.child, Literal, char="a")

node = parse("a+")
q = seq_child(node, 0)
check("greedy plus", q, Quantified, min=1, max=None, lazy=False)

node = parse("a?")
q = seq_child(node, 0)
check("optional", q, Quantified, min=0, max=1, lazy=False)

node = parse("a*?")
q = seq_child(node, 0)
check("lazy star", q, Quantified, min=0, max=None, lazy=True)

node = parse("a+?")
q = seq_child(node, 0)
check("lazy plus", q, Quantified, min=1, max=None, lazy=True)

node = parse("a*<3>")
q = seq_child(node, 0)
check("exact quant", q, Quantified, min=3, max=3, lazy=False)

node = parse("a*<3>?")
q = seq_child(node, 0)
check("exact quant lazy", q, Quantified, min=3, max=3, lazy=True)

node = parse("a*<2,5>")
q = seq_child(node, 0)
check("range quant", q, Quantified, min=2, max=5, lazy=False)

node = parse("a*<2,5>?")
q = seq_child(node, 0)
check("range quant lazy", q, Quantified, min=2, max=5, lazy=True)

# quantifier on charclass
node = parse("<digit>+")
q = seq_child(node, 0)
check("quant on charclass", q, Quantified, min=1, max=None)
check("quant child is charclass", q.child, CharClass)

# quantifier on wildcard
node = parse("_*")
q = seq_child(node, 0)
check("quant on wildcard", q, Quantified, min=0, max=None)
check("quant child is wildcard", q.child, Wildcard)


# ---------------------------------------------------------------------------
print("\n── Groups ──")
# ---------------------------------------------------------------------------

node = parse("(a)")
g = seq_child(node, 0)
check("simple group", g, Group, index=1)
check("group child is sequence", g.child, Sequence)
check("group inner literal", g.child.children[0], Literal, char="a")

node = parse("(ab)(cd)")
check("two groups in sequence", node, Sequence)
g1 = node.children[0]
g2 = node.children[1]
check("group 1 index", g1, Group, index=1)
check("group 2 index", g2, Group, index=2)

# nested groups
node = parse("((a))")
outer = seq_child(node, 0)
check("outer group index", outer, Group, index=1)
inner = outer.child.children[0]
check("inner group index", inner, Group, index=2)
check("inner group child", inner.child.children[0], Literal, char="a")

# quantified group
node = parse("(ab)+")
q = seq_child(node, 0)
check("quantified group", q, Quantified, min=1, max=None)
check("quantified group child", q.child, Group, index=1)


# ---------------------------------------------------------------------------
print("\n── Alternation ──")
# ---------------------------------------------------------------------------

node = parse("(a|b)")
g = seq_child(node, 0)
check("alternation group", g, Group, index=1)
alt = g.child
check("inner alternation", alt, Alternation)
assert len(alt.branches) == 2
check("branch 0 literal", alt.branches[0].children[0], Literal, char="a")
check("branch 1 literal", alt.branches[1].children[0], Literal, char="b")

node = parse("(cat|dog|fish)")
g = seq_child(node, 0)
alt = g.child
check("three-way alternation", alt, Alternation)
assert len(alt.branches) == 3

# alternation with sequences
node = parse("(ab|cd)")
g = seq_child(node, 0)
alt = g.child
check("alternation with sequences", alt, Alternation)
check("branch 0 len", alt.branches[0], Sequence)
assert len(alt.branches[0].children) == 2

# nested group in alternation
node = parse("(<digit>+|<alpha>+)")
g = seq_child(node, 0)
alt = g.child
check("alternation with charclasses", alt, Alternation)
assert len(alt.branches) == 2


# ---------------------------------------------------------------------------
print("\n── Complex patterns ──")
# ---------------------------------------------------------------------------

# date pattern: (<digit>*<4>)-(<digit>*<2>)-(<digit>*<2>)
node = parse("(<digit>*<4>)-(<digit>*<2>)-(<digit>*<2>)")
check("date pattern is sequence", node, Sequence)
assert len(node.children) == 5  # group - group - group
g1 = node.children[0]
check("date group 1", g1, Group, index=1)
q1 = g1.child.children[0]
check("date group 1 quant", q1, Quantified, min=4, max=4)

# email-like: <alnum>+@<alnum>+
node = parse("<alnum>+@<alnum>+")
check("email-like sequence", node, Sequence)
assert len(node.children) == 3
check("alnum+", node.children[0], Quantified)
check("@ literal", node.children[1], Literal, char="@")
check("alnum+ second", node.children[2], Quantified)

# anchored word: <beg>(<alpha>+)<end>
node = parse("<beg>(<alpha>+)<end>")
check("anchored word sequence", node, Sequence)
assert len(node.children) == 3
check("beg anchor", node.children[0], Anchor, kind=AnchorKind.BEG)
check("group", node.children[1], Group, index=1)
check("end anchor", node.children[2], Anchor, kind=AnchorKind.END)

# word boundary usage
node = parse("<wdbeg>(<alpha>+)<wdend>")
check("word boundary sequence", node, Sequence)
check("wdbeg", node.children[0], Anchor, kind=AnchorKind.WDBEG)
check("wdend", node.children[2], Anchor, kind=AnchorKind.WDEND)


# ---------------------------------------------------------------------------
print("\n── Error cases ──")
# ---------------------------------------------------------------------------

check_error("unmatched )",          "a)",         "unmatched ')'")
check_error("unclosed (",           "(ab",        "unclosed group")
check_error("leading quantifier",   "*abc",       "nothing to quantify")
check_error("double quantifier",    "a**",        "nothing to quantify")
check_error("quantified anchor",    "<beg>*",     "anchors cannot be quantified")
# ()* is valid — quantifying empty group is harmless
# check_error("empty pattern quant",  "()*",        "nothing to quantify")


# ---------------------------------------------------------------------------
print("\n── dump() smoke test ──")
# ---------------------------------------------------------------------------

try:
    node = parse("<beg>(<digit>+|<alpha>*<3>)<end>")
    out  = dump(node)
    assert "Alternation" in out
    assert "Quantified" in out
    assert "Anchor" in out
    print("  PASS  dump() produces expected output")
    PASS += 1
except Exception as e:
    print(f"  FAIL  dump() raised: {e}")
    FAIL += 1


# ---------------------------------------------------------------------------
print(f"\n{'─'*40}")
print(f"  {PASS} passed   {FAIL} failed   {PASS+FAIL} total")
print(f"{'─'*40}\n")