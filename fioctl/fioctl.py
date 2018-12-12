import click

from .config import config as fioconf
from datetime import datetime
from . import fio
from .projects import projects

@click.group()
def cli():
    """Frame.io on the command line"""

@cli.command(help="Updates/reads fioctl config, depending on if the value arg is present")
@click.argument("path")
@click.argument("value", required=False)
def config(path, value):
    path = path.split(".")
    if not value:
        click.secho(str(fioconf.fetch(path[0], path[1])))
        return
    
    fioconf.set_config(path[0], path[1], value)

cli.add_command(projects)