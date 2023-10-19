"""Console script for vidqa."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Union

import click

from . import config, sanitize_files, show_corrupt_videos, vidqa


def one_time(
    folder_path: Path,
    path_folder_convert: Union[Path, None],
    video_extensions: tuple,
):
    """Analyze the videos of a folder. Unique log file.
    Ensure that:
    - H264/AAC codec standard for all videos
    - All file paths have up to 260 characters

    Args:
        folder_input (Path): input path folder
        path_folder_convert (Path): A path to host the converted videos folder
        and report file, or `None` if no folder path is provided.
        video_extensions (tuple): video extensions to be analyzed
    """

    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    vidqa(
        folder_path,
        report_path=None,
        path_folder_convert=path_folder_convert,
        video_extensions=video_extensions,
    )
    show_corrupt_videos(folder_path, path_folder_convert)


def batch_mode(
    folder_path: Path,
    path_folder_convert: Union[Path, None],
    video_extensions: tuple,
):
    """Analyze the videos of each internal folders. Multiple log files.
    Ensure that:
    - H264/AAC codec standard for all videos
    - All file paths have up to 260 characters

    Args:
        folder_path (Path): input path folder
        path_folder_convert (Path): A path to host the converted videos folder
        and report file, or `None` if no folder path is provided.
        video_extensions (tuple): video extensions to be analyzed
    """

    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    config_file = Path(__file__).absolute().parent / "config.ini"
    config_data = config.get_data(config_file)
    max_path = int(config_data.get("max_path", 260))
    max_name = int(config_data.get("max_name", 150))
    sanitize_files(
        folder_path=folder_path, max_path=max_path, max_name=max_name
    )

    list_folder_path = [
        path for path in folder_path.iterdir() if path.is_dir()
    ]
    for folder_path in list_folder_path:
        vidqa(
            folder_path,
            report_path=None,
            path_folder_convert=path_folder_convert,
            video_extensions=video_extensions,
        )
    for folder_path in list_folder_path:
        show_corrupt_videos(folder_path, path_folder_convert)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "-i",
    "--folder_input",
    required=False,
    type=click.STRING,
    help="Input folder path",
)
@click.option(
    "-m",
    "--mode",
    required=False,
    default="unique",
    type=click.Choice(["unique", "batch"]),
    help="Type execution",
)
@click.option(
    "-fd",
    "--folder_destination",
    required=False,
    type=click.STRING,
    help="Temp converted videos and report folder",
)
def main(
    ctx: click.core.Context,
    folder_input: str,
    mode: str,
    folder_destination: str,
):
    """Console script for vidqa."""

    def get_path_folder_convert(
        config_data: dict, temp_folder: Union[str, None]
    ) -> Union[Path, None]:
        """Returns a `pathlib.Path` object representing the specified temporary
            folder path, or `None` if no path is provided.

        Args:
            config_data (dict): keys required: default_destination,
                                               folder_destination
            temp_folder (Union[str, None]): A string representing the path to
                host the converted videos folder and report file,
                or `None` if no folder path is provided.

        Raises:
            ValueError: If the specified temporary folder path is not valid.

        Returns:
            Union[Path, None]: A `pathlib.Path` object representing the
                specified temporary folder path, or `None` if no path is
                provided.
        """

        default_destination = int(config_data.get("default_destination", 0))
        if default_destination == 1:
            temp_folder = Path(config_data.get("folder_destination", None))

        if temp_folder is not None:
            path_folder_convert = Path(temp_folder)
            if not path_folder_convert.resolve():
                raise ValueError("Temp folder is not valid")
            return path_folder_convert
        return None

    if not ctx.invoked_subcommand:
        config_file = Path(__file__).absolute().parent / "config.ini"
        config_data = config.get_data(config_file)
        video_extensions = config_data["video_extensions"].split(",")
        if folder_input is None:
            print(
                "Select a mode of use\n"
                + "unique: Process all videos of a folder as a single "
                + "analysis project.\n"
                + "batch: From the Input folder, it treats each internal "
                + "folder as an independent analysis project.\n"
            )
            mode = input("Mode (unique / batch): ")
            folder_path = Path(input("Input folder: "))
            print(
                "\nFolder where the analysis report and temporary videos "
                + "should be stored during the conversion process."
            )
            path_folder_convert = Path(input("Report/Temp folder: "))
        else:
            folder_path = Path(folder_input)
            path_folder_convert = get_path_folder_convert(
                config_data, folder_destination
            )

        if mode == "unique":
            one_time(folder_path, path_folder_convert, video_extensions)
        else:
            batch_mode(folder_path, path_folder_convert, video_extensions)

        return 0


@main.command()
@click.option(
    "-c",
    "--crf",
    required=False,
    type=click.FLOAT,
    help="set crf",
)
@click.option(
    "-x",
    "--maxrate",
    required=False,
    type=click.FLOAT,
    help="set maxrate",
)
@click.option(
    "-fd",
    "--folder_dest",
    required=False,
    type=click.STRING,
    help="set folder_destination",
)
@click.option(
    "-dd",
    "--default_dest",
    required=False,
    type=click.Choice(["0", "1"]),
    help="set default_destination",
)
@click.option(
    "-mp",
    "--max_path",
    required=False,
    type=click.INT,
    help="set maximum file path length",
)
@click.option(
    "-mn",
    "--max_name",
    required=False,
    type=click.INT,
    help="set maximum file name length",
)
def flags(
    crf: Union[float, None],
    maxrate: Union[float, None],
    folder_dest: Union[str, None],
    default_dest: Union[str, None],
    max_path: Union[int, None],
    max_name: Union[int, None],
):
    """Update Flags from Config.ini file

    Args:
        crf (Union[float, None]): Constant Rate Factor (CRF) value to be set.
            Recommended to keep up between 18 to 35.
        maxrate (Union[float, None]): Maximum bitrate value to be set.
        folder_dest (Union[str, None]): Folder destination to save the output
            file.
        default_dest (Union[str, None]): Default folder to save the output
            file. If zero, the parent origin folder will be used.
        max_path (Union[int, None]): Maximum file path length.
        max_name (Union[int, None]): Maximum file name length.
    Raises:
        ValueError: If the given CRF value is not a number
            or not between 0 and 51
            or the given maximum bitrate value is not a positive number.
    """

    config_file = Path(__file__).absolute().parent / "config.ini"
    if crf is not None:
        try:
            crf = float(crf)
        except ValueError as e:
            raise ValueError("The CRF value should be a number.") from e
        if not 0 <= crf <= 51:
            raise ValueError("The CRF value should be between 0 and 51.")

        config.set_data(config_file, variable="crf", value=str(crf))
        click.echo(f"Flag crf set to: {crf}")
    elif maxrate:
        maxrate_error_msg = "The maxrate value should be a positive number"
        try:
            maxrate = float(maxrate)
            if maxrate <= 0:
                raise ValueError(maxrate_error_msg)
        except ValueError as e:
            raise ValueError(maxrate_error_msg) from e
        config.set_data(config_file, variable="maxrate", value=str(maxrate))
        click.echo(f"Flag maxrate set to: {maxrate}")
    elif folder_dest:
        config.set_data(
            config_file, variable="folder_destination", value=str(folder_dest)
        )
        click.echo(f"Flag folder_destination set to: {folder_dest}")
    elif default_dest:
        config.set_data(
            config_file,
            variable="default_destination",
            value=str(default_dest),
        )
        click.echo(f"Flag default_destination set to: {default_dest}")
    elif max_path:
        config.set_data(config_file, variable="max_path", value=str(max_path))
        click.echo(f"Flag max_path set to: {max_path}")
    elif max_name:
        config.set_data(config_file, variable="max_name", value=str(max_path))
        click.echo(f"Flag max_name set to: {max_name}")
    else:
        click.echo("--Actual flags--")
        config_data = config.get_data(config_file)
        for key, value in config_data.items():
            click.echo(f"{key}: {value}")


if __name__ == "__main__":
    sys.exit(main())
