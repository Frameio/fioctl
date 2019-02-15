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
    """
Frame.io on the command line

Commands are organized by application types.  So there are command groups like assets, projects,
teams, etc.  For the most part, they follow a RESTful pattern like the api itself, so you'll find
`fioctl teams list` as an option along with get, set, create, etc.

Shared Options:

    --format FORMAT - either table,csv,json, or occasionally tree

    --columns LIST - a comma separated lists of attributes you want to project to the console, with dot 
    operator support.  EG `id,name,properties.prop`

    --values UPDATE - used on update commands, similar to `--columns` but accepts an attribute like name=val. 
    It still supports the dot operator and is comma separated.

Basics:

    - To save preferred columns for a command group like `fioctl config assets.columns id,name,parent_id`

    - To set default table format, `fioctl config table.fmt psql` (see pypi docs for tabulate for options)

    - To create a profile:
    ```
    fioctl my_profile.bearer_token <token> # generate an access token in Frame.io
    fioctl profile my_profile # sets the current profile to my_profile
    ```
    """

@cli.command(help="Set up a profile for fioctl")
def configure():
    profile = click.prompt("Enter a profile name", default='default')
    token   = click.prompt("Enter the token for this profile")

    fioconf.set_config(profile, 'bearer_token', token)
    fioconf.set_config('profiles', 'default', profile)

@cli.command(help="Updates/reads fioctl config, depending on if the value arg is present")
@click.argument("path")
@click.argument("value", required=False)
def config(path, value):
    path = path.split(".")
    if not value:
        click.secho(str(fioconf.fetch(path[0], path[1])))
        return
    
    fioconf.set_config(path[0], path[1], value)

@cli.command(help='Sets (or returns) the current profile.  Used to switch between tokens/endpoints')
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