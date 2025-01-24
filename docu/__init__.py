"""Convert examples in Pulumi-style markdown.

This is useful when editing markdown in pulumi/docs or pulumi/registry.

Instead of updating every example in a chooser, update Pulumi YAML sources only, then run this script on top of the
markdown file. This will make sure all the other languages are translated from YAML.
"""

import re
import argparse
import subprocess as sp
import tempfile
import os


def render(yaml_text, lang):
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "Pulumi.yaml"), "w") as fp:
            fp.write(yaml_text+"\n")
        sp.check_call(["pulumi", "convert", "--generate-only",
                       "--from", "yaml",
                       "--language", lang,
                       "--out", os.path.join(tmp, "out")],
                      cwd=tmp)
        with open({
                "typescript": os.path.join(tmp, "out", "index.ts"),
                "go": os.path.join(tmp, "out", "main.go"),
                "python": os.path.join(tmp, "out", "__main__.py"),
                "java": os.path.join(tmp, "out", "src", "main", "java", "generated_program", "App.java"),
                "csharp": os.path.join(tmp, "out", "Program.cs"),
        }[lang], "r") as fp:
            code = fp.read()
        return code


def render_choosable(lang, source):
    return f"""
```{lang}
{source}
```
"""


def render_code(yaml_text):
    sources = {
        "yaml": yaml_text,
    }
    for lang in ["typescript", "python", "go", "csharp"]:
        sources[lang] = render(yaml_text, lang)
    return "".join([render_choosable(l, sources[l]) for l in sources.keys()])


def main_cli():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument("yaml", help="Pulumi YAML file")
    argparser.add_argument("-o", help="output file")
    args = argparser.parse_args()

    yaml = args.yaml
    o = args.o

    with open(yaml, "r") as f:
        yaml_text = f.read()

    with open(o, "w") as fp:
        fp.write(render_code(yaml_text))


if __name__ == "__main__":
    main_cli()
