# python split_pdf.py Files\Final_Thesis.pdf "1-2,3-4"



import fitz  # PyMuPDF
import os
import argparse


def parse_split_spec(spec: str, num_pages: int):
    """
    Parse user split string into list of (start, end) page ranges.

    Modes:

    1) Just page numbers (no '-'):
       e.g. "5"            -> cutpoints [5]       -> [1-5], [6-last]
            "2,4,10"       -> cutpoints [2,4,10]  -> [1-2], [3-4], [5-10], [11-last]

    2) Explicit ranges (contains '-'):
       e.g. "1-2,3-4"      -> explicit [1-2],[3-4] + remainder [5-last]
    """
    spec = spec.strip()
    if not spec:
        return [(1, num_pages)]

    # If there is no '-' anywhere, treat it as cutpoints list
    if "-" not in spec:
        cutpoints = []
        for token in spec.split(","):
            token = token.strip()
            if not token:
                continue
            p = int(token)
            if p < 1 or p >= num_pages:
                raise ValueError(f"Cutpoint {p} out of range 1..{num_pages-1}")
            cutpoints.append(p)

        cutpoints = sorted(set(cutpoints))
        ranges = []
        start = 1
        for cp in cutpoints:
            ranges.append((start, cp))
            start = cp + 1
        if start <= num_pages:
            ranges.append((start, num_pages))
        return ranges

    # Else: treat as explicit ranges like "1-2,3-4"
    ranges = []
    last_end = 0
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" not in token:
            # single page as range p-p
            start = end = int(token)
        else:
            s, e = token.split("-", 1)
            start = int(s.strip())
            end = int(e.strip())

        if start < 1 or end > num_pages or start > end:
            raise ValueError(f"Invalid range '{token}' for PDF with {num_pages} pages.")
        ranges.append((start, end))
        last_end = max(last_end, end)

    ranges = sorted(ranges, key=lambda x: x[0])

    # Add remainder after last explicit range, if any
    if last_end < num_pages:
        ranges.append((last_end + 1, num_pages))

    return ranges


def split_pdf(input_path: str, split_spec: str, output_dir: str = None):
    doc = fitz.open(input_path)
    num_pages = doc.page_count

    ranges = parse_split_spec(split_spec, num_pages)
    print(f"Total pages: {num_pages}")
    print("Splitting into ranges:", ranges)

    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_path)) or "."
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    for idx, (start, end) in enumerate(ranges, start=1):
        new_doc = fitz.open()
        # PyMuPDF pages are 0-based
        for pno in range(start - 1, end):
            new_doc.insert_pdf(doc, from_page=pno, to_page=pno)
        out_name = f"{base_name}_part{idx}_{start}-{end}.pdf"
        out_path = os.path.join(output_dir, out_name)
        new_doc.save(out_path)
        new_doc.close()
        print(f"  -> Created: {out_path}")

    doc.close()


def main():
    parser = argparse.ArgumentParser(
        description="Split a PDF into multiple PDFs based on page ranges / cutpoints."
    )
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("spec", help="Split spec, e.g. '5' or '1-2,3-4'")
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save split PDFs (default: same as input)"
    )
    args = parser.parse_args()

    split_pdf(args.input, args.spec, args.output_dir)


if __name__ == "__main__":
    main()
