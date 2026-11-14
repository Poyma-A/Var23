import json
import subprocess
import sys
from pathlib import Path


def d2_source(graph):
    ids = {
        node: f"n{index}"
        for index, node in enumerate(
            graph
        )
    }
    lines = []
    for node, children in graph.items():
        key = ids[node]
        label = json.dumps(
            node, ensure_ascii=False
        )
        lines.append(f"{key}: {label}")
        for child in children:
            target = ids[child]
            lines.append(
                f"{key} -> {target}"
            )
    return "\n".join(lines) + "\n"


def render_graph(graph, output):
    source = Path(output)
    image = source.with_suffix(".svg")
    source.write_text(
        d2_source(graph),
        encoding="utf-8",
    )
    subprocess.run(
        ["d2", "--", str(source),
         str(image)],
        check=True,
    )
    if sys.platform == "darwin":
        subprocess.run(
            ["open", "-a", "Safari",
             str(image)],
            check=True,
        )
    else:
        subprocess.run(
            ["xdg-open", str(image)],
            check=True,
        )
    return image
