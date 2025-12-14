'''
1. single file -> auto name
    python unlock_pdf_fitz.py Files/Final_Thesis_locked.pdf "yourPassword123"

2. single file -> custom output path
    python unlock_pdf_fitz.py Files/Final_Thesis_locked.pdf "yourPassword123" -o "Files/Final_Thesis_unlocked.pdf"

3. batch: unlock all PDFs in a folder to output folder (must supply output dir)
    python unlock_pdf_fitz.py "LockedPDFs" "commonPassword" -o "UnlockedPDFs"

'''
# PyMuPDF >= 1.23

import fitz
import os
import argparse

def unlock_pdf(input_path: str, password: str, output_path: str = None):
    """
    Open a password-protected PDF with the provided password and
    save an unlocked copy (works with modern PyMuPDF).
    """
    doc = fitz.open(input_path)

    # Try unlocking with password
    if doc.needs_pass:
        if not doc.authenticate(password):
            raise RuntimeError("❌ Wrong password! Could not open the PDF.")
    else:
        print("ℹ️ PDF was not encrypted, saving a copy anyway.")

    # Prepare output path
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(input_path)) or "."
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(base_dir, f"{base_name}_unlocked{ext or '.pdf'}")

    # Save without encryption
    doc.save(output_path, encryption=fitz.PDF_ENCRYPT_NONE)
    doc.close()

    print(f"✅ Unlocked PDF created: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Remove password from a PDF (you must know the password).")
    parser.add_argument("input", help="Input locked PDF path (file or directory)")
    parser.add_argument("password", help="Password to open the PDF (user or owner password)")
    parser.add_argument("-o", "--output", help="Output file path (or output directory for batch)")
    args = parser.parse_args()

    input_path = args.input
    password = args.password
    output = args.output

    if os.path.isfile(input_path):
        # single file
        out_path = output
        if output and os.path.isdir(output):
            os.makedirs(output, exist_ok=True)
            base = os.path.basename(input_path)
            out_path = os.path.join(output, base)
        unlock_pdf(input_path, password, out_path)
    elif os.path.isdir(input_path):
        # batch: output must be directory
        if not output:
            parser.error("Batch mode requires an output directory as the -o/--output argument.")
        os.makedirs(output, exist_ok=True)
        for fname in os.listdir(input_path):
            if not fname.lower().endswith(".pdf"):
                continue
            in_file = os.path.join(input_path, fname)
            try:
                out_file = os.path.join(output, fname)
                unlock_pdf(in_file, password, out_file)
            except Exception as e:
                print(f"Failed to unlock '{in_file}': {e}")
    else:
        parser.error("Input path is not a file or directory.")

if __name__ == "__main__":
    main()
