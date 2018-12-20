# fioctl

## Installation

Currently you can only install from source, so:

```bash
git clone git@github.com:Frameio/fioctl.git
cd fioctl && python3 setup.py install
```

Note that it does currently require python3.

## Set Up

First, generate an access token in frame.io and configure with:

```bash
fioctl configure
```

This will ask you to set a profile name, and input your token.

The cli supports multiple profiles in the event you have multiple tokens that can
be configured.  They can be specified like

```bash
fioctl config first_profile.bearer_token <token1>
fioctl config second_profile.bearer_token <token2>
fioctl config profiles.default first_profile
```

To see available commands, run:

```bash
fioctl --help
```

## Basics

Commands are organized around core API types, like `comments`, `assets`, etc.

Any command result can be formatted as `json`, `csv`, or as `table` (usually default),
using the `--format <format>` option.  Some commands, like `fioctl assets traverse <id>`
support `tree` formatting as well.  In addition, a default table format can be set with 
`fioctl config table.fmt <fmt>`

Additionally, you can select the columns to project in a command with the `--columns col1,col2,...`
option.  If you want to select a nested attribute in a column, use the `.` operator.

To preserve formatting for a command family, like `projects`, do `fioctl config projects.columns col1,col2,...`.  To set a new table format, do `fioctl config table.fmt <new_table_fmt>`.  Look at the python docs for tabulate to see the options available. 

Update commands usually accept an option like `--values col=val,col.nested=other_val`