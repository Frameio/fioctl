import click
from . import fio
from . import utils

@click.group()
def audits():
    """Audit log related commands"""

@audits.command(help="Lists audit logs for an account")
@click.argument("account_id")
@click.option('--format', type=utils.FormatType(), default='table')
def list(account_id, format):
    audits = fio.stream_endpoint(f"/accounts/{account_id}/audit_logs")

    click.echo(format(audits, cols=["id", "actor_id", "actor_type", "action", "resource", "inserted_at"]))