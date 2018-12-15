import os
import click
import urllib
from . import fio
from . import utils
from fioctl.assets import utils as asset_utils

from .fio import fio_client

DEFAULT_COLS=['id', 'name', 'type', 'project_id', 'filesize', 'private']

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
@click.option('--recursive', is_flag=True)
def upload(parent_id, file, values, format, columns, recursive):
    client = fio_client()
    if recursive:
        click.echo("Beginning recursive upload")
        click.echo(format(upload_stream(client, parent_id, file), cols=["source"] + columns))
        return
    
    filesize = os.path.getsize(file)
    name     = os.path.basename(file)

    values = values or {}
    values['name']     = name
    values['filesize'] = filesize
    values['type']     = 'file'

    asset = create_asset(client, parent_id, values)
    click.echo(format(asset, cols=columns))
    click.echo("Uploading...")
    client.upload(asset, open(file, 'rb'))
    click.echo("Upload finished")
    
@assets.command(help="Downloads an asset")
@click.argument('asset_id')
@click.argument('destination', type=click.Path(), required=False)
@click.option('--proxy', type=click.Choice(['original', 'h264_360', 'h264_540', 'h264_720', 'h264_1080_best', 'h264_2160']), default='original')
@click.option('--recursive', is_flag=True)
@click.option('--format', type=utils.FormatType(), default='table')
def download(asset_id, destination, proxy, recursive, format):
    client = fio_client()
    if recursive:
        click.echo("Beginning download")
        click.echo(format(download_stream(client, asset_id, destination), cols=["source_id", "destination"]))
        return

    asset = client._api_call('get', f"/assets/{asset_id}")
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

def create_asset(client, parent_id, asset):
    return client._api_call('post', f"/assets/{parent_id}/children", asset)

def upload_asset(client, parent_id, file):
   filesize = os.path.getsize(file)
   name     = os.path.basename(file)
   asset = {}
   asset['name']     = name
   asset['filesize'] = filesize
   asset['type']     = 'file'
   asset = create_asset(client, parent_id, asset)
   client.upload(asset, open(file, 'rb'))
   return asset

def download_stream(client, parent_id, root):
    os.makedirs(root, exist_ok=True)
    folders   = []
    downloads = []
    def download(operation):
        url, name, asset_id = operation
        click.echo(f"Downloading {asset_id} to {name}")
        urllib.request.urlretrieve(url, name)
        click.echo(f"Downloaded {asset_id}")
        return {"destination": name, "source_id": asset_id}
      
    for asset in fio.stream_endpoint(f"/assets/{parent_id}/children"):
        name = os.path.join(root, asset["name"])
        click.echo(f"Downloading {asset['id']} to {name}")
        if asset["_type"] == "folder":
            folders.append((name, asset["id"]))
        if asset["_type"] == "version_stack":
            downloads.append((asset["cover_asset"]["original"], name, asset["id"]))
        if asset["_type"] == "file":
            downloads.append((asset["original"], name, asset["id"]))
    
    for _, result in utils.parallelize(download, downloads):
        yield result
    
    for folder, asset_id in folders:
        os.makedirs(folder, exist_ok=True)
        for result in download_stream(client, asset_id, name):
            yield result

   
def upload_stream(client, parent_id, root):
    directories = {root: parent_id}
    def create_folder(folder, parent_id):
        return create_asset(client, parent_id, {"type": "folder", "name": folder})
   
    def upload_file(directory, file, parent_id):
        file = os.path.join(directory, file)
        click.echo(f"Uploading file {file}")
        asset = upload_asset(client, parent_id, file)
        click.echo(f"Uploaded file {file}")
        asset["source"] = os.path.relpath(file, root)
        return asset
    
    for directory, subdirs, files in os.walk(root):
        parent_id = directories[directory]
        for folder, asset in utils.exec_stream(subdirs, lambda d: create_folder(d, parent_id)):
            name = os.path.join(directory, folder)
            click.echo(f"Created directory for {name}")
            asset["source"] = os.path.relpath(name, root)
            yield asset
            directories[name] = asset["id"]
       
        for file, asset in utils.exec_stream(files, lambda f : upload_file(directory, f, parent_id)):
            yield asset
   
    click.echo("Upload results:")