import re
from pathlib import Path


NAME = re.compile(r"[A-Z]+")
ROOT_DEPTH = 0


def read_graph(filename):
    graph = {}
    source = Path(filename).read_text(
        encoding="utf-8"
    )
    for line in source.splitlines():
        if not line.strip():
            continue
        words = line.split()
        if not all(map(NAME.fullmatch,
                       words)):
            raise ValueError(
                "Use uppercase names"
            )
        node, *children = words
        graph[node] = children
    return graph


def is_excluded(package, substring):
    parts = package.split(":")
    name = package
    if ":" in package:
        name = parts[1]
    return bool(
        substring and substring in name
    )


def build_graph(root, fetch, limit,
                substring=None):
    graph = {}
    depths = {}
    cache = {}
    stack = [(root, ROOT_DEPTH)]
    while stack:
        node, depth = stack.pop()
        if depth >= depths.get(
            node, limit + 1
        ):
            continue
        depths[node] = depth
        graph.setdefault(node, [])
        if depth >= limit:
            continue
        if node not in cache:
            cache[node] = fetch(node)
        children = [
            child
            for child in cache[node]
            if not is_excluded(
                child, substring
            )
        ]
        graph[node] = children
        stack.extend(
            (child, depth + 1)
            for child in reversed(
                children
            )
        )
    return graph
