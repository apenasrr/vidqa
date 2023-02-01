from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd

from .video_tools import (
    convert_mp4_aac,
    convert_mp4_wo_reencode,
    convert_only_audio,
)


def get_next_video_to_reencode(path_file_report: Path) -> dict[str, str]:

    # load dataframe
    try:
        df = pd.read_csv(path_file_report)
    except Exception as e:
        logging.error(f"Can't open file: {str(path_file_report)}")
        logging.error(e)

    # create mask to reencode
    mask_df_to_convert = ~df["to_convert"].isin([0])
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
    dict_metadata: dict[str, str], path_file_dest: str
) -> None:
    """convert video

    Args:
        dict_metadata (dict[str, str]): keys: ["path_file", "video_codec",
                                               "audio_codec", "format_name"]

        path_file_dest (str): file_path destination for converted video
    Return:
        (boolean): False if error.
    """

    path_file_origin = dict_metadata["path_file"]

    video_codec = dict_metadata["video_codec"]
    audio_codec = dict_metadata["audio_codec"]
    format_name = dict_metadata["format_name"]

    # Make video conversion
    if video_codec == "h264" and audio_codec == "aac":
        logging.info(
            "Start conversion without reencode: %s-%s-%s | %s",
            audio_codec,
            video_codec,
            format_name,
            path_file_origin,
        )
        convert_mp4_wo_reencode(path_file_origin, path_file_dest)
    elif video_codec == "h264":
        # elif video_codec == "h264" and format_name == "mov,mp4,m4a,3gp,3g2,mj2":
        logging.info(
            "Start conversion only audio: %s-%s-%s | %s",
            audio_codec,
            video_codec,
            format_name,
            path_file_origin,
        )
        convert_only_audio(path_file_origin, path_file_dest)
    else:
        logging.info(
            "Start reencode: %s-%s-%s | %s",
            audio_codec,
            video_codec,
            format_name,
            path_file_origin,
        )
        convert_mp4_aac(path_file_origin, path_file_dest)


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
        df = pd.read_csv(path_file_report)
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
    path_file_report: Path, path_folder_encoded: Path
) -> pd.DataFrame:
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
        convert_video_from_dict(dict_video_data, path_file_dest)

        # after reencode, update flag conversion_done
        df = update_file_report(
            path_file_report, dict_video_data, path_file_dest
        )

        # Save reports
        df.to_csv(path_file_report, index=False)
    return df
