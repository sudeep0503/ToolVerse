# python extract_pages.py Files\Final_Thesis.pdf "1,3-5,7-8"

import fitz  # PyMuPDF
import os
import argparse


def parse_extract_spec(spec: str, num_pages: int):
    """
    Parse string like:
      "5"
      "3-7"
      "1-2,5,7-9"
    -> list of 0-based page indices to keep.
    """
    spec = spec.strip()
    if not spec:
        raise ValueError("No page specification given.")

    keep_pages = set()

    tokens = spec.split(",")
    for token in tokens:
        token = token.strip()
        if not token:
            continue

        if "-" in token:
            s, e = token.split("-", 1)
            start = int(s.strip())
            end = int(e.strip())
        else:
            start = end = int(token.strip())

        if start < 1 or end > num_pages or start > end:
            raise ValueError(f"Invalid range '{token}' for PDF with {num_pages} pages.")

        for p in range(start, end + 1):
            keep_pages.add(p - 1)  # convert to 0-based

    return sorted(keep_pages)


def extract_pages(input_path: str, extract_spec: str, output_path: str = None):
    doc = fitz.open(input_path)
    num_pages = doc.page_count

    keep = parse_extract_spec(extract_spec, num_pages)
    print(f"Total pages: {num_pages}")
    print(f"Pages to extract (0-based): {keep}")

    if not keep:
        raise ValueError("No valid pages to extract.")

    new_doc = fitz.open()
    for pno in keep:
        new_doc.insert_pdf(doc, from_page=pno, to_page=pno)

    # Default output name
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(input_path)) or "."
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(base_dir, f"{base_name}_extracted{ext or '.pdf'}")

    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract specific pages or ranges from a PDF into a new file."
    )
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("spec", help="Pages/ranges to extract, e.g. '5' or '3-7' or '1-2,5,7-9'")
    parser.add_argument(
        "-o", "--output",
        help="Output PDF file path (default: <input>_extracted.pdf in same folder)"
    )
    args = parser.parse_args()

    extract_pages(args.input, args.spec, args.output)


if __name__ == "__main__":
    main()
