from pathlib import Path
import zipfile
import io

from django.conf import settings
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render

from .pdf_2_docx import pdf_to_word_exact
from .merge_pdf import merge_pdfs
from .compress_pdf_lossy import compress_pdf_lossy_with_level
from .extract_pages import extract_pages
from .password_protect import password_protect
from .pdf_2_img import pdf_to_images
from .remove_pages import remove_pages
from .split_pdf import split_pdf
from .unlock_password import unlock_pdf


def _get_upload_output_dirs():
    """
    Helper: returns (uploads_dir, outputs_dir) as Path objects.
    """
    uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"
    outputs_dir = Path(settings.MEDIA_ROOT) / "outputs"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    return uploads_dir, outputs_dir


def home(request):
    """
    Show the main ToolVerse page (your index.html).
    """
    return render(request, "index.html")


# ---------- Existing tools ----------

def pdf_to_word_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload at least one PDF file.")

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    output_name = Path(uploaded_file.name).with_suffix(".docx").name
    output_path = outputs_dir / output_name

    pdf_to_word_exact(str(input_path), str(output_path))

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def merge_pdf_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if len(uploaded_files) < 2:
        return HttpResponseBadRequest("Please upload at least two PDF files.")

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    saved_paths = []
    for uploaded_file in uploaded_files[:10]:  # sanity cap
        save_path = uploads_dir / uploaded_file.name
        with open(save_path, "wb+") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        saved_paths.append(save_path)

    # For now: merge only first two
    output_path = outputs_dir / "merged_output.pdf"
    merge_pdfs(str(saved_paths[0]), str(saved_paths[1]), str(output_path))

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename="merged_output.pdf",
    )


# ---------- New tools ----------

def compress_pdf_view(request):
    """
    Compress a single PDF using compress_pdf_lossy_with_level(...).
    Extra POST field:
      - level (0-100, default 50)
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a PDF file.")

    uploaded_file = uploaded_files[0]

    level_str = request.POST.get("level", "50")
    try:
        level = int(level_str)
    except ValueError:
        level = 50

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    base = Path(uploaded_file.name)
    output_name = f"{base.stem}_compressed{base.suffix}"
    output_path = outputs_dir / output_name

    compress_pdf_lossy_with_level(str(input_path), str(output_path), level=level)

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def extract_pages_view(request):
    """
    Extract specific pages to a new PDF.
    Extra POST field:
      - pages_spec (e.g. '1-3,5')
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a PDF file.")

    pages_spec = request.POST.get("pages_spec", "").strip()
    if not pages_spec:
        return HttpResponseBadRequest("Please provide a pages specification.")

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    base = Path(uploaded_file.name)
    output_name = f"{base.stem}_extracted{base.suffix}"
    output_path = outputs_dir / output_name

    extract_pages(str(input_path), pages_spec, str(output_path))

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def remove_pages_view(request):
    """
    Remove specific pages from a PDF.
    Extra POST field:
      - remove_spec (e.g. '2,4-6')
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a PDF file.")

    remove_spec = request.POST.get("remove_spec", "").strip()
    if not remove_spec:
        return HttpResponseBadRequest("Please provide pages to remove.")

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    base = Path(uploaded_file.name)
    output_name = f"{base.stem}_removed{base.suffix}"
    output_path = outputs_dir / output_name

    remove_pages(str(input_path), remove_spec, str(output_path))

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def split_pdf_view(request):
    """
    Split a PDF into multiple PDFs and return them as a ZIP.
    Extra POST field:
      - split_spec (e.g. '5' or '1-2,3-4')
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a PDF file.")

    split_spec = request.POST.get("split_spec", "").strip()
    if not split_spec:
        return HttpResponseBadRequest("Please provide a split specification.")

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    # Create a subfolder for individual parts
    base = Path(uploaded_file.name)
    parts_dir = outputs_dir / f"{base.stem}_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    # Run your split tool (it writes multiple PDFs into parts_dir)
    split_pdf(str(input_path), split_spec, str(parts_dir))

    # Zip all generated PDFs
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for pdf_file in parts_dir.glob("*.pdf"):
            zf.write(pdf_file, arcname=pdf_file.name)

    zip_buffer.seek(0)
    zip_name = f"{base.stem}_split_parts.zip"
    return FileResponse(
        zip_buffer,
        as_attachment=True,
        filename=zip_name,
    )


def password_protect_view(request):
    """
    Apply password and restrictions.
    Extra POST fields:
      - user_password
      - owner_password (optional)
      - no_print (checkbox)
      - no_copy  (checkbox)
      - no_annot (checkbox)
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a PDF file.")

    user_pwd = request.POST.get("user_password") or None
    owner_pwd = request.POST.get("owner_password") or None

    if not user_pwd and not owner_pwd:
        return HttpResponseBadRequest("Provide at least one password.")

    no_print = bool(request.POST.get("no_print"))
    no_copy = bool(request.POST.get("no_copy"))
    no_annot = bool(request.POST.get("no_annot"))

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    base = Path(uploaded_file.name)
    output_name = f"{base.stem}_locked{base.suffix}"
    output_path = outputs_dir / output_name

    password_protect(
        str(input_path),
        str(output_path),
        user_pwd=user_pwd,
        owner_pwd=owner_pwd,
        no_print=no_print,
        no_copy=no_copy,
        no_annot=no_annot,
    )

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def unlock_pdf_view(request):
    """
    Unlock a password-protected PDF.
    Extra POST field:
      - password
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a locked PDF file.")

    password = request.POST.get("password", "").strip()
    if not password:
        return HttpResponseBadRequest("Please provide the PDF password.")

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    base = Path(uploaded_file.name)
    output_name = f"{base.stem}_unlocked{base.suffix}"
    output_path = outputs_dir / output_name

    unlock_pdf(str(input_path), password, str(output_path))

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def pdf_to_images_view(request):
    """
    Convert PDF pages to images, return all as ZIP.
    Extra POST field:
      - zoom (float, e.g. '2.0')
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload a PDF file.")

    zoom_str = request.POST.get("zoom", "2.0")
    try:
        zoom = float(zoom_str)
    except ValueError:
        zoom = 2.0

    uploaded_file = uploaded_files[0]

    uploads_dir, outputs_dir = _get_upload_output_dirs()

    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    base = Path(uploaded_file.name)
    images_dir = outputs_dir / f"{base.stem}_pages"
    images_dir.mkdir(parents=True, exist_ok=True)

    # This function writes multiple PNGs into images_dir
    pdf_to_images(str(input_path), output_folder=str(images_dir), zoom=zoom)

    # Zip all images
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for img_file in images_dir.glob("*.png"):
            zf.write(img_file, arcname=img_file.name)

    zip_buffer.seek(0)
    zip_name = f"{base.stem}_images.zip"
    return FileResponse(
        zip_buffer,
        as_attachment=True,
        filename=zip_name,
    )
