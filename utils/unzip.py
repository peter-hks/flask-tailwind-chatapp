"""this module contains the function to unzip a file."""

import logging
from zipfile import ZipFile


def unzip_file(zip_file: str, output_folder: str) -> None:
    """Unzips a zip file into a folder.

    args:
        - `zip_file: str`: path to the zip file.
        - `output_folder: str`: path to the folder where the zip file will be unzipped. \n
    """
    with ZipFile(zip_file) as zipfile_bytes:
        zipfile_bytes.extractall(output_folder)
    logging.info("Unzipped %s into %s", zip_file, output_folder)
