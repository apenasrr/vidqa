"""Main module."""

import logging
import os
import shutil

import pandas as pd

from . import config, make_reencode, video_report
from .check_path import test_folders_has_path_too_long


def logging_config():

    logfilename = "log-" + "vidqa" + ".txt"
    logging.basicConfig(
        filename=logfilename,
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


def get_list_path_video(path_dir: str, video_extensions: tuple) -> list:

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
    list_file_selected = []
    for root, _, files in os.walk(path_dir):
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(tuple_video_extension):
                logging.info("Selected file: %s", file)
                path_file = os.path.join(root, file)
                list_file_selected.append(path_file)
            else:
                logging.info("Unselected file: %s", file)
    return list_file_selected


def get_file_path_converted(path_origin):

    name_origin = os.path.basename(path_origin)
    folder_origin = os.path.dirname(path_origin)
    name_wo_ext = os.path.splitext(name_origin)[0]
    name_converted = name_wo_ext + ".mp4"
    file_path_converted = os.path.join(folder_origin, name_converted)
    return file_path_converted


def replace_converted_video(path_origin: str, path_converted: str) -> None:

    file_path_converted_destination = get_file_path_converted(path_origin)

    # confer existence of video converted
    if not os.path.exists(path_converted):
        raise ValueError("path_file_converted not found: %s", path_converted)

    # remove path_origin
    os.remove(path_origin)

    # mover path_converted para file_path_converted_destination
    try:
        shutil.move(path_converted, file_path_converted_destination)
    except Exception as e:
        logging.error(e)
        logging.error("move fail: %s", path_converted)
        raise ValueError(f"move fail: {path_converted}")


def replace_converted_video_all(report_path: str):

    while True:
        try:
            df = pd.read_csv(report_path)
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
        replace_converted_video(path_origin, path_converted)


def vidqa(
    path_dir: str,
    report_path: str = None,
    path_folder_convert: str = "temp",
    video_extensions: tuple = None,
):
    """Warning if file path or file name is greater than they should.
    Ensure that video profile is format mp4, v/a codec H264/aac.

    Args:
        report_path (str): file path of report metadata
        path_dir (str): input folder
        video_extensions (tuple): video file extension to be analyzed
        path_folder_convert (str): temp folder to receive converted videos
    """

    config_file = os.path.join(
        os.path.dirname(os.path.abspath(os.path.abspath(__file__))),
        "config.ini",
    )
    config_data = config.get_data(config_file)
    if video_extensions is None:
        video_extensions = config_data["video_extensions"].split(",")
    if report_path is None:
        report_path = os.path.basename(path_dir) + ".csv"

    logging.info("Star folder analysis: %s", path_dir)
    (
        list_folders_path_approved,
        list_folders_path_rejected,
    ) = test_folders_has_path_too_long([path_dir], max_path=260, max_name=100)

    if len(list_folders_path_rejected) > 0:
        input("\nAfter correcting, press something to continue.\n")

    if len(list_folders_path_approved) > 0:
        path_dir = list_folders_path_approved[0]
    else:
        return []

    list_path_video = get_list_path_video(path_dir, video_extensions)

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

    if not os.path.exists(path_folder_convert):
        os.mkdir(path_folder_convert)
    make_reencode.make_reencode(report_path, path_folder_convert)
    replace_converted_video_all(report_path)


def main():

    config_data = config.get_data("config.ini")
    video_extensions = config_data["video_extensions"].split(",")
    report_path = "report_metadata.csv"
    path_dir = ""

    vidqa(path_dir, report_path, video_extensions=video_extensions)


logging_config()
if __name__ == "__main__":
    main()
