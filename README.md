# fioctl

To set up, generate an access token in frame.io and configure with:

```bash
fioctl config user.bearer_token <my_token>
```

To see available commands, run:

```bash
fioctl --help
```

Commands are organized around core API types, like `comments`, `assets`, etc.

Any command result can be formatted as json, csv, or as a table (usually default),
using the `--format <format>` option.  Some commands, like `fioctl assets traverse <id>`
support tree formatting as well.

Additionally, you can select the columns to project in a command with the `--columns col1,col2,...`
option.  If you want to select a nested attribute in a column, use the `.` operator.

To preserve formatting for a command family, like `projects`, do `fioctl config projects.columns col1,col2,...`
