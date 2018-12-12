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
        click.echo(f"Calling {full_endpoint}")
        return client._api_call('get', full_endpoint)

    result_list = fetch_page(page)
    last = None
    while len(result_list) >= page_size and result_list[-1]["id"] != last:
        last = result_list[-1]["id"]
        for res in result_list:
            yield res

        page += 1
        result_list = fetch_page(page)

def merge_streams(stream, other_stream, comparison=lambda x, y: x["id"] <= y["id"]):
    fetch = lambda stream: next(stream, None)
    head1, head2 = fetch(stream), fetch(other_stream)

    while head1 and head2:
        if comparison(head1, head2):
            yield head1
            head1 = fetch(stream)
        else:
            yield head2
            head2 = fetch(other_stream)
    
    if head1:
        yield head1
        for head1 in stream:
            yield head1
    
    if head2:
        yield head2
        for head2 in other_stream:
            yield head2