import click
from . import fio
from . import utils
from .config import column_default

DEFAULT_COLS = column_default('review_links', "id,name,item_count,view_count,short_url,expires_at")

@click.group()
def review_links():
    """Review link related commands"""

@review_links.command(help="Lists review links for a project")
@click.argument("project_id")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', default=DEFAULT_COLS)
def list(project_id, format, columns):
    review_links = fio.stream_endpoint(f"/projects/{project_id}/review_links")

    format(review_links, cols=columns)