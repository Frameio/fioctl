import click

from .config import config as fioconf
from datetime import datetime
from . import fio

@click.group()
def cli():
    """Frame.io on the command line"""
    pass

@cli.command(help="Shows users on a project")
@click.argument('project_id')
def collaborators(project_id):
    collab_stream = fio.stream_endpoint(f"/projects/{project_id}/collaborators")
    pending_collab_stream = fio.stream_endpoint(f"/projects/{project_id}/pending_collaborators")
    merged = fio.merge_streams(
        collab_stream, 
        pending_collab_stream, 
        comparison=lambda x, y: datetime_compare(x["inserted_at"], y["inserted_at"])
    )

    for collab in merged:
        click.echo(f"id={collab['user_id']}, type={collab['_type']}")

@cli.command(help="Updates/reads fioctl config, depending on if the value arg is present")
@click.argument("path")
@click.argument("value", required=False)
def config(path, value):
    path = path.split(".")
    if not value:
        click.secho(str(fioconf.fetch(path[0], path[1])))
        return
    
    fioconf.set_config(path[0], path[1], value)

def datetime_compare(first, second):
    return from_iso(first) <= from_iso(second)

def from_iso(date_string):
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")