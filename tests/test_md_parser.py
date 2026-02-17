from devlog.md_parser import parse_draft, DraftBlock


def test_parse_plain_lines():
    text = """## Updates

* Feature A summary
* Feature B summary
"""
    blocks = parse_draft(text)
    assert len(blocks) == 3
    assert all(not b.expand for b in blocks)


def test_parse_expand_tags():
    text = (
        "## Updates\n"
        "\n"
        "* Feature A summary\n"
        "{{EXPAND}} * Feature B summary\n"
        "* Feature C summary\n"
    )
    blocks = parse_draft(text)
    expand_blocks = [b for b in blocks if b.expand]
    assert len(expand_blocks) == 1
    assert "Feature B" in expand_blocks[0].text


def test_parse_preserves_order():
    text = "Line 1\n{{EXPAND}} Line 2\nLine 3\n"
    blocks = parse_draft(text)
    texts = [b.text.strip() for b in blocks]
    assert texts == ["Line 1", "Line 2", "Line 3"]


def test_parse_extracts_frontmatter():
    text = """---
project: "Foo"
---

## Updates
* stuff
"""
    blocks = parse_draft(text)
    assert not any("---" in b.text for b in blocks)
