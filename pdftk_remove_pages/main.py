import re
import argparse
import os
import subprocess
import sys
from shlex import quote


def merge_ranges(pages):
    """Merges ranges given in the format [[1,3], [4, 6]].

    :param pages: The ranges to be merged.
    :return: Array of ranges.
    """
    result = []
    i, N = 0, len(pages)

    while i < N:
        j = i + 1
        en = pages[i][1]
        while j < N and pages[j][0] <= en + 1:
            en = max(en, pages[j][1])
            j += 1
        result.append([pages[i][0], en])
        i = j
    return result


def parse_pages(pages_string):
    """Parses the string given in format '1,2,3,4-10'

    :param pages_string: The string to be parsed.
    :return: Array of ranges of the pages.
    """
    pages = re.fullmatch(r"(\d+(-\d+)?,)*\d+(-\d+)?", pages_string)
    if not pages:
        raise RuntimeError("Page format is not as expected.")

    page_ranges = pages_string.split(",")
    pages = []
    for page_range in page_ranges:
        pg = [int(x) for x in page_range.split("-")]
        if len(pg) == 1:
            pages.append([pg[0], pg[0]])
        else:
            pages.append(pg)
    return pages


def output_ranges_in_pdftk_format(page_ranges, total_pages):
    """Outputs comma separated pages to feed to pdftk.

    :param page_ranges: Array of arrays like [[1, 3], [3, 5]].
    """
    for pr in page_ranges:
        if pr[0] <= 0 or pr[1] <= 0:
            raise RuntimeError(f"Pages should be positive integers.")
        if pr[0] > pr[1]:
            raise RuntimeError(
                f"Page ranges not defined properly. See [{pr[0]}, {pr[1]}]."
            )
        if pr[0] > total_pages:
            raise RuntimeError(
                f"Page number {pr[0]} exceeds the total pages ({total_pages})."
            )
        if pr[1] > total_pages:
            raise RuntimeError(
                "Page ranges not defined properly. See [10, 6]."
                f"Page number {pr[1]} exceeds the total pages ({total_pages})."
            )

    page_ranges.sort()

    merged_pages = merge_ranges(page_ranges)
    pdftk_pages = []
    for ind, pg in enumerate(merged_pages):
        if ind == 0 and pg[0] > 1:
            pdftk_pages += [f"1-{pg[0] - 1}"]
        if ind > 0:
            pdftk_pages += [f"{merged_pages[ind - 1][1] + 1}-{pg[0] - 1}"]

    if merged_pages[-1][1] < total_pages:
        pdftk_pages += [f"{merged_pages[-1][1] + 1}-{total_pages}"]

    if len(pdftk_pages) > 0:
        return " ".join(pdftk_pages)
    else:
        raise RuntimeError(
            "No pages will be left after removing requested pages.  Consider deleting the file."
        )


# TODO: This runs in /bin/sh but the intent is to run in /bin/bash.  The problem we
# saw was related to quoting, since the command to be run would be "/bin/bash -c 'pdftk ...'"
def run_command_in_bash(cmd_string):
    """Runs the command using the subprocess module in Bash.

    :param cmd_string: The command string to be run.
    """
    output = subprocess.check_output(cmd_string, shell=True, text=True)
    return output


def get_number_of_pages(pdf_filename):
    """Get number of pages in a pdf file. Doesn't check the existence of the file.

    :param pdf_filename: path to the pdf.
    """
    op = run_command_in_bash(f"pdftk {quote(pdf_filename)} dump_data")
    num_pages_regex = re.compile("NumberOfPages: (\d+)")
    num_pages_match = num_pages_regex.search(op)
    assert num_pages_match.group(0).startswith("NumberOfPages:")
    num_pages = int(num_pages_match.group(1))
    return num_pages


def run_pdftk_command(input_file, page_string, output_file, dry_run=True):
    """Run pdftk command using the arguments supplied

    :param input_file: The input pdf from which the pages need to be removed.
    :param page_string: Comma separated pages to remove.
    :param output_file: The output pdf.
    """
    page_ranges = parse_pages(page_string)
    total_pages = get_number_of_pages(input_file)
    pdftk_page_string = output_ranges_in_pdftk_format(page_ranges, total_pages)
    pdftk_command = (
        f"pdftk {quote(input_file)} cat {pdftk_page_string} output {quote(output_file)}"
    )
    run_command_in_bash(pdftk_command) if not dry_run else None
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
