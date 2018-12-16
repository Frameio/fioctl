import concurrent.futures
import click
import math
import requests
import time

from . import utils

def upload(asset, file):
    return FrameioUploader(asset, file).upload()

class FrameioUploader(object):
  def __init__(self, asset, file):
    self.asset = asset
    self.file = file

  def _read_chunk(self, file, size):
    while True:
      data = file.read(size)
      if not data:
        break
      yield data

  def _upload_chunk(self, url, chunk, attempt=1):
    requests.put(url, data=chunk, headers={
      'content-type': self.asset['filetype'],
      'x-amz-acl': 'private'
    })

  def upload(self):    
    upload_urls     = self.asset['upload_urls']
    chunks          = len(upload_urls)
    chunks_uploaded = 0

    total_size = self.asset['filesize']
    size       = int(math.ceil(total_size / len(upload_urls)))

    start = int(time.time())

    def handle_chunk(pair):
        i, chunk = pair
        return utils.retry(self._upload_chunk, upload_urls[i], chunk)

    click.echo(f"Uploading {self.asset['name']} in {chunks} chunk(s)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for _ in executor.map(handle_chunk, enumerate(self._read_chunk(self.file, size))):
            chunks_uploaded += 1
            click.echo(f"Uploaded chunk {chunks_uploaded} of {chunks} for {self.asset['name']}")
    
    click.echo(f"Uploaded {self.asset['name']} in {(int(time.time()) - start) / 60.0} mins")