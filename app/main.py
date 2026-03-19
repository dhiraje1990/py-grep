import sys
import argparse


# ──────────────────────────────────────────────
# BASE CLASS
# ──────────────────────────────────────────────

class Pattern:
    """
    The base class for ALL pattern types.

    Think of a Pattern as a single "rule" that knows how to check
    one thing in the text — like "is this character the letter 'a'?"

    Every pattern must implement the `match` method.
    """

    def match(self, text: str, pos: int) -> int:
        """
        Try to match this pattern at position `pos` inside `text`.

        Args:
            text (str): The full input string we are searching through.
                        e.g. "hello world"
            pos  (int): The current index (position) in the string
                        where we should try to match.
                        e.g. 0 means "start at the first character"

        Returns:
            int: If the match SUCCEEDS → return the next position
                 (i.e. pos + how many characters we consumed).

                 If the match FAILS → return -1 as a signal for failure.

        Example:
            text = "apple", pos = 0
            If this pattern matches 'a', it returns 1 (moved forward by 1).
            If this pattern matches 'z', it returns -1 (no match).
        """
        raise NotImplementedError(
            # Every subclass MUST override this method.
            # If they forget, Python will raise this error to remind them.
            "Each Pattern subclass must implement its own match() method."
        )


# ──────────────────────────────────────────────
# CONCRETE PATTERN: Literal Character
# ──────────────────────────────────────────────

class LiteralPattern(Pattern):
    """
    Matches ONE specific character — exactly as written.

    Example:
        LiteralPattern('a') will only match the letter 'a'.
        It will NOT match 'b', 'A', '1', etc.

    Used when the pattern is a plain character like:
        grep -E "a"   →  LiteralPattern('a')
        grep -E "cat" →  [LiteralPattern('c'), LiteralPattern('a'), LiteralPattern('t')]
    """

    def __init__(self, char: str) -> None:
        """
        Store the character this pattern should match.

        Args:
            char (str): A single character to look for in the text.
                        e.g. 'a', 'z', '9', '!'
        """
        # Save the character so we can use it later in match()
        self.char: str = char

    def match(self, text: str, pos: int) -> int:
        """
        Check if the character at position `pos` in `text` equals self.char.

        Steps:
            1. Make sure `pos` is still inside the string (not past the end).
            2. Compare the character at that position with self.char.
            3. If they match → return pos + 1 (advance by 1 character).
            4. If they don't → return -1 (signal failure).

        Args:
            text (str): The full string being searched. e.g. "apple"
            pos  (int): Where to look in the string.   e.g. 0 → 'a'

        Returns:
            int: pos + 1 on success, -1 on failure.

        Example:
            pattern = LiteralPattern('a')
            pattern.match("apple", 0)  →  1   ✅ 'a' == 'a'
            pattern.match("apple", 1)  → -1   ❌ 'p' != 'a'
            pattern.match("apple", 99) → -1   ❌ pos is out of bounds
        """
        # Guard: make sure we haven't walked past the end of the string
        is_in_bounds: bool = pos < len(text)

        # Check: does the character at this position match what we want?
        is_matching_char: bool = is_in_bounds and (text[pos] == self.char)

        if is_matching_char:
            # ✅ Match found! Move forward by 1 position.
            return pos + 1
        else:
            # ❌ No match. Return -1 to signal failure.
            return -1


# ──────────────────────────────────────────────
# PARSER + RUNNER: Matcher
# ──────────────────────────────────────────────

class Matcher:
    """
    The main engine that:
        1. Takes a raw pattern string (e.g. "cat")
        2. Parses it into a list of Pattern objects
        3. Tries to find a match anywhere inside the input text

    Think of Matcher like a conductor:
        - It reads the sheet music (the pattern string)
        - Turns each note into a Pattern object
        - Then plays them in sequence against the text

    Example:
        Matcher("cat") creates:
            [LiteralPattern('c'), LiteralPattern('a'), LiteralPattern('t')]

        Then tries to find "cat" anywhere in the input string.
    """

    def __init__(self, pattern_str: str) -> None:
        """
        Parse the raw pattern string into a list of Pattern objects.

        Args:
            pattern_str (str): The grep pattern as a plain string.
                               e.g. "cat", "a", "hello"
        """
        # Parse the pattern string and store the resulting list of Pattern objects.
        # Each character in the pattern becomes one Pattern object.
        self.patterns: list[Pattern] = self._parse(pattern_str)

    def _parse(self, pattern_str: str) -> list[Pattern]:
        """
        Convert the raw pattern string into a list of Pattern objects.

        Right now we only support literal characters, so every character
        in the pattern string becomes a LiteralPattern.

        As we add more stages (like \\d for digits), this method will grow
        to detect special sequences and create the right Pattern subclass.

        Args:
            pattern_str (str): The raw pattern. e.g. "cat"

        Returns:
            list[Pattern]: One Pattern object per character (for now).
                           e.g. "cat" → [LiteralPattern('c'),
                                         LiteralPattern('a'),
                                         LiteralPattern('t')]
        """
        # This will hold all the Pattern objects we build
        patterns: list[Pattern] = []

        # Walk through each character in the pattern string one by one
        for ch in pattern_str:
            # For now, every character is treated as a literal match
            patterns.append(LiteralPattern(ch))

        return patterns

    def match(self, text: str) -> bool:
        """
        Try to find a match for our pattern sequence ANYWHERE in `text`.

        Strategy (sliding window):
            We try every possible starting position in the text.
            At each starting position, we attempt to match ALL patterns
            in order. If ALL succeed → we found a match!
            If ANY pattern fails → we slide the window one step forward
            and try again from the next character.

        Args:
            text (str): The full input string to search through.
                        e.g. "I have a cat at home"

        Returns:
            bool: True if the pattern was found anywhere, False otherwise.

        Example:
            patterns = [LiteralPattern('c'), LiteralPattern('a'), LiteralPattern('t')]
            text = "I have a cat at home"

            Start=0  → 'I' vs 'c' → ❌ fail, move on
            Start=1  → ' ' vs 'c' → ❌ fail, move on
            ...
            Start=9  → 'c' vs 'c' → ✅, 'a' vs 'a' → ✅, 't' vs 't' → ✅ → MATCH!
        """
        # Try every starting position in the text
        for start in range(len(text)):

            # `pos` tracks where we currently are as we match each pattern
            pos: int = start

            # Try to match every pattern in our list, one by one
            for pattern in self.patterns:
                pos = pattern.match(text, pos)

                # If any single pattern fails, stop trying from this start position
                if pos == -1:
                    break  # ❌ This starting position didn't work

            else:
                # This `else` belongs to the `for` loop above.
                # It runs ONLY if the loop completed WITHOUT hitting `break`.
                # That means ALL patterns matched successfully! 🎉
                return True

        # If we tried every starting position and never got a full match → False
        return False


# ──────────────────────────────────────────────
# ARGUMENT PARSER
# ──────────────────────────────────────────────

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser for our grep program.

    argparse is Python's built-in library for handling command-line arguments.
    It automatically generates help messages, validates inputs, and gives us
    clean named attributes instead of raw sys.argv index juggling.

    Think of it like a receptionist:
        - You tell it what arguments to expect
        - It reads what the user typed
        - It hands you back a neat object with everything labelled

    Returns:
        argparse.ArgumentParser: A configured parser ready to parse arguments.

    Example CLI usage this supports:
        python app/main.py -E "cat"
        python app/main.py --extended-regexp "cat"
        python app/main.py --help   ← argparse generates this automatically!
    """
    # Create the parser with a helpful description shown in --help output
    parser = argparse.ArgumentParser(
        description=(
            "A minimal grep implementation built from scratch. "
            "Searches stdin for lines matching the given pattern."
        ),
        # Show default values in --help output automatically
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add the -E / --extended-regexp flag.
    # This is the flag real grep uses to indicate "extended regex" mode.
    # For us, it's how the user passes in their pattern.
    #
    # required=True  → the user MUST provide this flag; argparse errors if missing
    # metavar        → the placeholder name shown in --help (e.g. "PATTERN")
    # help           → the description shown next to the flag in --help
    parser.add_argument(
        "-E", "--extended-regexp",   # accepts both -E and --extended-regexp
        required=True,               # cannot run without a pattern
        metavar="PATTERN",           # shown in help as: -E PATTERN
        dest="pattern",              # stored as args.pattern (clean attribute name)
        help="The pattern to search for in the input text.",
    )

    return parser


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

def main() -> None:
    """
    The entry point of our grep program.

    What it does:
        1. Uses argparse to cleanly parse command-line arguments
        2. Reads the input text from stdin (piped in via echo)
        3. Uses Matcher to check if the pattern appears in the input
        4. Exits with code 0 (found) or 1 (not found) — standard Unix convention

    Expected usage:
        echo "apple" | python app/main.py -E "a"

    Exit codes (Unix convention):
        0 → pattern found       ✅
        1 → pattern not found   ❌
        2 → bad usage / error   ⚠️  (argparse handles this automatically)
    """
    # Build the argument parser (defines what flags/args we accept)
    parser: argparse.ArgumentParser = build_arg_parser()

    # Actually parse what the user typed on the command line.
    # If required args are missing or unknown flags are used,
    # argparse will automatically print a helpful error and exit with code 2.
    args: argparse.Namespace = parser.parse_args()

    # args.pattern now holds the string the user passed after -E
    # e.g. if user ran: python app/main.py -E "cat"
    #      then args.pattern == "cat"
    pattern_str: str = args.pattern

    # Read ALL of stdin into one string.
    # This is the text that was piped in, e.g.: echo "apple" | ...
    input_text: str = sys.stdin.read()

    # Build a Matcher from the pattern string.
    # This parses the pattern into Pattern objects internally.
    matcher: Matcher = Matcher(pattern_str)

    # Ask the matcher whether the pattern appears anywhere in the input
    found: bool = matcher.match(input_text)

    if found:
        sys.exit(0)  # ✅ Pattern found → exit 0 (success)
    else:
        sys.exit(1)  # ❌ Pattern not found → exit 1 (no match)


# Only run main() if this file is executed directly (not imported as a module)
if __name__ == "__main__":
    main()