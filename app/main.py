import sys
import argparse


# ──────────────────────────────────────────────
# BASE CLASS
# ──────────────────────────────────────────────

class Pattern:
    """
    The base class for ALL pattern types.

    Every pattern represents one rule — like "match a digit" or
    "match the letter k". Each subclass implements its own match().

    The match() contract:
        - Takes the text and a position
        - Returns the NEXT position on success
        - Returns -1 on failure
    """

    def match(self, text: str, pos: int) -> int:
        """
        Try to match this pattern at position `pos` inside `text`.

        Args:
            text (str): The full string being searched.
            pos  (int): The index to try matching at.

        Returns:
            int: pos + 1 on success, -1 on failure.
        """
        raise NotImplementedError(
            "Each Pattern subclass must implement its own match() method."
        )


# ──────────────────────────────────────────────
# CONCRETE PATTERN: Literal Character
# ──────────────────────────────────────────────

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
        Store the character this pattern should match.

        Args:
            char (str): A single character. e.g. 'a', 'z', '!'
        """
        self.char: str = char

    def __repr__(self) -> str:
        """
        Human-readable representation — useful when debugging.
        e.g. print(LiteralPattern('a')) → Literal('a')
        """
        return f"Literal('{self.char}')"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` equals self.char.

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 on success, -1 on failure.

        Example:
            LiteralPattern('a').match("apple", 0) →  1  ✅
            LiteralPattern('a').match("apple", 1) → -1  ❌
        """
        is_in_bounds: bool = pos < len(text)
        is_match: bool = is_in_bounds and (text[pos] == self.char)

        return (pos + 1) if is_match else -1


# ──────────────────────────────────────────────
# CONCRETE PATTERN: <int>
# ──────────────────────────────────────────────

class IntPattern(Pattern):
    """
    Custom token <int> — matches ANY single digit character (0-9).

    This is our custom syntax equivalent of \\d in standard regex.

    Example:
        <int> matches '0', '1', '2', ..., '9'
        <int> does NOT match 'a', ' ', '!'

    Usage in a pattern:
        "a<int>"  → [LiteralPattern('a'), IntPattern()]
                    matches "a1", "a5", "a9" etc.
    """

    def __repr__(self) -> str:
        return "IntPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is a digit (0-9).

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 if digit, -1 otherwise.

        Example:
            IntPattern().match("abc1", 3) →  4  ✅ '1' is a digit
            IntPattern().match("abc1", 0) → -1  ❌ 'a' is not a digit
        """
        is_in_bounds: bool = pos < len(text)
        is_digit: bool = is_in_bounds and text[pos].isdigit()

        return (pos + 1) if is_digit else -1


# ──────────────────────────────────────────────
# CONCRETE PATTERN: <alpha>
# ──────────────────────────────────────────────

class AlphaPattern(Pattern):
    """
    Custom token <alpha> — matches ANY single letter (a-z or A-Z).

    Does NOT match digits, spaces, punctuation — letters only.

    Example:
        <alpha> matches 'a', 'Z', 'g'
        <alpha> does NOT match '1', ' ', '!'

    Usage in a pattern:
        "<alpha><int>" → [AlphaPattern(), IntPattern()]
                         matches "a1", "Z9", "g0" etc.
    """

    def __repr__(self) -> str:
        return "AlphaPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is a letter (a-z or A-Z).

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 if letter, -1 otherwise.

        Example:
            AlphaPattern().match("abc", 0) →  1  ✅ 'a' is a letter
            AlphaPattern().match("1bc", 0) → -1  ❌ '1' is not a letter
        """
        is_in_bounds: bool = pos < len(text)
        is_alpha: bool = is_in_bounds and text[pos].isalpha()

        return (pos + 1) if is_alpha else -1


# ──────────────────────────────────────────────
# CONCRETE PATTERN: <word>
# ──────────────────────────────────────────────

class WordPattern(Pattern):
    """
    Custom token <word> — matches ANY single word character.

    A word character is: a letter (a-z, A-Z), a digit (0-9), or underscore (_).
    This is our custom syntax equivalent of \\w in standard regex.

    Example:
        <word> matches 'a', 'Z', '5', '_'
        <word> does NOT match ' ', '!', '-'

    Usage in a pattern:
        "<word><word>" → [WordPattern(), WordPattern()]
                         matches "ab", "a1", "_a", "1_" etc.
    """

    def __repr__(self) -> str:
        return "WordPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is a letter, digit, or underscore.

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 if word character, -1 otherwise.

        Example:
            WordPattern().match("a_1!", 0) →  1  ✅ 'a' is a word char
            WordPattern().match("a_1!", 1) →  2  ✅ '_' is a word char
            WordPattern().match("a_1!", 3) → -1  ❌ '!' is not a word char
        """
        is_in_bounds: bool = pos < len(text)
        is_word_char: bool = is_in_bounds and (
            text[pos].isalnum() or text[pos] == '_'
        )

        return (pos + 1) if is_word_char else -1


# ──────────────────────────────────────────────
# CONCRETE PATTERN: <space>
# ──────────────────────────────────────────────

class SpacePattern(Pattern):
    """
    Custom token <space> — matches ANY single whitespace character.

    Whitespace includes: space ' ', tab '\\t', newline '\\n' etc.
    This is our custom syntax equivalent of \\s in standard regex.

    Example:
        <space> matches ' ', '\\t', '\\n'
        <space> does NOT match 'a', '1', '_'

    Usage in a pattern:
        "hello<space>world" → matches "hello world", "hello\\tworld"
    """

    def __repr__(self) -> str:
        return "SpacePattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at `pos` is whitespace.

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 if whitespace, -1 otherwise.

        Example:
            SpacePattern().match("a b", 1) →  2  ✅ ' ' is whitespace
            SpacePattern().match("a b", 0) → -1  ❌ 'a' is not whitespace
        """
        is_in_bounds: bool = pos < len(text)
        is_space: bool = is_in_bounds and text[pos].isspace()

        return (pos + 1) if is_space else -1


# ──────────────────────────────────────────────
# CONCRETE PATTERN: <any>
# ──────────────────────────────────────────────

class AnyPattern(Pattern):
    """
    Custom token <any> — matches ANY single character, no exceptions.

    This is our custom syntax equivalent of '.' (dot) in standard regex.

    Example:
        <any> matches 'a', '1', ' ', '!', literally anything
        The only thing it can't match is... nothing (empty string / end of text)

    Usage in a pattern:
        "a<any>c" → matches "abc", "a1c", "a c", "a!c" etc.
    """

    def __repr__(self) -> str:
        return "AnyPattern()"

    def match(self, text: str, pos: int) -> int:
        """
        Match any character at `pos` — as long as we're still in bounds.

        Args:
            text (str): The full string being searched.
            pos  (int): Where to look.

        Returns:
            int: pos + 1 if in bounds, -1 if past end of string.

        Example:
            AnyPattern().match("abc", 0) →  1  ✅ 'a' — anything goes
            AnyPattern().match("abc", 2) →  3  ✅ 'c' — anything goes
            AnyPattern().match("abc", 3) → -1  ❌ past end of string
        """
        is_in_bounds: bool = pos < len(text)

        return (pos + 1) if is_in_bounds else -1


# ──────────────────────────────────────────────
# REGISTRY: Token → Pattern class mapping
# ──────────────────────────────────────────────

# This dictionary maps each custom token name (the part inside < >)
# to the Pattern class that handles it.
#
# Why a dict instead of a big if/elif chain?
#   - Adding a new token = adding ONE line here, nothing else changes
#   - Clean, readable, easy to extend
#
# To add a new token e.g. <vowel>:
#   1. Create class VowelPattern(Pattern)
#   2. Add "vowel": VowelPattern to this dict — done!
TOKEN_REGISTRY: dict[str, type[Pattern]] = {
    "int":   IntPattern,    # <int>   → matches digits 0-9
    "word":  WordPattern,   # <word>  → matches letters, digits, underscore
    "alpha": AlphaPattern,  # <alpha> → matches letters only
    "space": SpacePattern,  # <space> → matches whitespace
    "any":   AnyPattern,    # <any>   → matches any single character
}


# ──────────────────────────────────────────────
# PARSER + RUNNER: Matcher
# ──────────────────────────────────────────────

class Matcher:
    """
    The main engine that:
        1. Takes a raw pattern string  e.g. "hello<space><alpha>"
        2. Parses it into Pattern objects using _parse()
        3. Tries to find a match anywhere in the input text

    Supports:
        - Plain literal characters   e.g. "cat"
        - Custom angle-bracket tokens e.g. "<int>", "<word>", "<alpha>"
        - Mixed patterns             e.g. "a<int><alpha>"
    """

    def __init__(self, pattern_str: str) -> None:
        """
        Parse the raw pattern string into a list of Pattern objects.

        Args:
            pattern_str (str): e.g. "hello<int>", "<alpha><space><word>"
        """
        self.patterns: list[Pattern] = self._parse(pattern_str)

    def _parse(self, pattern_str: str) -> list[Pattern]:
        """
        Convert the raw pattern string into a list of Pattern objects.

        Parsing rules:
            1. If we see '<', we read everything up to '>' as a token name.
               Look it up in TOKEN_REGISTRY to get the right Pattern class.
            2. Everything else is treated as a plain LiteralPattern.

        Args:
            pattern_str (str): The raw pattern. e.g. "a<int>b"

        Returns:
            list[Pattern]:
                "a<int>b" → [LiteralPattern('a'), IntPattern(), LiteralPattern('b')]
                "<alpha><space>" → [AlphaPattern(), SpacePattern()]
                "cat" → [LiteralPattern('c'), LiteralPattern('a'), LiteralPattern('t')]

        Raises:
            ValueError: If an unknown token name is used e.g. "<banana>"
            ValueError: If a '<' is never closed with '>'
        """
        patterns: list[Pattern] = []

        # Index-based loop so we can jump forward when we consume a token
        i: int = 0
        while i < len(pattern_str):

            current_char: str = pattern_str[i]

            if current_char == '<':
                # ── We've hit the start of a custom token like <int> ──

                # Find the closing '>' to extract the token name
                closing_bracket: int = pattern_str.find('>', i)

                # If there's no closing '>', the pattern is malformed
                if closing_bracket == -1:
                    raise ValueError(
                        f"Unclosed '<' in pattern at position {i}. "
                        f"Did you forget to close your token with '>'?"
                    )

                # Extract just the name between < and >
                # e.g. "<int>" → "int"
                token_name: str = pattern_str[i + 1 : closing_bracket]

                # Look up the token name in our registry
                if token_name not in TOKEN_REGISTRY:
                    raise ValueError(
                        f"Unknown token '<{token_name}>'. "
                        f"Available tokens: {list(TOKEN_REGISTRY.keys())}"
                    )

                # Instantiate the correct Pattern class and add it to the list
                pattern_class: type[Pattern] = TOKEN_REGISTRY[token_name]
                patterns.append(pattern_class())

                # Jump past the entire token  e.g. past "<int>" (5 chars)
                i = closing_bracket + 1

            else:
                # ── Plain literal character ──
                patterns.append(LiteralPattern(current_char))
                i += 1

        return patterns

    def match(self, text: str) -> bool:
        """
        Try to find a match for our pattern sequence ANYWHERE in `text`.

        Sliding window strategy:
            Try every starting position. At each one, attempt to match
            ALL patterns in sequence. First full match → return True.
            Exhausted all positions → return False.

        Args:
            text (str): The full input string to search through.

        Returns:
            bool: True if the pattern matched anywhere, False otherwise.
        """
        for start in range(len(text)):

            pos: int = start

            for pattern in self.patterns:
                pos = pattern.match(text, pos)
                if pos == -1:
                    break  # ❌ failed at this start position

            else:
                return True  # ✅ all patterns matched!

        return False


# ──────────────────────────────────────────────
# ARGUMENT PARSER
# ──────────────────────────────────────────────

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser.

    Returns:
        argparse.ArgumentParser: ready to parse CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            "A custom regex engine with angle-bracket token syntax.\n"
            "Supported tokens: <int> <alpha> <word> <space> <any>\n"
            "Example: echo 'hello 1' | python app/main.py -E 'hello<space><int>'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-E", "--extended-regexp",
        required=True,
        metavar="PATTERN",
        dest="pattern",
        help=(
            "Pattern to search for. "
            "Use <int>, <alpha>, <word>, <space>, <any> as special tokens. "
            "Everything else is treated as a literal character."
        ),
    )

    return parser


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

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
    input_text: str = sys.stdin.read()

    try:
        matcher: Matcher = Matcher(pattern_str)
    except ValueError as e:
        # Bad pattern syntax — print the error and exit with code 2
        print(f"Error in pattern: {e}", file=sys.stderr)
        sys.exit(2)

    found: bool = matcher.match(input_text)

    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()