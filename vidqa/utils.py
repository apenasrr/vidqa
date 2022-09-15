from __future__ import annotations

import logging
from pathlib import Path

import natsort
import unidecode


def get_all_file_path(folder_path: Path, sort=True) -> dict[str, list[Path]]:
    """Returns List of all file paths inside a folder, recursively.
    Option to Sort naturally.

    Args:
    -----
        folder_path (Path): folder path
        sort (bool, optional): Return classified. Defaults to True.

    Returns:
    --------
        dict[str, list[Path]]: keys: ['content', 'errors']. values: list[Path]
    """

    def iter_folder(
        sub_folder,
        list_file_path: list[Path] = [],
        list_error: list[Path] = [],
    ) -> tuple[list[Path], list[Path]]:

        for x in sub_folder.iterdir():
            if not x.exists():
                logging.error("path_too_long: %s", x)
                list_error.append(x)
                continue
            if x.is_dir():
                iter_folder(x, list_file_path, list_error)
            else:
                list_file_path.append(x)
        return list_file_path, list_error

    if not folder_path.exists():
        logging.error("Folder not exists: %s", folder_path)
        raise FileNotFoundError(f"Folder not exists: {folder_path}")

    list_file_path, list_error = iter_folder(folder_path)

    if sort:
        list_file_path = natsort.natsorted(
            list_file_path, lambda x: unidecode.unidecode(str(x).lower())
        )
        list_error = natsort.natsorted(
            list_error, lambda x: unidecode.unidecode(str(x).lower())
        )

    return {"content": list_file_path, "errors": list_error}
