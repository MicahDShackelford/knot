import click
import os

from knot import __version__
from knot.utils.output import dict_to_type
from knot.utils.config import put_knot

@click.command()
@click.argument('path', default=".")
def use(path):
    """Install a knot into your user configuration."""

    # Path we are using
    path = (os.path
        .abspath(os.path.join(os.getcwd(), path))
        .rstrip('/'))
    
    put_knot(path)