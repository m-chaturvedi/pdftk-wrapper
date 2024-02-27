import unittest
from pdftk_wrapper import common


class TestCommonMethods(unittest.TestCase):

    def test_parse_pages(self):
        good_strings = dict(
            {
                "1": [[1, 1]],
                "2,3": [[2, 2], [3, 3]],
                "3-4": [[3, 4]],
                "1,2,3,4-5,6-10": [[1, 1], [2, 2], [3, 3], [4, 5], [6, 10]],
                "100-0,2,3,7-5,10-0": [[100, 0], [2, 2], [3, 3], [7, 5], [10, 0]],
            }
        )

        for good_string in good_strings:
            self.assertEqual(
                common.parse_pages(good_string),
                good_strings[good_string],
            )

        error_strings = [
            ",",
            "-",
            " ",
            "",
            ",,",
            "--",
            "1,2,,4-5,6-10",
            "1,2,4--5,6-10",
            "1,2,4--5,6-10",
            "1,2,4-5,6-10,",
            ",1,2,4-5,6-10,",
            "1,2,4-5,6-10,",
            "1,2,-5,6-10",
            "-4",
        ]

        for err_string in error_strings:
            self.assertRaisesRegex(
                RuntimeError,
                r"Page format is not as expected\.",
                common.parse_pages,
                err_string,
            )

    def test_merge_ranges(self):
        self.assertEqual(common.merge_ranges([[1, 1], [1, 1]]), [[1, 1]])
        self.assertEqual(common.merge_ranges([[10, 10], [10, 10]]), [[10, 10]])
        self.assertEqual(common.merge_ranges([[1, 3], [4, 10]]), [[1, 10]])
        self.assertEqual(common.merge_ranges([[1, 3], [3, 10]]), [[1, 10]])
        self.assertEqual(common.merge_ranges([[1, 1], [4, 10]]), [[1, 1], [4, 10]])
        self.assertEqual(common.merge_ranges([[1, 2], [3, 10], [4, 56]]), [[1, 56]])
        self.assertEqual(
            common.merge_ranges([[1, 3], [5, 10], [12, 15]]),
            [[1, 3], [5, 10], [12, 15]],
        )

    def test_output_ranges_in_pdftk_format(self):
        error_strings = []

        self.assertRaisesRegex(
            RuntimeError,
            r"Page ranges not defined properly. See \[10, 6\]\.",
            common.output_ranges_in_pdftk_format,
            [[1, 1], [2, 2], [3, 3], [4, 5], [10, 6]],
            100,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Pages should be positive integers\.",
            common.output_ranges_in_pdftk_format,
            [[100, 0], [2, 3], [7, 5], [10, 0]],
            101,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Page ranges not defined properly. See \[100, 1\]\.",
            common.output_ranges_in_pdftk_format,
            [[100, 1], [2, 3], [7, 5], [10, 1]],
            101,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Page number 100 exceeds the total pages \(70\)\.",
            common.output_ranges_in_pdftk_format,
            [[1, 15], [2, 100], [7, 5], [1, 1]],
            70,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Page number 101 exceeds the total pages \(71\)\.",
            common.output_ranges_in_pdftk_format,
            [[1, 15], [101, 102], [7, 5], [1, 1]],
            71,
        )

        self.assertRaisesRegex(
            RuntimeError,
            "No pages will be left after removing requested pages.  Consider deleting the file.",
            common.output_ranges_in_pdftk_format,
            [[1, 1]],
            1,
        )

        relevant_f = common.output_ranges_in_pdftk_format
        self.assertEqual(relevant_f([[1, 1], [1, 1]], 2), "2-2")
        self.assertEqual(
            relevant_f([[10, 10], [10, 10]], 11),
            "1-9 11-11",
        )

        self.assertRaisesRegex(
            RuntimeError,
            "No pages will be left after removing requested pages.  Consider deleting the file.",
            relevant_f,
            [[1, 3], [4, 10]],
            10,
        )

        self.assertEqual(
            relevant_f([[1, 3], [4, 10]], 11),
            "11-11",
        )

        self.assertEqual(relevant_f([[1, 1], [4, 10]], 10), "2-3")

        self.assertEqual(relevant_f([[1, 2], [3, 10], [4, 56]], 100), "57-100")

        self.assertEqual(relevant_f([[1, 3], [5, 10], [12, 15]], 15), "4-4 11-11")

        self.assertEqual(
            relevant_f([[1, 15], [101, 102], [5, 7], [1, 1]], 102), "16-100"
        )

    def test_get_number_of_pages(self):
        self.assertEqual(common.get_number_of_pages("tests/sample_1.pdf"), 195)

    def test_run_command_in_bash(self):
        output = common.run_command_in_bash("ls -l tests/sample_1.pdf")
        self.assertTrue(output.endswith("tests/sample_1.pdf\n"))

    def test_run_command_in_bash_escape(self):
        file_name = "tests/sdfjk \ fjlkdsf \ fsdf^&#^*$*!*@&$*$1.pdf"
        self.assertEqual(common.get_number_of_pages(file_name), 5)

if __name__ == "__main__":
    unittest.main()
