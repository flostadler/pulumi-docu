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
            fp.write(yaml_text)
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


def update_choosable(s):
    yaml_text = extract_yaml(s.group(0))
    if not yaml_text:
        return s.group(0)
    yaml_text = yaml_text.strip()
    return render_code({
        "yaml": yaml_text,
        "typescript": render(yaml_text, "typescript"),
        "python": render(yaml_text, "python"),
        "go": render(yaml_text, "go"),
        "csharp": render(yaml_text, "csharp"),
        "java": render(yaml_text, "java"),
    })


def extract_yaml(text):
    pat = re.compile(r"""```yaml([^`]*)```""", re.DOTALL)
    m = pat.search(text)
    if m:
        code = m.group(1)
        return code


def replace_choosables(s):
    pat = re.compile(r"""{{< chooser[^>]+>}}(?:[^{]|[{](?!{<))*{{< /chooser >}}""", re.DOTALL)
    return re.sub(pat, update_choosable, s)


def render_choosable(lang, source):
    return f"""
{{{{% choosable language {lang} %}}}}

```{lang}
{source}
```

{{{{% /choosable %}}}}
"""


def render_code(sources):
    selected_langs = []
    for lang in ["typescript", "python", "go", "csharp", "java", "yaml"]:
        if lang in sources:
            selected_langs.append(lang)
    body = "".join([render_choosable(l, sources[l]) for l in selected_langs])
    languages = ",".join(selected_langs)
    return f"""{{{{< chooser language "{languages}" >}}}}
{body}
{{{{< /chooser >}}}}"""


def main_cli():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument("doc", help="markdown file")
    argparser.add_argument("-o", help="output file")
    args = argparser.parse_args()

    doc = args.doc
    o = args.o

    with open(doc, "r") as f:
        doc_text = f.read()

    with open(o, "w") as fp:
        fp.write(replace_choosables(doc_text))


if __name__ == "__main__":
    main_cli()
