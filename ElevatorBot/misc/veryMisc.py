import os
from typing import Generator


def yield_files_in_folder(folder: str, extension: str) -> Generator:
    """ Yields all paths of all files with the correct extension in the specified folder """

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(f".{extension}") and not file.startswith("__init__"):
                file = file.removesuffix(f".{extension}")
                path = os.path.join(root, file)
                yield path.replace("/", ".").replace("\\", ".")
