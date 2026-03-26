# Custom Regex Engine

A from-scratch regular expression engine implemented in Python, with a custom pattern syntax. Supports matching, searching, finding all matches, and substitution with capture group backreferences.

---

## Project structure

```
lexer.py        tokenizes a pattern string into a token stream
parser.py       builds an AST from the token stream
engine.py       evaluates the AST against an input string
test_lexer.py   87 tests for the lexer
test_parser.py  71 tests for the parser
test_engine.py  96 tests for the engine
```

---

## Pattern syntax

### Literals and wildcard

| syntax | meaning                  | example         |
|--------|--------------------------|-----------------|
| `a`    | literal character        | `cat`           |
| `_`    | any single character     | `h_llo`         |
| `\`    | escape next character    | `\<` → literal `<` |

### Anchors

| syntax       | meaning                    |
|--------------|----------------------------|
| `<beg>`      | start of string            |
| `<end>`      | end of string              |
| `<wdbeg>`    | word start boundary        |
| `<wdend>`    | word end boundary          |
| `!<wdbeg>`   | not a word start boundary  |
| `!<wdend>`   | not a word end boundary    |

### Character classes

Character classes are always written inside `< >`. The `!` prefix negates the class.

| syntax          | meaning                        | example              |
|-----------------|--------------------------------|----------------------|
| `<a-z>`         | character range                | matches a through z  |
| `<5\|b-d>`      | union of chars and ranges      | matches 5, b, c, d   |
| `!<a-c\|6>`     | negated class                  | any char except a,b,c,6 |
| `<digit>`       | digits 0–9                     |                      |
| `<alpha>`       | letters a–z and A–Z            |                      |
| `<upper>`       | uppercase A–Z                  |                      |
| `<lower>`       | lowercase a–z                  |                      |
| `<alnum>`       | letters and digits             |                      |
| `<space>`       | whitespace (space, tab, newline, etc.) |             |

All named classes support `!` negation: `!<digit>`, `!<alpha>`, etc.

### Quantifiers

Quantifiers follow the atom they apply to. Anchors cannot be quantified.

| syntax      | meaning                        | lazy variant  |
|-------------|--------------------------------|---------------|
| `*`         | 0 or more (greedy)             | `*?`          |
| `+`         | 1 or more (greedy)             | `+?`          |
| `?`         | 0 or 1                         | —             |
| `*<3>`      | exactly 3                      | `*<3>?`       |
| `*<2,4>`    | between 2 and 4 (greedy)       | `*<2,4>?`     |

### Grouping and alternation

| syntax      | meaning                                      |
|-------------|----------------------------------------------|
| `(pattern)` | capture group — numbered left to right by `(` |
| `(a\|b\|c)` | alternation — match any one branch           |

Alternation lives inside `( )` only. To alternate between single characters use a character class instead: `<a\|b>`.

### Substitution backreferences

In the replacement string passed to `replace()`, use `{1}`, `{2}`, etc. to refer to captured groups.

```python
replace("(<alpha>+)(<digit>+)", "{2}-{1}", "abc123")
# → "123-abc"
```

---

## API

```python
from engine import match, search, findall, replace
```

### match(pattern, string)

Matches the pattern at the **beginning** of the string only. Returns a `Match` object or `None`.

```python
m = match("<digit>+", "123abc")
m.matched   # "123"
m.start     # 0
m.end       # 3
m.group(0)  # "123"  (full match)
```

### search(pattern, string)

Finds the **first** match anywhere in the string. Returns a `Match` object or `None`.

```python
m = search("<digit>+", "abc123def")
m.matched   # "123"
m.start     # 3
m.end       # 6
```

### findall(pattern, string)

Finds **all non-overlapping** matches. Always returns a list of tuples. Each tuple contains the captured groups, or the full match if there are no groups.

```python
findall("<digit>+", "a1b22c333")
# → [("1",), ("22",), ("333",)]

findall("(<alpha>+)(<digit>+)", "ab12cd34")
# → [("ab", "12"), ("cd", "34")]
```

### replace(pattern, repl, string)

Replaces all non-overlapping matches. Backreferences `{1}`, `{2}`, ... expand to captured groups. Raises `ReplaceError` if a backreference refers to an unmatched group.

```python
replace("<digit>+", "[{0}]", "a1b22")   # note: use group() not {0} — see below
replace("(<digit>+)", "[{1}]", "a1b22")
# → "a[1]b[22]"

replace("(<alpha>+)-(<alpha>+)", "{2}-{1}", "foo-bar")
# → "bar-foo"
```

---

## Running the tests

Each module has its own test file. Run them independently:

```bash
python test_lexer.py    # 87 tests
python test_parser.py   # 71 tests
python test_engine.py   # 96 tests
```

All three files are self-contained — no test framework required.

---

## Design patterns used

### 1. Pipeline (lexer → parser → evaluator)

The engine is structured as a three-stage pipeline where each stage has a single responsibility and communicates through a well-defined data structure:

```
string  →  [Lexer]  →  tokens  →  [Parser]  →  AST  →  [Evaluator]  →  Match
```

Each stage is isolated — the lexer knows nothing about the AST, the parser knows nothing about matching. This makes each module independently testable and replaceable.

### 2. Composite (AST nodes)

The AST is built from the **Composite** pattern — every node implements the same `Node` base type, and container nodes (`Sequence`, `Alternation`, `Group`, `Quantified`) hold other nodes. This lets the evaluator recurse uniformly over any tree shape without special-casing the depth.

### 3. Interpreter (evaluator)

The evaluator implements the **Interpreter** pattern — each AST node type has a corresponding evaluation rule in `_eval()`. The AST is the "language", and `_eval` is the interpreter that gives it meaning by walking the tree against an input string.

### 4. Iterator / Generator (backtracking)

Each node in `_eval()` is a Python **generator** that yields all possible ways it can match — `(end_position, groups)` pairs. This models NFA non-determinism naturally: the caller tries each yielded result in order, backtracking automatically when a path leads to a dead end. No explicit stack management is needed.

### 5. Immutable state (groups dict)

To make backtracking safe, the captured groups state is never mutated in place. Each step that updates a group calls `_set_group()` which returns a **new dict** — the original is untouched. This means abandoned backtrack paths can't corrupt the groups state of successful paths.

---

## How the NFA works

The engine uses **recursive backtracking**, which is behaviourally equivalent to a Non-deterministic Finite Automaton (NFA).

At each position in the input string, the evaluator asks every AST node: *"in how many ways can you match here?"* Each node yields its answers one at a time. The evaluator tries the first answer and continues matching the rest of the pattern. If anything fails downstream, it comes back (backtracks) and tries the next answer.

Greedy quantifiers yield longer matches first. Lazy quantifiers yield shorter matches first. The NFA structure is identical in both cases — only the yield order changes.

Capture groups are handled by threading a `groups` dict through every recursive call. Because the dict is replaced (not mutated) on each update, backtracking automatically restores the previous group state.

---

## Example walkthrough

Pattern: `(<alpha>+)-(<alpha>+)`
Input: `"foo-bar"`

1. Lexer produces: `LPAREN CHARCLASS(alpha) QUANT_PLUS RPAREN LITERAL(-) LPAREN CHARCLASS(alpha) QUANT_PLUS RPAREN`
2. Parser builds:
   ```
   Sequence
     Group(#1, Quantified(1..∞, CharClass(alpha)))
     Literal('-')
     Group(#2, Quantified(1..∞, CharClass(alpha)))
   ```
3. Evaluator at pos 0:
   - Group #1 tries to match `<alpha>+` greedily → consumes `"foo"`, pos → 3, group 1 = `"foo"`
   - Literal `-` matches at pos 3 → pos → 4
   - Group #2 tries to match `<alpha>+` greedily → consumes `"bar"`, pos → 7, group 2 = `"bar"`
   - End of pattern, pos 7 = end of string → **match**
4. Result: `Match(matched="foo-bar", groups=("foo", "bar"))`