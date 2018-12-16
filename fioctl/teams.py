import click
from . import fio
from . import utils

from .fio import fio_client
from .config import column_default

DEFAULT_COLS=column_default('teams', 'id,account_id,name,creator_id,storage,member_count,collaborator_count')

@click.group()
def teams():
    """Team  related commands"""

@teams.command(help="List all teams you're a member of")
@click.argument('account_id', required=False)
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def list(account_id, format, columns):
    endpoint = f"/accounts/{account_id}/teams" if account_id else "/teams"
    teams = fio.stream_endpoint(endpoint)

    format(teams, cols=columns)

@teams.command(help="List all teams you're a member of")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def get(team_id, format, columns):
    team = fio_client()._api_call("get", f"/teams/{team_id}")

    format(team, cols=columns)

@teams.command(help="Updates a team")
@click.argument('team_id')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def set(team_id, values, format, columns):
    team = fio_client()._api_call('put', f"/teams/{team_id}", values)
    format(team, cols=columns)