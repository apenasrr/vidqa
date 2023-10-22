"""Main module."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
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
    """
    Retrieves a list of file paths with specified video extensions in the given
    folder.

    Args:
        folder_path (Path): Path object representing the directory to search
                            for video files.
        video_extensions (tuple): A tuple of strings representing valid video
                                  file extensions.

    Returns:
        list: A list of Path objects representing the selected video files.

    Raises:
        ValueError: Raised if there are file paths that exceed the maximum
                    allowed length.

    Example:
        folder_path = Path("/path/to/your/folder")
        video_extensions = (".mp4", ".avi", ".mov")
        video_files = get_list_path_video(folder_path, video_extensions)
        for video_file in video_files:
            print(video_file)

    Note:
        To input more video file extensions, refer to:
        https://dotwhat.net/type/video-movie-files
    """

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
            logging.error("File path too long: %s", file_path_too_long)
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
    # if destination exists, rename with suffix _2
    if file_path_converted_destination.exists():
        file_path_converted_destination = (
            file_path_converted_destination.parent
            / (file_path_converted_destination.stem + "_2.mp4")
        )

    # remove path_origin
    path_origin.unlink()

    # move path_converted to file_path_converted_destination
    while True:
        try:
            path_converted.rename(file_path_converted_destination)
            break
        except Exception as e:
            logging.error(
                "%s\nMove fail. Trying again.: %s", e, str(path_converted)
            )
            time.sleep(2)


def replace_converted_video_all(report_path: Path):
    """
    Reads a report file containing information about original and converted
    video paths.
    Replaces the original videos with the corresponding converted videos.

    Args:
        report_path (Path): Path object representing the location of the report
                            file.

    Returns:
        None

    Raises:
        Exception: If the report file cannot be opened, the function logs the
                   error and prompts the user to close the file.

    Example:
        report_path = Path("/path/to/your/report.csv")
        replace_converted_video_all(report_path)

    Note:
        The report file should contain columns 'path_file' for original video
        paths and 'path_file_converted' for corresponding converted video paths.
    """

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


def sanitize_files(folder_path: Path, max_path=250, max_name=150):
    """Ensures that file path lengths are reasonable.
    Review in a loop with pauses until the need is satisfied.

    Args:
        folder_path (Path): folder path
    """

    logging.info("Star folder analysis: %s", str(folder_path))
    while True:
        (
            list_folders_path_approved,
            list_folders_path_rejected,
        ) = test_folders_has_path_too_long(
            [folder_path], max_path=max_path, max_name=max_name
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
    report_path: Path, folder_path: Path, video_extensions: tuple, flags: dict
) -> list:
    """
    Creates a video metadata report identifying which ones need conversion and
    saves it to a CSV file.
    Also dumps all video metadata into a single JSON file located in the same
    folder as the report.

    Args:
        report_path (Path): Path object specifying the location to save the CSV
                            report.
        folder_path (Path): Path object representing the directory to search
                            for video files.
        video_extensions (tuple): A tuple of strings representing valid video
                                  file extensions.

    Returns:
        None

    Example:
        report_path = Path("/path/to/save/report.csv")
        folder_path = Path("/path/to/your/folder")
        video_extensions = (".mp4", ".avi", ".mov")
        create_video_report(report_path, folder_path, video_extensions)

    Note:
        - Sanitizes file and folder names within the specified
          directory to be UTF-8 compatible.
        - Extracts video metadata from valid video files with extensions
          specified in `video_extensions`.
        - Dumps all video metadata into a single JSON file located in the
          same folder as the report. Named {report_name}_metadata.json
        - Generates a CSV report containing video metadata and saves it to the
          specified `report_path`.
        - Videos to be converted are identified in the report.
    """

    max_path = flags.get("max_path", 260)
    max_name = flags.get("max_name", 150)
    list_folders_path_approved = sanitize_files(
        folder_path, max_path=max_path, max_name=max_name
    )

    if len(list_folders_path_approved) == 0:
        return []

    # sanitize all file/folder names
    apply_recursive_in_folder(sanitize_file_or_folder, folder_path)

    list_path_video = get_list_path_video(folder_path, video_extensions)
    if len(list_path_video) == 0:
        logging.info("There are no video files.")
        return

    inf_ffprobe = video_report.get_inf_ffprobe(list_path_video)
    list_dict_inf_ffprobe = inf_ffprobe.get("metadata", "")
    list_corrupt_videos = inf_ffprobe.get("corrupt", "")

    # save metadata json file
    metadata_json_path = report_path.parent / (
        report_path.stem + "_metadata.json"
    )
    save_list_dict_as_json_file(
        list_dict=list_dict_inf_ffprobe, file_path=metadata_json_path
    )
    # format list_dict to report needs
    list_dict_report_video_metadata = video_report.format_video_metadata(
        list_dict_inf_ffprobe
    )

    # generates CSV metadata report
    df_video_metadata = pd.DataFrame(list_dict_report_video_metadata)

    # set which videos need conversion
    df_video_metadata = video_report.include_video_to_convert(
        df_video_metadata
    )

    df_video_metadata.to_csv(report_path, index=False)
    return list_corrupt_videos


def save_list_dict_as_json_file(list_dict: list, file_path: Path):
    """Save list_dict as json file

    Args:
        list_dict (list): list of dict
        file_path (Path): path file
    """

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(list_dict, f, indent=4)


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


def get_folder_log(
    folder_path: Path, path_folder_convert: Path = None
) -> Path:
    """
    Returns the log  folder path for storing converted videos
    and metadata report.

    Args:
        folder_path (Path): Path to the source folder containing files to be
            converted.
        path_folder_convert (Path, optional): Path to the log folder
            for storing converted files. If not specified, converted files will
            be stored in the parent directory of the source folder with the
            prefix "vidqa_".

    Returns:
        Path: Full path to the log folder where the converted files
            will be stored.

    Raises:
        FileNotFoundError: If the source folder specified in `folder_path` does
            not exist.
    """

    if not folder_path.exists() or not folder_path.is_dir():
        raise FileNotFoundError(
            f"{folder_path}\nThe source folder does not exist."
        )

    if not path_folder_convert:
        folder_log = (
            Path(folder_path).absolute().parents[0]
            / f"vidqa_{folder_path.name}"
        )
    else:
        if not path_folder_convert.exists():
            path_folder_convert.mkdir()
        folder_log = Path(path_folder_convert) / (
            "vidqa_" + Path(folder_path).name
        )
    folder_log.mkdir(exist_ok=True)
    return folder_log


def vidqa(
    folder_path: Path,
    report_path: Union[Path, None] = None,
    path_folder_convert: Union[Path, None] = None,
    video_extensions: tuple = None,
    flags: Union[dict, None] = None,
):
    """Warning if file path or file name is greater than they should.
    Ensure that video profile is format mp4, v/a codecs H264/aac,
    audio channels <=2.

    Args:
        folder_path (Path): Path object representing project location.
        report_path (Optional[Path]): Path object representing report metadata.
        path_folder_convert (Optional[Path]): Path object representing the
            temporary folder to receive converted videos.
        video_extensions (Optional[Tuple[str, ...]]): Tuple of video file
            extensions to be analyzed.
        flags (Optional[Dict[str, Any]]): Dictionary of flags.
    """

    config_file = Path(__file__).absolute().parent / "config.ini"

    config_data = config.get_data(config_file)
    if video_extensions is None:
        video_extensions = config_data["video_extensions"].split(",")

    if flags is None:
        crf = float(config_data.get("crf", 18))
        maxrate = float(config_data.get("maxrate", 2))
        max_path = int(config_data.get("max_path", 240))
        max_name = int(config_data.get("max_name", 150))
        corrupt_del = int(config_data.get("corrupt_del", 0))
        corrupt_bkp = int(config_data.get("corrupt_bkp", 1))
        flags = {
            "crf": crf,
            "maxrate": maxrate,
            "corrupt_del": corrupt_del,
            "corrupt_bkp": corrupt_bkp,
            "max_path": max_path,
            "max_name": max_name,
        }

    folder_log = get_folder_log(folder_path, path_folder_convert)

    if report_path is None:
        report_path = Path(folder_log) / (folder_path.name + ".csv")

    if report_path.exists():
        integrity_check_passed = check_report_integrity(report_path)
    else:
        integrity_check_passed = False

    if not integrity_check_passed:
        list_corrupt_videos = create_video_report(
            report_path, folder_path, video_extensions, flags
        )
        # save list_corrupt_videos to report_erros_path and delete
        # or backup them
        report_erros_path = Path(folder_log) / (
            folder_path.name + "_errors.csv"
        )
        corrupt_handler(list_corrupt_videos, report_erros_path, flags)

    make_reencode.make_reencode(report_path, folder_log, flags)
    replace_converted_video_all(report_path)
    return report_path


def show_corrupt_videos(
    folder_path: Path, path_folder_convert: Union[Path, None]
):
    """
    Show a consolidated list of corrupt video files from multiple project
    reports.

    Args:
        folder_path (Path): Path objects representing project location.
        path_folder_convert (Path | None): Path object representing the location
                                           of converted temp folder.

    Example:
        folder_path = Path("/path/to/mytempproject)
        path_folder_convert = Path("/path/temp/vidqa_mytempproject/")
        show_corrupt_videos(folder_path, path_folder_convert)

    Note:
        - Infers the path of the corrupt video report from the folder where the
          project_report is.
        - Reads each corrupt video report file, extracts the list of corrupt
          videos, and consolidates them.
        - Show the paths of all corrupt videos found across the specified
          reports.
    """

    if not path_folder_convert:
        folder_log = (
            folder_path.absolute().parents[0] / f"vidqa_{folder_path.name}"
        )
    else:
        folder_log = path_folder_convert / (f"vidqa_{folder_path.name}")
    if not folder_log.exists():
        raise FileNotFoundError("folder_log not found")

    report_erros_path = folder_log / (folder_path.name + "_errors.csv")
    if report_erros_path.exists():
        list_corrupt_videos = pd.read_csv(report_erros_path)[
            "path_file"
        ].to_list()
        print(f"\nCorrupt videos: {folder_path.name}")
        for corrupt_video in list_corrupt_videos:
            print(f"- {str(corrupt_video)}")


def corrupt_handler(
    list_corrupt_videos: list, report_erros_path: Path, flags: dict
):
    """
    Handles corrupted video files by saving their paths to a CSV report and
    optionally creating backups or deleting them.

    Args:
        list_corrupt_videos (list): A list of file paths representing corrupted
                                    video files.
        report_errors_path (Path): Path object specifying the location to save
                                   the CSV report.
        flags (dict): A dictionary containing options for handling corrupted
                      files:
                      - 'corrupt_bkp' (int): 1 to create backups, 0 to disable.
                      - 'corrupt_del' (int): 1 to delete corrupted files, 0 to
                        disable.

    Returns:
        None

    Example:
        list_corrupt_videos = ["path/to/corrupted_video1.mp4",
                               "path/to/corrupted_video2.avi"]
        report_errors_path = Path("/path/to/save/corruption_report.csv")
        flags = {'corrupt_bkp': 1, 'corrupt_del': 1}
        corrupt_handler(list_corrupt_videos, report_errors_path, flags)
    """

    if len(list_corrupt_videos) == 0:
        return

    list_str_corrupt_videos = [str(x) for x in list_corrupt_videos]
    df = pd.DataFrame({"path_file": list_str_corrupt_videos})
    df.to_csv(report_erros_path, index=False, encoding="utf-8")

    # Copy videos corrupted to folder where is the report_erros_path
    if flags.get("corrupt_bkp", 1) == 1:
        for corrupt_video in list_corrupt_videos:
            hash = hashlib.md5(
                str(corrupt_video.parent).encode("utf-8")
            ).hexdigest()[:5]
            corrupt_video_backup_path = report_erros_path.parent / (
                Path(corrupt_video).stem
                + f"_{hash}"
                + Path(corrupt_video).suffix
            )
            shutil.copy(corrupt_video, corrupt_video_backup_path)
            logging.info("corrupt video backup: %s", corrupt_video)

    # Delete videos corrupted
    print(flags["corrupt_del"])
    if flags.get("corrupt_del", 0) == 1:
        for corrupt_video in list_corrupt_videos:
            Path(corrupt_video).unlink()


def move_project(
    folder_path: Path,
    move_done: Union[Path, None] = None,
    folder_destination: Union[Path, None] = None,
):
    """
    Moves a project folder to a specified destination based on configuration
    settings.

    Args:
        folder_path (Path): Path object representing the source project folder.
        move_done (int, optional): Flag indicating if the move operation is
            allowed (1 for allowed, 0 for disallowed).
        folder_destination (str, optional): Path to the destination folder
            where the project should be moved.

    Raises:
        FileNotFoundError: If the configuration file does not exist.

    Returns:
        None

    Notes:
        The `config_data` dictionary is expected to contain the following keys:
        - 'move_done' (int): Flag indicating if the move operation is allowed
            (1 for allowed, 0 for disallowed).
        - 'folder_destination' (str): Path to the destination folder where the
            project should be moved.
    """

    config_file = Path(__file__).absolute().parent / "config.ini"

    config_data = config.get_data(config_file)
    if move_done is None:
        move_done = int(config_data.get("move_done", 0))
    if move_done == 1:
        if folder_destination is None:
            folder_destination = Path(
                config_data.get("folder_destination", "")
            )
        if folder_destination.exists():
            folder_to = Path(folder_destination) / folder_path.name
            if not folder_to.exists():
                while True:
                    try:
                        folder_path.rename(folder_to)
                        break
                    except Exception as e:
                        logging.error("Fail to move: %s", e)
                        logging.error("Retrying in 2 seconds...")
                        time.sleep(2)
                logging.info("Project moved to: %s", str(folder_to))
            else:
                logging.info(
                    "Fail to move. Project already exists in: %s",
                    str(folder_to),
                )
        else:
            logging.info(
                "Fail to move. Folder destination that was set in "
                + "flags did not exist: %s",
                str(folder_destination),
            )


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
