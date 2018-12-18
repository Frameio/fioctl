import click

from .config import config as fioconf
from datetime import datetime
from . import fio
from .projects import projects
from .audit_logs import audits
from .accounts import accounts
from .teams import teams
from .assets import assets
from .users import users
from .comments import comments
from .presentations import presentations
from .review_links import review_links

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

@cli.command(help='Sets (or returns) the current profile')
@click.argument('profile', required=False)
def profile(profile):
    if not profile:
        click.echo(fioconf.fetch('profiles', 'default') or 'default')
        return

    fioconf.set_config('profiles', 'default', profile)

cli.add_command(projects)
cli.add_command(audits)
cli.add_command(accounts)
cli.add_command(teams)
cli.add_command(assets)
cli.add_command(users)
cli.add_command(comments)
cli.add_command(presentations)
cli.add_command(review_links)