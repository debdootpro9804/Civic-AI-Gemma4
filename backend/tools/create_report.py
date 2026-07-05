"""Generate polished, single-page PDF reports for civic issues."""

import html
import tempfile
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

from backend.models.schemas import (
    CitizenDetails,
    Complaint,
    DepartmentInfo,
    ImageAnalysisResult,
)


_PAGE_WIDTH, _PAGE_HEIGHT = A4
_MARGIN = 16 * mm
_CONTENT_WIDTH = _PAGE_WIDTH - (2 * _MARGIN)
_HEADER_HEIGHT = 29 * mm
_FOOTER_HEIGHT = 10 * mm
_CONTENT_HEIGHT = (
    _PAGE_HEIGHT - (2 * _MARGIN) - _HEADER_HEIGHT - _FOOTER_HEIGHT
)

_NAVY = colors.HexColor("#172554")
_INDIGO = colors.HexColor("#4F46E5")
_BLUE = colors.HexColor("#2563EB")
_SLATE = colors.HexColor("#475569")
_LIGHT_SLATE = colors.HexColor("#E2E8F0")
_PALE_BLUE = colors.HexColor("#EEF2FF")
_WHITE = colors.white


def create_report(
    citizen_details: CitizenDetails,
    image_analysis: ImageAnalysisResult,
    department: DepartmentInfo,
    complaint: Complaint,
) -> str:
    """Create a professional one-page civic issue report as a PDF.

    The report contains the supplied citizen details, structured image
    analysis, responsible department, and complaint text. All content is
    escaped before rendering, and progressively compact typography is used to
    accommodate realistic complaint lengths without clipping or pagination.

    The function is independent of routes, agents, storage services, and email
    delivery. It creates a uniquely named temporary file that the caller owns
    and is responsible for removing after use.

    Args:
        citizen_details: Citizen identity, contact number, and issue location.
        image_analysis: Structured issue type, description, and confidence.
        department: Responsible department name and contact email.
        complaint: Generated complaint title, subject, and body.

    Returns:
        Absolute path to the generated PDF file.

    Raises:
        ValueError: If the supplied content cannot fit legibly on one page.
        RuntimeError: If ReportLab cannot create the PDF file.
    """
    temporary_file = tempfile.NamedTemporaryFile(
        prefix="civicai_report_",
        suffix=".pdf",
        delete=False,
    )
    output_path = Path(temporary_file.name)
    temporary_file.close()

    try:
        for body_font_size in (9.0, 8.25, 7.5, 7.0):
            elements = _build_report_elements(
                citizen_details=citizen_details,
                image_analysis=image_analysis,
                department=department,
                complaint=complaint,
                body_font_size=body_font_size,
            )
            if _elements_height(elements) <= _CONTENT_HEIGHT:
                _render_pdf(output_path, elements)
                return str(output_path.resolve())

        raise ValueError(
            "Report content is too long to fit legibly on one PDF page."
        )
    except ValueError:
        output_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("Failed to generate the civic report PDF.") from exc


def _build_report_elements(
    citizen_details: CitizenDetails,
    image_analysis: ImageAnalysisResult,
    department: DepartmentInfo,
    complaint: Complaint,
    body_font_size: float,
) -> list[Flowable]:
    """Build measured ReportLab flowables for the report body."""
    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=body_font_size,
        leading=body_font_size * 1.35,
        textColor=_SLATE,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    value_style = ParagraphStyle(
        "Value",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=_NAVY,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=body_style,
        fontSize=max(body_font_size - 1, 6),
        leading=body_font_size * 1.15,
        textColor=_INDIGO,
        fontName="Helvetica-Bold",
    )
    section_style = ParagraphStyle(
        "Section",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=body_font_size + 2,
        leading=(body_font_size + 2) * 1.2,
        textColor=_NAVY,
    )

    confidence = f"{image_analysis.confidence:.0%}"
    elements: list[Flowable] = []
    elements.extend(
        _section(
            "Citizen details",
            [
                _details_table(
                    [
                        ("Full name", citizen_details.full_name),
                        ("Contact number", citizen_details.contact_number),
                        ("Location", citizen_details.location),
                    ],
                    label_style,
                    value_style,
                )
            ],
            section_style,
        )
    )
    elements.extend(
        _section(
            "Issue analysis",
            [
                _details_table(
                    [
                        ("Issue type", image_analysis.issue_type),
                        ("AI confidence", confidence),
                        ("Description", image_analysis.description),
                    ],
                    label_style,
                    value_style,
                )
            ],
            section_style,
        )
    )
    elements.extend(
        _section(
            "Responsible department",
            [
                _details_table(
                    [
                        ("Department", department.department_name),
                        ("Contact", department.email),
                    ],
                    label_style,
                    value_style,
                )
            ],
            section_style,
        )
    )
    elements.extend(
        _section(
            "Complaint",
            [
                _details_table(
                    [
                        ("Title", complaint.title),
                        ("Subject", complaint.subject),
                    ],
                    label_style,
                    value_style,
                ),
                Spacer(1, 2.5 * mm),
                Paragraph(
                    _safe_text(complaint.body),
                    body_style,
                ),
            ],
            section_style,
            final=True,
        )
    )
    return elements


def _section(
    title: str,
    content: list[Flowable],
    section_style: ParagraphStyle,
    final: bool = False,
) -> list[Flowable]:
    """Create a visually consistent report section."""
    elements: list[Flowable] = [
        Paragraph(_safe_text(title), section_style),
        Spacer(1, 1.8 * mm),
        *content,
    ]
    if not final:
        elements.extend(
            [
                Spacer(1, 3.2 * mm),
                Table(
                    [[""]],
                    colWidths=[_CONTENT_WIDTH],
                    rowHeights=[0.35],
                    style=TableStyle(
                        [("BACKGROUND", (0, 0), (-1, -1), _LIGHT_SLATE)]
                    ),
                ),
                Spacer(1, 3.2 * mm),
            ]
        )
    return elements


def _details_table(
    rows: list[tuple[str, str]],
    label_style: ParagraphStyle,
    value_style: ParagraphStyle,
) -> Table:
    """Create an aligned label-value table."""
    table_rows = [
        [
            Paragraph(_safe_text(label), label_style),
            Paragraph(_safe_text(value), value_style),
        ]
        for label, value in rows
    ]
    table = Table(
        table_rows,
        colWidths=[35 * mm, _CONTENT_WIDTH - (35 * mm)],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 4 * mm),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def _elements_height(elements: Iterable[Flowable]) -> float:
    """Return total rendered height for a sequence of flowables."""
    total_height = 0.0
    for element in elements:
        _, height = element.wrap(_CONTENT_WIDTH, _CONTENT_HEIGHT)
        total_height += height
    return total_height


def _render_pdf(output_path: Path, elements: list[Flowable]) -> None:
    """Render measured flowables and fixed page furniture to a PDF."""
    pdf = Canvas(str(output_path), pagesize=A4, pageCompression=1)
    pdf.setTitle("CivicAI Civic Issue Report")
    pdf.setAuthor("CivicAI")

    pdf.setFillColor(_NAVY)
    pdf.roundRect(
        _MARGIN,
        _PAGE_HEIGHT - _MARGIN - _HEADER_HEIGHT,
        _CONTENT_WIDTH,
        _HEADER_HEIGHT,
        5 * mm,
        fill=1,
        stroke=0,
    )
    pdf.setFillColor(_WHITE)
    pdf.setFont("Helvetica-Bold", 21)
    pdf.drawString(
        _MARGIN + 7 * mm,
        _PAGE_HEIGHT - _MARGIN - 12 * mm,
        "CivicAI",
    )
    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        _MARGIN + 7 * mm,
        _PAGE_HEIGHT - _MARGIN - 19 * mm,
        "Civic Issue Report",
    )
    pdf.setFillColor(_BLUE)
    pdf.circle(
        _PAGE_WIDTH - _MARGIN - 12 * mm,
        _PAGE_HEIGHT - _MARGIN - 14.5 * mm,
        6 * mm,
        fill=1,
        stroke=0,
    )
    pdf.setFillColor(_WHITE)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(
        _PAGE_WIDTH - _MARGIN - 12 * mm,
        _PAGE_HEIGHT - _MARGIN - 16 * mm,
        "AI",
    )

    y_position = (
        _PAGE_HEIGHT - _MARGIN - _HEADER_HEIGHT - (5 * mm)
    )
    for element in elements:
        _, height = element.wrap(_CONTENT_WIDTH, _CONTENT_HEIGHT)
        y_position -= height
        element.drawOn(pdf, _MARGIN, y_position)

    pdf.setStrokeColor(_LIGHT_SLATE)
    footer_y = _MARGIN + 5 * mm
    pdf.line(_MARGIN, footer_y + 3 * mm, _PAGE_WIDTH - _MARGIN, footer_y + 3 * mm)
    pdf.setFillColor(_SLATE)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(_MARGIN, footer_y, "Generated by CivicAI")
    pdf.drawRightString(
        _PAGE_WIDTH - _MARGIN,
        footer_y,
        "For review before submission",
    )

    pdf.showPage()
    pdf.save()


def _safe_text(value: str) -> str:
    """Escape user- or model-provided text for ReportLab paragraphs."""
    return html.escape(value).replace("\n", "<br/>")
