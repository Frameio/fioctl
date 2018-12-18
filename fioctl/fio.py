import frameioclient
import click
from .config import config as fioconf
from .config import nested_get

def fio_client(profile=None):
    profile = profile or fioconf.fetch('profiles', 'default') or 'default'
    token = fioconf.fetch(profile, 'bearer_token')
    host  = fioconf.fetch(profile, 'host') or 'http://api.frame.io'
    return frameioclient.FrameioClient(token, host=host)

def stream_endpoint(endpoint, page=1, page_size=15, client=None, dedupe_key=["id"]):
    client = client or fio_client()
    def fetch_page(page):
        return client._api_call('get', endpoint, {"page": page, "page_size": page_size})

    result_list = fetch_page(page)
    last = None
    while result_list:
        if nested_get(result_list[-1], dedupe_key) == last:
            return

        for res in result_list:
            yield res
        
        if len(res) < page_size:
            return

        page += 1
        last = nested_get(result_list[-1], dedupe_key)
        result_list = fetch_page(page)

        