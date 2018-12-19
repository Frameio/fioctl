import concurrent.futures
import click
import math
import requests
import time
from tqdm import tqdm
from . import utils

def upload(asset, file, position=None):
    return FrameioUploader(asset, file, position=position).upload()

class FrameioUploader(object):
  def __init__(self, asset, file, position=None):
    self.asset = asset
    self.file = file
    self.position = position

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
        utils.retry(self._upload_chunk, upload_urls[i], chunk)
        return len(chunk)
  
    args = dict(
      total=total_size, 
      desc=self.asset['name'], 
      miniters=1, unit='B', 
      unit_scale=True, 
      leave=False
    )
    if self.position:
      args['position'] = self.position

    with tqdm(**args) as bar:
      with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
          for size in executor.map(handle_chunk, enumerate(self._read_chunk(self.file, size))):
              bar.update(size)
