import click
from . import fio
from . import utils
from . import assets

from .fio import fio_client
from .config import column_default
from .config import nested_move

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

@projects.group()
def delete():
    """Deletes any of the project-related types"""

@delete.command(help="Deletes a project")
@click.argument('id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def project(id, format, columns):
    result = fio_client()._api_call('delete', f"/projects/{id}")
    format(result, cols=columns)

@delete.command(help="Deletes a collaborator")
@click.argument('id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=["id", "_type", "user.email" "deleted_at"])
def collaborator(id, format, columns):
    result = fio_client()._api_call('delete', f"/collaborators/{id}")
    format(result, cols=columns)

@delete.command(help="Deletes a pending collaborator")
@click.argument('id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=["id", "_type",  "email"])
def pending_collaborator(id, format, columns):
    result = fio_client()._api_call('delete', f"/pending_collaborators/{id}")
    format(result, cols=columns)

@projects.command(help="Shows users on a project")
@click.argument('project_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=["id", "_type", "email", "inserted_at"])
def collaborators(project_id, format, columns):
    collab_stream = fio.stream_endpoint(f"/projects/{project_id}/collaborators?sort=user.email")
    pending_collab_stream = fio.stream_endpoint(f"/projects/{project_id}/pending_collaborators?sort=email")
    merged = utils.merge_streams(
        (nested_move(c, ['user', 'email'], ['email']) for c in collab_stream), 
        pending_collab_stream,
        key=lambda x: x['email']
    )

    format(merged, cols=columns)