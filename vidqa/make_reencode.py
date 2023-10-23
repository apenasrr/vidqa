from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd

from .video_tools import (
    convert_audio_video,
    convert_container,
    convert_only_audio,
    convert_only_video,
)


def get_next_video_to_reencode(file_path_report: Path) -> dict[str, str]:
    """
    Retrieves the next video to be reencoded based on the provided report file.

    Args:
        file_path_report (Path): Path object representing the file path of the
            report.

    Returns:
        Union[Dict[str, str], bool]: A dictionary containing the information of
            the next video to be reencoded
        if available, or False if there are no videos to reencode.

    Raises:
        FileNotFoundError: If the specified report file does not exist.
        Exception: If there is an issue while reading the report file.
    """

    # load dataframe
    try:
        df = pd.read_csv(file_path_report)
    except Exception as e:
        logging.error(f"Can't open file: {str(file_path_report)}")
        logging.error(e)

    # create mask to reencode
    mask_df_to_convert = ~df["type_conversion"].isin(["1_not_needed"])
    mask_df_convert_not_done = df["conversion_done"].isin([0])
    mask_df_to_convert = mask_df_to_convert & mask_df_convert_not_done

    # filter df to reencode
    df_to_convert = df.loc[mask_df_to_convert, :]

    # check if there is videos to reencode. Return False if note
    qt_videos_to_convert = df_to_convert.shape[0]

    if qt_videos_to_convert == 0:
        return False
    logging.info("There are %s videos to convert.", qt_videos_to_convert)

    # get first line as dict
    df_to_convert = df_to_convert.reset_index(drop=True)
    dict_first_line = df_to_convert.loc[0, :]
    return dict_first_line


def convert_video_from_dict(
    dict_metadata: dict[str, str],
    path_file_dest: str,
    flags: dict = {"crf": 18, "maxrate": 4},
) -> None:
    """convert video

    Args:
        dict_metadata (dict[str, str]): keys: ["path_file", "video_codec",
                                               "audio_codec", "format_name"]

        path_file_dest (str): file_path destination for converted video
        flags (dict, optional): video conversion flags.
            Defaults to {'crf': 18, 'maxrate': 4}.
    Return:
        (boolean): False if error.
    """

    video_codec = dict_metadata["video_codec"]
    audio_codec = dict_metadata["audio_codec"]
    audio_channels = dict_metadata["audio_channels"]
    format_name = dict_metadata["format_name"]

    path_file_origin = dict_metadata["path_file"]

    dict_func_conversion = {
        "2_container": {"func": convert_container, "name": "container"},
        "3_only_audio": {"func": convert_only_audio, "name": "only audio"},
        "4_only_video": {"func": convert_only_video, "name": "only video"},
        "5_total_conv": {
            "func": convert_audio_video,
            "name": "both audio and video",
        },
    }

    type_conversion = dict_metadata["type_conversion"]
    if type_conversion in dict_func_conversion:
        dict_optimal_conversion = dict_func_conversion[type_conversion]
        optimal_conversion_name = dict_optimal_conversion["name"]
        logging.info(
            "Start conversion '%s': %s-%s ac-%s-%s",
            optimal_conversion_name,
            audio_codec,
            audio_channels,
            video_codec,
            format_name,
        )
        optimal_conversion_func = dict_optimal_conversion["func"]
        optimal_conversion_func(path_file_origin, path_file_dest, flags)
        print("")
    else:
        logging.error(
            "type_conversion not recognized: %s",
            path_file_origin,
        )
        logging.info("File: %s", path_file_origin)
        sys.exit()


def get_file_name_dest(
    file_folder_origin: Path,
    file_name_origin: Path,
    prefix: str,
    file_extension: bool = None,
) -> Path:
    """
    Create a hashed file name through a unique identification from the path
    of the parent folder.

    Args:
        file_folder_origin (Path): file_folder_origin
        file_name_origin (Path): file_name_origin
        prefix (str): prefix
        file_extension (bool, optional): file_extension. Defaults to None.

    Returns:
        (Path): file name with hash
    """

    file_folder_origin_encode = str(file_folder_origin).encode("utf-8")
    hash = hashlib.md5(file_folder_origin_encode).hexdigest()[:5]
    file_name_origin_without_extension = file_name_origin.stem
    if file_extension is None:
        file_extension = file_name_origin.suffix
    else:
        file_extension = "." + file_extension

    file_name_dest = (
        prefix
        + str(file_name_origin_without_extension)
        + "_"
        + hash
        + file_extension
    )
    return Path(file_name_dest)


def update_file_report(
    path_file_report: Path,
    dict_video_data: dict[str, str],
    path_file_dest: Path,
) -> pd.DataFrame:
    try:
        df = pd.read_csv(path_file_report, dtype={"path_file_converted": str})
    except Exception as e:
        logging.error(f"Can't open file: {path_file_report}")
        logging.error(e)

    file_folder_origin = dict_video_data["file_path_folder"]
    file_name_origin = dict_video_data["file_name"]
    path_file_origin = Path(file_folder_origin) / file_name_origin

    # Check if file_name_dest exist
    if not path_file_dest.exists():
        logging.error(
            "After reencode, when update, "
            + f"reencoded file not exist:\n{path_file_dest}"
        )
        sys.exit()

    # locate index video in df
    mask_file_folder = df["file_path_folder"].isin([file_folder_origin])
    mask_file_name = df["file_name"].isin([file_name_origin])
    mask_line = mask_file_folder & mask_file_name
    df_filter = df.loc[mask_line, :]
    len_df_filter = len(df_filter)
    if len_df_filter != 1:
        logging.error(
            f"Need 1. Find {len_df_filter} line for "
            f"video: {path_file_origin}"
        )
        sys.exit()
    index_video = df_filter.index
    df.loc[index_video, "conversion_done"] = 1
    df.loc[index_video, "path_file_converted"] = str(path_file_dest.absolute())
    return df


def make_reencode(
    path_file_report: Path,
    path_folder_encoded: Path,
    flags: dict = {"crf": 18, "maxrate": 4},
) -> pd.DataFrame:
    """Converts all videos of the report.
        Required columns: file_path_folder, file_name, type_conversion

    Args:
        path_file_report (Path): report path. csv.
        path_folder_encoded (Path): converted videos folder path
        flags (dict, optional): video conversion flags. Defaults to
            {'crf': 18, 'maxrate': 4}.

    Returns:
        pd.DataFrame: updated report dataframe
    """

    def get_path_file_dest(dict_video_data, path_folder_encoded):
        # find path_folder_dest and path_file_dest
        file_folder_origin = Path(dict_video_data["file_path_folder"])
        file_name_origin = Path(dict_video_data["file_name"])

        file_name_dest = get_file_name_dest(
            file_folder_origin, file_name_origin, "", "mp4"
        )

        path_file_dest = path_folder_encoded / file_name_dest
        return path_file_dest

    df = pd.read_csv(path_file_report)
    # Ensure creation of column 'conversion_done'.
    if "conversion_done" not in df.columns:
        df["conversion_done"] = 0
        df["path_file_converted"] = ""
        # Save reports
        df.to_csv(path_file_report, index=False)

    need_reencode = True
    while need_reencode:
        dict_video_data = get_next_video_to_reencode(path_file_report)

        if dict_video_data is False:
            print("")
            logging.info("There are no videos to convert")
            need_reencode = False
            continue

        path_file_dest = get_path_file_dest(
            dict_video_data, path_folder_encoded
        )
        # run reencode
        convert_video_from_dict(dict_video_data, path_file_dest, flags)

        # after reencode, update flag conversion_done
        df = update_file_report(
            path_file_report, dict_video_data, path_file_dest
        )

        # Save reports
        df.to_csv(path_file_report, index=False)
    return df
