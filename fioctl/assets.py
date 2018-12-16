import os
import click
import urllib
from . import fio
from . import utils
from . import uploader
from .fio import fio_client
from .config import column_default

DEFAULT_COLS=column_default('assets', 'id,name,type,project_id,filesize,private')

@click.group()
def assets():
    """Asset related commands"""

@assets.command(help="List all assets you're a member of")
@click.argument('parent_id', required=False)
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def list(parent_id, format, columns):
    assets = fio.stream_endpoint(f"/assets/{parent_id}/children")

    format(assets, cols=columns)

@assets.command(help="Views a specific asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def get(asset_id, format, columns):
    assets= fio_client()._api_call("get", f"/assets/{asset_id}")

    format(assets, cols=columns)

@assets.command(help="Shows the file tree within a given asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='tree')
@click.option('--columns', type=utils.ListType(), default=['id','type','name'])
def traverse(asset_id, format, columns):
    def line_fmt(col_vals):
        attrs = ', '.join(f"{col}: {val}" for col, val in col_vals)
        return f"Asset[{attrs}]"

    format((asset for _, asset in folder_stream(fio_client(), asset_id, "/", recurse_vs=True)), 
        cols=columns, root=(f"Asset[id: {asset_id}]", asset_id), line_fmt=line_fmt)

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
        format(upload_stream(client, parent_id, file), cols=["source"] + columns)
        return
    
    filesize = os.path.getsize(file)
    name     = os.path.basename(file)

    values = values or {}
    values['name']     = name
    values['filesize'] = filesize
    values['type']     = 'file'

    asset = create_asset(client, parent_id, values)
    format(asset, cols=columns)
    uploader.upload(asset, open(file, 'rb'))
    
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
        format(download_stream(client, asset_id, destination), cols=["source_id", "destination"])
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
    format(assets, cols=columns)

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
   uploader.upload(asset, open(file, 'rb'))
   return asset

def download_stream(client, parent_id, root):
    os.makedirs(root, exist_ok=True)
    def download(name, file):
        url, asset_id = file["original"], file["id"]
        click.echo(f"Downloading {asset_id} to {name}")
        urllib.request.urlretrieve(url, name)
        click.echo(f"Downloaded {asset_id} to {name}")
        return {"destination": name, "source_id": asset_id}
    
    def make_folder(name, asset):
        click.echo(f"Creating folder {name} for {asset['id']}")
        os.makedirs(name, exist_ok=True)
        return {"destination": name, "source_id": asset['id']}
    
    def make_asset(operation):
        name, asset = operation
        return (make_folder, download)[asset["_type"] == "file"](name, asset)
    
    for result in utils.parallelize(make_asset, folder_stream(client, parent_id, root)):
        yield result
    
    click.echo("Download results:")

def folder_stream(client, parent_id, root, recurse_vs=False):
    for asset in fio.stream_endpoint(f"/assets/{parent_id}/children"):
        name = os.path.join(root, asset["name"])
        if asset["_type"] == "folder":
            yield (name, asset)

            for result in folder_stream(client, asset['id'], name):
                yield result

        if recurse_vs and asset['_type'] == 'version_stack':
            yield (name, asset)
            for result in folder_stream(client, asset['id'], os.path.join(name, 'versions')):
                yield result

        elif asset["_type"] == "version_stack":
            yield (name, asset["cover_asset"])

        if asset["_type"] == "file":
            yield (name, asset)

   
def upload_stream(client, parent_id, root):
    directories = {root: parent_id}

    def create_folder(folder):
        parent_id = directories[os.path.dirname(folder)]
        asset = create_asset(client, parent_id, {"type": "folder", "name": os.path.basename(folder)})
        directories[folder] = asset['id']
        click.echo(f"Created folder for {folder}")
        asset['source'] = folder
        return asset
   
    def upload_file(f):
        parent_id = directories.get(os.path.dirname(f))
        asset = upload_asset(client, parent_id, f)
        asset["source"] = os.path.relpath(f, root)
        return asset
    
    def handle_fs(fs):
        type, path = fs
        return (create_folder, upload_file)[type == 'f'](path)

    for _, result in utils.exec_stream(handle_fs, utils.stream_fs(root), sync=lambda pair: pair[0] == 'd'):
        yield result

    click.echo("Upload results:")