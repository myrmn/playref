"""Parser for IFAB Laws of the Game PDF."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pymupdf


class RawSection:
    def __init__(
        self,
        law_number: int,
        law_title: str,
        section_number: str,
        section_title: str,
        sub_section: Optional[str],
        page: int,
        parent_id: Optional[str] = None,
    ):
        self.law_number = law_number
        self.law_title = law_title
        self.section_number = section_number
        self.section_title = section_title
        self.sub_section = sub_section
        self.page = page
        self.parent_id = parent_id
        self.paragraphs: List[str] = []
        self.page_images: List[int] = []

    @property
    def section_path(self) -> str:
        base = f"{self.section_number}. {self.section_title}".strip(". ")
        if self.sub_section:
            return f"{base} > {self.sub_section}"
        return base

    @property
    def full_text(self) -> str:
        return "\n\n".join(self.paragraphs).strip()


class PDFParser:
    """Parses IFAB Laws of the Game PDF extracting structured Law sections."""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

    def is_diagram_page(self, page: pymupdf.Page) -> bool:
        """Identify pages that consist almost entirely of diagrams or illustrations."""
        text = page.get_text().strip()
        # Exclude running header lines
        lines = [
            l.strip()
            for l in text.split("\n")
            if l.strip() and not l.strip().isdigit() and "Laws of the Game" not in l
        ]
        body_text = " ".join(lines)
        drawings = len(page.get_drawings())
        images = len(page.get_images())

        # Low text density + graphical elements
        if (drawings > 20 or images > 0) and len(body_text) < 180:
            return True
        return False

    def parse(self) -> List[RawSection]:
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found at {self.pdf_path}")

        doc = pymupdf.open(str(self.pdf_path))
        sections: List[RawSection] = []

        current_law_num: Optional[int] = None
        current_law_title: Optional[str] = None
        current_sec_num: str = "1"
        current_sec_title: str = "General"
        current_sub_sec: Optional[str] = None
        current_raw_section: Optional[RawSection] = None
        current_parent_id: Optional[str] = None

        # Track diagram pages to attach to surrounding sections
        diagram_pages: List[int] = []

        for pno in range(len(doc)):
            page_num = pno + 1
            page = doc[pno]

            # Detect Law header from running header
            text = page.get_text()
            m_law = re.search(
                r"Laws of the Game \d{4}/\d{2,4}\s+\|\s+Law\s+(\d+)\s+\|\s+([^\n\r]+)", text
            )
            m_var = re.search(r"Laws of the Game \d{4}/\d{2,4}\s+\|\s+VAR protocol", text)
            m_guidelines = re.search(
                r"Laws of the Game \d{4}/\d{2,4}\s+\|\s+Practical guidelines for match officials",
                text,
            )

            new_law_detected = False
            if m_law:
                law_num = int(m_law.group(1))
                law_title = m_law.group(2).strip()
                if law_num != current_law_num:
                    current_law_num = law_num
                    current_law_title = law_title
                    current_sec_num = "1"
                    current_sec_title = "Overview"
                    current_sub_sec = None
                    current_parent_id = f"law{law_num}-s1"
                    new_law_detected = True
            elif m_var:
                if current_law_num != 18:
                    current_law_num = 18
                    current_law_title = "VAR Protocol"
                    current_sec_num = "1"
                    current_sec_title = "Protocol"
                    current_sub_sec = None
                    current_parent_id = "law18-s1"
                    new_law_detected = True
            elif m_guidelines:
                if current_law_num != 19:
                    current_law_num = 19
                    current_law_title = "Practical Guidelines for Match Officials"
                    current_sec_num = "1"
                    current_sec_title = "Guidelines"
                    current_sub_sec = None
                    current_parent_id = "law19-s1"
                    new_law_detected = True

            # If not in a recognized Law section, skip
            if current_law_num is None:
                continue

            # Diagram page check
            if self.is_diagram_page(page):
                diagram_pages.append(page_num)
                if current_raw_section:
                    current_raw_section.page_images.append(page_num)
                continue

            # Extract text blocks
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" not in b:
                    continue

                for line in b["lines"]:
                    spans = line["spans"]
                    if not spans:
                        continue

                    first_span = spans[0]
                    font_name = first_span["font"]
                    font_size = round(first_span["size"], 1)
                    line_text = "".join(s["text"] for s in spans).strip()

                    # Filter out running headers & footer page numbers
                    if font_size <= 6.5 or line_text.isdigit() or "Laws of the Game" in line_text:
                        continue

                    # Filter out big Law title banners (30pt+)
                    if font_size >= 28.0:
                        continue

                    # Check for main numbered section header (e.g. '1. Direct free kick' or '2. Field markings')
                    m_sec = re.match(r"^(\d+)\.\s+(.+)$", line_text)
                    if (
                        ("Roag-ExtraBold" in font_name or "Roag-Bold" in font_name)
                        and m_sec
                        and font_size >= 8.5
                    ):
                        current_sec_num = m_sec.group(1)
                        current_sec_title = m_sec.group(2).strip()
                        current_sub_sec = None
                        current_parent_id = f"law{current_law_num}-s{current_sec_num}"

                        current_raw_section = RawSection(
                            law_number=current_law_num,
                            law_title=current_law_title or f"Law {current_law_num}",
                            section_number=current_sec_num,
                            section_title=current_sec_title,
                            sub_section=None,
                            page=page_num,
                            parent_id=current_parent_id,
                        )
                        sections.append(current_raw_section)
                        continue

                    # Check for sub-section bold header (e.g. 'Handling the ball', 'Advantage')
                    if (
                        ("Roag-Bold" in font_name or "Roag-ExtraBold" in font_name)
                        and font_size >= 8.5
                        and len(line_text) > 3
                        and not line_text.endswith(":")
                        and not line_text.startswith("•")
                        and len(line_text.split()) <= 8
                    ):
                        current_sub_sec = line_text
                        current_raw_section = RawSection(
                            law_number=current_law_num,
                            law_title=current_law_title or f"Law {current_law_num}",
                            section_number=current_sec_num,
                            section_title=current_sec_title,
                            sub_section=current_sub_sec,
                            page=page_num,
                            parent_id=current_parent_id,
                        )
                        sections.append(current_raw_section)
                        continue

                    # Body text line
                    if not current_raw_section:
                        current_raw_section = RawSection(
                            law_number=current_law_num,
                            law_title=current_law_title or f"Law {current_law_num}",
                            section_number=current_sec_num,
                            section_title=current_sec_title,
                            sub_section=current_sub_sec,
                            page=page_num,
                            parent_id=current_parent_id,
                        )
                        sections.append(current_raw_section)

                    # Add text to current section
                    if line_text:
                        if (
                            current_raw_section.paragraphs
                            and not line_text.startswith("•")
                            and not current_raw_section.paragraphs[-1].startswith("•")
                            and not current_raw_section.paragraphs[-1].endswith(".")
                            and not current_raw_section.paragraphs[-1].endswith(":")
                        ):
                            # Append to continuing paragraph
                            current_raw_section.paragraphs[-1] += " " + line_text
                        else:
                            current_raw_section.paragraphs.append(line_text)

        # Filter out empty sections
        valid_sections = [s for s in sections if s.full_text]
        return valid_sections

