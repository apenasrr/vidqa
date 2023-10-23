from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

import pandas as pd

from .ffprobe_micro import ffprobe


def get_video_codec(stream_video: dict) -> str:
    video_codec = stream_video["codec_name"]
    return video_codec


def get_video_profile(stream_video: dict) -> str:
    video_profile = stream_video.get("profile", "")
    if video_profile == "":
        logging.info("Not have video_profile")
    return video_profile


def get_video_resolution_height(stream_video: dict) -> str:
    video_resolution_height = stream_video["height"]
    return video_resolution_height


def get_video_resolution_width(stream_video: dict) -> str:
    video_resolution_width = stream_video["width"]
    return video_resolution_width


def get_video_bitrate(dict_inf: dict, stream_video: dict) -> int:
    """Bitrate search. It may be in one of the 2 possible places.

    Args:
        dict_inf (dict): video metadata
        stream_video (dict): video stream data

    Raises:
        NameError: If Bitrate is not found in any of the possible places

    Returns:
        int: video bitrate
    """

    try:
        video_bitrate = stream_video["bit_rate"]
    except Exception as e:
        try:
            video_bitrate = dict_inf["format"]["bit_rate"]
        except Exception as e:
            video_bitrate = 0

    return int(video_bitrate)


def get_is_avc(stream_video: dict) -> int:
    try:
        is_avc_str = stream_video["is_avc"]
        if is_avc_str == "true":
            is_avc = 1
        else:
            is_avc = 0
    except Exception as e:
        is_avc = 0
    return is_avc


def get_audio_codec(stream_audio: dict) -> str:
    return stream_audio["codec_name"]


def get_audio_channels(stream_audio: dict) -> int:
    return stream_audio.get("channels", 0)


def timedelta_to_string(timestamp) -> str:
    microsec = timedelta(microseconds=timestamp.microseconds)
    timestamp = timestamp - microsec
    hou, min_full = divmod(timestamp.seconds, 3600)
    min, sec = divmod(min_full, 60)
    str_microsec = int(microsec.microseconds / 10000)
    str_timestamp = "%02d:%02d:%02d.%02d" % (hou, min, sec, str_microsec)

    return str_timestamp


def float_seconds_to_string(float_sec: float) -> str:
    """Convert seconds in float, to string in format hh:mm:ss

    Args:
        float_sec (float): Seconds

    Returns:
        String: Time in format hh:mm:ss
    """

    timedelta_seconds = timedelta(seconds=float_sec)

    # format string: hh:mm:ss
    string_timedelta = timedelta_to_string(timestamp=timedelta_seconds)
    return string_timedelta


def get_duration_ffprobe(dict_inf: dict) -> dict:
    d = {}
    try:
        file = dict_inf["format"]["filename"]
    except Exception as e:
        print("")
        logging.error("Video without format-filename metadata:\n%s", dict_inf)
        print("")
        logging.error(e)
        return False

    try:
        duration_unformat = dict_inf["format"]["duration"]
        duration = float_seconds_to_string(float_sec=float(duration_unformat))
        d["duration_str"] = duration
        d["duration_seconds"] = float(duration_unformat)
    except Exception as e:
        logging.error(e)
        logging.error(
            "Video without duration:\n%s\n"
            + "Please check and delete the file if "
            + "necessary",
            file,
        )
        return False
    return d


def get_inf_ffprobe(list_path_file: list[Path]) -> dict:
    """
    Extracts FFprobe metadata for a list of video files.

    Args:
        list_path_file (list[Path]): A list of file paths for which FFprobe metadata
        needs to be extracted.

    Returns:
        dict: A dictionary containing two keys - 'metadata' and 'corrupt'.
              - 'metadata': A list of dictionaries, each containing 'path_file'
                (file path) and 'metadata' (video metadata).
              - 'corrupt': A list of file paths for likely corrupted or
                unsupported video files.

    Example:
        list_path_file = ["path/to/video1.mp4", "path/to/video2.avi"]
        result = get_list_dict_inf_ffprobe(list_path_file)
        metadata_list = result['metadata']
        corrupt_files = result['corrupt']

    Note:
        - Is considered corrupted and added to the 'corrupt' list when:
          - If FFprobe fails to extract metadata for a file or
          - If metadata does not contain format-filename key or
          - If metadata does not contain format-duration key.
    """

    list_path_corrupt = []
    list_dict = []
    for file_selected in list_path_file:
        d = {}
        d["path_file"] = str(file_selected)
        logging.info("run ffprobe: %s", file_selected)
        # generate raw metadata
        dict_inf_ffprobe = ffprobe(file_selected).get_output_as_dict()

        # corrupted for lack of metadata
        if len(dict_inf_ffprobe) == 0:
            logging.error(
                "File likely corrupted-No metadata:\n" + "_" * 25 + "%s\n",
                file_selected,
            )
            list_path_corrupt.append(file_selected)
            continue

        # corrupt by lack of format-filename metadata
        try:
            _ = dict_inf_ffprobe["format"]["filename"]
        except Exception as e:
            d["metadata"] = dict_inf_ffprobe
            list_dict.append(d)
            list_path_corrupt.append(file_selected)
            continue

        # corrupt by lack of duration metadata
        try:
            _ = dict_inf_ffprobe["format"]["duration"]
        except Exception as e:
            logging.error(
                "%s\nVideo without format-filename metadata:\n%s",
                e,
                dict_inf_ffprobe,
            )
            d["metadata"] = dict_inf_ffprobe
            list_dict.append(d)
            list_path_corrupt.append(file_selected)
            continue

        d["metadata"] = dict_inf_ffprobe
        list_dict.append(d)
    return {"metadata": list_dict, "corrupt": list_path_corrupt}


def get_total_bitrate(dict_inf: dict) -> int:
    """Total Bitrate search.

    Args:
        dict_inf (dict): video metadata

    Returns:
        int: video bitrate
    """

    try:
        total_bitrate = int(dict_inf["format"]["bit_rate"])
    except Exception as e:
        total_bitrate = 0
        logging.error(dict_inf)
        logging.error(e)
        file = dict_inf["format"]["filename"]
        msg_err = (
            "File bellow don't have 'total_bitrate' in "
            + f"detail file:\n{file}"
        )
        logging.error(msg_err)

    return total_bitrate


def format_video_metadata(list_dict_inf_ffprobe: list[dict[str, str]]):
    """Generates video metadata report

    Args:
        list_dict_inf_ffprobe (list[dict[str, str]]):
            List of Dictionaries returned from FFProbe Metadata Analysis

    Returns:
        list[dict]: List of Dictionaries formatted
    """

    list_dict = []
    for dict_file in list_dict_inf_ffprobe:
        path_file = dict_file["path_file"]
        logging.info("parsing: %s", path_file)
        dict_inf_ffprobe = dict_file["metadata"]
        # parse data
        duration_dict = get_duration_ffprobe(dict_inf=dict_inf_ffprobe)
        if duration_dict is False:
            logging.error("!File seems corrupt.\n")
            continue
        duration = duration_dict["duration_str"]
        duration_seconds = duration_dict["duration_seconds"]
        total_bitrate = get_total_bitrate(dict_inf_ffprobe)
        format_name = dict_inf_ffprobe["format"]["format_name"]

        is_video = False
        for stream in dict_inf_ffprobe["streams"]:
            if stream["codec_type"] == "video":
                stream_video = stream
                is_video = True
                break

        if is_video:
            video_codec = get_video_codec(stream_video)
            video_profile = get_video_profile(stream_video)
            video_resolution_height = get_video_resolution_height(stream_video)
            video_resolution_width = get_video_resolution_width(stream_video)
            video_bitrate = get_video_bitrate(dict_inf_ffprobe, stream_video)
            is_avc = get_is_avc(stream_video)
        else:
            logging.error(
                "File above don't have tag 'video' in "
                + f"detail file:\n{path_file}"
            )
            continue

        has_audio = False
        for stream in dict_inf_ffprobe["streams"]:
            if stream["codec_type"] == "audio":
                stream_audio = stream
                has_audio = True
                break

        if has_audio is False:
            logging.info(
                "File above don't have tag 'audio' in "
                + f"detail file:\n{path_file}"
            )
            has_audio = False

        if has_audio:
            audio_codec = get_audio_codec(stream_audio)
            audio_channels = get_audio_channels(stream_audio)

        else:
            audio_codec = ""
            audio_channels = 0

        # generate dict
        d = {}
        d["duration"] = duration
        d["duration_seconds"] = duration_seconds
        d["file_size"] = Path(path_file).stat().st_size
        d["format_name"] = format_name
        d["total_bitrate"] = total_bitrate
        d["video_bitrate"] = video_bitrate
        d["video_codec"] = video_codec
        d["audio_codec"] = audio_codec
        d["audio_channels"] = audio_channels
        d["is_avc"] = is_avc
        d["video_profile"] = video_profile
        d["video_resolution_height"] = video_resolution_height
        d["video_resolution_width"] = video_resolution_width
        d["path_file"] = path_file
        d["file_path_folder"] = str(Path(path_file).parent)
        d["file_name"] = Path(path_file).name
        list_dict.append(d)

    return list_dict


def include_type_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Determines the required type of conversion for each video in the DataFrame
    and creates a 'type_conversion' column accordingly.

    Conversion Types:
    - '1_not_needed': No conversion needed.
    - '2_container': Container conversion needed.
    - '3_only_audio': Audio conversion needed.
    - '4_only_video': Video conversion needed.
    - '5_total_conv': Audio and video conversion needed.

    Args:
        df (pd.DataFrame): Input DataFrame containing video information.
            It must have the following columns:
            - 'video_codec': Video codec information.
            - 'audio_codec': Audio codec information.
            - 'audio_channels': Number of audio channels.
            - 'is_avc': AVC (Advanced Video Coding) flag.
            - 'path_file': File path of the video file.
            - 'format_name': Video file format name.

    Returns:
        pd.DataFrame: DataFrame with an added 'type_conversion' column
            indicating the required conversion type.
    """

    # check if Dataframe has the necessary columns
    required_columns = [
        "video_codec",
        "audio_codec",
        "audio_channels",
        "is_avc",
        "path_file",
        "format_name",
    ]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

    mask_cv_ok = df["video_codec"].isin(["h264"])
    mask_ca_ok = df["audio_codec"].isin(["aac"])
    mask_ac_ok = df["audio_channels"] <= 2
    mask_isavc = df["is_avc"].isin([1])
    mask_mp4 = df["path_file"].apply(
        lambda x: Path(x).suffix.lower() == ".mp4"
    )
    mask_format = df["format_name"] == "mov,mp4,m4a,3gp,3g2,mj2"

    stream_video_ok = mask_cv_ok
    audio_stream_ok = mask_ca_ok & mask_ac_ok
    container_ok = mask_mp4 & mask_format & mask_isavc

    df["type_conversion"] = ""

    mask_1_not_needed = stream_video_ok & audio_stream_ok & container_ok
    df.loc[mask_1_not_needed, "type_conversion"] = "1_not_needed"

    mask_2_container = (stream_video_ok & audio_stream_ok) & ~container_ok
    df.loc[mask_2_container, "type_conversion"] = "2_container"

    mask_3_only_audio = stream_video_ok & ~audio_stream_ok
    df.loc[mask_3_only_audio, "type_conversion"] = "3_only_audio"

    mask_4_only_video = ~stream_video_ok & audio_stream_ok
    df.loc[mask_4_only_video, "type_conversion"] = "4_only_video"

    mask_5_total_conv = ~stream_video_ok & ~audio_stream_ok
    df.loc[mask_5_total_conv, "type_conversion"] = "5_total_conv"
    return df
