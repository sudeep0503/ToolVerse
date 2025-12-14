'''
1. Just lock the PDF with an open 
    python password_protect.py Files\Final_Thesis.pdf -u mypass123

2. Separate owner password
    python password_protect.py Files\Final_Thesis.pdf -u read123 -p admin456

3. Add restrictions (disable printing & copy)
    python password_protect.py Files\Final_Thesis.pdf -u read123 --no-print --no-copy

4. Custom Output Path
    python password_protect.py Files\Report.pdf -u secure -p admin -o Files\Report_secure.pdf

'''




import fitz  # PyMuPDF
import os
import argparse


def password_protect(input_path: str, output_path: str = None,
                     user_pwd: str = None, owner_pwd: str = None,
                     no_print=False, no_copy=False, no_annot=False):
    """
    Apply password protection and optional restrictions to a PDF.
    """
    if not user_pwd and not owner_pwd:
        raise ValueError("At least one password (user or owner) must be provided.")

    doc = fitz.open(input_path)

    # Build permissions bitmask
    perms = 0
    if no_print:
        perms |= fitz.PDF_PERM_PRINT
    if no_copy:
        perms |= fitz.PDF_PERM_COPY
    if no_annot:
        perms |= fitz.PDF_PERM_ANNOTATE

    # Save encrypted copy
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(input_path)) or "."
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(base_dir, f"{base_name}_locked{ext or '.pdf'}")

    doc.save(
        output_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,  # Strong AES-256 encryption
        owner_pw=owner_pwd,
        user_pw=user_pwd,
        permissions=~perms,  # invert: bits unset = disallowed
    )
    doc.close()

    print(f"🔐 Created password-protected PDF: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Add password protection to a PDF.")
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output PDF file path")
    parser.add_argument("-u", "--user", help="User password (required to open PDF)")
    parser.add_argument("-p", "--owner", help="Owner password (full access)")
    parser.add_argument("--no-print", action="store_true", help="Disallow printing")
    parser.add_argument("--no-copy", action="store_true", help="Disallow text/image copying")
    parser.add_argument("--no-annot", action="store_true", help="Disallow adding annotations")

    args = parser.parse_args()
    password_protect(
        args.input,
        args.output,
        user_pwd=args.user,
        owner_pwd=args.owner,
        no_print=args.no_print,
        no_copy=args.no_copy,
        no_annot=args.no_annot,
    )


if __name__ == "__main__":
    main()
