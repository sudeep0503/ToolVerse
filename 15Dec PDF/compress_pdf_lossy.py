# python compress_pdf_lossy.py Files\Final_Thesis.pdf --level 50


import fitz  # PyMuPDF
import os
import argparse


def map_level_to_params(level: int):
    """
    Map a human-friendly 'compression level' (0-100)
    to internal parameters for rewrite_images.

    level = 0   -> very light compression (high quality, high DPI)
    level = 100 -> strong compression (lower quality, lower DPI)
    """
    level = max(0, min(100, level))

    # JPEG quality: 0 -> 85, 100 -> 50  (smooth, not extreme)
    quality = int(85 - (35 * level / 100))

    # First choose a threshold: 0 -> 220 dpi, 100 -> 150 dpi
    dpi_threshold = int(220 - (70 * level / 100))

    # Target must be LESS than threshold. Keep a 40 dpi gap.
    dpi_target = max(72, dpi_threshold - 40)

    return dpi_threshold, dpi_target, quality



def compress_pdf_lossy_with_level(input_path, output_path, level=50):
    """
    Compress a single PDF with a percentage-like 'level' (0-100).
    Higher level => stronger compression.
    """
    dpi_threshold, dpi_target, quality = map_level_to_params(level)

    print(f"Using level={level} -> dpi_threshold={dpi_threshold}, "
          f"dpi_target={dpi_target}, quality={quality}")

    doc = fitz.open(input_path)

    # 1) lossy recompression of images
    doc.rewrite_images(
        dpi_threshold=dpi_threshold,
        dpi_target=dpi_target,
        quality=quality,
        lossy=True,
        lossless=True,
        bitonal=True,
        color=True,
        gray=True,
        set_to_gray=False,
    )

    # 2) still do font subsetting (lossless for text)
    doc.subset_fonts()

    # 3) save with structural optimization
    doc.ez_save(output_path)
    doc.close()

    print(f"Compressed (level {level}) '{input_path}' -> '{output_path}'")


def main():
    parser = argparse.ArgumentParser(
        description="Lossy PDF compression with a 0-100 'level' knob."
    )
    parser.add_argument("input", help="Input PDF file or directory")
    parser.add_argument("output", nargs="?", help="Output PDF file or output directory (for batch)")
    parser.add_argument("--level", type=int, default=50,
                        help="Compression level 0-100 (higher = more compression, default: 50)")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    level = args.level

    # Single file
    if os.path.isfile(input_path):
        if output_path:
            if os.path.isdir(output_path):
                os.makedirs(output_path, exist_ok=True)
                base = os.path.basename(input_path)
                out_file = os.path.join(output_path, base)
            else:
                out_file = output_path
        else:
            base, ext = os.path.splitext(input_path)
            out_file = f"{base}_lossy{ext or '.pdf'}"

        compress_pdf_lossy_with_level(input_path, out_file, level=level)

    # Batch: directory
    elif os.path.isdir(input_path):
        if not output_path:
            parser.error("Batch mode requires an output directory as the second argument.")
        os.makedirs(output_path, exist_ok=True)

        for fname in os.listdir(input_path):
            if not fname.lower().endswith(".pdf"):
                continue
            in_file = os.path.join(input_path, fname)
            out_file = os.path.join(output_path, fname)
            compress_pdf_lossy_with_level(in_file, out_file, level=level)
    else:
        parser.error(f"Input path '{input_path}' is not a file or directory.")


if __name__ == "__main__":
    main()
