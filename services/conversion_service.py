# Conversion service: converts PPT/PPTX files to PDF using LibreOffice headless mode.
# Requires LibreOffice installed on the server (sudo apt install libreoffice).

import subprocess
import os
from pathlib import Path


def convert_to_pdf(input_path: str) -> str:
    """Convert a PPT/PPTX file to PDF. Returns the path of the generated PDF."""
    input_path = Path(input_path).resolve()
    output_dir = input_path.parent

    result = subprocess.run(
        ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(output_dir), str(input_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # LibreOffice may succeed even with non-zero exit on some platforms; check file first
    pdf_path = output_dir / (input_path.stem + '.pdf')
    if not pdf_path.exists():
        # Fallback: LibreOffice on Windows sometimes ignores --outdir and writes to cwd
        cwd_pdf = Path.cwd() / (input_path.stem + '.pdf')
        if cwd_pdf.exists():
            cwd_pdf.rename(pdf_path)
        else:
            raise FileNotFoundError(
                f'LibreOffice conversion failed. PDF not found at {pdf_path}. '
                f'stderr: {result.stderr.strip()}'
            )

    return str(pdf_path)
