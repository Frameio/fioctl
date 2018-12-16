import frameioclient
import click
from .config import config as fioconf

def fio_client():
    token = fioconf.fetch('user', 'bearer_token')
    return frameioclient.FrameioClient(token)

def stream_endpoint(endpoint, page=1, page_size=15, client=None):
    client = client or fio_client()
    def fetch_page(page):
        full_endpoint = f"{endpoint}?page={page}&page_size={page_size}"
        return client._api_call('get', full_endpoint)

    result_list = fetch_page(page)
    last = None
    while True:
        for res in result_list:
            yield res

        if len(result_list) < page_size or result_list[-1]["id"] == last:
            return
        page += 1
        last = result_list[-1]['id']
        result_list = fetch_page(page)

        