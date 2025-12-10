from pdf2docx import Converter
from pathlib import Path


def pdf_to_word_exact(pdf_path: Path, docx_path: Path):
    """
    Convert a PDF to DOCX while preserving layout and formatting.
    Uses pdf2docx (pure Python, no external dependencies).
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"****    Converting '{pdf_path.name}' → '{docx_path.name}' ...    ****")

    # Initialize converter
    converter = Converter(str(pdf_path))
    converter.convert(str(docx_path), start=0, end=None)
    converter.close()

    print(f"====    Done: {docx_path.name}    ====\n")


def batch_convert_folder(input_folder: str, output_folder: str = None):
    """
    Convert all PDFs in a folder to DOCX.
    Overwrites existing DOCX files if they exist.
    """
    input_folder = Path(input_folder)
    output_folder = Path(output_folder) if output_folder else input_folder

    if not input_folder.exists():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    pdf_files = list(input_folder.glob("*.pdf"))

    if not pdf_files:
        print(f"%%%%    No PDF files found in: {input_folder}    %%%%")
        return

    print(f"\n{'='*80}")
    print(f"Batch PDF → DOCX Conversion Started")
    print(f"{'='*80}")
    print(f"Input Folder : {input_folder}")
    print(f"Output Folder: {output_folder}")
    print(f"Found {len(pdf_files)} PDF file(s)\n")

    for pdf_file in pdf_files:
        output_docx = output_folder / pdf_file.with_suffix(".docx").name
        pdf_to_word_exact(pdf_file, output_docx)

    print(f"{'='*80}")
    print(f"All PDFs converted successfully!")
    print(f"Output saved in: {output_folder}")
    print(f"{'='*80}\n")


def main():
    # Configure your folder paths here
    input_folder = r"ilovepdf_extracted-pages"  # folder containing PDFs
    output_folder = input_folder  # same as input for now

    # Run batch conversion
    batch_convert_folder(input_folder, output_folder)


if __name__ == "__main__":
    main()
