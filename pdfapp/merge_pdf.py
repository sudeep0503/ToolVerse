from PyPDF2 import PdfMerger
from pathlib import Path


def merge_pdfs(pdf1_path: str, pdf2_path: str, output_path: str):
    """
    Merge two PDF files into one single PDF.
    """
    pdf1_path = Path(pdf1_path)
    pdf2_path = Path(pdf2_path)
    output_path = Path(output_path)

    if not pdf1_path.exists() or not pdf2_path.exists():
        raise FileNotFoundError("One or both PDF files were not found.")

    merger = PdfMerger()
    merger.append(str(pdf1_path))
    merger.append(str(pdf2_path))
    merger.write(str(output_path))
    merger.close()

    print(f"✅ Merged PDF saved at: {output_path}")


def main():
    # Input PDF files here
    pdf1 = "ilovepdf_extracted-pages\Marksheets-1.pdf"
    pdf2 = "ilovepdf_extracted-pages\Marksheets-2.pdf"

    # Output merged PDF path
    output_pdf = "merged_output.pdf"

    # Merge them
    merge_pdfs(pdf1, pdf2, output_pdf)


if __name__ == "__main__":
    main()
