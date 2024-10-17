# pulumi-docu

CLI for editing helpers for pulumi/registry and pulumi/docs.


## Installation

```
uv tool install .
```

## Usage

``` shell
$ pulumi-docu --help
usage: pulumi-docu [-h] [-o O] doc

Convert examples in Pulumi-style markdown. This is useful when editing markdown in pulumi/docs or pulumi/registry. Instead of updating every
example in a chooser, update Pulumi YAML sources only, then run this script on top of the markdown file. This will make sure all the other
languages are translated from YAML.

positional arguments:
  doc         markdown file

options:
  -h, --help  show this help message and exit
  -o O        output file
```
