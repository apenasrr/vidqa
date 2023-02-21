"""Main module."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, Union

import pandas as pd

from vidqa import utils

from . import config, make_reencode, video_report
from .check_path import test_folders_has_path_too_long


def logging_config():
    logfilename = "log-" + "vidqa" + ".txt"
    logging.basicConfig(
        handlers=[
            logging.FileHandler(
                filename=logfilename, encoding="utf-8", mode="a+"
            )
        ],
        level=logging.INFO,
        format=" %(asctime)s-%(levelname)s-%(message)s",
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def get_list_path_video(folder_path: Path, video_extensions: tuple) -> list:
    # To input more file video extension:
    #  https://dotwhat.net/type/video-movie-files

    tuple_video_extension_raw = tuple(video_extensions)
    tuple_video_extension = tuple(
        "." + ext for ext in tuple_video_extension_raw
    )
    str_tuple_video_extension = ", ".join(tuple_video_extension)
    logging.info(
        "Find for video with extension: %s", str_tuple_video_extension
    )

    # get_all_file_path
    dict_all_file_result = utils.get_all_file_path(folder_path)

    # In case of error by max_path, interrupts execution
    if len(dict_all_file_result["errors"]) != 0:
        list_file_path_too_long = [
            str(x) for x in dict_all_file_result["errors"]
        ]
        for file_path_too_long in list_file_path_too_long:
            logging.error(f"File path too long: %s", file_path_too_long)
        raise ValueError("file_path_too_long")

    # Select desired videos by extension
    list_file_selected = []
    list_file_path = dict_all_file_result["content"].copy()
    for file_path in list_file_path:
        if file_path.name.lower().endswith(tuple_video_extension):
            logging.info("Selected file: %s", file_path.name)
            list_file_selected.append(file_path)
        else:
            logging.info("___Unselected: %s", file_path.name)

    return list_file_selected


def get_file_path_converted(path_origin: Path) -> Path:
    """ "Converts the absolute path of a video file, to its MP4 equivalent"

    Args:
        path_origin (Path): video path

    Returns:
        Path: video path in mp4
    """

    file_path_c = path_origin.parent / (path_origin.stem + ".mp4")
    return file_path_c


def replace_converted_video(path_origin: Path, path_converted: Path) -> None:
    """Replaces original video with converted video

    Args:
        path_origin (Path): path origin video
        path_converted (Path): path converted video

    Raises:
        FileNotFoundError: path file video not found
        PermissionError: It was not possible to replace the file
    """

    # check existence of video converted
    if not path_origin.exists():
        raise FileNotFoundError(f"path_file_origin not found: {path_origin}")
    if not path_converted.exists():
        raise FileNotFoundError(
            f"path_file_converted not found: {path_converted}"
        )

    file_path_converted_destination = get_file_path_converted(path_origin)

    # remove path_origin
    path_origin.unlink()

    # move path_converted to file_path_converted_destination
    while True:
        try:
            path_converted.rename(file_path_converted_destination)
            break
        except Exception as e:
            logging.error("Move fail. Trying again.: %s", str(path_converted))
            time.sleep(2)


def replace_converted_video_all(report_path: Path):
    while True:
        try:
            df = pd.read_csv(str(report_path))
            break
        except Exception as e:
            logging.error(e)
            logging.info(
                "It was not possible to open the report. "
                + "If it is open, close it."
            )
            input("Press any key...")

    mask_to_move = ~df["path_file_converted"].isna()
    df_to_move = df.loc[
        mask_to_move, ["path_file", "path_file_converted"]
    ].reset_index(drop=True)
    if df_to_move.shape[0] == 0:
        logging.info("Finish conversion")
        return

    for _, row in df_to_move.iterrows():
        path_origin = row["path_file"]
        path_converted = row["path_file_converted"]
        replace_converted_video(Path(path_origin), Path(path_converted))


def sanitize_files(folder_path: Path):
    """Ensures that the path of files are reasonable

    Args:
        folder_path (Path): folder path
    """

    logging.info("Star folder analysis: %s", str(folder_path))
    while True:
        (
            list_folders_path_approved,
            list_folders_path_rejected,
        ) = test_folders_has_path_too_long(
            [folder_path], max_path=250, max_name=150
        )

        if len(list_folders_path_rejected) > 0:
            input("\nAfter correcting, press something to continue.\n")
        else:
            return list_folders_path_approved


def sanitize_file_or_folder(item: Path):
    """Check if the file name or folder is compatible with Encoding UTF-8.
    If not, it renames to become compatible.

    Args:
        item (Path): Path of file or folder
    """

    try:
        item.name.encode("utf-8")
    except UnicodeEncodeError:
        new_item_name = item.name.encode("utf-8", errors="ignore").decode()
        new_item = item.parent / new_item_name
        logging.error(
            "Charmap error name: %s, location: %s",
            item.name.encode(errors="replace").decode(),
            item.parent,
        )
        logging.error("_Fixing. Rename to: %s", new_item_name)
        item.rename(new_item)


def apply_recursive_in_folder(func_: Callable, folder_path: Path):
    """Sanitizes all folders and files for UTF-8 compatible names

    Args:
        func_ (Callable): function to be apply to all folder and files
        folder_path (Path): folder path
    """

    for item in folder_path.rglob("*"):
        if item.is_file() or item.is_dir():
            func_(item)


def create_video_report(
    report_path: Path, folder_path: Path, video_extensions: tuple
):
    list_folders_path_approved = sanitize_files(folder_path)

    if len(list_folders_path_approved) == 0:
        return []

    # sanitize all file/folder names
    apply_recursive_in_folder(sanitize_file_or_folder, folder_path)

    list_path_video = get_list_path_video(folder_path, video_extensions)
    if len(list_path_video) == 0:
        logging.info("There are no video files.")
        return
    list_dict_report_video_metadata = (
        video_report.get_list_dict_report_video_metadata(list_path_video)
    )

    # generates CSV metadata report
    df_video_metadata = pd.DataFrame(list_dict_report_video_metadata)

    # set which videos need conversion
    df_video_metadata = video_report.include_video_to_convert(
        df_video_metadata
    )

    df_video_metadata.to_csv(report_path, index=False)


def check_report_integrity(report_path: Path) -> bool:
    """Checks the existence of the input and output files in the report
    If any of them don't exist, offers the option to delete the report and
    output files.
    Also offers the option to check again.

    Args:
        report_path (Path): report path.
                            Necessary columns: path_file, path_file_converted

    Returns:
        bool: True to continue. False to start from scratch.
    """

    message = (
        "\nAttention:\nThere are file paths recorded in the plan_report that "
        + "were not found and thus it is not possible to continue the "
        + "conversion.\n\n"
        + "Press 'y' to delete both the already converted videos and the "
        + "report and start from scratch.\n\n"
        + "Press any other key to check again the existence of the necessary "
        + "files to continue from where it stopped."
    )

    while True:
        df = pd.read_csv(Path(report_path))
        list_path_not_exists = [
            x
            for x in df["path_file"].dropna().to_list()
            + df["path_file_converted"].dropna().to_list()
            if not Path(x).exists()
        ]
        if len(list_path_not_exists) == 0:
            return True
        else:
            for path_file in list_path_not_exists:
                print(f"- {path_file}")
            print(message)
            delete_all = input("Answer: ")
            if delete_all == "y":
                report_path.unlink()
                list_path_exists = [
                    x
                    for x in df["path_file_converted"].dropna().to_list()
                    if Path(x).exists()
                ]
                if len(list_path_exists) != 0:
                    for path_file in list_path_exists:
                        Path(path_file).unlink()
                return False
            else:
                # loop to check report again
                pass


def get_folder_destination(
    folder_path: Path, path_folder_convert: Path = None
) -> Path:
    """
    Returns the destination folder path for storing converted videos
    and metadata report.

    Args:
        folder_path (Path): Path to the source folder containing files to be
            converted.
        path_folder_convert (Path, optional): Path to the destination folder
            for storing converted files. If not specified, converted files will
            be stored in the parent directory of the source folder with the
            prefix "vidqa_".

    Returns:
        Path: Full path to the destination folder where the converted files
            will be stored.

    Raises:
        FileNotFoundError: If the source folder specified in `folder_path` does
            not exist.
    """
    # TODO: test this funcion
    if not folder_path.exists() or not folder_path.is_dir():
        raise FileNotFoundError(
            f"{folder_path}\nThe source folder does not exist."
        )

    if not path_folder_convert:
        folder_destination = (
            Path(folder_path).absolute().parents[0]
            / f"vidqa_{folder_path.name}"
        )
    else:
        if not path_folder_convert.exists():
            path_folder_convert.mkdir()
        folder_destination = Path(path_folder_convert) / (
            "vidqa_" + Path(folder_path).name
        )
    folder_destination.mkdir(exist_ok=True)
    return folder_destination


def vidqa(
    folder_path: Path,
    report_path: Union[Path, None] = None,
    path_folder_convert: Union[Path, None] = None,
    video_extensions: tuple = None,
    flags: dict = None,
):
    """Warning if file path or file name is greater than they should.
    Ensure that video profile is format mp4, v/a codec H264/aac.

    Args:
        report_path (str): file path of report metadata
        path_dir (str): input folder
        video_extensions (tuple): video file extension to be analyzed
        path_folder_convert (str): temp folder to receive converted videos
        flags (dict, optional): video conversion flags. Defaults to None.
    """

    config_file = Path(__file__).absolute().parent / "config.ini"

    config_data = config.get_data(config_file)
    if video_extensions is None:
        video_extensions = config_data["video_extensions"].split(",")

    if flags is None:
        crf = float(config_data.get("crf", 18))
        maxrate = float(config_data.get("maxrate", 2))
        flags = {"crf": crf, "maxrate": maxrate}

    folder_destination = get_folder_destination(
        folder_path, path_folder_convert
    )

    if report_path is None:
        report_path = Path(folder_destination) / (folder_path.name + ".csv")

    if report_path.exists():
        integrity_check_passed = check_report_integrity(report_path)
    else:
        integrity_check_passed = False

    if not integrity_check_passed:
        create_video_report(report_path, folder_path, video_extensions)

    make_reencode.make_reencode(report_path, folder_destination, flags)
    replace_converted_video_all(report_path)


def main():
    config_data = config.get_data("config.ini")
    video_extensions = config_data["video_extensions"].split(",")

    crf = config_data.get("crf", 18)
    maxrate = config_data.get("maxrate", 2)
    flags = {"crf": crf, "maxrate": maxrate}

    report_path = Path("report_metadata.csv")
    folder_path = ""

    vidqa(folder_path, report_path, video_extensions, flags)


logging_config()
if __name__ == "__main__":
    main()
