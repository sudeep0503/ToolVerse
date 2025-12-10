from django.shortcuts import render

# Create your views here.

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render

from .pdf_2_docx import pdf_to_word_exact
from .merge_pdf import merge_pdfs


def home(request):
    """
    Show the main ToolVerse page (your index.html).
    """
    return render(request, "index.html")


def pdf_to_word_view(request):
    """
    Handle PDF → Word conversion.
    - Expects file input with name 'pdf_files'.
    - Uses your pdf_to_word_exact() to convert first uploaded PDF.
    - Returns the generated DOCX as a download.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST method is allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if not uploaded_files:
        return HttpResponseBadRequest("Please upload at least one PDF file.")

    # For now: use only the first file
    uploaded_file = uploaded_files[0]

    uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"
    outputs_dir = Path(settings.MEDIA_ROOT) / "outputs"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded PDF to disk
    input_path = uploads_dir / uploaded_file.name
    with open(input_path, "wb+") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)

    # Create output DOCX path
    output_name = Path(uploaded_file.name).with_suffix(".docx").name
    output_path = outputs_dir / output_name

    # Call your converter function
    pdf_to_word_exact(input_path, output_path)

    # Return DOCX file as download
    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename=output_name,
    )


def merge_pdf_view(request):
    """
    Handle PDF merge.
    - Expects file input with name 'pdf_files'.
    - For now merges the first two uploaded PDFs.
    - Uses your merge_pdfs() function.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST method is allowed.")

    uploaded_files = request.FILES.getlist("pdf_files")
    if len(uploaded_files) < 2:
        return HttpResponseBadRequest("Please upload at least two PDF files.")

    uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"
    outputs_dir = Path(settings.MEDIA_ROOT) / "outputs"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    # For now: only the first two files
    for uploaded_file in uploaded_files[:2]:
        save_path = uploads_dir / uploaded_file.name
        with open(save_path, "wb+") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        saved_paths.append(save_path)

    output_path = outputs_dir / "merged_output.pdf"

    # Use your existing merge_pdfs(pdf1_path, pdf2_path, output_path)
    merge_pdfs(str(saved_paths[0]), str(saved_paths[1]), str(output_path))

    return FileResponse(
        open(output_path, "rb"),
        as_attachment=True,
        filename="merged_output.pdf",
    )
