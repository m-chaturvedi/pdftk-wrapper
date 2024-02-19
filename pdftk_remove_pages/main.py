import re
import argparse
import os
import subprocess
import sys


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
        return ",".join(pdftk_pages)
    else:
        raise RuntimeError(
            "No pages will be left after removing requested pages.  Consider deleting the file."
        )


def run_command_in_bash(cmd_string):
    output = subprocess.check_output(
        "/bin/bash -c '" + cmd_string + "'", shell=True, text=True
    )
    return output


def get_number_of_pages(pdf_filename):
    op = run_command_in_bash(f"pdftk {pdf_filename} dump_data")
    num_pages_regex = re.compile("NumberOfPages: (\d+)")
    num_pages_match = num_pages_regex.search(op)
    assert num_pages_match.group(0).startswith("NumberOfPages:")
    num_pages = int(num_pages_match.group(1))
    return num_pages


def run_pdftk_command(args):
    page_ranges = parse_pages(args.pages)
    pdf_filename = args.pdf_filename
    total_pages = get_number_of_pages(pdf_filename)
    pdftk_page_string = output_ranges_in_pdftk_format(page_ranges, total_pages)
    __import__('pdb').set_trace()


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="pdftk-remove-pages",
        description="A wrapper over pdftk to remove pages from a pdf.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "pdf_filename", help="Path to the pdf file to remove pages from.", type=str
    )
    parser.add_argument("pages", help="Remove specific pages from the pdf.", type=str)

    parser.add_argument("output_filename", help="Path of the output file.", type=str)

    args = parser.parse_args()
    if not os.path.isfile(args.pdf_filename):
        raise RuntimeError(f"Pdf file doesn't exist: {args.pdf_filename}")
    return args


def main():
    args = parse_arguments()
    run_pdftk_command(args)


if __name__ == "__main__":
    main()
