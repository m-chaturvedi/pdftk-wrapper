import unittest

from warnings import warn
from pdftk_remove_pages import main as pdftk_module


class TestPdftkRemovePagesMethods(unittest.TestCase):

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
                pdftk_module.parse_pages(good_string),
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
                pdftk_module.parse_pages,
                err_string,
            )

    def test_merge_ranges(self):
        self.assertEqual(pdftk_module.merge_ranges([[1, 1], [1, 1]]), [[1, 1]])
        self.assertEqual(pdftk_module.merge_ranges([[10, 10], [10, 10]]), [[10, 10]])
        self.assertEqual(pdftk_module.merge_ranges([[1, 3], [4, 10]]), [[1, 10]])
        self.assertEqual(pdftk_module.merge_ranges([[1, 3], [3, 10]]), [[1, 10]])
        self.assertEqual(
            pdftk_module.merge_ranges([[1, 1], [4, 10]]), [[1, 1], [4, 10]]
        )
        self.assertEqual(
            pdftk_module.merge_ranges([[1, 2], [3, 10], [4, 56]]), [[1, 56]]
        )
        self.assertEqual(
            pdftk_module.merge_ranges([[1, 3], [5, 10], [12, 15]]),
            [[1, 3], [5, 10], [12, 15]],
        )

    def test_output_ranges_in_pdftk_format(self):
        error_strings = []

        self.assertRaisesRegex(
            RuntimeError,
            r"Page ranges not defined properly. See \[10, 6\]\.",
            pdftk_module.output_ranges_in_pdftk_format,
            [[1, 1], [2, 2], [3, 3], [4, 5], [10, 6]],
            100,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Pages should be positive integers\.",
            pdftk_module.output_ranges_in_pdftk_format,
            [[100, 0], [2, 3], [7, 5], [10, 0]],
            101,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Page ranges not defined properly. See \[100, 1\]\.",
            pdftk_module.output_ranges_in_pdftk_format,
            [[100, 1], [2, 3], [7, 5], [10, 1]],
            101,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Page number 100 exceeds the total pages \(70\)\.",
            pdftk_module.output_ranges_in_pdftk_format,
            [[1, 15], [2, 100], [7, 5], [1, 1]],
            70,
        )

        self.assertRaisesRegex(
            RuntimeError,
            r"Page number 101 exceeds the total pages \(71\)\.",
            pdftk_module.output_ranges_in_pdftk_format,
            [[1, 15], [101, 102], [7, 5], [1, 1]],
            71,
        )

        self.assertRaisesRegex(
            RuntimeError,
            "No pages will be left after removing requested pages.  Consider deleting the file.",
            pdftk_module.output_ranges_in_pdftk_format,
            [[1, 1]],
            1,
        )

        relevant_f = pdftk_module.output_ranges_in_pdftk_format
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
        self.assertEqual(pdftk_module.get_number_of_pages("tests/sample_1.pdf"), 195)

    def test_run_command_in_bash(self):
        output = pdftk_module.run_command_in_bash("ls -l tests/sample_1.pdf")
        self.assertTrue(output.endswith("tests/sample_1.pdf\n"))

    def test_run_command_in_bash_escape(self):
        file_name = "tests/sdfjk \ fjlkdsf \ fsdf^&#^*$*!*@&$*$1.pdf"
        self.assertEqual(pdftk_module.get_number_of_pages(file_name), 5)

    def test_run_pdftk_command(self):
        complicated_file_name = "tests/sdfjk \ fjlkdsf \ fsdf^&#^*$*!*@&$*$1.pdf"
        input_output_map = [
            (
                ["tests/sample_1.pdf", "1-100", "gitignore_output_1.pdf"],
                "pdftk tests/sample_1.pdf cat 101-195 output gitignore_output_1.pdf",
                int(195 - (100 - 1 + 1)),
            ),
            (
                ["tests/sample_1.pdf", "1-10,20-30,50-194", "gitignore_output_1.pdf"],
                "pdftk tests/sample_1.pdf cat 11-19 31-49 195-195 output gitignore_output_1.pdf",
                int(195 - ((10 - 1 + 1) + (30 - 20 + 1) + (194 - 50 + 1))),
            ),
            (
                ["tests/sample_1.pdf", "20-30,50-194", "gitignore_output_1.pdf"],
                "pdftk tests/sample_1.pdf cat 1-19 31-49 195-195 output gitignore_output_1.pdf",
                int(195 - ((30 - 20 + 1) + (194 - 50 + 1))),
            ),
            (
                [complicated_file_name, "1,5", "gitignore_output_1.pdf"],
                f"pdftk '{complicated_file_name}' cat 2-4 output gitignore_output_1.pdf",
                int(5 - (1 + 1)),
            ),
        ]

        for input_output_tuple in input_output_map:
            self.assertEqual(
                pdftk_module.run_pdftk_command(*(input_output_tuple[0]), dry_run=False),
                input_output_tuple[1],
            )
            self.assertEqual(
                pdftk_module.get_number_of_pages("gitignore_output_1.pdf"),
                input_output_tuple[2],
            )


if __name__ == "__main__":
    unittest.main()
