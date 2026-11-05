"""Unit tests for PDF chunking and section extraction."""

from backend.app.ingestion.chunker import LawChunker, clean_str, slugify
from backend.app.ingestion.parser import RawSection


def test_clean_str():
    assert clean_str("hello\u2002world\x07\t") == "hello world"
    assert clean_str("multiple    spaces") == "multiple spaces"


def test_slugify():
    assert slugify("Direct free kick") == "direct-free-kick"
    assert slugify("Handling the ball (2026)") == "handling-the-ball-2026"


def test_chunker_invariants():
    chunker = LawChunker(min_tokens=50, max_tokens=150, edition="2026/27")

    section = RawSection(
        law_number=12,
        law_title="Fouls and Misconduct",
        section_number="1",
        section_title="Direct free kick",
        sub_section="Handling the ball",
        page=116,
        parent_id="law12-s1",
    )
    # Add paragraphs
    section.paragraphs = [
        "A player is penalised if they deliberately touch the ball with their hand or arm.",
        "This includes moving the hand or arm towards the ball.",
        "It is an offence if a player touches the ball with their hand/arm when it has made their body unnaturally bigger.",
    ]

    chunks = chunker.chunk_section(section)
    assert len(chunks) >= 1

    for c in chunks:
        assert c.law_number == 12
        assert c.law_title == "Fouls and Misconduct"
        assert c.parent_id == "law12-s1"
        assert "1. Direct free kick" in c.section_path
        assert "Handling the ball" in c.section_path
        assert c.edition == "2026/27"
        assert c.page == 116
        assert c.chunk_id.startswith("law12-s1-handling-the-ball")
        assert c.token_count <= 250
        assert c.clean_text in c.text_for_embedding
