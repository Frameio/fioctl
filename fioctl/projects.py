import click
from . import fio
from . import utils
from . import assets

from .fio import fio_client
from .config import column_default

DEFAULT_COLS=column_default('projects', 'id,team_id,name,owner_id,storage,collaborator_count,root_asset_id')

@click.group()
def projects():
    """Project related commands"""

@projects.command(help="Fetch a single project")
@click.argument('project_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def get(project_id, format, columns):
    project = fio_client()._api_call('get', f"/projects/{project_id}")
    format(project, cols=columns)
    
@projects.command(help="Updates a project")
@click.argument('project_id')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def set(project_id, values, format, columns):
    project = fio_client()._api_call('put', f"/projects/{project_id}", values)
    format(project, cols=columns)

@projects.command(help="List projects for a team")
@click.argument('team_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def list(team_id, format, columns):
    projects = fio.stream_endpoint(f"/teams/{team_id}/projects")

    format(projects, cols=columns)

@projects.command(help="List shared projects you are on")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def shared(format, columns):
    projects = fio.stream_endpoint(f"/projects/shared")

    format(projects, cols=columns)

@projects.command(help="List deleted assets on a project")
@click.argument('project_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=assets.DEFAULT_COLS)
def trash(project_id, format, columns):
    assets = fio.stream_endpoint(f"/projects/{project_id}/trash")

    format(assets, cols=columns)

@projects.command(help="Shows users on a project")
@click.argument('project_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=["id", "_type", "user_id", "email", "inserted_at"])
def collaborators(project_id, format, columns):
    collab_stream = fio.stream_endpoint(f"/projects/{project_id}/collaborators")
    pending_collab_stream = fio.stream_endpoint(f"/projects/{project_id}/pending_collaborators")
    merged = utils.merge_streams(
        collab_stream, 
        pending_collab_stream, 
        comparison=lambda x, y: utls.datetime_compare(x["inserted_at"], y["inserted_at"])
    )

    format(merged, cols=columns)