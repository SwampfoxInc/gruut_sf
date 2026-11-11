#!/usr/bin/env python3
"""Tests for Spanish (ZOR-451 address abbreviations, ordinals)"""
import unittest

from gruut import sentences
from gruut.text_processor import TextProcessor


class SpanishTestCase(unittest.TestCase):
    """Test cases for Spanish text processing"""

    def _spoken(self, text, ssml=True):
        sents = list(sentences(text, lang="es", ssml=ssml, phonemes=False, pos=False))
        self.assertEqual(1, len(sents), [s.text for s in sents])
        return [word.text for word in sents[0] if word.is_spoken]

    def _address(self, text):
        return self._spoken(f'<say-as interpret-as="address">{text}</say-as>')

    def test_address_slash_calle(self):
        """ZOR-451: C/ Mayor -> Calle Mayor, number cardinal, postal code digit by digit"""
        self.assertEqual(
            [
                "quince",
                "Calle",
                "Mayor",
                "Piso",
                "tres",
                "Madrid",
                "dos",
                "ocho",
                "cero",
                "cero",
                "uno",
            ],
            self._address("15 C/ Mayor, Piso 3, Madrid 28001"),
        )

    def test_address_slash_attached(self):
        """C/Mayor (no space) splits into Calle Mayor; lower case too"""
        self.assertEqual(["Calle", "Mayor", "quince"], self._address("C/Mayor 15"))
        self.assertEqual(["Calle", "Mayor", "quince"], self._address("c/Mayor 15"))

    def test_address_abbreviation_period_no_split(self):
        """Avda. / Pza. periods do not split the sentence"""
        self.assertEqual(
            ["Avenida", "de", "la", "Constitución", "doce", "Plaza", "Mayor", "tres"],
            self._address("Avda. de la Constitución 12, Pza. Mayor 3"),
        )

    def test_address_sin_numero_and_numero(self):
        """s/n and Nº markers"""
        self.assertEqual(
            ["Plaza", "Mayor", "sin", "número", "número", "cuatro"],
            self._address("Pza. Mayor s/n, Nº 4"),
        )

    def test_address_ordinal_floor_and_door_letter(self):
        """3º -> tercero; a trailing C is a door letter, not Calle"""
        self.assertEqual(["tercero", "C"], self._address("3º C"))
        self.assertEqual(["tercero", "C", "Madrid"], self._address("3º C, Madrid"))

    def test_address_calle_with_period(self):
        """C. Mayor -> Calle Mayor"""
        self.assertEqual(["Calle", "Mayor"], self._address("C. Mayor"))

    def test_address_feminine_ordinal(self):
        """2ª planta -> segunda planta"""
        self.assertEqual(["segunda", "planta"], self._address("2ª planta"))

    def test_address_saint(self):
        """St. before a name is San, after a street name is Calle"""
        self.assertEqual(["San", "Paul"], self._address("St. Paul"))
        self.assertEqual(["Main", "Calle"], self._address("Main St"))
        self.assertEqual(["Calle", "Santa", "María"], self._address("C/ Sta. María"))

    def test_plain_ordinal_not_a_date(self):
        """Ordinal indicators outside an address are not parsed as dates"""
        self.assertEqual(["tercero", "piso"], self._spoken("3º piso", ssml=False))
        self.assertEqual(["segunda", "planta"], self._spoken("2ª planta", ssml=False))

    def test_time_after_english_request(self):
        """A collapsed time ("3:45 p.m.") stays Spanish on a processor whose default
        language is English (one TextProcessor per thread serves every language)"""
        processor = TextProcessor(default_lang="en_US")
        graph, root = processor("a las 3:45 p.m.", lang="es", ssml=False)
        sents = list(processor.sentences(graph, root, phonemes=False, pos=False))
        self.assertEqual(1, len(sents))
        self.assertEqual(
            ["a", "las", "tres", "cuarenta", "y", "cinco", "de", "la", "tarde"],
            [word.text for word in sents[0] if word.is_spoken],
        )

    def test_plain_date_still_detected(self):
        """Separator dates are still verbalized"""
        words = self._spoken("12/03/2024", ssml=False)
        self.assertIn("marzo", words)


if __name__ == "__main__":
    unittest.main()
