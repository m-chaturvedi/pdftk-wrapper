import unittest

from warnings import warn
from pdftk_wrapper import pdftk_remove_pages
from pdftk_wrapper import common


class TestPdftkRemovePagesMethods(unittest.TestCase):

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
                pdftk_remove_pages.run_pdftk_command(
                    *(input_output_tuple[0]), dry_run=False
                ),
                input_output_tuple[1],
            )
            self.assertEqual(
                common.get_number_of_pages("gitignore_output_1.pdf"),
                input_output_tuple[2],
            )


if __name__ == "__main__":
    unittest.main()
