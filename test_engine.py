"""test_engine.py — tests for match, search, findall, replace."""

from engine import match, search, findall, replace, EngineError, ReplaceError

PASS = 0
FAIL = 0


def ok(label, got, expected):
    global PASS, FAIL
    if got == expected:
        print(f"  PASS  {label}")
        PASS += 1
    else:
        print(f"  FAIL  {label}")
        print(f"        expected: {expected!r}")
        print(f"        got:      {got!r}")
        FAIL += 1


def check_error(label, fn, exc_type, fragment):
    global PASS, FAIL
    try:
        fn()
        print(f"  FAIL  {label} — expected {exc_type.__name__}, got no error")
        FAIL += 1
    except exc_type as e:
        if fragment in str(e):
            print(f"  PASS  {label}")
            PASS += 1
        else:
            print(f"  FAIL  {label} — wrong message: {e}")
            FAIL += 1
    except Exception as e:
        print(f"  FAIL  {label} — unexpected {type(e).__name__}: {e}")
        FAIL += 1


def m(pattern, string):
    r = match(pattern, string)
    return r.matched if r else None

def mg(pattern, string):
    r = match(pattern, string)
    return r.groups() if r else None

def s(pattern, string):
    r = search(pattern, string)
    return (r.matched, r.start, r.end) if r else None


# ---------------------------------------------------------------------------
print("\n── match() — literals & wildcard ──")
# ---------------------------------------------------------------------------

ok("exact literal match",        m("abc", "abc"),        "abc")
ok("partial match at start",     m("ab",  "abcd"),       "ab")
ok("no match",                   m("xyz", "abc"),        None)
ok("wildcard matches any char",  m("a_c", "axc"),        "axc")
ok("wildcard matches digit",     m("a_c", "a9c"),        "a9c")
ok("wildcard needs a char",      m("a_c", "ac"),         None)
ok("empty pattern matches",      m("",    "abc"),        "")
ok("empty pattern on empty str", m("",    ""),           "")


# ---------------------------------------------------------------------------
print("\n── match() — character classes ──")
# ---------------------------------------------------------------------------

ok("digit class match",          m("<digit>", "5"),      "5")
ok("digit class no match",       m("<digit>", "a"),      None)
ok("negated digit",              m("!<digit>", "a"),     "a")
ok("negated digit rejects num",  m("!<digit>", "5"),     None)
ok("alpha class",                m("<alpha>", "z"),      "z")
ok("alpha rejects digit",        m("<alpha>", "3"),      None)
ok("upper class",                m("<upper>", "A"),      "A")
ok("upper rejects lower",        m("<upper>", "a"),      None)
ok("lower class",                m("<lower>", "a"),      "a")
ok("lower rejects upper",        m("<lower>", "A"),      None)
ok("alnum matches letter",       m("<alnum>", "q"),      "q")
ok("alnum matches digit",        m("<alnum>", "4"),      "4")
ok("alnum rejects space",        m("<alnum>", " "),      None)
ok("space matches space",        m("<space>", " "),      " ")
ok("space matches tab",          m("<space>", "\t"),     "\t")
ok("space rejects letter",       m("<space>", "a"),      None)
ok("literal range",              m("<a-c>", "b"),        "b")
ok("literal range no match",     m("<a-c>", "d"),        None)
ok("union class",                m("<5|b-d>", "5"),      "5")
ok("union class range",          m("<5|b-d>", "c"),      "c")
ok("union class no match",       m("<5|b-d>", "a"),      None)


# ---------------------------------------------------------------------------
print("\n── match() — anchors ──")
# ---------------------------------------------------------------------------

ok("<beg> at start",             m("<beg>hi",  "hi"),        "hi")
ok("<beg> fails mid string",     s("<beg>hi",  "say hi"),    None)
ok("<end> at end",               m("hi<end>",  "hi"),        "hi")
ok("<end> fails before end",     m("hi<end>",  "hix"),       None)
ok("<wdbeg> word start",         s("<wdbeg>cat", "the cat"), ("cat", 4, 7))
ok("<wdend> word end",           s("cat<wdend>", "the cat"), ("cat", 4, 7))
ok("!<wdbeg> not word start",    s("!<wdbeg><alpha>+", "abc"), ("bc", 1, 3))
ok("!<wdend> not word end",      s("<alpha>+!<wdend>", "abc def"), ("ab", 0, 2))


# ---------------------------------------------------------------------------
print("\n── match() — quantifiers ──")
# ---------------------------------------------------------------------------

ok("star 0 times",               m("a*b",   "b"),       "b")
ok("star 1 time",                m("a*b",   "ab"),      "ab")
ok("star many times",            m("a*b",   "aaab"),    "aaab")
ok("plus needs 1",               m("a+b",   "b"),       None)
ok("plus 1 time",                m("a+b",   "ab"),      "ab")
ok("plus many",                  m("a+b",   "aaab"),    "aaab")
ok("optional absent",            m("a?b",   "b"),       "b")
ok("optional present",           m("a?b",   "ab"),      "ab")
ok("exact *<3>",                 m("a*<3>", "aaa"),     "aaa")
ok("exact *<3> too few",         m("a*<3>", "aa"),      None)
ok("exact *<3> greedy stops",    m("a*<3>b","aaab"),    "aaab")
ok("range *<2,4> low",           m("a*<2,4>","aa"),     "aa")
ok("range *<2,4> mid",           m("a*<2,4>","aaa"),    "aaa")
ok("range *<2,4> high",          m("a*<2,4>","aaaa"),   "aaaa")
ok("range *<2,4> too few",       m("a*<2,4>","a"),      None)
ok("range *<2,4> greedy cap",    s("a*<2,4>b","aaaaab"),("aaaab",1,6))
ok("lazy star",                  m("a*?b",  "aaab"),    "aaab")
ok("lazy plus",                  m("a+?b",  "aaab"),    "aaab")
ok("lazy range",                 m("a*<2,4>?b","aaab"), "aaab")


# ---------------------------------------------------------------------------
print("\n── match() — groups ──")
# ---------------------------------------------------------------------------

ok("simple group",               mg("(ab)",        "ab"),      ("ab",))
ok("two groups",                 mg("(a)(b)",      "ab"),      ("a", "b"))
ok("nested groups",              mg("((a)b)",      "ab"),      ("ab", "a"))
ok("group with quantifier",      mg("(a+)",        "aaa"),     ("aaa",))
ok("group captures greedy",      mg("(a*)",        "aaa"),     ("aaa",))
ok("non-capturing sequence",     mg("ab",          "ab"),      ())


# ---------------------------------------------------------------------------
print("\n── match() — alternation ──")
# ---------------------------------------------------------------------------

ok("simple alternation a",       m("(a|b)",    "a"),       "a")
ok("simple alternation b",       m("(a|b)",    "b"),       "b")
ok("alternation no match",       m("(a|b)",    "c"),       None)
ok("word alternation cat",       m("(cat|dog)","cat"),     "cat")
ok("word alternation dog",       m("(cat|dog)","dog"),     "dog")
ok("alternation in sequence",    m("x(a|b)y",  "xay"),    "xay")
ok("alternation group capture",  mg("(cat|dog)","cat"),    ("cat",))
ok("three-way alternation",      m("(a|b|c)",  "c"),       "c")
ok("alternation first wins",     mg("(a|ab)",  "ab"),      ("a",))


# ---------------------------------------------------------------------------
print("\n── search() ──")
# ---------------------------------------------------------------------------

ok("search finds mid string",    s("<digit>+", "abc123def"),  ("123", 3, 6))
ok("search finds at start",      s("<digit>+", "123abc"),     ("123", 0, 3))
ok("search finds at end",        s("<digit>+", "abc123"),     ("123", 3, 6))
ok("search returns first",       s("<digit>+", "12 34"),      ("12", 0, 2))
ok("search no match",            s("<digit>+", "abc"),        None)


# ---------------------------------------------------------------------------
print("\n── findall() ──")
# ---------------------------------------------------------------------------

ok("findall no groups",          findall("<digit>+", "a1b22c333"),  [("1",), ("22",), ("333",)])
ok("findall with group",         findall("(<digit>+)", "a1b22"),    [("1",), ("22",)])
ok("findall two groups",         findall("(<alpha>+)(<digit>+)", "ab12cd34"),
                                                                    [("ab","12"), ("cd","34")])
ok("findall no match",           findall("<digit>+", "abc"),        [])
ok("findall overlapping avoided",findall("a+", "aaaa"),             [("aaaa",)])


# ---------------------------------------------------------------------------
print("\n── replace() ──")
# ---------------------------------------------------------------------------

ok("simple replace",             replace("cat", "dog", "the cat sat"),  "the dog sat")
ok("replace all occurrences",    replace("a", "o", "banana"),           "bonono")
ok("replace with group ref",     replace("(<digit>+)", "[{1}]", "a1b22c333"), "a[1]b[22]c[333]")
ok("replace swap groups",        replace("(<alpha>+)(<digit>+)", "{2}{1}", "ab12"), "12ab")
ok("replace no match",           replace("xyz", "???", "hello"),        "hello")
ok("replace group 0 not used",   replace("a(b)c", ">{1}<", "abc"),      ">b<")


# ---------------------------------------------------------------------------
print("\n── complex patterns ──")
# ---------------------------------------------------------------------------

ok("date search",
   s("(<digit>*<4>)-(<digit>*<2>)-(<digit>*<2>)", "today is 2024-03-15"),
   ("2024-03-15", 9, 19))

ok("email-like match",
   m("<alnum>+@<alnum>+\.<alnum>+", "user@host.com"),
   "user@host.com")

ok("word boundary search",
   s("<wdbeg>cat<wdend>", "concatenate cat cats"),
   ("cat", 12, 15))

ok("anchored replace",
   replace("<beg><space>*", "", "   hello"),
   "hello")

ok("findall words",
   findall("<wdbeg>(<alpha>+)<wdend>", "one two three"),
   [("one",), ("two",), ("three",)])


# ---------------------------------------------------------------------------
print("\n── error cases ──")
# ---------------------------------------------------------------------------

check_error("bad pattern",
    lambda: match("(<digit>", "1"),
    EngineError, "parse error")

check_error("replace unmatched group",
    lambda: replace("(a)|(b)", "{2}", "a"),
    ReplaceError, "unmatched group")

check_error("replace invalid ref",
    lambda: replace("a", "{x}", "a"),
    ReplaceError, "invalid backreference")

check_error("replace unclosed brace",
    lambda: replace("a", "{1", "a"),
    ReplaceError, "unclosed")


# ---------------------------------------------------------------------------
print(f"\n{'─'*40}")
print(f"  {PASS} passed   {FAIL} failed   {PASS+FAIL} total")
print(f"{'─'*40}\n")