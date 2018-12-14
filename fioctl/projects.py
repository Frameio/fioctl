import click
from . import fio
from . import utils

@click.group()
def projects():
    """project related commands"""

@projects.command(help="Fetch a single project")
@click.argument('project_id')
@click.option('--format', type=utils.FormatType(), default='json')
def get(project_id, format):
    project = fio.fio_client()._api_call('get', f"/projects/{project_id}")
    click.echo(format(project))

@projects.command(help="Shows users on a project")
@click.argument('project_id')
@click.option('--format', type=utils.FormatType(), default='json')
def collaborators(project_id, format):
    collab_stream = fio.stream_endpoint(f"/projects/{project_id}/collaborators")
    pending_collab_stream = fio.stream_endpoint(f"/projects/{project_id}/pending_collaborators")
    merged = utils.merge_streams(
        collab_stream, 
        pending_collab_stream, 
        comparison=lambda x, y: utls.datetime_compare(x["inserted_at"], y["inserted_at"])
    )

    click.echo(format(merged, cols=["id", "user_id", "email", "inserted_at"]))