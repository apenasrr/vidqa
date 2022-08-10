import logging
import os
from datetime import timedelta

import pandas as pd

from .ffprobe_micro import ffprobe


def get_video_codec(stream_video: dict) -> str:

    video_codec = stream_video["codec_name"]
    return video_codec


def get_video_profile(stream_video: dict) -> str:

    try:
        video_profile = stream_video["profile"]
    except Exception as e:
        logging.info("Not have video_profile: %s", e)
        video_profile = ""
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
            logging.error(dict_inf)
            logging.error(e)
            file = dict_inf["format"]["filename"]
            msg_err = (
                "File bellow don't have 'bit_rate' in "
                + f"detail file:\n{file}"
            )
            logging.error(msg_err)
            raise NameError(msg_err)

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

    audio_codec = stream_audio["codec_name"]
    return audio_codec


def get_list_path_video(path_dir: str, video_extensions: list) -> list:

    # To input more file video extension:
    #  https://dotwhat.net/type/video-movie-files

    tuple_video_extension_raw = tuple(video_extensions)
    tuple_video_extension = tuple(
        "." + ext for ext in tuple_video_extension_raw
    )
    str_tuple_video_extension = ", ".join(tuple_video_extension)
    logging.info(f"Find for video with extension: {str_tuple_video_extension}")
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
        logging.error("%s", dict_inf)
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
        d["duration_str"] = ""
        d["duration_seconds"] = ""

    return d


def get_list_dict_report_video_metadata(list_path_file: list):
    """Generates video metadata report in list of dict

    Args:
        list_path_file (list): Video file lists

    Returns:
        list[dict]: Video Metadata
    """

    list_dict_inf_ffprobe = get_list_dict_inf_ffprobe(list_path_file)
    list_dict_report_video_metadata = format_video_metadata(
        list_dict_inf_ffprobe
    )
    return list_dict_report_video_metadata


def get_list_dict_inf_ffprobe(list_path_file: list):
    """Returns metadata from a video file lists

    Args:
        list_path_file (list): Video file lists

    Returns:
        list[dict]: Video Metadata
    """

    list_dict = []
    for file_selected in list_path_file:
        d = {}
        d["path_file"] = file_selected
        logging.info("run ffproble: %s", file_selected)
        # generate raw metadata
        dict_inf_ffprobe = ffprobe(file_selected).get_output_as_dict()
        d["metadata"] = dict_inf_ffprobe
        list_dict.append(d)
    return list_dict


def format_video_metadata(list_dict_inf_ffprobe):
    """Generates video metadata report in list of dict

    Args:
        list_dict_inf_ffprobe (list[dict]):
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
            # TODO: export dict as json file
            continue
        duration = duration_dict["duration_str"]
        duration_seconds = duration_dict["duration_seconds"]
        total_bitrate = int(dict_inf_ffprobe["format"]["bit_rate"])
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
        else:
            audio_codec = ""

        # generate dict
        d = {}
        d["duration"] = duration
        d["duration_seconds"] = duration_seconds
        d["file_size"] = os.path.getsize(path_file)
        d["format_name"] = format_name
        d["total_bitrate"] = total_bitrate
        d["video_bitrate"] = video_bitrate
        d["video_codec"] = video_codec
        d["audio_codec"] = audio_codec
        d["is_avc"] = is_avc
        d["video_profile"] = video_profile
        d["video_resolution_height"] = video_resolution_height
        d["video_resolution_width"] = video_resolution_width
        d["path_file"] = path_file
        d["file_path_folder"] = os.path.dirname(path_file)
        d["file_name"] = os.path.split(path_file)[1]
        list_dict.append(d)

    return list_dict


def include_video_to_convert(df: pd.DataFrame) -> pd.DataFrame:
    """Define which videos should be converted.

    Args:
        df (pd.DataFrame): video_details dataframe.
            Required columns: 'video_codec', 'audio_codec', 'is_avc',
                              'format_name'
    Returns:
        pd.DataFrame:
            Original dataframe with new column 'to_convert'
    """

    mask_cv_ok = df["video_codec"].isin(["h264"])
    mask_ca_ok = df["audio_codec"].isin(["aac"])
    mask_isavc = df["is_avc"].isin([1])
    mask_mp4 = df["path_file"].apply(
        lambda x: os.path.splitext(x)[-1].lower() == ".mp4"
    )
    mask_format = df["format_name"] == "mov,mp4,m4a,3gp,3g2,mj2"
    mask_ok = mask_cv_ok & mask_ca_ok & mask_isavc & mask_mp4 & mask_format
    df["to_convert"] = 0
    df.loc[~mask_ok, "to_convert"] = 1
    return df
