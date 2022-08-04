"""Console script for vidqa."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for vidqa."""
    click.echo("Replace this message by putting your code into "
               "vidqa.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
