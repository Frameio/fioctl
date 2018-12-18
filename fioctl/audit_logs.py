import click
from . import fio
from . import utils
from .config import column_default

DEFAULT_COLS = column_default('audits', "id,actor_id,action,resoure._type,resource.id")

@click.group()
def audits():
    """Audit log related commands"""

@audits.command(help="Lists audit logs for an account")
@click.argument("account_id")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', default=DEFAULT_COLS)
def list(account_id, format, columns):
    audits = fio.stream_endpoint(f"/accounts/{account_id}/audit_logs")

    format(audits, cols=columns)