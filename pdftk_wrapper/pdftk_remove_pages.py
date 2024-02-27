import argparse
import os
from . import common
from shlex import quote


def run_pdftk_command(input_file, page_string, output_file, dry_run=True):
    """Run pdftk command using the arguments supplied

    :param input_file: The input pdf from which the pages need to be removed.
    :param page_string: Comma separated pages to remove.
    :param output_file: The output pdf.
    """
    page_ranges = common.parse_pages(page_string)
    total_pages = common.get_number_of_pages(input_file)
    pdftk_page_string = common.output_ranges_in_pdftk_format(page_ranges, total_pages)
    pdftk_command = (
        f"pdftk {quote(input_file)} cat {pdftk_page_string} output {quote(output_file)}"
    )
    common.run_command_in_bash(pdftk_command) if not dry_run else None
    #  print(f"Running command: {pdftk_command}")
    return pdftk_command


def parse_arguments():
    """Parses the arguments passed using argparse"""
    parser = argparse.ArgumentParser(
        prog="pdftk-remove-pages",
        description="A wrapper over pdftk to remove pages from a pdf.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "input_file", help="Path to the pdf file to remove pages from.", type=str
    )
    parser.add_argument(
        "page_string",
        help="Remove specific pages from the pdf. Example: 1-10,13,15-20,32",
        type=str,
    )

    parser.add_argument("output_file", help="Path of the output file.", type=str)

    args = parser.parse_args()
    if not os.path.isfile(os.path.expanduser(args.input_file)):
        raise RuntimeError(f"Pdf file doesn't exist: {args.input_file}")
    return args


def main():
    """The main function.  This is the entry point."""
    args = parse_arguments()
    input_file, page_string, output_file = (
        os.path.expanduser(args.input_file),
        args.page_string,
        args.output_file,
    )
    run_pdftk_command(input_file, page_string, output_file, False)


if __name__ == "__main__":
    main()
