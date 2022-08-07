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

    logging.info(
        "Convert video extension without reencode: %s", path_file_video_origin
    )

    stringa = (
        f'ffmpeg -y -i "{path_file_video_origin}" '
        + "-vcodec copy "
        + f'-c:a aac "{path_file_video_dest}"'
    )

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
        f'ffmpeg -y -i "{path_file_video_origin}" '
        + "-vcodec copy "
        + f'-acodec copy "{path_file_video_dest}"'
    )

    os.system(stringa)
    logging.info("Done")


def convert_mp4_aac(
    path_file_video_origin: str, path_file_video_dest: str
) -> None:
    """Make release for mp4 H264/AAC

    Args:
        path_file_video_origin (str): Original video file path
        path_file_video_dest (str): Path of the edited video file
    """

    stringa = (
        f'ffmpeg -y -i "{path_file_video_origin}" '
        + "-c:v libx264 "
        + "-crf 18 "
        + "-maxrate 2.5M "
        + "-bufsize 4M "
        + "-preset ultrafast "
        + "-flags +global_header "
        + "-pix_fmt yuv420p "
        + "-profile:v baseline "
        + "-tune zerolatency "
        + "-movflags +faststart "
        + f'-c:a aac "{path_file_video_dest}"'
    )

    os.system(stringa)
    logging.info("Done")
