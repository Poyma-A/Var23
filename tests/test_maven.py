import unittest
from unittest.mock import patch
from xml.etree import ElementTree

from src.maven import (
    direct_dependencies as fetch,
    pom_path,
)


class MavenTests(unittest.TestCase):
    def test_pom_path(self):
        self.assertEqual(
            pom_path("org.demo:app:1"),
            "org/demo/app/1/app-1.pom",
        )

    def test_direct_dependencies(self):
        root = ElementTree.fromstring(
            "<project><dependencies>"
            "<dependency>"
            "<groupId>org.demo"
            "</groupId>"
            "<artifactId>lib"
            "</artifactId>"
            "<version>2</version>"
            "</dependency>"
            "</dependencies></project>"
        )
        with patch(
            "src.maven.load_pom",
            return_value=root,
        ):
            result = fetch(
                "https://example.org",
                "org.demo:app:1",
            )
        self.assertEqual(
            result, ["org.demo:lib:2"]
        )
