import argparse
from argparse import ArgumentTypeError
import re
from pathlib import Path
from urllib.parse import urlsplit


MIN_DEPTH = 0
MIN_PORT = 0
PACKAGE_PATTERN = (
    r"[A-Za-z0-9]"
    r"(?:[A-Za-z0-9._-]*"
    r"[A-Za-z0-9])?"
)
FILE_ERROR = (
    "--repository: "
    "нужен доступный файл"
)
URL_ERROR = (
    "--repository: нужен "
    "корректный URL HTTP или HTTPS"
)


def package_name(value):
    match = re.fullmatch(
        PACKAGE_PATTERN, value
    )
    if not match:
        raise ArgumentTypeError(
            "некорректное имя пакета"
        )
    return value


def depth_limit(value):
    try:
        depth = int(value)
    except ValueError:
        raise ArgumentTypeError(
            "глубина должна быть целой"
        ) from None
    if depth < MIN_DEPTH:
        raise ArgumentTypeError(
            "глубина должна быть "
            "неотрицательной"
        )
    return depth


def filter_text(value):
    has_text = bool(value.strip())
    if not (
        has_text and value.isprintable()
    ):
        raise ArgumentTypeError(
            "нужна непустая "
            "печатная подстрока"
        )
    return value


def valid_url(value):
    has_whitespace = any(
        char.isspace() for char in value
    )
    if (
        has_whitespace
        or not value.isprintable()
    ):
        return False
    try:
        url = urlsplit(value)
        if url.port == MIN_PORT:
            return False
    except ValueError:
        return False
    web_scheme = url.scheme in (
        "http", "https"
    )
    return web_scheme and bool(
        url.hostname
    )


def check_repository(
    parser, repository, test_mode
):
    if test_mode == "on":
        path = Path(repository)
        try:
            if not path.is_file():
                parser.error(FILE_ERROR)
            with path.open("rb"):
                pass
        except (OSError, ValueError):
            parser.error(FILE_ERROR)
    elif not valid_url(repository):
        parser.error(URL_ERROR)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Конфигурация "
            "анализа пакета"
        )
    )
    parser.add_argument(
        "--package",
        required=True,
        type=package_name,
    )
    parser.add_argument(
        "--repository", required=True
    )
    parser.add_argument(
        "--test-mode",
        choices=("on", "off"),
        default="off",
    )
    parser.add_argument(
        "--max-depth",
        required=True,
        type=depth_limit,
    )
    parser.add_argument(
        "--filter", type=filter_text
    )
    options = parser.parse_args()
    check_repository(
        parser,
        options.repository,
        options.test_mode,
    )

    settings = vars(options)
    for key, val in settings.items():
        if val is None:
            val = ""
        print(f"{key}={val}")


if __name__ == "__main__":
    main()
