"""This module contains a function to combine all the pdfs in a folder into one pdf."""

import logging
import os
import tempfile
import time

from pypdf import PdfReader, PdfWriter


def combine_pdfs(*dirs_or_pdfs: str, output_path: str = None) -> None | PdfWriter:
    """Combines all the pdfs in a folder into one pdf.

    args:
        - `dirs_or_pdfs: str`: path to the folder containing the pdf files.
        - `output_path: str`: path to the folder where the combined pdf will be saved. \
            if `None`, do not save and return a `PDFMerger` instead  \n
    returns:
        - `None`
    """
    merger = PdfWriter()
    if output_path and os.path.exists(output_path):
        os.remove(output_path)
    for item in dirs_or_pdfs:
        if os.path.isdir(item):
            for _f in os.listdir(item):
                merger.append(combine_pdfs(os.path.join(item, _f)))
        if item.endswith(".pdf"):
            merger.append(item)
            logging.info("Appended %s", item)
    if not output_path:
        temp_pdf = os.path.join(tempfile.gettempdir(), f"{time.perf_counter()}.pdf")
        merger.write(temp_pdf)
        return PdfReader(temp_pdf)
    logging.info("Combined all pdfs into %s", output_path)
    merger.write(output_path)
    merger.close()
    return None
