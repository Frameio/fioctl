import os
import click
import urllib
from . import fio
from . import utils

from .fio import fio_client

DEFAULT_COLS=['id', 'name', 'type', 'project_id', 'parent_id', 'filesize', 'private']

@click.group()
def assets():
    """Asset related commands"""

@assets.command(help="List all assets you're a member of")
@click.argument('parent_id', required=False)
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def list(parent_id, format, columns):
    assets = fio.stream_endpoint(f"/assets/{parent_id}/children")

    click.echo(format(assets, cols=columns))

@assets.command(help="Views a specific asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def get(asset_id, format, columns):
    assets= fio_client()._api_call("get", f"/assets/{asset_id}")

    click.echo(format(assets, cols=columns))

@assets.command(help="Uploads an asset with a given file")
@click.argument('parent_id')
@click.argument('file', type=click.Path(exists=True))
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def upload(parent_id, file, values, format, columns):
    client = fio_client()
    filesize = os.path.getsize(file)
    name     = os.path.basename(file)

    values = values or {}
    values['name']     = name
    values['filesize'] = filesize
    values['type']     = 'file'

    asset = client._api_call('post', f"/assets/{parent_id}/children", values)
    click.echo(format(asset, cols=columns))
    click.echo("Uploading...")
    client.upload(asset, open(file, 'rb'))
    click.echo("Upload finished")
    
@assets.command(help="Downloads an asset")
@click.argument('asset_id')
@click.argument('destination', type=click.Path(), required=False)
@click.option('--proxy', type=click.Choice(['original', 'h264_360', 'h264_540', 'h264_720', 'h264_1080_best', 'h264_2160']), default='original')
def download(asset_id, destination, proxy):
    asset = fio_client()._api_call('get', f"/assets/{asset_id}")
    url = asset[proxy]
    name, ext = os.path.splitext(asset['name'])

    default_name = f"{name}.{ext}" if proxy == 'original' else f"{name}.{proxy}.mp4"
    destination  = destination or os.path.abspath(default_name)
    click.echo(f"Downloading to {destination}...")
    urllib.request.urlretrieve(url, destination)
    click.echo("Finished download")

@assets.command(help="Updates an asset")
@click.argument('asset_id')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def set(asset_id, values, format, columns):
    assets = fio_client()._api_call('put', f"/assets/{asset_id}", values)
    click.echo(format(assets, cols=columns))