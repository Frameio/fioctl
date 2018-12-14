from datetime import datetime
import json
import click
from tabulate import tabulate

from .config import nested_get

class ListType(click.ParamType):
    def convert(self, value, _param, _ctx):
        if isinstance(value, list):
            return value
        return [val.strip() for val in value.split(",")]

class FormatType(click.ParamType):
    def convert(self, value, _param, _ctx):
        return self.formatters()[value]

    def formatters(self):
        return {
            "json": self.format_json,
            "table": self.format_table
        }
    
    def format_json(self, value, **kwargs):
        return json.dumps(value, indent=2, sort_keys=True)

    def format_table(self, value, cols=None):
        if isinstance(value, dict):
            cols = cols or value.keys()
            fetch_map = {col: col.split(".") for col in cols}
            return tabulate(
                [(col, self._convert(nested_get(value, fetch_map[col]))) for col in cols], headers=["attribute", "value"], tablefmt='psql')
        
        value = list(value)
        if not value:
            return "No results"
        
        cols = cols or list(value[0].keys())
        fetch_map = {col: col.split(".") for col in cols}
        return tabulate(self._list_table_format(value, cols, fetch_map), headers=cols, tablefmt="psql")
    
    def _convert(self, value):
        if isinstance(value, dict):
            return self.format_json(value)
        return value
        
    def _list_table_format(self, l, cols, fetch_map):
        def tableize_row(row):
            return [self._convert(nested_get(row, fetch_map[col])) for col in cols]
        
        return [tableize_row(row) for row in l]


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


def datetime_compare(first, second):
    return from_iso(first) <= from_iso(second)

def from_iso(date_string):
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")