import pytest

# Import the classes we want to test directly
from app.main import LiteralPattern, Matcher


# ──────────────────────────────────────────────
# Tests for LiteralPattern
# ──────────────────────────────────────────────

class TestLiteralPattern:
    """Tests for the LiteralPattern class."""

    def test_match_succeeds_when_char_matches(self) -> None:
        """'a' pattern should match 'a' at position 0."""
        pattern = LiteralPattern('a')
        result: int = pattern.match("apple", 0)
        assert result == 1  # moved forward by 1

    def test_match_fails_when_char_differs(self) -> None:
        """'a' pattern should NOT match 'p'."""
        pattern = LiteralPattern('a')
        result: int = pattern.match("apple", 1)  # pos 1 is 'p'
        assert result == -1

    def test_match_fails_when_pos_out_of_bounds(self) -> None:
        """Should return -1 when pos is past the end of the string."""
        pattern = LiteralPattern('a')
        result: int = pattern.match("apple", 99)
        assert result == -1

    def test_match_at_last_character(self) -> None:
        """Should correctly match at the very last character."""
        pattern = LiteralPattern('e')
        result: int = pattern.match("apple", 4)  # pos 4 is 'e'
        assert result == 5

    def test_match_is_case_sensitive(self) -> None:
        """'a' should NOT match 'A' — grep is case sensitive by default."""
        pattern = LiteralPattern('a')
        result: int = pattern.match("Apple", 0)  # pos 0 is 'A'
        assert result == -1


# ──────────────────────────────────────────────
# Tests for Matcher
# ──────────────────────────────────────────────

class TestMatcher:
    """Tests for the Matcher class (the full engine)."""

    def test_single_char_found(self) -> None:
        """Pattern 'a' should be found in 'apple'."""
        matcher = Matcher("a")
        assert matcher.match("apple") is True

    def test_single_char_not_found(self) -> None:
        """Pattern 'z' should NOT be found in 'apple'."""
        matcher = Matcher("z")
        assert matcher.match("apple") is False

    def test_multi_char_pattern_found(self) -> None:
        """Pattern 'cat' should be found in 'I have a cat'."""
        matcher = Matcher("cat")
        assert matcher.match("I have a cat") is True

    def test_multi_char_pattern_not_found(self) -> None:
        """Pattern 'cat' should NOT be found in 'I have a dog'."""
        matcher = Matcher("cat")
        assert matcher.match("I have a dog") is False

    def test_pattern_at_start(self) -> None:
        """Pattern found at the very beginning of the string."""
        matcher = Matcher("app")
        assert matcher.match("apple") is True

    def test_pattern_at_end(self) -> None:
        """Pattern found at the very end of the string."""
        matcher = Matcher("ple")
        assert matcher.match("apple") is True

    def test_empty_text(self) -> None:
        """Nothing can be found in an empty string."""
        matcher = Matcher("a")
        assert matcher.match("") is False

    def test_pattern_longer_than_text(self) -> None:
        """Pattern longer than text can never match."""
        matcher = Matcher("toolongpattern")
        assert matcher.match("hi") is False