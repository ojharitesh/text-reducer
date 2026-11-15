import unittest

from text_reducer.reducer import InputDoesNotFail, reduce_text


class ReducerTests(unittest.TestCase):
    def test_reduces_to_failure_inducing_character(self) -> None:
        # The reducer should discard everything except the character causing failure.
        result = reduce_text("abcXdef", lambda text: "X" in text)
        self.assertEqual(result.text, "X")
        self.assertGreater(result.tests, 1)

    def test_no_reduction_is_possible(self) -> None:
        # A one-character failing input cannot be reduced further.
        result = reduce_text("X", lambda text: text == "X")
        self.assertEqual(result.text, "X")
        self.assertEqual(result.tests, 1)

    def test_original_input_must_fail(self) -> None:
        # Reduction must stop immediately when the starting input passes.
        with self.assertRaises(InputDoesNotFail):
            reduce_text("safe", lambda text: "X" in text)

    def test_empty_input(self) -> None:
        # Empty input is valid when the checker reports failure for it.
        result = reduce_text("", lambda text: text == "")
        self.assertEqual(result.text, "")
        self.assertEqual(result.tests, 1)

    def test_small_input(self) -> None:
        # The reducer should handle a candidate with only two characters.
        result = reduce_text("ab", lambda text: "a" in text)
        self.assertEqual(result.text, "a")


if __name__ == "__main__":
    unittest.main()
