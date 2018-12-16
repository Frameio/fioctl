import click
from . import fio
from . import utils
from . import uploader
from .fio import fio_client

DEFAULT_COLS = ['id', 'asset_id', 'parent_id', 'text', 'timestamp', 'inserted_at']

@click.group()
def comments():
    """Comment related commands"""

@comments.command(help="Fetch a single comment")
@click.argument("comment_id")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def get(comment_id, format, columns):
    comment = fio_client()._api_call('get', f"/comments/{comment_id}")

    format(comment, cols=columns)

@comments.command(help="Lists comments for an asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def list(asset_id, format, columns):
    comments = fio.stream_endpoint(f"/assets/{asset_id}/comments")

    format(comments, cols=columns, root=f"asset[{asset_id}]")

@comments.command(help="Lists replies for a comment")
@click.argument('comment_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def replies(comment_id, format, columns):
    comments = fio.stream_endpoint(f"/comments/{comment_id}/replies")

    format(comments, cols=columns, root=f"comment[{comment_id}]")

@comments.command(help="Creates a comment for an asset")
@click.argument('asset_id')
@click.argument('comment')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def create(asset_id, comment, values, format, columns):
    values = values or {}
    values['text'] = comment
    comment = fio_client()._api_call('post', f"/assets/{asset_id}/comments", values)

    format(comment, cols=columns)

@comments.command(help="Creates a reply for a comment")
@click.argument('comment_id')
@click.argument('comment')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def reply(comment_id, comment, values, format, columns):
    values = values or {}
    values['text'] = comment
    comment = fio_client()._api_call('post', f"/comments/{comment_id}/replies", values)

    format(comment, cols=columns)

