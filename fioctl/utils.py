from datetime import datetime
import json
import click
from tabulate import tabulate

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
            return tabulate([(k, self._convert(v)) for (k, v) in value.items()], headers=["attribute", "value"], tablefmt='psql')
        
        return tabulate(list(self._list_table_format(value, cols)), headers="firstrow", tablefmt="psql")
    
    def _convert(self, value):
        if isinstance(value, dict):
            return self.format_json(value)
        return value
        
    def _list_table_format(self, l, cols):
        l = list(l)
        if not l:
            return

        first = l[0]
        
        def tableize_row(vals):
            if not cols:
                return list(self._convert(val) for val in vals.values())
            
            return list(self._convert(vals.get(col)) for col in cols)
        
        if not cols:
            yield list(first.keys())
        else:
            yield cols
        
        yield tableize_row(first)

        for value in l[1:]:
            yield tableize_row(value)


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