from __future__ import annotations

import logging
import os


def convert_only_audio(
    path_file_video_origin: str, path_file_video_dest: str
) -> None:
    """Make release for mp4 H264/AAC reencoding only audio

    Args:
        path_file_video_origin (str): Original video file path
        path_file_video_dest (str): Path of the edited video file
    """

    logging.info("Convert only audio: %s", path_file_video_origin)

    stringa = (
        f'ffmpeg -v quiet -stats -y -i "{path_file_video_origin}" '
        + "-vcodec copy "
        + "-c:a aac "
        + "-ac 2 "
        + f'"{path_file_video_dest}"'
    )
    print("\n", stringa)
    os.system(stringa)
    logging.info("Done")


def convert_mp4_wo_reencode(
    path_file_video_origin: str, path_file_video_dest: str
) -> None:
    """Make release for mp4 H264/AAC without reencode

    Args:
        path_file_video_origin (str): Original video file path
        path_file_video_dest (str): Path of the edited video file
    """

    logging.info(
        "Convert video extension without reencode: %s", path_file_video_origin
    )

    stringa = (
        f'ffmpeg -v quiet -stats -y -i "{path_file_video_origin}" '
        + "-vcodec copy "
        + f'-acodec copy "{path_file_video_dest}"'
    )
    print("\n", stringa)
    os.system(stringa)
    logging.info("Done")


def convert_mp4_aac_get_stringa(
    path_file_video_origin: str,
    path_file_video_dest: str,
    flags: dict = {"crf": 18, "maxrate": 4},
) -> str:
    """get ffmpeg command to reencode a video as mp4 H264/AAC

    Args:
        path_file_video_origin (str): input video path
        path_file_video_dest (str): output video path
        flags (dict, optional): video conversion flags.
            Defaults to {'crf': 18, 'maxrate': 4}.

    Returns:
        str: ffmpeg string command
    """

    crf = float(flags.get("crf", 18))
    maxrate = float(flags.get("maxrate", 4))
    bufsize = maxrate * 2
    stringa = (
        "ffmpeg -v quiet -stats -y "
        + f'-i "{path_file_video_origin}" '
        + "-c:v libx264 "
        + f"-crf {str(crf)} "
        + f"-maxrate {str(maxrate)}M "
        + f"-bufsize {str(bufsize)}M "
        + "-preset ultrafast "
        + "-flags +global_header "
        + "-pix_fmt yuv420p "
        + "-profile:v baseline "
        + "-tune zerolatency "
        + "-movflags +faststart "
        + "-c:a aac "
        + "-ac 2 "
        + f'"{path_file_video_dest}"'
    )
    return stringa


def convert_mp4_aac(
    path_file_video_origin: str,
    path_file_video_dest: str,
    flags: dict = {"crf": 18, "maxrate": 4},
) -> None:
    """Make release for mp4 H264/AAC

    Args:
        path_file_video_origin (str): Original video file path
        path_file_video_dest (str): Path of the edited video file
        flags (dict, optional): video conversion flags.
            Defaults to {'crf': 18, 'maxrate': 4}.
    """

    stringa = convert_mp4_aac_get_stringa(
        path_file_video_origin, path_file_video_dest, flags
    )
    print("\n", stringa)
    os.system(stringa)
    logging.info("Done")
