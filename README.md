# Welcome to pdftk-wrapper

## Installation

```
python3 -m pip install pdftk-wrapper
```



Has been tested with `python>=3.8`.

## Usage

This is a Python wrapper over pdftk.  At present it supports only removing
pages from a pdf.  Example of a run:

```
pdftk-remove-pages ./tests/sample_1.pdf 1,3-195 ./gitignore_sample_1.pdf
```

Assuming the file `sample_1.pdf` has 195 pages.  The above would remove the first page, and pages 3 up to 195 and output the resulting pdf to `gitignore_sample_1.pdf` . So the resulting file `gitignore_sample_1.pdf` would just contain one page which was the second page in `sample_1.pdf`.

# 

```
$  pdftk-remove-pages --help
usage: pdftk-remove-pages [-h] input_file page_string output_file

A wrapper over pdftk to remove pages from a pdf.

positional arguments:
  input_file   Path to the pdf file to remove pages from.
  page_string  Remove specific pages from the pdf. Example: 1-10,13,15-20,32
  output_file  Path of the output file.

options:
  -h, --help   show this help message and exit
```
