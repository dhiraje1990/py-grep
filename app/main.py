import sys
import argparse


# ══════════════════════════════════════════════════════════════════
# BASE CLASS
# ══════════════════════════════════════════════════════════════════

class Pattern:
    """
    The base class for ALL pattern types.

    Every pattern represents one rule — e.g. "match a digit",
    "match the letter k", or "match any one of: a, b, c".

    The match() contract (all subclasses must follow this):
        - Takes the full text and a current position
        - Returns the NEXT position (pos + N) on success
        - Returns -1 on failure

    Think of pos like a cursor. Each pattern moves the cursor
    forward by however many characters it consumed.
    """

    def match(self, text: str, pos: int) -> int:
        """
        Try to match this pattern at position `pos` inside `text`.

        Args:
            text (str): The full string being searched.
            pos  (int): The index to try matching at.

        Returns:
            int: new position on success, -1 on failure.
        """
        raise NotImplementedError(
            "Each Pattern subclass must implement its own match() method."
        )


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: Literal Character
# ══════════════════════════════════════════════════════════════════

class LiteralPattern(Pattern):
    """
    Matches ONE specific character exactly as written.

    Example:
        LiteralPattern('a') matches only 'a', nothing else.

    Used for plain characters in the pattern:
        "cat" → [LiteralPattern('c'), LiteralPattern('a'), LiteralPattern('t')]
    """

    def __init__(self, char: str) -> None:
        """
        Args:
            char (str): A single character to match. e.g. 'a', '3', '!'
        """
        self.char: str = char

    def __repr__(self) -> str:
        return f"Literal('{self.char}')"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` equals self.char.

        Example:
            LiteralPattern('a').match("apple", 0) →  1  ✅
            LiteralPattern('a').match("apple", 1) → -1  ❌ ('p' != 'a')
        """
        is_in_bounds: bool = pos < len(text)
        is_match: bool = is_in_bounds and (text[pos] == self.char)
        return (pos + 1) if is_match else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: <int>  — any digit 0-9
# ══════════════════════════════════════════════════════════════════

class IntPattern(Pattern):
    """
    Custom token <int> — matches ANY single digit character (0-9).

    Example:
        <int> matches '0', '5', '9'
        <int> does NOT match 'a', ' ', '_'
    """

    def __repr__(self) -> str:
        return "IntPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is a digit (0-9).

        Example:
            IntPattern().match("abc1", 3) →  4  ✅
            IntPattern().match("abc1", 0) → -1  ❌
        """
        is_in_bounds: bool = pos < len(text)
        is_digit: bool = is_in_bounds and text[pos].isdigit()
        return (pos + 1) if is_digit else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: <alpha>  — any letter a-z or A-Z
# ══════════════════════════════════════════════════════════════════

class AlphaPattern(Pattern):
    """
    Custom token <alpha> — matches ANY single letter (a-z or A-Z).

    Example:
        <alpha> matches 'a', 'Z', 'g'
        <alpha> does NOT match '1', ' ', '_', '!'
    """

    def __repr__(self) -> str:
        return "AlphaPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is a letter.

        Example:
            AlphaPattern().match("abc", 0) →  1  ✅
            AlphaPattern().match("1bc", 0) → -1  ❌
        """
        is_in_bounds: bool = pos < len(text)
        is_alpha: bool = is_in_bounds and text[pos].isalpha()
        return (pos + 1) if is_alpha else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: <word>  — letter, digit, or underscore
# ══════════════════════════════════════════════════════════════════

class WordPattern(Pattern):
    """
    Custom token <word> — matches any letter, digit, or underscore.

    Example:
        <word> matches 'a', '5', '_'
        <word> does NOT match ' ', '!', '-'
    """

    def __repr__(self) -> str:
        return "WordPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is a letter, digit, or '_'.

        Example:
            WordPattern().match("a_1!", 0) →  1  ✅ 'a'
            WordPattern().match("a_1!", 3) → -1  ❌ '!'
        """
        is_in_bounds: bool = pos < len(text)
        is_word_char: bool = is_in_bounds and (
            text[pos].isalnum() or text[pos] == '_'
        )
        return (pos + 1) if is_word_char else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: <space>  — any whitespace
# ══════════════════════════════════════════════════════════════════

class SpacePattern(Pattern):
    """
    Custom token <space> — matches ANY whitespace character.

    Whitespace includes: space ' ', tab '\\t', newline '\\n' etc.

    Example:
        <space> matches ' ', '\\t', '\\n'
        <space> does NOT match 'a', '1', '_'
    """

    def __repr__(self) -> str:
        return "SpacePattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is whitespace.

        Example:
            SpacePattern().match("a b", 1) →  2  ✅
            SpacePattern().match("a b", 0) → -1  ❌
        """
        is_in_bounds: bool = pos < len(text)
        is_space: bool = is_in_bounds and text[pos].isspace()
        return (pos + 1) if is_space else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: <_>  — any single character (wildcard)
# ══════════════════════════════════════════════════════════════════

class AnyPattern(Pattern):
    """
    Custom token <_> — matches ANY single character, no exceptions.

    This replaced the old <any> token. Inspired by '_' being a
    common "don't care" placeholder in many languages.

    The only way this fails is if we're past the end of the string.

    Example:
        <_> matches 'a', '1', ' ', '!', literally anything
        <_> fails only on empty string or out-of-bounds position
    """

    def __repr__(self) -> str:
        return "AnyPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Match any character at `pos` — succeeds as long as in bounds.

        Example:
            AnyPattern().match("abc", 0) →  1  ✅ anything goes
            AnyPattern().match("abc", 3) → -1  ❌ past end of string
        """
        is_in_bounds: bool = pos < len(text)
        return (pos + 1) if is_in_bounds else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: <[abc]>  — positive character group
# ══════════════════════════════════════════════════════════════════

class CharGroupPattern(Pattern):
    """
    Custom token <[...]> — matches any ONE character from a defined set.

    This is called a "Positive Character Group" — it succeeds if the
    character at the current position is a member of the group.

    Supports two ways to define the group:

    1. Explicit characters:
        <[abc]>   → matches 'a', 'b', or 'c'
        <[aeiou]> → matches any vowel

    2. Ranges using '-':
        <[a-z]>   → matches any lowercase letter
        <[A-Z]>   → matches any uppercase letter
        <[0-9]>   → matches any digit
        <[a-zA-Z]>→ matches any letter (lower or upper)

    3. Mixed (explicit + ranges):
        <[a-z0-9]> → matches lowercase letter OR digit
        <[aeiou0-9]> → matches a vowel OR a digit

    How ranges work:
        "a-z" means every character whose ASCII value is between
        ord('a') and ord('z') inclusive. So 'b', 'c', ..., 'y' all match.

    Example:
        CharGroupPattern("aeiou").match("hello", 1) →  2  ✅ 'e' is a vowel
        CharGroupPattern("aeiou").match("hello", 0) → -1  ❌ 'h' not in group
        CharGroupPattern("a-z").match("hello", 0)   →  1  ✅ 'h' in a-z
        CharGroupPattern("0-9").match("abc3", 3)    →  4  ✅ '3' in 0-9
    """

    def __init__(self, group_str: str) -> None:
        """
        Parse the group string into a set of allowed characters.

        The group_str is the raw content inside <[...]>
        e.g. for <[a-z0-9]>, group_str = "a-z0-9"

        We expand all ranges and collect every allowed character
        into a single set for O(1) lookup during match().

        Args:
            group_str (str): Raw content between [ and ].
                             e.g. "abc", "a-z", "a-z0-9", "aeiou"
        """
        # Build the complete set of allowed characters by parsing group_str
        self.allowed_chars: set[str] = self._expand_group(group_str)

        # Keep the original string for __repr__ / debugging
        self.group_str: str = group_str

    def _expand_group(self, group_str: str) -> set[str]:
        """
        Parse the group string and return a set of all allowed characters.

        Parsing rules:
            - If we see X-Y (a char, a dash, another char), it's a range.
              We expand it to every character from X to Y inclusive.
            - Otherwise, each character is added to the set individually.

        Args:
            group_str (str): e.g. "a-z", "abc", "a-z0-9", "aeiou0-9"

        Returns:
            set[str]: All characters that this group should match.

        Example:
            _expand_group("abc")    → {'a', 'b', 'c'}
            _expand_group("a-c")    → {'a', 'b', 'c'}
            _expand_group("a-z0-9") → {'a','b',...,'z','0','1',...,'9'}
        """
        allowed: set[str] = set()

        # Index-based loop so we can peek ahead to detect ranges (X-Y)
        i: int = 0
        while i < len(group_str):

            # Check if this is a range: current char, dash, next char
            # e.g. 'a', '-', 'z'  →  range from 'a' to 'z'
            is_range: bool = (
                i + 2 < len(group_str) and  # enough chars left for X-Y
                group_str[i + 1] == '-'      # middle char is a dash
            )

            if is_range:
                range_start: str = group_str[i]
                range_end: str   = group_str[i + 2]

                # Validate: start must come before end in ASCII order
                if ord(range_start) > ord(range_end):
                    raise ValueError(
                        f"Invalid range '{range_start}-{range_end}' in "
                        f"character group — start must be <= end in ASCII order."
                    )

                # Expand: add every character from range_start to range_end
                for code in range(ord(range_start), ord(range_end) + 1):
                    allowed.add(chr(code))

                # Jump past all 3 characters: start, dash, end
                i += 3

            else:
                # Plain character — just add it directly
                allowed.add(group_str[i])
                i += 1

        return allowed

    def __repr__(self) -> str:
        return f"CharGroup('[{self.group_str}]')"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is in the allowed set.

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 if char is in group, -1 otherwise.

        Example:
            CharGroupPattern("aeiou").match("hello", 1) →  2  ✅ 'e' is vowel
            CharGroupPattern("aeiou").match("hello", 0) → -1  ❌ 'h' not vowel
            CharGroupPattern("a-z").match("hello", 0)   →  1  ✅ 'h' in a-z
        """
        is_in_bounds: bool = pos < len(text)
        is_in_group: bool  = is_in_bounds and (text[pos] in self.allowed_chars)
        return (pos + 1) if is_in_group else -1


# ══════════════════════════════════════════════════════════════════
# CONCRETE PATTERN: RepeatPattern  — <token*N>
# ══════════════════════════════════════════════════════════════════

class RepeatPattern(Pattern):
    """
    Wraps any Pattern and repeats it exactly N times.

    This is how <int*3> and <_*5> work — instead of writing
    <int><int><int>, you write <int*3> and get the same effect.

    How it works:
        RepeatPattern(IntPattern(), 3) will call IntPattern.match()
        3 times in a row, advancing pos each time.
        If ANY of the 3 calls fails → the whole thing fails (-1).
        Only if ALL N calls succeed → return the final position.

    Example:
        RepeatPattern(IntPattern(), 3).match("abc123", 3)
            → tries IntPattern at pos 3 ('1') → pos 4
            → tries IntPattern at pos 4 ('2') → pos 5
            → tries IntPattern at pos 5 ('3') → pos 6
            → all 3 succeeded → returns 6  ✅

        RepeatPattern(IntPattern(), 3).match("abc12x", 3)
            → tries IntPattern at pos 3 ('1') → pos 4
            → tries IntPattern at pos 4 ('2') → pos 5
            → tries IntPattern at pos 5 ('x') → -1
            → failed → returns -1  ❌
    """

    def __init__(self, inner: Pattern, count: int) -> None:
        """
        Args:
            inner (Pattern): The pattern to repeat. e.g. IntPattern()
            count (int):     How many times to repeat it. e.g. 3
        """
        # The pattern to run N times
        self.inner: Pattern = inner

        # How many times to run it
        self.count: int = count

    def __repr__(self) -> str:
        return f"Repeat({self.inner!r}, {self.count})"

    def match(self, text: str, pos: int) -> int:
        """
        Run self.inner exactly self.count times, advancing pos each time.

        Args:
            text (str): The full string being searched.
            pos  (int): Starting position.

        Returns:
            int: Final position after N matches, or -1 if any match fails.
        """
        # Run the inner pattern N times in a row
        for _ in range(self.count):
            pos = self.inner.match(text, pos)

            # If any single repetition fails, the whole repeat fails
            if pos == -1:
                return -1

        # All N repetitions succeeded — return final position
        return pos


# ══════════════════════════════════════════════════════════════════
# REGISTRY: token name → Pattern class
# ══════════════════════════════════════════════════════════════════

# Maps each simple token name to its Pattern class.
# Used by _parse() when it sees e.g. <int> or <space>.
#
# To add a new token:
#   1. Create a new Pattern subclass above
#   2. Add one line here — nothing else changes!
#
# Note: <_> and <[...]> are handled separately in _parse()
# because they need special parsing logic, not just a class lookup.
TOKEN_REGISTRY: dict[str, type[Pattern]] = {
    "int":   IntPattern,    # <int>   → any digit 0-9
    "word":  WordPattern,   # <word>  → letter, digit, or _
    "alpha": AlphaPattern,  # <alpha> → any letter a-z A-Z
    "space": SpacePattern,  # <space> → any whitespace
}


# ══════════════════════════════════════════════════════════════════
# PARSER + RUNNER: Matcher
# ══════════════════════════════════════════════════════════════════

class Matcher:
    """
    The main engine that:
        1. Takes a raw pattern string  e.g. "hi<space><[a-z]*3>"
        2. Parses it into a list of Pattern objects via _parse()
        3. Tries to find a match anywhere in the input text via match()

    Full syntax supported:
        <int>       → any digit
        <alpha>     → any letter
        <word>      → letter, digit, or _
        <space>     → any whitespace
        <_>         → any single character (wildcard)
        <int*N>     → repeat IntPattern N times
        <alpha*N>   → repeat AlphaPattern N times
        <word*N>    → repeat WordPattern N times
        <space*N>   → repeat SpacePattern N times
        <_*N>       → repeat AnyPattern N times
        <[abc]>     → any one of: a, b, c
        <[a-z]>     → any one character in range a-z
        <[a-z0-9]>  → any one character in range a-z OR 0-9
        <[abc]*N>   → repeat CharGroupPattern N times
        abc         → literal characters
    """

    def __init__(self, pattern_str: str) -> None:
        """
        Parse the raw pattern string into a list of Pattern objects.

        Args:
            pattern_str (str): e.g. "hello<space><int*3>"
        """
        self.patterns: list[Pattern] = self._parse(pattern_str)

    def _parse(self, pattern_str: str) -> list[Pattern]:
        """
        Convert the raw pattern string into a list of Pattern objects.

        Parsing walkthrough:
            We scan character by character. When we hit '<', we peek at the
            NEXT character to decide whether this is a literal quote or a token.

        Two cases when we see '<':

            Case A — Literal quote: next char is also '<'
                Syntax:  <<some text>>
                Meaning: treat every character inside as a plain LiteralPattern.
                Example: <<hello>> → [Literal('h'), Literal('e'), Literal('l'),
                                       Literal('l'), Literal('o')]
                Example: <<<>>    → [Literal('<')]
                Example: <<>>     → []  (empty — no patterns added, no-op)

                Why this exists:
                    Without this, writing a literal '<' in your pattern would
                    confuse the parser into thinking a token is starting.
                    <<...>> is the "quoting" or "escaping" mechanism.

            Case B — Token: next char is NOT '<'
                e.g. <int*3>, <[a-z]>, <_>
                → Read up to '>', parse as a token via _parse_token()

        Args:
            pattern_str (str): The raw pattern string.

        Returns:
            list[Pattern]: Ordered list of Pattern objects.

        Raises:
            ValueError: For unknown tokens, unclosed brackets, bad multipliers,
                        or an unclosed << quote.
        """
        patterns: list[Pattern] = []

        # Index-based loop — we sometimes jump forward multiple characters
        i: int = 0
        while i < len(pattern_str):

            current_char: str = pattern_str[i]

            if current_char == '<':

                # ── Peek at the next character to decide which case we're in ──
                has_next: bool = (i + 1) < len(pattern_str)
                next_char: str = pattern_str[i + 1] if has_next else ""

                if next_char == '<':
                    # ════════════════════════════════════════════════
                    # CASE A: Angle-bracket literal  <<X>>  →  <X>
                    # ════════════════════════════════════════════════
                    #
                    # We've seen '<<'. Read everything up to '>>' as
                    # content X, then emit literals for the text <X>.
                    #
                    # The < and > are ALWAYS added automatically:
                    #   <<int>>  →  matches "<int>"  (not a digit token)
                    #   <<a-z>>  →  matches "<a-z>"  (not a range token)
                    #   <<a:z>>  →  matches "<a:z>"  (arbitrary content)
                    #   <<>>     →  matches "<>"      (empty content)

                    # Find the closing '>>'
                    # We search for '>>' starting from i+2 (after the '<<')
                    closing_quote: int = pattern_str.find('>>', i + 2)

                    if closing_quote == -1:
                        raise ValueError(
                            f"Unclosed '<<' literal quote at position {i}. "
                            f"Did you forget to close with '>>'?"
                        )

                    # Extract the raw text between << and >>
                    # e.g. "<<int>>"  → quoted_text = "int"
                    # e.g. "<<a-z>>"  → quoted_text = "a-z"
                    # e.g. "<<>>"     → quoted_text = ""
                    quoted_text: str = pattern_str[i + 2 : closing_quote]

                    # <<X>> matches the LITERAL TEXT <X>
                    # i.e. the < and > are automatically added around the content.
                    #
                    # So we always emit:
                    #   Literal('<')  +  one Literal per char in content  +  Literal('>')
                    #
                    # Examples:
                    #   <<int>>  → '<', 'i', 'n', 't', '>'  →  matches "<int>"
                    #   <<a-z>>  → '<', 'a', '-', 'z', '>'  →  matches "<a-z>"
                    #   <<a:z>>  → '<', 'a', ':', 'z', '>'  →  matches "<a:z>"
                    #   <<>>     → '<', '>'                  →  matches "<>"
                    patterns.append(LiteralPattern('<'))
                    for ch in quoted_text:
                        patterns.append(LiteralPattern(ch))
                    patterns.append(LiteralPattern('>'))

                    # Jump past the entire <<...>> block
                    # closing_quote points to the first '>' of '>>'
                    # so we need to skip past BOTH '>' characters → +2
                    i = closing_quote + 2

                else:
                    # ════════════════════════════════════════════════
                    # CASE B: Token  <int*3>, <[a-z]>, <_>, etc.
                    # ════════════════════════════════════════════════

                    # Find the closing single '>'
                    closing: int = pattern_str.find('>', i)
                    if closing == -1:
                        raise ValueError(
                            f"Unclosed '<' in pattern at position {i}. "
                            f"Did you forget to close your token with '>'?"
                        )

                    # Extract the raw content between < and >
                    # e.g. "<int*3>"   → token_content = "int*3"
                    # e.g. "<[a-z]*2>" → token_content = "[a-z]*2"
                    # e.g. "<_>"       → token_content = "_"
                    token_content: str = pattern_str[i + 1 : closing]

                    # Parse and create the appropriate Pattern object
                    pattern: Pattern = self._parse_token(token_content)
                    patterns.append(pattern)

                    # Jump past the entire token including < and >
                    i = closing + 1

            else:
                # ── Plain literal character — not inside any brackets ──
                patterns.append(LiteralPattern(current_char))
                i += 1

        return patterns

    def _parse_token(self, token_content: str) -> Pattern:
        """
        Parse the content inside < > and return the right Pattern object.

        This method handles three token forms:

            Case 1 — Range token:  e.g. <a-z>, <A-Z*3>, <0-9*2>
                Detected by: exactly one '-' with a single char on each side,
                             before any '*' multiplier.
                Syntax:  <START-END>  or  <START-END*N>
                Example: <a-z>   → CharGroupPattern("a-z")
                         <a-z*3> → RepeatPattern(CharGroupPattern("a-z"), 3)

            Case 2 — Wildcard:  e.g. <_>, <_*5>
                Detected by: token starts with '_'
                Example: <_>   → AnyPattern()
                         <_*5> → RepeatPattern(AnyPattern(), 5)

            Case 3 — Named token:  e.g. <int>, <alpha*3>, <word*2>
                Detected by: everything else — look up in TOKEN_REGISTRY
                Example: <int>    → IntPattern()
                         <int*3>  → RepeatPattern(IntPattern(), 3)

        Args:
            token_content (str): Everything between < and >.
                                 e.g. "a-z", "a-z*3", "int*3", "_", "alpha"

        Returns:
            Pattern: The appropriate Pattern object, possibly wrapped
                     in a RepeatPattern if a *N multiplier was found.

        Raises:
            ValueError: For unknown token names or bad multiplier values.
        """

        # ── CASE 1: Range token  e.g. a-z  or  a-z*3  or  0-9*2 ──
        #
        # Detection rule:
        #   Split off any *N multiplier first, then check if what remains
        #   looks like "X-Y" — exactly one char, a dash, exactly one char.
        #
        # Examples:
        #   "a-z"    → base="a-z",   multiplier=""   → range ✅
        #   "a-z*3"  → base="a-z",   multiplier="*3" → range ✅
        #   "int"    → base="int",   multiplier=""   → not a range ❌
        #   "int*3"  → base="int*3", no '-' at pos 1 → not a range ❌

        # Split on '*' to isolate the base name from any multiplier
        # e.g. "a-z*3" → parts = ["a-z", "3"]
        # e.g. "a-z"   → parts = ["a-z"]
        parts: list[str] = token_content.split('*', maxsplit=1)

        # The base is everything before the first '*'
        base: str = parts[0]

        # A range looks like exactly: one char, '-', one char  → length 3
        # and the middle character must be '-'
        is_range: bool = (
            len(base) == 3 and   # must be exactly "X-Y"
            base[1] == '-'       # middle character must be a dash
        )

        if is_range:
            # Extract the range start and end characters
            range_str: str = base  # e.g. "a-z"

            # Extract the multiplier string (e.g. "*3" or "" if none)
            multiplier_str: str = f"*{parts[1]}" if len(parts) == 2 else ""
            count: int = self._parse_multiplier(multiplier_str, token_content)

            # Build a CharGroupPattern from the range string "X-Y"
            # CharGroupPattern already knows how to expand "a-z" into a full set
            base_pattern: Pattern = CharGroupPattern(range_str)

            # Wrap in RepeatPattern if count > 1
            return RepeatPattern(base_pattern, count) if count > 1 else base_pattern

        # ── CASE 2: Wildcard  e.g. _  or  _*5 ──
        elif token_content.startswith('_'):

            # Everything after '_' should be empty or a *N multiplier
            after_underscore: str = token_content[1:]
            count = self._parse_multiplier(after_underscore, token_content)

            base_pattern = AnyPattern()
            return RepeatPattern(base_pattern, count) if count > 1 else base_pattern

        # ── CASE 3: Named token  e.g. int, alpha, int*3, word*2 ──
        else:

            # The token name is the base (already split above)
            token_name: str = base

            # Parse the multiplier from the second part (if present)
            multiplier_str = f"*{parts[1]}" if len(parts) == 2 else ""
            count = self._parse_multiplier(multiplier_str, token_content)

            # Validate: is this a known token name?
            if token_name not in TOKEN_REGISTRY:
                raise ValueError(
                    f"Unknown token '<{token_name}>'. "
                    f"Available tokens: {list(TOKEN_REGISTRY.keys())} "
                    f"plus <_>, <START-END> ranges e.g. <a-z>, "
                    f"and <<...>> for literals."
                )

            # Instantiate the correct Pattern class from the registry
            base_pattern = TOKEN_REGISTRY[token_name]()

            # Wrap in RepeatPattern if count > 1
            return RepeatPattern(base_pattern, count) if count > 1 else base_pattern

    def _parse_multiplier(self, multiplier_str: str, token_content: str) -> int:
        """
        Parse an optional *N multiplier string and return the count.

        Args:
            multiplier_str (str): The part after the token name.
                                  e.g. "*3", "*10", "" (empty = no multiplier)
            token_content  (str): The full token content — used in error messages.

        Returns:
            int: The repeat count. Returns 1 if no multiplier is present.

        Raises:
            ValueError: If *N is malformed (e.g. "*abc", "*0", "*-1")

        Example:
            _parse_multiplier("*3",  "int*3")  → 3
            _parse_multiplier("*10", "_*10")   → 10
            _parse_multiplier("",    "alpha")  → 1
            _parse_multiplier("*0",  "int*0")  → raises ValueError
        """
        # No multiplier — default to 1 (match exactly once)
        if multiplier_str == "":
            return 1

        # Must start with '*' — anything else is malformed
        if not multiplier_str.startswith('*'):
            raise ValueError(
                f"Unexpected content '{multiplier_str}' in token '<{token_content}>'. "
                f"Did you mean '*{multiplier_str}' for a multiplier?"
            )

        # Extract just the number after '*'
        count_str: str = multiplier_str[1:]

        # Make sure it's actually a number
        if not count_str.isdigit():
            raise ValueError(
                f"Invalid multiplier '*{count_str}' in token '<{token_content}>'. "
                f"Multiplier must be a positive integer e.g. *3."
            )

        count: int = int(count_str)

        # Multiplier must be at least 1
        if count < 1:
            raise ValueError(
                f"Multiplier must be >= 1, got *{count} in '<{token_content}>'."
            )

        return count

    def match(self, text: str) -> bool:
        """
        Try to find a match for our pattern sequence ANYWHERE in `text`.

        Sliding window strategy:
            Try every starting position in the text.
            At each position, run all patterns in sequence.
            If ALL succeed → match found!
            If ANY fails → slide one step forward and try again.

        Args:
            text (str): The full input string to search.

        Returns:
            bool: True if pattern matched anywhere, False otherwise.

        Example:
            Matcher("<int*3>").match("price is 500 dollars") → True
            Matcher("<int*3>").match("no numbers here")      → False
        """
        for start in range(len(text)):

            pos: int = start

            for pattern in self.patterns:
                pos = pattern.match(text, pos)
                if pos == -1:
                    break  # ❌ failed at this start — try next

            else:
                return True  # ✅ all patterns matched!

        return False


# ══════════════════════════════════════════════════════════════════
# ARGUMENT PARSER
# ══════════════════════════════════════════════════════════════════

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser.

    Returns:
        argparse.ArgumentParser: ready to parse CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            "A custom regex engine with angle-bracket token syntax.\n\n"
            "Tokens:\n"
            "  <int>        any digit 0-9\n"
            "  <alpha>      any letter a-z A-Z\n"
            "  <word>       letter, digit, or _\n"
            "  <space>      any whitespace\n"
            "  <_>          any single character (wildcard)\n"
            "  <int*N>      repeat token N times  e.g. <int*3>\n"
            "  <[abc]>      any one of: a, b, c\n"
            "  <[a-z]>      any char in range a-z\n"
            "  <[a-z]*N>    repeat char group N times\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-E", "--extended-regexp",
        required=True,
        metavar="PATTERN",
        dest="pattern",
        help="Pattern to search for in stdin.",
    )

    return parser


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Entry point. Parses args, reads stdin, runs matcher, exits 0 or 1.

    Exit codes:
        0 → pattern found       ✅
        1 → pattern not found   ❌
        2 → bad usage / error   ⚠️
    """
    parser: argparse.ArgumentParser = build_arg_parser()
    args: argparse.Namespace = parser.parse_args()

    pattern_str: str = args.pattern
    input_text: str  = sys.stdin.read()

    try:
        matcher: Matcher = Matcher(pattern_str)
    except ValueError as e:
        print(f"Error in pattern: {e}", file=sys.stderr)
        sys.exit(2)

    found: bool = matcher.match(input_text)
    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()