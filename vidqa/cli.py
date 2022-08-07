"""Console script for vidqa."""
import os
import sys

import click

from . import config, vidqa


def one_time(input: str, video_extensions: tuple):

    report = os.path.basename(input) + ".csv"
    vidqa.vidqa(input, report, video_extensions=video_extensions)


def batch_mode(input: str, video_extensions: tuple):

    list_dir_name = os.listdir(input)
    for dir_name in list_dir_name:
        path_dir = os.path.join(input, dir_name)
        report = os.path.basename(path_dir) + ".csv"
        vidqa.vidqa(path_dir, report, video_extensions=video_extensions)


@click.command()
@click.option(
    "-i",
    "--input",
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
def main(input: str, mode: str):
    """Console script for vidqa."""

    click.echo("vidqa.cli.main")
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(os.path.abspath(__file__))),
        "config.ini",
    )

    config_data = config.get_data(config_file)
    video_extensions = config_data["video_extensions"].split(",")

    if mode == "unique":
        one_time(input, video_extensions)
    else:
        batch_mode(input, video_extensions)

    return 0


if __name__ == "__main__":
    input_ = input("input: ")
    mode = input("mode: ")
    sys.exit(main(input_, mode))  # pragma: no cover
