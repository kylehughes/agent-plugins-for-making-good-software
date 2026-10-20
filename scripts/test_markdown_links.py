"""Exercise authored Markdown routes using temporary source and target files."""

from pathlib import Path
import tempfile
import unittest

from markdown_links import link_errors, local_links, markdown_anchors


class MarkdownLinkTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_same_file_fragment_and_missing_fragment(self):
        source = self.write("source.md", "# Start\n[Valid](#start)\n[Broken](#missing)\n")
        self.assertEqual(link_errors(source), ["line 3: missing Markdown fragment: #missing"])

    def test_cross_file_fragment_and_missing_file(self):
        self.write("references/target.md", "# Target\n")
        source = self.write(
            "source.md",
            "[Valid](references/target.md#target)\n"
            "[Broken fragment](references/target.md#missing)\n"
            "[Broken path](references/missing.md#target)\n",
        )
        self.assertEqual(link_errors(source), [
            "line 2: missing Markdown fragment: references/target.md#missing",
            "line 3: link target does not exist: 'references/missing.md'",
        ])

    def test_renaming_target_heading_breaks_existing_route(self):
        target = self.write("target.md", "# Original heading\n")
        source = self.write("source.md", "[Target](target.md#original-heading)\n")
        self.assertEqual(link_errors(source), [])
        target.write_text("# Renamed heading\n", encoding="utf-8")
        self.assertEqual(link_errors(source), [
            "line 1: missing Markdown fragment: target.md#original-heading",
        ])

    def test_explicit_ids_are_independent_of_heading_spelling(self):
        target = self.write(
            "target.md", '<a id="stable-ID"></a>\n# Renamed heading\n<div id=\'other\'></div>\n',
        )
        source = self.write("source.md", "[One](target.md#stable-ID)\n[Two](target.md#other)\n")
        self.assertEqual(markdown_anchors(target), {"stable-ID", "renamed-heading", "other"})
        self.assertEqual(link_errors(source), [])

    def test_duplicate_headings_do_not_reuse_generated_suffixes(self):
        target = self.write("target.md", "# Repeat\n# Repeat\n# Repeat-1\n# Repeat\n")
        self.assertEqual(markdown_anchors(target), {
            "repeat", "repeat-1", "repeat-1-1", "repeat-2",
        })
        source = self.write("source.md", "[Collision](target.md#repeat-1-1)\n[Last](target.md#repeat-2)\n")
        self.assertEqual(link_errors(source), [])

    def test_atx_setext_and_formatted_headings(self):
        target = self.write(
            "target.md", "## `Key_Value` and [Name](elsewhere.md) ##\n\nSecond title\n===\n",
        )
        self.assertEqual(markdown_anchors(target), {"key_value-and-name", "second-title"})

    def test_fenced_examples_are_neither_routes_nor_anchors(self):
        source = self.write(
            "source.md",
            "# Real\n````markdown\n# Fake\n[Fake](missing.md)\n```\n"
            "<a id=\"fake-id\"></a>\n````\n~~~markdown\n[Fake](also-missing.md)\n~~~\n"
            "[Real](#real)\n",
        )
        self.assertEqual(link_errors(source), [])
        self.assertEqual(markdown_anchors(source), {"real"})

    def test_frontmatter_and_inline_examples_preserve_error_line_numbers(self):
        source = self.write(
            "source.md", "---\nexample: '[Example](missing.md)'\n---\n"
            "`[Example](missing.md)` and ``[Example](also-missing.md)``\n"
            "[Broken](#missing)\n",
        )
        self.assertEqual(link_errors(source), ["line 5: missing Markdown fragment: #missing"])

    def test_reference_definitions_validate_their_paths_and_fragments(self):
        self.write("target.md", "# Target\n")
        source = self.write(
            "source.md", "[Valid][good] and [Invalid][bad]\n\n"
            '[good]: target.md#target "A title"\n'
            "[bad]: target.md#missing\n",
        )
        self.assertEqual(link_errors(source), [
            "line 4: missing Markdown fragment: target.md#missing",
        ])

    def test_encoded_and_angle_destinations_support_spaces_and_unicode(self):
        self.write("references/Guide notes.md", "# Café notes\n")
        source = self.write(
            "source.md", "[Encoded](references/Guide%20notes.md#caf%C3%A9-notes)\n"
            "[Angle](<references/Guide notes.md#café-notes>)\n"
            "[Reference][notes]\n[notes]: <references/Guide notes.md#café-notes>\n",
        )
        self.assertEqual(link_errors(source), [])
        self.assertEqual(len(list(local_links(source.read_text()))), 3)

    def test_external_links_images_and_glob_routes_are_out_of_scope(self):
        source = self.write(
            "source.md", "[External](https://example.invalid/a#missing)\n"
            "[Mail](mailto:someone@example.invalid)\n[Remote](//example.invalid/a)\n"
            "![Image](missing.png)\n[Glob](references/*.md)\n",
        )
        self.assertEqual(link_errors(source), [])


if __name__ == "__main__":
    unittest.main()
