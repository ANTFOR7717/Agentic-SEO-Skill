# tests/test_parse_html.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from fetch.parse_html import parse_html


DATA_FILE = Path(__file__).parent.parent / "data" / "parse_html_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestTitleExtraction:
    @pytest.mark.parametrize("case", CASES["title"])
    def test_title_extraction(self, case):
        result = parse_html(case["html"])
        assert result["title"] == case["expected"]


class TestMetaTags:
    @pytest.mark.parametrize("case", CASES["meta_description"])
    def test_meta_description(self, case):
        result = parse_html(case["html"])
        assert result["meta_description"] == case["expected"]

    @pytest.mark.parametrize("case", CASES["meta_robots"])
    def test_meta_robots(self, case):
        result = parse_html(case["html"])
        assert result["meta_robots"] == case["expected"]

    @pytest.mark.parametrize("case", CASES["open_graph"])
    def test_open_graph(self, case):
        result = parse_html(case["html"])
        assert result["open_graph"] == case["expected"]

    @pytest.mark.parametrize("case", CASES["twitter_card"])
    def test_twitter_card(self, case):
        result = parse_html(case["html"])
        assert result["twitter_card"] == case["expected"]


class TestHeadings:
    @pytest.mark.parametrize("case", CASES["headings"])
    def test_heading_extraction(self, case):
        result = parse_html(case["html"])
        assert result[case["tag"]] == case["expected"]


class TestCanonicalAndHreflang:
    @pytest.mark.parametrize("case", CASES["canonical"])
    def test_canonical(self, case):
        result = parse_html(case["html"])
        assert result["canonical"] == case["expected"]

    @pytest.mark.parametrize("case", CASES["hreflang"])
    def test_hreflang(self, case):
        result = parse_html(case["html"])
        assert result["hreflang"] == case["expected"]


class TestImages:
    @pytest.mark.parametrize("case", CASES["images"])
    def test_image_extraction(self, case):
        result = parse_html(case["html"], base_url=case.get("base_url"))
        assert result["images"] == case["expected"]


class TestLinks:
    @pytest.mark.parametrize("case", CASES["links"])
    def test_link_categorization(self, case):
        result = parse_html(case["html"], base_url=case["base_url"])
        assert len(result["links"]["internal"]) == case["expected_internal"]
        assert len(result["links"]["external"]) == case["expected_external"]

    @pytest.mark.parametrize("case", CASES["link_text"])
    def test_link_text_extraction(self, case):
        result = parse_html(case["html"], base_url=case["base_url"])
        assert result["links"]["internal"][0]["text"] == case["expected"]

    def test_link_text_truncation(self):
        text = "x" * 50 + "This is a very long link text that should be truncated at 100 characters"
        html = f'<html><body><a href="/long">{text}</a></body></html>'
        result = parse_html(html, base_url="https://example.com")
        assert len(result["links"]["internal"][0]["text"]) == 100


class TestSchema:
    @pytest.mark.parametrize("case", CASES["schema"])
    def test_schema_extraction(self, case):
        result = parse_html(case["html"])
        if not result["schema"]:
            pytest.skip("No schema found in test case")
        schema = result["schema"][0]
        if "expected_type" in case:
            assert schema["@type"] == case["expected_type"]
        if "expected_status" in case:
            assert schema["status"] == case["expected_status"]
        if "expected_error" in case:
            assert schema.get("error") == case["expected_error"]


class TestWordCount:
    @pytest.mark.parametrize("case", CASES["word_count"])
    def test_word_count(self, case):
        result = parse_html(case["html"])
        assert result["word_count"] == case["expected"]


class TestFullIntegration:
    def test_full_html_parsing(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
    <meta name="description" content="A test page">
    <meta property="og:title" content="OG Title">
    <link rel="canonical" href="https://example.com/page">
</head>
<body>
    <h1>Main</h1>
    <h2>Sub</h2>
    <img src="img.jpg" alt="Image">
    <a href="/about">About</a>
    <script type="application/ld+json">{"@type": "Article"}</script>
    <p>some content here</p>
</body>
</html>"""
        result = parse_html(html, base_url="https://example.com")

        assert result["title"] == "Test Page"
        assert result["meta_description"] == "A test page"
        assert result["open_graph"]["og:title"] == "OG Title"
        assert result["canonical"] == "https://example.com/page"
        assert result["h1"] == ["Main"]
        assert result["h2"] == ["Sub"]
        assert len(result["images"]) == 1
        assert result["images"][0]["alt"] == "Image"
        assert len(result["links"]["internal"]) == 1
        assert result["links"]["internal"][0]["text"] == "About"
        assert len(result["schema"]) == 1
        assert result["schema"][0]["@type"] == "Article"
        assert result["word_count"] == 8


class TestMalformedHTML:
    @pytest.mark.parametrize("case", CASES.get("malformed", []))
    def test_malformed_handling(self, case):
        result = parse_html(case["html"])
        assert result["title"] == case.get("expected_title")
