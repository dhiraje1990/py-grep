import pytest
from app.main import (
    LiteralPattern,
    IntPattern,
    AlphaPattern,
    WordPattern,
    SpacePattern,
    AnyPattern,
    CharGroupPattern,
    RepeatPattern,
    Matcher,
)


# ══════════════════════════════════════════════
# LiteralPattern
# ══════════════════════════════════════════════

class TestLiteralPattern:
    def test_matches_correct_char(self) -> None:
        assert LiteralPattern('a').match("apple", 0) == 1

    def test_fails_on_wrong_char(self) -> None:
        assert LiteralPattern('a').match("apple", 1) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        assert LiteralPattern('a').match("apple", 99) == -1

    def test_matches_at_last_position(self) -> None:
        assert LiteralPattern('e').match("apple", 4) == 5

    def test_is_case_sensitive(self) -> None:
        assert LiteralPattern('a').match("Apple", 0) == -1

    def test_matches_digit_as_literal(self) -> None:
        assert LiteralPattern('3').match("abc3", 3) == 4

    def test_matches_special_char(self) -> None:
        assert LiteralPattern('!').match("hi!", 2) == 3

    def test_fails_on_empty_string(self) -> None:
        assert LiteralPattern('a').match("", 0) == -1


# ══════════════════════════════════════════════
# IntPattern  →  <int>
# ══════════════════════════════════════════════

class TestIntPattern:
    def test_matches_digit_1(self) -> None:
        assert IntPattern().match("abc1", 3) == 4

    def test_matches_digit_0(self) -> None:
        assert IntPattern().match("0", 0) == 1

    def test_matches_digit_9(self) -> None:
        assert IntPattern().match("9", 0) == 1

    def test_fails_on_letter(self) -> None:
        assert IntPattern().match("abc", 0) == -1

    def test_fails_on_space(self) -> None:
        assert IntPattern().match(" 1", 0) == -1

    def test_fails_on_underscore(self) -> None:
        assert IntPattern().match("_1", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        assert IntPattern().match("123", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        assert IntPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# AlphaPattern  →  <alpha>
# ══════════════════════════════════════════════

class TestAlphaPattern:
    def test_matches_lowercase(self) -> None:
        assert AlphaPattern().match("abc", 0) == 1

    def test_matches_uppercase(self) -> None:
        assert AlphaPattern().match("Z", 0) == 1

    def test_fails_on_digit(self) -> None:
        assert AlphaPattern().match("1bc", 0) == -1

    def test_fails_on_space(self) -> None:
        assert AlphaPattern().match(" a", 0) == -1

    def test_fails_on_underscore(self) -> None:
        assert AlphaPattern().match("_a", 0) == -1

    def test_fails_on_special_char(self) -> None:
        assert AlphaPattern().match("!", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        assert AlphaPattern().match("abc", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        assert AlphaPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# WordPattern  →  <word>
# ══════════════════════════════════════════════

class TestWordPattern:
    def test_matches_letter(self) -> None:
        assert WordPattern().match("a", 0) == 1

    def test_matches_digit(self) -> None:
        assert WordPattern().match("5", 0) == 1

    def test_matches_underscore(self) -> None:
        assert WordPattern().match("_", 0) == 1

    def test_matches_uppercase(self) -> None:
        assert WordPattern().match("Z", 0) == 1

    def test_fails_on_space(self) -> None:
        assert WordPattern().match(" a", 0) == -1

    def test_fails_on_exclamation(self) -> None:
        assert WordPattern().match("!", 0) == -1

    def test_fails_on_hyphen(self) -> None:
        assert WordPattern().match("-", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        assert WordPattern().match("abc", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        assert WordPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# SpacePattern  →  <space>
# ══════════════════════════════════════════════

class TestSpacePattern:
    def test_matches_space(self) -> None:
        assert SpacePattern().match(" ", 0) == 1

    def test_matches_tab(self) -> None:
        assert SpacePattern().match("\t", 0) == 1

    def test_matches_newline(self) -> None:
        assert SpacePattern().match("\n", 0) == 1

    def test_matches_space_in_middle(self) -> None:
        assert SpacePattern().match("hello world", 5) == 6

    def test_fails_on_letter(self) -> None:
        assert SpacePattern().match("a b", 0) == -1

    def test_fails_on_digit(self) -> None:
        assert SpacePattern().match("1 2", 0) == -1

    def test_fails_when_out_of_bounds(self) -> None:
        assert SpacePattern().match("   ", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        assert SpacePattern().match("", 0) == -1


# ══════════════════════════════════════════════
# AnyPattern  →  <_>
# ══════════════════════════════════════════════

class TestAnyPattern:
    def test_matches_letter(self) -> None:
        assert AnyPattern().match("abc", 0) == 1

    def test_matches_digit(self) -> None:
        assert AnyPattern().match("123", 0) == 1

    def test_matches_space(self) -> None:
        assert AnyPattern().match(" ", 0) == 1

    def test_matches_special_char(self) -> None:
        assert AnyPattern().match("!", 0) == 1

    def test_matches_last_character(self) -> None:
        assert AnyPattern().match("abc", 2) == 3

    def test_fails_when_out_of_bounds(self) -> None:
        assert AnyPattern().match("abc", 3) == -1

    def test_fails_on_empty_string(self) -> None:
        assert AnyPattern().match("", 0) == -1


# ══════════════════════════════════════════════
# CharGroupPattern  →  <[...]>
# ══════════════════════════════════════════════

class TestCharGroupPattern:

    # ── Explicit character groups ──

    def test_matches_char_in_explicit_group(self) -> None:
        assert CharGroupPattern("aeiou").match("hello", 1) == 2

    def test_fails_char_not_in_explicit_group(self) -> None:
        assert CharGroupPattern("aeiou").match("hello", 0) == -1

    def test_matches_first_char_in_group(self) -> None:
        assert CharGroupPattern("abc").match("a", 0) == 1

    def test_matches_last_char_in_group(self) -> None:
        assert CharGroupPattern("abc").match("c", 0) == 1

    def test_fails_char_outside_explicit_group(self) -> None:
        assert CharGroupPattern("abc").match("d", 0) == -1

    # ── Range groups ──

    def test_matches_lowercase_range(self) -> None:
        assert CharGroupPattern("a-z").match("h", 0) == 1

    def test_fails_uppercase_in_lowercase_range(self) -> None:
        assert CharGroupPattern("a-z").match("H", 0) == -1

    def test_matches_uppercase_range(self) -> None:
        assert CharGroupPattern("A-Z").match("Z", 0) == 1

    def test_matches_digit_range(self) -> None:
        assert CharGroupPattern("0-9").match("5", 0) == 1

    def test_fails_letter_in_digit_range(self) -> None:
        assert CharGroupPattern("0-9").match("a", 0) == -1

    def test_matches_boundary_range_start(self) -> None:
        assert CharGroupPattern("a-z").match("a", 0) == 1

    def test_matches_boundary_range_end(self) -> None:
        assert CharGroupPattern("a-z").match("z", 0) == 1

    # ── Mixed (explicit + range) ──

    def test_matches_digit_in_mixed_group(self) -> None:
        assert CharGroupPattern("a-z0-9").match("5", 0) == 1

    def test_matches_letter_in_mixed_group(self) -> None:
        assert CharGroupPattern("a-z0-9").match("g", 0) == 1

    def test_fails_uppercase_in_mixed_group(self) -> None:
        assert CharGroupPattern("a-z0-9").match("G", 0) == -1

    # ── Edge cases ──

    def test_fails_when_out_of_bounds(self) -> None:
        assert CharGroupPattern("abc").match("abc", 99) == -1

    def test_fails_on_empty_string(self) -> None:
        assert CharGroupPattern("abc").match("", 0) == -1

    def test_raises_on_invalid_range(self) -> None:
        with pytest.raises(ValueError, match="Invalid range"):
            CharGroupPattern("z-a")


# ══════════════════════════════════════════════
# RepeatPattern  →  <token*N>
# ══════════════════════════════════════════════

class TestRepeatPattern:

    def test_repeats_int_3_times_success(self) -> None:
        p = RepeatPattern(IntPattern(), 3)
        assert p.match("abc123", 3) == 6

    def test_repeats_int_3_times_partial_fail(self) -> None:
        p = RepeatPattern(IntPattern(), 3)
        assert p.match("abc12x", 3) == -1

    def test_repeats_any_5_times(self) -> None:
        p = RepeatPattern(AnyPattern(), 5)
        assert p.match("hello world", 0) == 5

    def test_repeats_alpha_2_times(self) -> None:
        p = RepeatPattern(AlphaPattern(), 2)
        assert p.match("ab1", 0) == 2

    def test_repeat_1_same_as_base(self) -> None:
        p = RepeatPattern(IntPattern(), 1)
        assert p.match("5", 0) == 1
        assert p.match("a", 0) == -1

    def test_repeat_char_group(self) -> None:
        p = RepeatPattern(CharGroupPattern("a-z"), 3)
        assert p.match("abcDEF", 0) == 3
        assert p.match("abDEF", 0)  == -1


# ══════════════════════════════════════════════
# Matcher._parse()
# ══════════════════════════════════════════════

class TestMatcherParse:

    def test_parses_literal_chars(self) -> None:
        m = Matcher("cat")
        assert len(m.patterns) == 3
        assert all(isinstance(p, LiteralPattern) for p in m.patterns)

    def test_parses_int_token(self) -> None:
        assert isinstance(Matcher("<int>").patterns[0], IntPattern)

    def test_parses_alpha_token(self) -> None:
        assert isinstance(Matcher("<alpha>").patterns[0], AlphaPattern)

    def test_parses_word_token(self) -> None:
        assert isinstance(Matcher("<word>").patterns[0], WordPattern)

    def test_parses_space_token(self) -> None:
        assert isinstance(Matcher("<space>").patterns[0], SpacePattern)

    def test_parses_wildcard_token(self) -> None:
        assert isinstance(Matcher("<_>").patterns[0], AnyPattern)

    def test_parses_int_with_multiplier(self) -> None:
        p = Matcher("<int*3>").patterns[0]
        assert isinstance(p, RepeatPattern)
        assert isinstance(p.inner, IntPattern)
        assert p.count == 3

    def test_parses_wildcard_with_multiplier(self) -> None:
        p = Matcher("<_*5>").patterns[0]
        assert isinstance(p, RepeatPattern)
        assert isinstance(p.inner, AnyPattern)
        assert p.count == 5

    def test_parses_char_group(self) -> None:
        assert isinstance(Matcher("<[abc]>").patterns[0], CharGroupPattern)

    def test_parses_char_group_range_expands_correctly(self) -> None:
        p = Matcher("<[a-z]>").patterns[0]
        assert isinstance(p, CharGroupPattern)
        assert 'a' in p.allowed_chars
        assert 'z' in p.allowed_chars
        assert 'A' not in p.allowed_chars

    def test_parses_char_group_with_multiplier(self) -> None:
        p = Matcher("<[a-z]*3>").patterns[0]
        assert isinstance(p, RepeatPattern)
        assert isinstance(p.inner, CharGroupPattern)
        assert p.count == 3

    def test_parses_mixed_pattern(self) -> None:
        m = Matcher("a<int>b")
        assert isinstance(m.patterns[0], LiteralPattern)
        assert isinstance(m.patterns[1], IntPattern)
        assert isinstance(m.patterns[2], LiteralPattern)

    def test_raises_on_unknown_token(self) -> None:
        with pytest.raises(ValueError, match="Unknown token"):
            Matcher("<banana>")

    def test_raises_on_unclosed_angle_bracket(self) -> None:
        with pytest.raises(ValueError, match="Unclosed '<'"):
            Matcher("<int")

    def test_raises_on_unclosed_square_bracket(self) -> None:
        with pytest.raises(ValueError, match="Unclosed '\\['"):
            Matcher("<[abc>")

    def test_raises_on_bad_multiplier(self) -> None:
        with pytest.raises(ValueError):
            Matcher("<int*abc>")


# ══════════════════════════════════════════════
# Matcher.match() — Literals
# ══════════════════════════════════════════════

class TestMatcherLiterals:
    def test_single_char_found(self) -> None:
        assert Matcher("a").match("apple") is True

    def test_single_char_not_found(self) -> None:
        assert Matcher("z").match("apple") is False

    def test_multi_char_found(self) -> None:
        assert Matcher("cat").match("I have a cat") is True

    def test_multi_char_not_found(self) -> None:
        assert Matcher("cat").match("I have a dog") is False

    def test_pattern_at_start(self) -> None:
        assert Matcher("app").match("apple") is True

    def test_pattern_at_end(self) -> None:
        assert Matcher("ple").match("apple") is True

    def test_empty_text(self) -> None:
        assert Matcher("a").match("") is False

    def test_pattern_longer_than_text(self) -> None:
        assert Matcher("toolongpattern").match("hi") is False


# ══════════════════════════════════════════════
# Matcher.match() — <int>
# ══════════════════════════════════════════════

class TestMatcherInt:
    def test_found_in_mixed_string(self) -> None:
        assert Matcher("<int>").match("abc123") is True

    def test_not_found_in_all_letters(self) -> None:
        assert Matcher("<int>").match("abcdef") is False

    def test_literal_then_int(self) -> None:
        assert Matcher("a<int>").match("a1") is True
        assert Matcher("a<int>").match("ab") is False

    def test_int_then_literal(self) -> None:
        assert Matcher("<int>!").match("3!") is True
        assert Matcher("<int>!").match("a!") is False


# ══════════════════════════════════════════════
# Matcher.match() — <alpha>
# ══════════════════════════════════════════════

class TestMatcherAlpha:
    def test_found_in_word(self) -> None:
        assert Matcher("<alpha>").match("hello") is True

    def test_not_found_in_digits(self) -> None:
        assert Matcher("<alpha>").match("12345") is False

    def test_alpha_then_int(self) -> None:
        assert Matcher("<alpha><int>").match("a1") is True
        assert Matcher("<alpha><int>").match("11") is False

    def test_not_matching_underscore(self) -> None:
        assert Matcher("<alpha>").match("_") is False


# ══════════════════════════════════════════════
# Matcher.match() — <word>
# ══════════════════════════════════════════════

class TestMatcherWord:
    def test_matches_letter(self) -> None:
        assert Matcher("<word>").match("hello") is True

    def test_matches_digit(self) -> None:
        assert Matcher("<word>").match("123") is True

    def test_matches_underscore(self) -> None:
        assert Matcher("<word>").match("_var") is True

    def test_not_found_in_symbols(self) -> None:
        assert Matcher("<word>").match("!!! ...") is False


# ══════════════════════════════════════════════
# Matcher.match() — <space>
# ══════════════════════════════════════════════

class TestMatcherSpace:
    def test_space_found(self) -> None:
        assert Matcher("<space>").match("hello world") is True

    def test_space_not_found(self) -> None:
        assert Matcher("<space>").match("helloworld") is False

    def test_word_space_word(self) -> None:
        assert Matcher("hello<space>world").match("hello world") is True
        assert Matcher("hello<space>world").match("helloworld")  is False

    def test_matches_tab(self) -> None:
        assert Matcher("<space>").match("a\tb") is True


# ══════════════════════════════════════════════
# Matcher.match() — <_>  (wildcard)
# ══════════════════════════════════════════════

class TestMatcherWildcard:
    def test_matches_letter(self) -> None:
        assert Matcher("<_>").match("a") is True

    def test_matches_digit(self) -> None:
        assert Matcher("<_>").match("1") is True

    def test_matches_symbol(self) -> None:
        assert Matcher("<_>").match("!") is True

    def test_not_matching_empty(self) -> None:
        assert Matcher("<_>").match("") is False

    def test_wildcard_between_literals(self) -> None:
        assert Matcher("a<_>c").match("abc") is True
        assert Matcher("a<_>c").match("a1c") is True
        assert Matcher("a<_>c").match("a!c") is True
        assert Matcher("a<_>c").match("ac")  is False


# ══════════════════════════════════════════════
# Matcher.match() — <token*N> multipliers
# ══════════════════════════════════════════════

class TestMatcherMultiplier:
    def test_int_times_3(self) -> None:
        assert Matcher("<int*3>").match("price 500 dollars") is True
        assert Matcher("<int*3>").match("price 50 dollars")  is False

    def test_wildcard_times_3(self) -> None:
        assert Matcher("<_*3>").match("abc") is True
        assert Matcher("<_*3>").match("ab")  is False

    def test_alpha_times_2(self) -> None:
        assert Matcher("<alpha*2>").match("ab1") is True
        assert Matcher("<alpha*2>").match("a1b") is False

    def test_multiplier_1_same_as_no_multiplier(self) -> None:
        assert Matcher("<int*1>").match("5abc") is True
        assert Matcher("<int*1>").match("abc")  is False

    def test_combined_multipliers(self) -> None:
        assert Matcher("<alpha*2><int*3>").match("ab123") is True
        assert Matcher("<alpha*2><int*3>").match("ab12")  is False
        assert Matcher("<alpha*2><int*3>").match("a123")  is False


# ══════════════════════════════════════════════
# Matcher.match() — <[...]> character groups
# ══════════════════════════════════════════════

class TestMatcherCharGroup:
    def test_explicit_group_match(self) -> None:
        assert Matcher("<[aeiou]>").match("hello")  is True
        assert Matcher("<[aeiou]>").match("rhythm") is False

    def test_range_lowercase(self) -> None:
        assert Matcher("<[a-z]>").match("Hello") is True
        assert Matcher("<[a-z]>").match("123")   is False

    def test_range_digits(self) -> None:
        assert Matcher("<[0-9]>").match("abc5") is True
        assert Matcher("<[0-9]>").match("abcd") is False

    def test_mixed_range_and_explicit(self) -> None:
        assert Matcher("<[a-z0-9]>").match("Hello5") is True
        assert Matcher("<[a-z0-9]>").match("HELLO")  is False

    def test_char_group_with_multiplier(self) -> None:
        assert Matcher("<[a-z]*3>").match("abcDEF") is True
        assert Matcher("<[a-z]*3>").match("abDEF")  is False

    def test_char_group_in_complex_pattern(self) -> None:
        # "Ab12" → 'A' ✅, 'b' ✅ (1st lowercase), '1' ❌ (needs 2nd lowercase)
        # needs TWO lowercase letters → "Abc1" is the correct match
        assert Matcher("<[A-Z]><[a-z]*2><int>").match("Ab12") is False
        assert Matcher("<[A-Z]><[a-z]*2><int>").match("Abc1") is True
        assert Matcher("<[A-Z]><[a-z]*2><int>").match("ab12") is False  # no uppercase


# ══════════════════════════════════════════════
# Matcher.match() — Complex Mixed Patterns
# ══════════════════════════════════════════════

class TestMatcherMixed:
    def test_alpha_space_int(self) -> None:
        assert Matcher("<alpha><space><int>").match("a 1") is True
        assert Matcher("<alpha><space><int>").match("1 a") is False

    def test_all_tokens_combined(self) -> None:
        assert Matcher("<int><space><alpha><word><_>").match("1 ab!") is True
        assert Matcher("<int><space><alpha><word><_>").match("a 1b!") is False

    def test_pattern_found_in_middle_of_long_text(self) -> None:
        assert Matcher("<int*3>").match("the price is 500 dollars") is True

    def test_pattern_not_found_in_long_text(self) -> None:
        assert Matcher("<int*3>").match("no numbers here at all") is False

    def test_complex_all_features(self) -> None:
        """'<[A-Z]><[a-z]*4><space><int*2>' matches e.g. 'Hello 42'"""
        assert Matcher("<[A-Z]><[a-z]*4><space><int*2>").match("Hello 42") is True
        assert Matcher("<[A-Z]><[a-z]*4><space><int*2>").match("hello 42") is False
        assert Matcher("<[A-Z]><[a-z]*4><space><int*2>").match("Hello 4")  is False


# ══════════════════════════════════════════════
# Matcher._parse() — << >> literal quoting
# ══════════════════════════════════════════════

class TestMatcherLiteralQuoting:
    """
    Tests for the <<...>> literal quoting syntax.

    <<...>> tells the parser: "treat every character inside as a plain
    literal — do NOT interpret it as a token."

    This solves the problem of writing characters like '<' in a pattern
    without the parser thinking a token is starting.
    """

    def test_quoted_word_matches(self) -> None:
        """<<hello>> should match the literal text 'hello'."""
        assert Matcher("<<hello>>").match("say hello there") is True

    def test_quoted_word_no_match(self) -> None:
        """<<hello>> should NOT match text without 'hello'."""
        assert Matcher("<<hello>>").match("say goodbye") is False

    def test_quoted_angle_bracket(self) -> None:
        """<<<>> should match a literal '<' character."""
        assert Matcher("<<<>>").match("a<b") is True
        assert Matcher("<<<>>").match("abc") is False

    def test_quoted_token_name_is_literal(self) -> None:
        """<<int>> should match the literal text 'int', NOT a digit."""
        assert Matcher("<<int>>").match("int value") is True
        assert Matcher("<<int>>").match("123")       is False

    def test_quoted_space_is_literal_space(self) -> None:
        """<<space>> should match the literal word 'space', not whitespace."""
        assert Matcher("<<space>>").match("outer space") is True
        assert Matcher("<<space>>").match("hello world") is False

    def test_empty_quote_is_noop(self) -> None:
        """
        <<>> is an empty quote — adds zero patterns to the list.

        With zero patterns, the for..else loop in match() completes
        immediately (no patterns to fail), so it returns True for any
        non-empty string. An empty string never enters the sliding window
        loop at all (range(0) is empty), so it returns False.
        """
        assert Matcher("<<>>").match("anything") is True   # loop runs, 0 patterns → True
        assert Matcher("<<>>").match("")          is False  # range(0) never runs → False

    def test_quote_mixed_with_tokens(self) -> None:
        """Mixing <<...>> with real tokens should work correctly."""
        # Pattern: literal 'val=' then a digit
        assert Matcher("<<val=>><int>").match("val=5") is True
        assert Matcher("<<val=>><int>").match("val=x") is False

    def test_quote_mixed_with_literals(self) -> None:
        """<<...>> next to plain literal chars should all parse correctly."""
        # "a<<bc>>d" → Literal(a), Literal(b), Literal(c), Literal(d)
        # effectively same as matching "abcd"
        assert Matcher("a<<bc>>d").match("abcd") is True
        assert Matcher("a<<bc>>d").match("axcd") is False

    def test_unclosed_quote_raises(self) -> None:
        """<<hello without closing >> should raise ValueError."""
        with pytest.raises(ValueError, match="Unclosed '<<'"):
            Matcher("<<hello")