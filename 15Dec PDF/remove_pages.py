# python remove_pages.py Files\Final_Thesis.pdf "1,3-5,7-8"

import fitz  # PyMuPDF
import os
import argparse


def parse_remove_spec(spec: str, num_pages: int):
    """
    Parse a string like:
      "5"
      "3-7"
      "1-2,5,7-9"
    into a sorted list of 0-based page indices to remove.

    Pages are 1-based in the spec, but we convert to 0-based for PyMuPDF.
    """
    spec = spec.strip()
    if not spec:
        return []

    pages_to_remove = set()

    tokens = spec.split(",")
    for token in tokens:
        token = token.strip()
        if not token:
            continue

        if "-" in token:
            start_str, end_str = token.split("-", 1)
            start = int(start_str.strip())
            end = int(end_str.strip())
        else:
            start = end = int(token)

        if start < 1 or end > num_pages or start > end:
            raise ValueError(
                f"Invalid page / range '{token}' for PDF with {num_pages} pages."
            )

        for p in range(start, end + 1):
            pages_to_remove.add(p - 1)  # convert to 0-based

    return sorted(pages_to_remove)


def remove_pages(input_path: str, remove_spec: str, output_path: str = None):
    doc = fitz.open(input_path)
    num_pages = doc.page_count

    to_remove = parse_remove_spec(remove_spec, num_pages)
    print(f"Total pages: {num_pages}")
    print(f"Pages to remove (0-based): {to_remove}")

    if not to_remove:
        print("No pages to remove. Exiting without changes.")
        doc.close()
        return

    # Compute pages to keep (0-based)
    keep = [i for i in range(num_pages) if i not in to_remove]

    if not keep:
        doc.close()
        raise ValueError("Remove spec would delete all pages. Refusing to create empty PDF.")

    # Select only the pages we keep
    doc.select(keep)

    # Output path
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(input_path)) or "."
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(base_dir, f"{base_name}_removed{ext or '.pdf'}")

    # Save optimized
    doc.ez_save(output_path)
    doc.close()
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Remove pages from a PDF (single pages, ranges, or combinations)."
    )
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("spec", help="Pages to remove, e.g. '5' or '3-7' or '1-2,5,7-9'")
    parser.add_argument(
        "-o", "--output",
        help="Output PDF file path (default: <input>_removed.pdf in same folder)"
    )
    args = parser.parse_args()

    remove_pages(args.input, args.spec, args.output)


if __name__ == "__main__":
    main()
