import re
from urllib.request import urlopen
from xml.etree import ElementTree


COORDINATE = re.compile(
    r"[A-Za-z0-9_][A-Za-z0-9_.+-]*"
)
PLACEHOLDER = re.compile(
    r"\$\{([^}]+)\}"
)
TIMEOUT = 15


def pom_path(package):
    parts = package.split(":")
    if len(parts) != COORDINATE_SIZE:
        raise ValueError(BAD_COORDINATE)
    if not all(map(COORDINATE.fullmatch,
                   parts)):
        raise ValueError(BAD_COORDINATE)
    group, artifact, version = parts
    folder = group.replace(".", "/")
    name = f"{artifact}-{version}.pom"
    return (
        f"{folder}/{artifact}/"
        f"{version}/{name}"
    )


COORDINATE_SIZE = 3
BAD_COORDINATE = (
    "Нужны координаты "
    "groupId:artifactId:version"
)


def load_pom(repository, package):
    path = pom_path(package)
    base = repository.rstrip("/")
    with urlopen(
        f"{base}/{path}",
        timeout=TIMEOUT,
    ) as response:
        root = ElementTree.parse(
            response
        ).getroot()
    for element in root.iter():
        element.tag = element.tag.split(
            "}"
        )[-1]
    return root


def read_properties(root, package):
    group, artifact, version = (
        package.split(":")
    )
    properties = {
        "project.groupId": group,
        "project.artifactId": artifact,
        "project.version": version,
        "pom.version": version,
    }
    for element in root.findall(
        "properties/*"
    ):
        properties[element.tag] = (
            element.text or ""
        ).strip()
    return properties


def expand(value, properties):
    seen = set()
    while PLACEHOLDER.search(value):
        if value in seen:
            break
        seen.add(value)
        updated = PLACEHOLDER.sub(
            lambda m: properties.get(
                m[1], m[0]
            ),
            value,
        )
        if updated == value:
            break
        value = updated
        if len(value) > MAX_EXPANSION:
            break
    if PLACEHOLDER.search(value):
        raise ValueError(
            "Не разрешено свойство POM"
        )
    return value


MAX_EXPANSION = 4096


def coordinates(entry, properties):
    values = []
    for field in (
        "groupId",
        "artifactId",
        "version",
    ):
        value = entry.findtext(field)
        value = (value or "").strip()
        values.append(
            expand(value, properties)
        )
    return values


def direct_dependencies(repository,
                        package):
    root = load_pom(repository, package)
    properties = read_properties(
        root, package
    )
    managed = {}
    for entry in root.findall(
        "dependencyManagement/"
        "dependencies/dependency"
    ):
        group, name, version = (
            coordinates(
                entry, properties
            )
        )
        managed[group, name] = version
    dependencies = []
    for entry in root.findall(
        "dependencies/dependency"
    ):
        group, name, version = (
            coordinates(
                entry, properties
            )
        )
        fallback = managed.get(
            (group, name), ""
        )
        version = version or fallback
        if not version:
            raise ValueError(
                "Нет версии: "
                f"{group}:{name}"
            )
        dependencies.append(
            f"{group}:{name}:{version}"
        )
    return dependencies
