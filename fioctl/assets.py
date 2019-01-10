import os
import click
import urllib
import time
import sys
from tqdm import tqdm
from collections import Counter
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

@assets.command(help="Restores a deleted asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def restore(asset_id, format, columns):
    asset = fio_client()._api_call('put', f"/assets/{asset_id}/restore")
    format(asset, cols=columns)

@assets.command(help="Moves an asset to a new parent")
@click.argument('asset_id')
@click.argument('parent_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def mv(asset_id, parent_id, format, columns):
    asset = fio_client()._api_call('post', f"/assets/{parent_id}/move", {'id': asset_id})

    format(asset, cols=columns)

@assets.command(help="Zips an asset and its children up")
@click.argument("asset_id")
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def zip(asset_id, format, columns):
    asset = fio_client()._api_call('post', f"/assets/{asset_id}/zip")

    format(asset, cols=columns)

@assets.command(help="Copies an asset a new parent")
@click.argument('asset_id')
@click.argument('parent_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def cp(asset_id, parent_id, format, columns):
    asset = fio_client()._api_call('post', f"/assets/{parent_id}/copy", {'id': asset_id})

    format(asset, cols=columns)

@assets.command(help="Deletes an asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def rm(asset_id, format, columns):
    columns.append('deleted_at')
    asset = fio_client()._api_call('delete', f"/assets/{asset_id}")

    format(asset, cols=columns)


@assets.command(help="Updates the workflow status on an asset")
@click.argument('asset_id')
@click.argument('label', type=click.Choice(['none', 'in_progress', 'needs_review', 'approved']))
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def label(asset_id, label, format, columns):
    columns.append('label')
    asset = fio_client()._api_call('post', f"/assets/{asset_id}/label", {'label': label})

    format(asset, cols=columns)

@assets.command(help="Versions an asset onto another asset")
@click.argument('asset_id')
@click.argument('prev_asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def version(asset_id, prev_asset_id, format, columns):
    asset = fio_client()._api_call('post', f"/assets/{prev_asset_id}/version", {'next_asset_id': asset_id})

    format(asset, cols=columns)

@assets.command(help="Unversions an asset")
@click.argument('asset_id')
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def unversion(asset_id, format, columns):
    asset = fio_client()._api_call('delete', f"/assets/{asset_id}/unversion")

    format(asset, cols=columns)

@assets.command(help="Uploads an asset with a given file")
@click.argument('parent_id')
@click.argument('file', type=click.Path(exists=True))
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
@click.option('--recursive', is_flag=True, help="Upload the contents of the specified folder and all (transitive) subfolders")
def upload(parent_id, file, values, format, columns, recursive):
    client = fio_client()
    utils.initialize_tqdm()
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
@click.option('--proxy', type=click.Choice([
    'original', 'h264_360', 'h264_540', 'h264_720', 'h264_1080_best', 'h264_2160', 'high', 'medium', 'low']), 
    default='original')
@click.option('--recursive', is_flag=True, help="Downloads the children of a given asset and all of their (transitive) children")
@click.option('--format', type=utils.FormatType(), default='table')
def download(asset_id, destination, proxy, recursive, format):
    client = fio_client()
    utils.initialize_tqdm()
    if recursive:
        format(download_stream(client, asset_id, destination, proxy), cols=["source_id", "destination"])
        return

    asset = client._api_call('get', f"/assets/{asset_id}")
    proxy, url = get_proxy(asset, proxy)
    destination  = destination or filename(asset['name'], proxy)
    click.echo(f"Downloading to {destination}...")
    utils.download(url, destination, desc=asset['name'])
    click.echo("Finished download")

@assets.command(help="Updates an asset")
@click.argument('asset_id')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def set(asset_id, values, format, columns):
    assets = fio_client()._api_call('put', f"/assets/{asset_id}", values)
    format(assets, cols=columns)

@assets.command(help="Updates an asset")
@click.argument('parent_id')
@click.option('--values', type=utils.UpdateType())
@click.option('--format', type=utils.FormatType(), default='table')
@click.option('--columns', type=utils.ListType(), default=DEFAULT_COLS)
def create(parent_id, values, format, columns):
    assets = fio_client()._api_call('post', f"/assets/{parent_id}/children", values)
    format(assets, cols=columns)

def create_asset(client, parent_id, asset):
    return client._api_call('post', f"/assets/{parent_id}/children", asset)

def upload_asset(client, parent_id, file, position=None):
   filesize = os.path.getsize(file)
   name     = os.path.basename(file)
   asset = {}
   asset['name']     = name
   asset['filesize'] = filesize
   asset['type']     = 'file'
   asset = create_asset(client, parent_id, asset)
   uploader.upload(asset, open(file, 'rb'), position)
   return asset

PROXY_TABLE={
    ('high', 'stream'): ['h264_2160', 'h264_1080_best'],
    ('medium', 'stream'): ['h264_720'],
    ('low', 'stream'): ['h264_540', 'h264_360'],
    ('high', 'image'): ['image_high'],
    ('medium', 'image'): ['image_full'],
    ('low', 'image'): ['image_small']
}

PROXY_CASCADE=['high', 'medium', 'low']

def filename(name, proxy, path=None):
    def proxy_ext(proxy):
        if 'image' in proxy:
            return 'jpeg'
        return 'mp4'

    name, ext = os.path.splitext(name)
    
    default_name = f"{name}{ext}" if proxy == 'original' else f"{name}.{proxy}.{proxy_ext(proxy)}"
    return os.path.join(path, default_name) if path else os.path.abspath(default_name)

def get_proxy(asset, proxy):
    asset_type = 'image' if asset.get('asset_type') == 'document' else asset.get('asset_type', 'stream')
    if not proxy or proxy == 'original':
        return ('original', asset['original'])

    if proxy not in PROXY_CASCADE:
        return asset.get(proxy)
    
    idx = PROXY_CASCADE.index(proxy)
    for level in PROXY_CASCADE[idx:]:
        for proxy in PROXY_TABLE.get((level, asset_type), []):
            if asset.get(proxy):
                return (proxy, asset[proxy])
    
    return ('original', asset['original'])

def download_stream(client, parent_id, root, proxy=None, capacity=10):
    os.makedirs(root, exist_ok=True)
    tracker = utils.PositionTracker(capacity)
    def download(name, file):
        proxy_name, url = get_proxy(file, proxy)
        asset_id = file["id"]
        name     = filename(name, proxy_name)
        position = tracker.acquire()
        utils.download(url, name, position=position, desc=os.path.relpath(name, root))
        tracker.release(position)
        return {"destination": name, "source_id": asset_id}
    
    def make_folder(name, asset):
        os.makedirs(name, exist_ok=True)
        return {"destination": name, "source_id": asset['id']}
    
    def make_asset(operation):
        name, asset = operation
        return (make_folder, download)[asset["_type"] == "file"](name, asset)

    for result in utils.parallelize(make_asset, folder_stream(client, parent_id, root), capacity=capacity):
        yield result

def folder_stream(client, parent_id, root, recurse_vs=False):
    sibling_counter = Counter()
    for asset in fio.stream_endpoint(f"/assets/{parent_id}/children"):
        name = os.path.join(root, asset["name"])
        sibling_counter[name] += 1
        if sibling_counter[name] > 1:
            base, ext = os.path.splitext(name)
            name = f"{base}_{sibling_counter[name]}{ext}"

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

   
def upload_stream(client, parent_id, root, capacity=10):
    directories = {root: parent_id}
    tracker = utils.PositionTracker(capacity)
    def create_folder(folder):
        parent_id = directories[os.path.dirname(folder)]
        asset = create_asset(client, parent_id, {"type": "folder", "name": os.path.basename(folder)})
        directories[folder] = asset['id']
        asset['source'] = folder
        return asset
   
    def upload_file(f):
        parent_id = directories.get(os.path.dirname(f))
        position = tracker.acquire()
        asset = upload_asset(client, parent_id, f, position)
        tracker.release(position)
        asset["source"] = os.path.relpath(f, root)
        return asset
    
    def handle_fs(fs):
        type, path = fs
        return (create_folder, upload_file)[type == 'f'](path)

    for _, result in utils.exec_stream(handle_fs, utils.stream_fs(root),
                            sync=lambda pair: pair[0] == 'd'):
        yield result