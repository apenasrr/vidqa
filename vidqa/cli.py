"""Console script for vidqa."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from . import config, sanitize_files, vidqa


def one_time(folder_path: Path, video_extensions: tuple):
    """Analyze the videos of a folder. Unique log file.
    Ensure that:
    - H264/AAC codec standard for all videos
    - All file paths have up to 260 characters

    Args:
        folder_input (str): input path folder
        video_extensions (tuple): video extensions to be analyzed
    """

    report_file_name = folder_path.name + ".csv"
    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    vidqa(folder_path, report_file_name, video_extensions=video_extensions)


def batch_mode(folder_path: Path, video_extensions: tuple):
    """Analyze the videos of each internal folders. Multiple log files.
    Ensure that:
    - H264/AAC codec standard for all videos
    - All file paths have up to 260 characters

    Args:
        folder_path (Path): input path folder
        video_extensions (tuple): video extensions to be analyzed
    """

    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    sanitize_files(folder_path)

    list_folder_path = [
        path for path in folder_path.iterdir() if path.is_dir()
    ]
    for folder_path in list_folder_path:

        report_file_name = Path(folder_path.name + ".csv")
        vidqa(folder_path, report_file_name, video_extensions=video_extensions)


@click.command()
@click.option(
    "-i",
    "--folder_input",
    required=True,
    type=click.STRING,
    help="Input folder path",
)
@click.option(
    "-m",
    "--mode",
    required=True,
    default="unique",
    type=click.Choice(["unique", "batch"]),
    help="Type execution",
)
def main(folder_input: str, mode: str):
    """Console script for vidqa."""

    click.echo("vidqa.cli.main")

    config_file = Path(__file__).absolute().parent / "config.ini"
    config_data = config.get_data(config_file)
    video_extensions = config_data["video_extensions"].split(",")
    folder_path = Path(folder_input)
    if mode == "unique":
        one_time(folder_path, video_extensions)
    else:
        batch_mode(folder_path, video_extensions)

    return 0


if __name__ == "__main__":
    folder_input = input("input: ")
    mode = input("mode: ")
    sys.exit(main(folder_input, mode))  # pragma: no cover
