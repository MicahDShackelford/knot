import click

from knot import __version__
from knot.utils.output import dict_to_type

@click.command()
@click.option('-o', '--output', default=None, help="Output the version in another format")
def version(output):
    """Get the current version of knot."""

    if output:
        click.echo(dict_to_type({
            'version': __version__
        }, output))
    else:
        click.echo(click.style(f"knot version v{__version__}"))
    