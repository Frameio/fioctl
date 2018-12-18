import frameioclient
import click
from furl import furl
from frameioclient import utils as client_utils
from .config import config as fioconf
from .config import nested_get

def fio_client(profile=None):
    profile = profile or fioconf.fetch('profiles', 'default') or 'default'
    token = fioconf.fetch(profile, 'bearer_token')
    host  = fioconf.fetch(profile, 'host') or 'http://api.frame.io'
    return frameioclient.FrameioClient(token, host=host)

def stream_endpoint(endpoint, page=1, page_size=15, client=None, **_kwargs):
    client = client or fio_client()
    def fetch_page(page=1, page_size=15):
        return client._api_call('get', furl(endpoint).add({'page': page, 'page_size': page_size}).url)

    for result in client_utils.stream(fetch_page, page=page, page_size=page_size):
        yield result

        