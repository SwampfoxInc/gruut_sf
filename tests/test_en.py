#!/usr/bin/env python3
"""Tests for English class"""
import unittest

from gruut import sentences


class EnglishTestCase(unittest.TestCase):
    """Test cases for English"""

    def test_unclean_text(self):
        """Test text with lots of noise"""
        text = (
            "IT’S <a> 'test' (seNtEnce) for-only $100, Dr., & [I] ## *like* ## it 100%!"
        )
        sentence = next(sentences(text, lang="en_US"))

        self.assertEqual(
            [
                "IT'S",
                "<",
                "a",
                ">",
                "'",
                "test",
                "'",
                "(",
                "seNtEnce",
                ")",
                "for",
                "only",
                "one",
                "hundred",
                "dollars",
                ",",
                "Doctor",
                ",",
                "and",
                "[",
                "I",
                "]",
                "*",
                "like",
                "*",
                "it",
                "one",
                "hundred",
                "percent",
                "!",
            ],
            [word.text for word in sentence],
        )

    def test_spell_out(self):
        """Test spell-out in say-as SSML tag"""
        text = '<say-as interpret-as="spell-out">abc@1+2-3*.*</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))

        self.assertEqual(
            [
                "a",
                "b",
                "c",
                "at",
                "one",
                "plus",
                "two",
                "dash",
                "three",
                "star",
                "dot",
                "star",
            ],
            [word.text for word in sentence],
        )

    def test_initialisms(self):
        """Test expansion of initialisms"""
        text = "ABC abc A.B.C."
        sentence = next(sentences(text, lang="en_US"))

        self.assertEqual(
            ["A", "B", "C", "abc", "A", "B", "C"],
            [word.text for word in sentence],
        )

    def test_dates(self):
        """Test expansion of dates"""
        text = "1/4/1999 vs. 4/1/1999"
        sentence = next(sentences(text, lang="en_US"))

        self.assertEqual(
            [
                "January",
                "fourth",
                ",",
                "nineteen",
                "ninety",
                "nine",
                "versus",
                "April",
                "first",
                ",",
                "nineteen",
                "ninety",
                "nine",
            ],
            [word.text for word in sentence],
        )

    def test_ordinals(self):
        """Test parsing of ordinal numbers"""
        text = "1st, 2nd, 3rd, 4th, 5th, 23rd, 32nd, 44th, 121st, 5,111st."
        sentence = next(sentences(text, lang="en_US"))

        self.assertEqual(
            [
                "first",
                ",",
                "second",
                ",",
                "third",
                ",",
                "fourth",
                ",",
                "fifth",
                ",",
                "twenty",
                "third",
                ",",
                "thirty",
                "second",
                ",",
                "forty",
                "fourth",
                ",",
                "one",
                "hundred",
                "and",
                "twenty",
                "first",
                ",",
                "five",
                "thousand",
                ",",
                "one",
                "hundred",
                "and",
                "eleventh",
                ".",
            ],
            [word.text for word in sentence],
        )

    def test_times(self):
        """Test expansion of times"""
        text = "4:01am and 4:01 p.m."
        sentence = next(sentences(text, lang="en_US"))

        self.assertEqual(
            ["four", "oh", "one", "A", "M", "and", "four", "oh", "one", "P", "M"],
            [word.text for word in sentence],
        )

    def test_address_abbreviation_expansion(self):
        """Test directional and street suffix expansion in address context"""
        text = '<say-as interpret-as="address">N Main St</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertIn("North", words)
        self.assertIn("Street", words)
        self.assertIn("Main", words)

    def test_address_state_abbreviation(self):
        """Test US state abbreviation expansion"""
        text = '<say-as interpret-as="address">WA</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertEqual(["Washington"], words)

    def test_address_period_stripping(self):
        """Test that trailing periods are stripped for abbreviation matching"""
        text = '<say-as interpret-as="address">St.</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertEqual(["Street"], words)

    def test_address_zip_code(self):
        """Test ZIP code is read digit by digit"""
        text = '<say-as interpret-as="address">98001</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertEqual(["nine", "eight", "zero", "zero", "one"], words)

    def test_address_passthrough(self):
        """Test that non-abbreviation words pass through unchanged"""
        text = '<say-as interpret-as="address">Redmond</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertEqual(["Redmond"], words)

    def test_address_number_verbalization(self):
        """Test that street numbers are verbalized as cardinals"""
        text = '<say-as interpret-as="address">123</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        # Should be verbalized via normal number pipeline
        self.assertIn("one", words)
        self.assertIn("hundred", words)

    def test_address_trailing_punctuation(self):
        """Test that trailing punctuation (comma) is preserved after expansion"""
        text = '<say-as interpret-as="address">St, Main</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence]

        # "St," should expand to "Street" with comma preserved as minor break
        self.assertIn("Street", words)
        self.assertIn(",", words)
        self.assertIn("Main", words)

    def test_address_multi_word_expansion(self):
        """Test state abbreviation that expands to multiple words"""
        text = '<say-as interpret-as="address">DC</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        # DC -> District of Columbia (3 words)
        self.assertEqual(["District", "of", "Columbia"], words)

    def test_address_dr_in_address_context(self):
        """Test Dr. expands to Drive (not Doctor) in address context"""
        text = '<say-as interpret-as="address">Dr</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertEqual(["Drive"], words)

    def test_address_unit_designator(self):
        """Test unit designator expansion"""
        text = '<say-as interpret-as="address">Apt</say-as>'
        sentence = next(sentences(text, lang="en_US", ssml=True))
        words = [word.text for word in sentence if word.is_spoken]

        self.assertEqual(["Apartment"], words)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
