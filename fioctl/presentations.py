import click
from . import fio
from . import utils
from .config import column_default

DEFAULT_COLS = column_default('presentations', "id,vanity,title,enabled,expires_at")

@click.group()
def presentations():
    """Presentation related commands"""

@presentations.command(help="Lists presentations")
@click.argument("project_id")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', default=DEFAULT_COLS)
def list(project_id, format, columns):
    presentations = fio.stream_endpoint(f"/projects/{project_id}/presentations")

    format(presentations, cols=columns)