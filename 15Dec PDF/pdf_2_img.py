from pathlib import Path
import fitz  # PyMuPDF


def pdf_to_images(pdf_path: str, output_folder: str = None, zoom: float = 2.0):
    """
    Export each page of a PDF as an image.

    Args:
        pdf_path (str): Path to input PDF.
        output_folder (str): Folder to save images. If None, uses PDF's folder.
        zoom (float): Scale factor for quality. >1 = higher resolution.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Resolve output folder
    if output_folder is None:
        output_dir = pdf_path.parent / (pdf_path.stem + "_pages")
    else:
        output_dir = Path(output_folder)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Open PDF
    doc = fitz.open(str(pdf_path))
    print(f"📄 PDF: {pdf_path}")
    print(f"📁 Output folder: {output_dir}")
    print(f"📑 Pages: {doc.page_count}")

    # Matrix for zoom (quality)
    matrix = fitz.Matrix(zoom, zoom)

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        # File name: page_001.png, page_002.png, ...
        img_name = f"page_{page_index + 1:03d}.png"
        img_path = output_dir / img_name

        pix.save(str(img_path))
        print(f"✅ Saved: {img_path}")

    doc.close()
    print("✨ Done. All pages exported as images.")


def main():
    # 🔧 Set your PDF path here
    input_pdf = r"Files\Final_Thesis.pdf"  # change this

    # Optional: set output folder (None = auto folder next to PDF)
    output_folder = None

    # zoom=2.0 → decent quality, 3.0 → higher but bigger files
    pdf_to_images(input_pdf, output_folder=output_folder, zoom=2.0)


if __name__ == "__main__":
    main()
