import click
from . import fio
from . import utils
from .fio import fio_client
from .config import column_default

DEFAULT_COLS = column_default('accounts', 'id,owner.email,plan.name,storage,member_count,collaborator_count,inserted_at')

@click.group()
def accounts():
    """Account related commands"""

@accounts.command(help="Fetch a single account")
@click.argument("account_id")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def get(account_id, format, columns):
    account = fio_client()._api_call('get', f"/accounts/{account_id}")

    format(account, cols=columns)

@accounts.command(help="Lists accounts accessible to the current user")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def list(format, columns):
    accounts = fio.stream_endpoint(f"/accounts")

    format(accounts, cols=columns)