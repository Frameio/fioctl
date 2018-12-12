import click
from . import fio
from . import utils

@click.group()
def projects():
    """project related commands"""

@projects.command(help="Shows users on a project")
@click.argument('project_id')
def collaborators(project_id):
    collab_stream = fio.stream_endpoint(f"/projects/{project_id}/collaborators")
    pending_collab_stream = fio.stream_endpoint(f"/projects/{project_id}/pending_collaborators")
    merged = utils.merge_streams(
        collab_stream, 
        pending_collab_stream, 
        comparison=lambda x, y: utls.datetime_compare(x["inserted_at"], y["inserted_at"])
    )

    for collab in merged:
        click.echo(f"id={collab['user_id']}, type={collab['_type']}")