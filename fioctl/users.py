import click
from . import fio
from . import utils

from .fio import fio_client
from .config import column_default

DEFAULT_COLS=column_default('users', 'id,email,name,email_preferences')

@click.group()
def users():
    """user  related commands"""

@users.command(help="Show yourself")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def me(format, columns):
    user = fio_client()._api_call('get', '/me')

    format(user, cols=columns)