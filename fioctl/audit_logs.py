import click
import time
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
@click.option('--item', multiple=True, help="items to filter for, should be of form id,type")
def list(account_id, format, columns, item):
    base_url = f"/accounts/{account_id}/audit_logs"
    stream = []
    if item:
        items = (i.split(',') for i in item)
        streams = [fio.stream_endpoint(f"{base_url}?filter[item_id]={item[0]}&filter[item_type]={item[1]}")
                   for item in items]
        stream = utils.merge_streams(*streams, key=lambda x: -int(utils.from_iso(x['inserted_at']).strftime('%s')))
    else:
        stream = fio.stream_endpoint(base_url)

    format(stream, cols=columns)