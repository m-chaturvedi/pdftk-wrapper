#!/usr/bin/env python3
import re
import sys


def merge_ranges(pages):
    """merge_ranges.

    :param pages:
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
    pages = re.fullmatch(r"\d+(-\d+,)?", pages_string)
    if not pages:
        return RuntimeError("Page format is not as expected.")

    page_ranges = pages_string.split(",")
    pages = []
    for page_range in page_ranges:
        pg = [int(x) for x in page_range.split("-")]
        if len(pg) == 1:
            pages.append([pg[0], pg[0]])
        else:
            pages.append(pg)
    return pages


def main():
    assert (
        len(sys.argv) == 3
    ), "Usage: pdftk-remove-pages <file> <comma separated pages>"

    pdf_file = sys.argv[1]
    page_ranges = sys.argv[2].split(",")
    pages = []
    for page_range in page_ranges:
        assert re.fullmatch(
            r"\d+(-\d+)?", page_range
        ), "Page format is not as expected."

        pg = [int(x) for x in page_range.split("-")]
        if len(pg) == 1:
            pages.append([pg[0], pg[0]])
        else:
            pages.append(pg)
    pages.sort()
    print(pages)
    merged_pages = merge_ranges(pages)
    print(merged_pages)
    pdftk_pages = []
    for ind, pg in enumerate(merged_pages):
        if ind == 0 and pg[0] > 1:
            pdftk_pages += [f"1-{pg[0] - 1}"]
        if ind > 0:
            pdftk_pages += [f"{merged_pages[ind - 1][1] + 1}-{pg[0] - 1}"]

    pdftk_pages += [f"{merged_pages[-1][1] + 1}-end"]
    print(",".join(pdftk_pages))


def main1():
    parser = argparse.ArgumentParser(
        prog="pdftk-remove-pages",
        description="A wrapper over pdftk to remove pages from a pdf.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "pdf_filename", help="Path to the pdf file to remove pages from.", type=str
    )
    parser.add_argument("pages", help="Remove specific pages from the pdf.", type=str)

    if not os.path.isfile(pdf_filename):
        print(f"Pdf file doesn't exist: {config_file_path}")
        sys.exit(1)

    remove_results_dir = False
    if not args.directory:
        remove_results_dir = True

    args.directory = args.directory or tempfile.mkdtemp(prefix="occ_")
    logging.getLogger().setLevel(level=args.logging_level)
    logging.debug(args)
    num_holes, _, _ = read_rtp_streams(parser, args, config_dict)

    if remove_results_dir:
        shutil.rmtree(args.directory, ignore_errors=True)

    print(num_holes)


if __name__ == "__main__":
    main()
