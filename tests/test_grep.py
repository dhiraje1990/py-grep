import pytest
from app.main import (
    LiteralPattern,
    IntPattern,
    AlphaPattern,
    WordPattern,
    SpacePattern,
    AnyPattern,
    Matcher,
)


# ══════════════════════════════════════════════
# LiteralPattern Tests
# ══════════════════════════════════════════════

class TestLiteralPattern:
    """
    Tests for LiteralPattern — matches one exact character.

    Rule: LiteralPattern('x') should ONLY match the character 'x'.
    """

    def test_matches_correct_char(self) -> None:
        """'a' pattern at pos 0 of 'apple' should match and return 1."""
        assert LiteralPattern('a').match("apple", 0) == 1

    def test_fails_on_wrong_char(self) -> None:
        """'a' pattern at pos 1 of 'apple' ('p') should fail."""
        assert LiteralPattern('a').match("apple", 1) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        """Any pattern should return -1 when pos is past the string."""
        assert LiteralPattern('a').match("apple", 99) == -1

    def test_matches_at_last_position(self) -> None:
        """Should correctly match the very last character in the string."""
        assert LiteralPattern('e').match("apple", 4) == 5

    def test_is_case_sensitive(self) -> None:
        """'a' should NOT match 'A' — matching is case sensitive."""
        assert LiteralPattern('a').match("Apple", 0) == -1

    def test_matches_digit_as_literal(self) -> None:
        """LiteralPattern('3') should match the character '3'."""
        assert LiteralPattern('3').match("abc3", 3) == 4

    def test_matches_special_char(self) -> None:
        """LiteralPattern('!') should match '!' literally."""
        assert LiteralPattern('!').match("hi!", 2) == 3

    def test_fails_on_empty_string(self) -> None:
        """Matching against an empty string should always return -1."""
        assert LiteralPattern('a').match("", 0) == -1


# ══════════════════════════════════════════════
# IntPattern Tests  →  <int>
# ══════════════════════════════════════════════

class TestIntPattern:
    """
    Tests for IntPattern — matches any single digit (0-9).

    Token: <int>
    Rule: matches '0' through '9', nothing else.
    """

    def test_matches_digit_1(self) -> None:
        """Should match '1' at pos 3 of 'abc1'."""
        assert IntPattern().match("abc1", 3) == 4

    def test_matches_digit_0(self) -> None:
        """Should match '0' — the smallest digit."""
        assert IntPattern().match("0", 0) == 1

    def test_matches_digit_9(self) -> None:
        """Should match '9' — the largest digit."""
        assert IntPattern().match("9", 0) == 1

    def test_fails_on_letter(self) -> None:
        """'a' is not a digit — should return -1."""
        assert IntPattern().match("abc", 0) == -1

    def test_fails_on_space(self) -> None:
        """A space is not a digit — should return -1."""
        assert IntPattern().match(" 1", 0) == -1

    def test_fails_on_underscore(self) -> None:
        """'_' is not a digit — should return -1."""
        assert IntPattern().match("_1", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        """Should return -1 when pos is past end of string."""
        assert IntPattern().match("123", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        """Matching against empty string should return -1."""
        assert IntPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# AlphaPattern Tests  →  <alpha>
# ══════════════════════════════════════════════

class TestAlphaPattern:
    """
    Tests for AlphaPattern — matches any single letter (a-z or A-Z).

    Token: <alpha>
    Rule: letters only — digits, spaces, symbols all fail.
    """

    def test_matches_lowercase_letter(self) -> None:
        """Should match lowercase 'a'."""
        assert AlphaPattern().match("abc", 0) == 1

    def test_matches_uppercase_letter(self) -> None:
        """Should match uppercase 'Z'."""
        assert AlphaPattern().match("Z", 0) == 1

    def test_fails_on_digit(self) -> None:
        """'1' is not a letter — should return -1."""
        assert AlphaPattern().match("1bc", 0) == -1

    def test_fails_on_space(self) -> None:
        """A space is not a letter — should return -1."""
        assert AlphaPattern().match(" a", 0) == -1

    def test_fails_on_underscore(self) -> None:
        """'_' is not a letter — should return -1."""
        assert AlphaPattern().match("_a", 0) == -1

    def test_fails_on_special_char(self) -> None:
        """'!' is not a letter — should return -1."""
        assert AlphaPattern().match("!", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        """Should return -1 when pos is past end of string."""
        assert AlphaPattern().match("abc", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        """Matching against empty string should return -1."""
        assert AlphaPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# WordPattern Tests  →  <word>
# ══════════════════════════════════════════════

class TestWordPattern:
    """
    Tests for WordPattern — matches letters, digits, or underscore.

    Token: <word>
    Rule: isalnum() OR '_' — spaces, symbols all fail.
    """

    def test_matches_letter(self) -> None:
        """'a' is a word character — should match."""
        assert WordPattern().match("a", 0) == 1

    def test_matches_digit(self) -> None:
        """'5' is a word character — should match."""
        assert WordPattern().match("5", 0) == 1

    def test_matches_underscore(self) -> None:
        """'_' is a word character — should match."""
        assert WordPattern().match("_", 0) == 1

    def test_matches_uppercase(self) -> None:
        """'Z' is a word character — should match."""
        assert WordPattern().match("Z", 0) == 1

    def test_fails_on_space(self) -> None:
        """Space is NOT a word character — should return -1."""
        assert WordPattern().match(" a", 0) == -1

    def test_fails_on_exclamation(self) -> None:
        """'!' is NOT a word character — should return -1."""
        assert WordPattern().match("!", 0) == -1

    def test_fails_on_hyphen(self) -> None:
        """'-' is NOT a word character — should return -1."""
        assert WordPattern().match("-", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        """Should return -1 when pos is past end of string."""
        assert WordPattern().match("abc", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        """Matching against empty string should return -1."""
        assert WordPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# SpacePattern Tests  →  <space>
# ══════════════════════════════════════════════

class TestSpacePattern:
    """
    Tests for SpacePattern — matches any whitespace character.

    Token: <space>
    Rule: matches ' ', '\\t', '\\n' etc. — anything isspace() returns True for.
    """

    def test_matches_space(self) -> None:
        """A regular space should match."""
        assert SpacePattern().match(" ", 0) == 1

    def test_matches_tab(self) -> None:
        """A tab character should match."""
        assert SpacePattern().match("\t", 0) == 1

    def test_matches_newline(self) -> None:
        """A newline character should match."""
        assert SpacePattern().match("\n", 0) == 1

    def test_matches_space_in_middle(self) -> None:
        """Should match space at pos 5 in 'hello world'."""
        assert SpacePattern().match("hello world", 5) == 6

    def test_fails_on_letter(self) -> None:
        """'a' is not whitespace — should return -1."""
        assert SpacePattern().match("a b", 0) == -1

    def test_fails_on_digit(self) -> None:
        """'1' is not whitespace — should return -1."""
        assert SpacePattern().match("1 2", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        """Should return -1 when pos is past end of string."""
        assert SpacePattern().match("   ", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        """Matching against empty string should return -1."""
        assert SpacePattern().match("", 0) == -1


# ══════════════════════════════════════════════
# AnyPattern Tests  →  <any>
# ══════════════════════════════════════════════

class TestAnyPattern:
    """
    Tests for AnyPattern — matches ANY single character.

    Token: <any>
    Rule: always succeeds as long as pos is within bounds.
    """

    def test_matches_letter(self) -> None:
        """Should match a letter."""
        assert AnyPattern().match("abc", 0) == 1

    def test_matches_digit(self) -> None:
        """Should match a digit."""
        assert AnyPattern().match("123", 0) == 1

    def test_matches_space(self) -> None:
        """Should match a space."""
        assert AnyPattern().match(" ", 0) == 1

    def test_matches_special_char(self) -> None:
        """Should match '!' — anything goes."""
        assert AnyPattern().match("!", 0) == 1

    def test_matches_last_character(self) -> None:
        """Should match the very last character in the string."""
        assert AnyPattern().match("abc", 2) == 3

    def test_fails_when_out_of_bounds(self) -> None:
        """Should return -1 when pos equals len(text) — nothing left."""
        assert AnyPattern().match("abc", 3) == -1

    def test_fails_on_empty_string(self) -> None:
        """Matching against empty string should return -1."""
        assert AnyPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# Matcher._parse() Tests
# ══════════════════════════════════════════════

class TestMatcherParse:
    """
    Tests for Matcher._parse() — the pattern string parser.

    Checks that the right Pattern objects are created from a pattern string.
    We use repr() to verify the type of each parsed pattern cleanly.
    """

    def test_parses_literal_chars(self) -> None:
        """'cat' should produce 3 LiteralPattern objects."""
        m = Matcher("cat")
        assert len(m.patterns) == 3
        assert all(isinstance(p, LiteralPattern) for p in m.patterns)

    def test_parses_int_token(self) -> None:
        """'<int>' should produce one IntPattern."""
        m = Matcher("<int>")
        assert len(m.patterns) == 1
        assert isinstance(m.patterns[0], IntPattern)

    def test_parses_alpha_token(self) -> None:
        """'<alpha>' should produce one AlphaPattern."""
        m = Matcher("<alpha>")
        assert len(m.patterns) == 1
        assert isinstance(m.patterns[0], AlphaPattern)

    def test_parses_word_token(self) -> None:
        """'<word>' should produce one WordPattern."""
        m = Matcher("<word>")
        assert len(m.patterns) == 1
        assert isinstance(m.patterns[0], WordPattern)

    def test_parses_space_token(self) -> None:
        """'<space>' should produce one SpacePattern."""
        m = Matcher("<space>")
        assert len(m.patterns) == 1
        assert isinstance(m.patterns[0], SpacePattern)

    def test_parses_any_token(self) -> None:
        """'<any>' should produce one AnyPattern."""
        m = Matcher("<any>")
        assert len(m.patterns) == 1
        assert isinstance(m.patterns[0], AnyPattern)

    def test_parses_mixed_pattern(self) -> None:
        """'a<int>b' should produce [Literal, Int, Literal]."""
        m = Matcher("a<int>b")
        assert len(m.patterns) == 3
        assert isinstance(m.patterns[0], LiteralPattern)
        assert isinstance(m.patterns[1], IntPattern)
        assert isinstance(m.patterns[2], LiteralPattern)

    def test_raises_on_unknown_token(self) -> None:
        """'<banana>' should raise a ValueError — not in registry."""
        with pytest.raises(ValueError, match="Unknown token"):
            Matcher("<banana>")

    def test_raises_on_unclosed_bracket(self) -> None:
        """'<int' (no closing '>') should raise a ValueError."""
        with pytest.raises(ValueError, match="Unclosed '<'"):
            Matcher("<int")


# ══════════════════════════════════════════════
# Matcher.match() Tests — Literals
# ══════════════════════════════════════════════

class TestMatcherLiterals:
    """
    End-to-end tests for Matcher using plain literal patterns.
    """

    def test_single_char_found(self) -> None:
        """'a' should be found in 'apple'."""
        assert Matcher("a").match("apple") is True

    def test_single_char_not_found(self) -> None:
        """'z' should NOT be found in 'apple'."""
        assert Matcher("z").match("apple") is False

    def test_multi_char_found(self) -> None:
        """'cat' should be found in 'I have a cat'."""
        assert Matcher("cat").match("I have a cat") is True

    def test_multi_char_not_found(self) -> None:
        """'cat' should NOT be found in 'I have a dog'."""
        assert Matcher("cat").match("I have a dog") is False

    def test_pattern_at_start(self) -> None:
        """Pattern found at the beginning of the string."""
        assert Matcher("app").match("apple") is True

    def test_pattern_at_end(self) -> None:
        """Pattern found at the end of the string."""
        assert Matcher("ple").match("apple") is True

    def test_empty_text(self) -> None:
        """Nothing should be found in an empty string."""
        assert Matcher("a").match("") is False

    def test_pattern_longer_than_text(self) -> None:
        """A pattern longer than the text can never match."""
        assert Matcher("toolongpattern").match("hi") is False


# ══════════════════════════════════════════════
# Matcher.match() Tests — <int>
# ══════════════════════════════════════════════

class TestMatcherInt:
    """
    End-to-end tests for Matcher using <int> token.
    """

    def test_int_found_in_mixed_string(self) -> None:
        """<int> should find a digit in 'abc123'."""
        assert Matcher("<int>").match("abc123") is True

    def test_int_not_found_in_all_letters(self) -> None:
        """<int> should NOT match 'abcdef' — no digits."""
        assert Matcher("<int>").match("abcdef") is False

    def test_literal_then_int(self) -> None:
        """'a<int>' should match 'a' followed by any digit."""
        assert Matcher("a<int>").match("a1") is True
        assert Matcher("a<int>").match("a9") is True
        assert Matcher("a<int>").match("ab") is False

    def test_int_then_literal(self) -> None:
        """'<int>!' should match a digit followed by '!'."""
        assert Matcher("<int>!").match("3!") is True
        assert Matcher("<int>!").match("a!") is False

    def test_multiple_ints(self) -> None:
        """'<int><int>' should match two consecutive digits."""
        assert Matcher("<int><int>").match("42") is True
        assert Matcher("<int><int>").match("4a") is False


# ══════════════════════════════════════════════
# Matcher.match() Tests — <alpha>
# ══════════════════════════════════════════════

class TestMatcherAlpha:
    """
    End-to-end tests for Matcher using <alpha> token.
    """

    def test_alpha_found_in_word(self) -> None:
        """<alpha> should match any letter in 'hello'."""
        assert Matcher("<alpha>").match("hello") is True

    def test_alpha_not_found_in_digits(self) -> None:
        """<alpha> should NOT match '12345' — no letters."""
        assert Matcher("<alpha>").match("12345") is False

    def test_alpha_then_int(self) -> None:
        """'<alpha><int>' should match a letter followed by a digit."""
        assert Matcher("<alpha><int>").match("a1") is True
        assert Matcher("<alpha><int>").match("Z9") is True
        assert Matcher("<alpha><int>").match("11") is False

    def test_alpha_not_matching_underscore(self) -> None:
        """<alpha> should NOT match '_' — underscore is not a letter."""
        assert Matcher("<alpha>").match("_") is False


# ══════════════════════════════════════════════
# Matcher.match() Tests — <word>
# ══════════════════════════════════════════════

class TestMatcherWord:
    """
    End-to-end tests for Matcher using <word> token.
    """

    def test_word_matches_letter(self) -> None:
        """<word> should match a letter."""
        assert Matcher("<word>").match("hello") is True

    def test_word_matches_digit(self) -> None:
        """<word> should match a digit."""
        assert Matcher("<word>").match("123") is True

    def test_word_matches_underscore(self) -> None:
        """<word> should match underscore."""
        assert Matcher("<word>").match("_var") is True

    def test_word_not_found_in_symbols(self) -> None:
        """<word> should NOT match '!!! ...' — no word characters."""
        assert Matcher("<word>").match("!!! ...") is False

    def test_word_sequence(self) -> None:
        """'<word><word><word>' should match any 3 consecutive word chars."""
        assert Matcher("<word><word><word>").match("abc") is True
        assert Matcher("<word><word><word>").match("a_1") is True
        assert Matcher("<word><word><word>").match("a! ") is False


# ══════════════════════════════════════════════
# Matcher.match() Tests — <space>
# ══════════════════════════════════════════════

class TestMatcherSpace:
    """
    End-to-end tests for Matcher using <space> token.
    """

    def test_space_found(self) -> None:
        """<space> should find the space in 'hello world'."""
        assert Matcher("<space>").match("hello world") is True

    def test_space_not_found(self) -> None:
        """<space> should NOT match 'helloworld' — no whitespace."""
        assert Matcher("<space>").match("helloworld") is False

    def test_word_space_word(self) -> None:
        """'hello<space>world' should match 'hello world'."""
        assert Matcher("hello<space>world").match("hello world") is True
        assert Matcher("hello<space>world").match("helloworld") is False

    def test_space_matches_tab(self) -> None:
        """<space> should match a tab character."""
        assert Matcher("<space>").match("a\tb") is True


# ══════════════════════════════════════════════
# Matcher.match() Tests — <any>
# ══════════════════════════════════════════════

class TestMatcherAny:
    """
    End-to-end tests for Matcher using <any> token.
    """

    def test_any_matches_letter(self) -> None:
        """<any> should match a letter."""
        assert Matcher("<any>").match("a") is True

    def test_any_matches_digit(self) -> None:
        """<any> should match a digit."""
        assert Matcher("<any>").match("1") is True

    def test_any_matches_symbol(self) -> None:
        """<any> should match any symbol."""
        assert Matcher("<any>").match("!") is True

    def test_any_not_matching_empty(self) -> None:
        """<any> should NOT match an empty string."""
        assert Matcher("<any>").match("") is False

    def test_any_as_wildcard(self) -> None:
        """'a<any>c' should match 'abc', 'a1c', 'a!c' etc."""
        assert Matcher("a<any>c").match("abc") is True
        assert Matcher("a<any>c").match("a1c") is True
        assert Matcher("a<any>c").match("a!c") is True
        assert Matcher("a<any>c").match("ac")  is False  # nothing between a and c


# ══════════════════════════════════════════════
# Matcher.match() Tests — Complex Mixed Patterns
# ══════════════════════════════════════════════

class TestMatcherMixed:
    """
    End-to-end tests using combinations of multiple token types.
    These simulate real-world usage of the custom regex engine.
    """

    def test_alpha_space_int(self) -> None:
        """'<alpha><space><int>' should match a letter, space, then digit."""
        assert Matcher("<alpha><space><int>").match("a 1") is True
        assert Matcher("<alpha><space><int>").match("a 9") is True
        assert Matcher("<alpha><space><int>").match("1 a") is False

    def test_word_with_literals(self) -> None:
        """'hello<space><word>' should match 'hello ' followed by a word char."""
        assert Matcher("hello<space><word>").match("hello world") is True
        assert Matcher("hello<space><word>").match("hello !!!!") is False

    def test_any_between_literals(self) -> None:
        """'c<any>t' should match 'cat', 'c1t', 'c t' etc."""
        assert Matcher("c<any>t").match("cat") is True
        assert Matcher("c<any>t").match("c1t") is True
        assert Matcher("c<any>t").match("ct")  is False

    def test_all_tokens_combined(self) -> None:
        """A pattern using all 5 tokens together."""
        # Pattern: one digit, space, one letter, one word char, any char
        pattern = "<int><space><alpha><word><any>"
        assert Matcher(pattern).match("1 ab!") is True
        assert Matcher(pattern).match("1 a1!") is True
        assert Matcher(pattern).match("a 1b!") is False  # starts with letter not digit

    def test_pattern_found_in_middle_of_text(self) -> None:
        """Pattern should be found even if it's in the middle of a long string."""
        assert Matcher("<int><int><int>").match("price is 500 dollars") is True

    def test_pattern_not_found_in_long_text(self) -> None:
        """Pattern should correctly fail when not present in long text."""
        assert Matcher("<int><int><int>").match("no numbers here at all") is False