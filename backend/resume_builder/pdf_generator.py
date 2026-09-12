from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .resume_data import (
    csv_list,
    entry_has_content,
    format_dates,
    normalize_resume,
    skill_list,
)
from .template_engine import get_template


def _esc(value):
    if value is None:
        return ""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _hex(value):
    return colors.HexColor(value)


def _link(label, url):
    text = _esc(label or url)
    href = str(url or "").strip()
    if href.startswith("http://") or href.startswith("https://"):
        safe = href.replace("&", "&amp;").replace('"', "&quot;")
        return f'<link href="{safe}" color="blue">{text}</link>'
    return text


def generate_pdf(resume, output_file):
    if isinstance(resume, dict) and "sections" in resume and "theme" in resume:
        return _generate_legacy_pdf(resume, output_file)

    data = normalize_resume(resume)
    theme = get_template(data["template"])
    if theme.get("order") == "two_column":
        _build_two_column(data, theme, output_file)
    else:
        _build_single_column(data, theme, output_file)


def _base_styles(theme, centered=False, compact=False):
    header_font = "Times-Bold" if theme.get("serif") else "Helvetica-Bold"
    body_font = "Times-Roman" if theme.get("serif") else "Helvetica"
    body_bold = "Times-Bold" if theme.get("serif") else "Helvetica-Bold"
    accent = theme["accent"]
    header = theme["header"]
    muted = theme["muted"]
    name_size = 18 if compact else 20
    body_size = 8.8 if compact else 9.2
    return {
        "name": ParagraphStyle(
            "ResumeName",
            fontName=header_font,
            fontSize=name_size,
            leading=name_size + 4,
            textColor=_hex(header if header not in ("#f8fafc",) else "#0f172a"),
            alignment=TA_CENTER if centered else TA_LEFT,
            spaceAfter=2,
        ),
        "name_bar": ParagraphStyle(
            "ResumeNameBar",
            fontName=header_font,
            fontSize=20,
            leading=24,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "role": ParagraphStyle(
            "ResumeRole",
            fontName=body_font,
            fontSize=11,
            leading=14,
            textColor=_hex(accent if accent != "#f8fafc" else "#0f766e"),
            alignment=TA_CENTER if centered else TA_LEFT,
            spaceAfter=6,
        ),
        "role_bar": ParagraphStyle(
            "ResumeRoleBar",
            fontName=body_font,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#e2e8f0"),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            fontName=body_font,
            fontSize=8.5,
            leading=12,
            textColor=_hex(muted if muted != "#cbd5e1" else "#475569"),
            alignment=TA_CENTER if centered else TA_LEFT,
            spaceAfter=8,
        ),
        "contact_bar": ParagraphStyle(
            "ResumeContactBar",
            fontName=body_font,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#e2e8f0"),
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "heading": ParagraphStyle(
            "ResumeHeading",
            fontName=header_font,
            fontSize=10.5,
            leading=13,
            textColor=_hex(accent if accent != "#f8fafc" else "#0f766e"),
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            fontName=body_font,
            fontSize=body_size,
            leading=body_size + 3.2,
            textColor=_hex("#1f2937"),
            alignment=TA_JUSTIFY,
        ),
        "item_title": ParagraphStyle(
            "ResumeItemTitle",
            fontName=body_bold,
            fontSize=9.5,
            leading=12,
            textColor=_hex("#111827"),
        ),
        "item_meta": ParagraphStyle(
            "ResumeItemMeta",
            fontName=body_font,
            fontSize=8.5,
            leading=11,
            textColor=_hex(muted if muted != "#cbd5e1" else "#475569"),
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            fontName=body_font,
            fontSize=9 if not compact else 8.6,
            leading=12,
            textColor=_hex("#1f2937"),
            leftIndent=8,
        ),
        "sidebar_heading": ParagraphStyle(
            "SidebarHeading",
            fontName=header_font,
            fontSize=9,
            leading=12,
            textColor=_hex(theme.get("header") or "#f8fafc"),
            spaceBefore=10,
            spaceAfter=4,
        ),
        "sidebar_body": ParagraphStyle(
            "SidebarBody",
            fontName=body_font,
            fontSize=8.2,
            leading=11.2,
            textColor=_hex(theme.get("sidebar_text") or "#e2e8f0"),
        ),
    }


def _contact_line(data, linked=True):
    parts = []
    mapping = (
        ("email", data.get("email"), f"mailto:{data.get('email')}" if data.get("email") else ""),
        ("phone", data.get("phone"), ""),
        ("location", data.get("location"), ""),
        ("linkedin", "LinkedIn" if data.get("linkedin") else "", data.get("linkedin")),
        ("github", "GitHub" if data.get("github") else "", data.get("github")),
        ("portfolio", "Portfolio" if data.get("portfolio") else "", data.get("portfolio")),
    )
    for key, label, url in mapping:
        value = (data.get(key) or "").strip()
        if not value:
            continue
        if linked and url and (url.startswith("http") or url.startswith("mailto:")):
            display = label if key in ("linkedin", "github", "portfolio") else value
            parts.append(_link(display, url if url.startswith("http") else url))
        elif key in ("linkedin", "github", "portfolio"):
            parts.append(_esc(value))
        else:
            parts.append(_esc(value))
    return "  |  ".join(parts)


def _section_rule(theme):
    return HRFlowable(
        width="100%",
        thickness=1,
        color=_hex(theme["rule"]),
        spaceBefore=0,
        spaceAfter=6,
    )


def _heading(text, styles, theme):
    return KeepTogether(
        [
            Paragraph(_esc(text).upper(), styles["heading"]),
            _section_rule(theme),
        ]
    )


def _bullets(text, styles):
    lines = [
        line.strip(" •-\t")
        for line in str(text or "").replace("\r\n", "\n").split("\n")
        if line.strip()
    ]
    flow = []
    for line in lines:
        flow.append(Paragraph(f"• {_esc(line)}", styles["bullet"]))
    return flow


def _experience_block(item, styles):
    if not entry_has_content(item):
        return None
    title = " • ".join(
        part for part in (item.get("role"), item.get("company")) if part
    )
    meta_bits = [
        format_dates(item.get("start"), item.get("end"), item.get("current")),
        item.get("location") or "",
    ]
    meta = "  |  ".join(bit for bit in meta_bits if bit)
    blocks = []
    if title:
        blocks.append(Paragraph(_esc(title), styles["item_title"]))
    if meta:
        blocks.append(Paragraph(_esc(meta), styles["item_meta"]))
    blocks.extend(_bullets(item.get("bullets"), styles))
    blocks.append(Spacer(1, 6))
    return KeepTogether(blocks)


def _education_block(item, styles):
    if not entry_has_content(item):
        return None
    title = " • ".join(
        part for part in (item.get("degree"), item.get("field")) if part
    ) or item.get("school")
    meta_bits = [
        item.get("school") if title != item.get("school") else "",
        format_dates(item.get("start"), item.get("end")),
        item.get("location") or "",
        f"GPA {item['gpa']}" if item.get("gpa") else "",
    ]
    meta = "  |  ".join(bit for bit in meta_bits if bit)
    blocks = []
    if title:
        blocks.append(Paragraph(_esc(title), styles["item_title"]))
    if meta:
        blocks.append(Paragraph(_esc(meta), styles["item_meta"]))
    if item.get("details"):
        blocks.append(Paragraph(_esc(item["details"]), styles["body"]))
    blocks.append(Spacer(1, 6))
    return KeepTogether(blocks)


def _project_block(item, styles):
    if not entry_has_content(item):
        return None
    title = item.get("name") or "Project"
    blocks = [Paragraph(_esc(title), styles["item_title"])]
    links = []
    if item.get("tech"):
        links.append(_esc(item["tech"]))
    if item.get("github"):
        links.append(_link("GitHub", item["github"]))
    if item.get("live"):
        links.append(_link("Live", item["live"]))
    elif item.get("url"):
        links.append(_link(item["url"], item["url"]))
    if links:
        blocks.append(Paragraph("  |  ".join(links), styles["item_meta"]))
    if item.get("description"):
        blocks.append(Paragraph(_esc(item["description"]), styles["body"]))
    blocks.append(Spacer(1, 6))
    return KeepTogether(blocks)


def _simple_lines(items, name_key, extra_keys, styles):
    flow = []
    for item in items:
        if not entry_has_content(item):
            continue
        title = item.get(name_key) or ""
        extras = [item.get(key) or "" for key in extra_keys]
        line = " — ".join(
            part for part in [title, " | ".join(part for part in extras if part)] if part
        )
        if line:
            flow.append(Paragraph(f"• {_esc(line)}", styles["bullet"]))
    return flow


def _append_standard_sections(story, data, styles, theme):
    order = theme.get("order")
    if data.get("summary"):
        story.append(_heading("Professional Summary", styles, theme))
        story.append(Paragraph(_esc(data["summary"]), styles["body"]))

    if order == "graduate":
        sequence = (
            "education",
            "projects",
            "experience",
            "skills",
            "certifications",
            "achievements",
            "languages",
            "interests",
            "custom",
        )
    else:
        sequence = (
            "experience",
            "projects",
            "education",
            "skills",
            "certifications",
            "achievements",
            "languages",
            "interests",
            "custom",
        )

    for key in sequence:
        if key == "experience":
            blocks = [
                _experience_block(item, styles) for item in data.get("experience") or []
            ]
            blocks = [block for block in blocks if block]
            if blocks:
                story.append(_heading("Work Experience", styles, theme))
                story.extend(blocks)
        elif key == "education":
            blocks = [
                _education_block(item, styles) for item in data.get("education") or []
            ]
            blocks = [block for block in blocks if block]
            if blocks:
                story.append(_heading("Education", styles, theme))
                story.extend(blocks)
        elif key == "projects":
            blocks = [
                _project_block(item, styles) for item in data.get("projects") or []
            ]
            blocks = [block for block in blocks if block]
            if blocks:
                story.append(_heading("Projects", styles, theme))
                story.extend(blocks)
        elif key == "skills":
            skills = skill_list(data)
            if skills:
                story.append(_heading("Skills", styles, theme))
                story.append(Paragraph(_esc(", ".join(skills)), styles["body"]))
        elif key == "certifications":
            lines = _simple_lines(
                data.get("certifications") or [],
                "name",
                ("issuer", "year"),
                styles,
            )
            if lines:
                story.append(_heading("Certifications", styles, theme))
                story.extend(lines)
        elif key == "achievements":
            lines = _simple_lines(
                data.get("achievements") or [],
                "title",
                ("description",),
                styles,
            )
            if lines:
                story.append(_heading("Achievements", styles, theme))
                story.extend(lines)
        elif key == "languages":
            languages = csv_list(data.get("languages"))
            if languages:
                story.append(_heading("Languages", styles, theme))
                story.append(Paragraph(_esc(", ".join(languages)), styles["body"]))
        elif key == "interests":
            interests = csv_list(data.get("interests"))
            if interests:
                story.append(_heading("Interests", styles, theme))
                story.append(Paragraph(_esc(", ".join(interests)), styles["body"]))
        elif key == "custom":
            for item in data.get("custom_sections") or []:
                if not entry_has_content(item):
                    continue
                title = item.get("title") or "Additional"
                story.append(_heading(title, styles, theme))
                story.append(Paragraph(_esc(item.get("content") or ""), styles["body"]))


def _header_flow(data, styles, theme, centered):
    flow = []
    name = data.get("full_name") or "Name"
    if theme.get("header_bar"):
        inner = [
            Paragraph(_esc(name), styles["name_bar"]),
        ]
        if data.get("professional_title"):
            inner.append(Paragraph(_esc(data["professional_title"]), styles["role_bar"]))
        contact = _contact_line(data)
        if contact:
            inner.append(Paragraph(contact, styles["contact_bar"]))
        table = Table([[inner]], colWidths=["100%"])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), _hex(theme["header"])),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ]
            )
        )
        flow.append(table)
        flow.append(Spacer(1, 10))
        return flow

    flow.append(Paragraph(_esc(name), styles["name"]))
    if data.get("professional_title"):
        flow.append(Paragraph(_esc(data["professional_title"]), styles["role"]))
    contact = _contact_line(data)
    if contact:
        flow.append(Paragraph(contact, styles["contact"]))
    flow.append(
        HRFlowable(
            width="100%",
            thickness=0.8 if theme.get("compact") else 2,
            color=_hex(theme["rule"]),
            spaceBefore=2,
            spaceAfter=8,
        )
    )
    return flow


def _page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#94a3b8"))
    canvas.drawRightString(A4[0] - 16 * mm, 10 * mm, str(doc.page))
    canvas.restoreState()


def _build_single_column(data, theme, output_file):
    centered = bool(theme.get("centered"))
    styles = _base_styles(theme, centered=centered, compact=bool(theme.get("compact")))
    side = 18 * mm if theme.get("wide") else 16 * mm
    top = 16 * mm if theme.get("wide") else 14 * mm
    if theme.get("header_bar"):
        top = 10 * mm
        side = 14 * mm
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=side,
        rightMargin=side,
        topMargin=top,
        bottomMargin=14 * mm,
        title=data.get("full_name") or "Resume",
        author=data.get("full_name") or "",
    )
    story = []
    story.extend(_header_flow(data, styles, theme, centered))
    _append_standard_sections(story, data, styles, theme)
    if len(story) <= 2:
        story.append(
            Paragraph(
                "Add your resume details in the editor to generate a complete resume.",
                styles["body"],
            )
        )
    doc.build(story, onFirstPage=_page_number, onLaterPages=_page_number)


def _build_two_column(data, theme, output_file):
    styles = _base_styles(theme, centered=False)
    page_w, page_h = A4
    sidebar_w = page_w * 0.32
    main_w = page_w - sidebar_w - 18 * mm

    left = []
    left.append(Paragraph(_esc(data.get("full_name") or "Name"), styles["sidebar_heading"]))
    if data.get("professional_title"):
        left.append(Paragraph(_esc(data["professional_title"]), styles["sidebar_body"]))
    left.append(Spacer(1, 8))
    left.append(Paragraph("CONTACT", styles["sidebar_heading"]))
    for key, label in (
        ("email", None),
        ("phone", None),
        ("location", None),
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
        ("portfolio", "Portfolio"),
    ):
        value = (data.get(key) or "").strip()
        if not value:
            continue
        if key in ("linkedin", "github", "portfolio"):
            left.append(Paragraph(_link(label, value), styles["sidebar_body"]))
        else:
            left.append(Paragraph(_esc(value), styles["sidebar_body"]))
    skills = skill_list(data)
    if skills:
        left.append(Paragraph("SKILLS", styles["sidebar_heading"]))
        left.append(Paragraph(_esc(" • ".join(skills)), styles["sidebar_body"]))
    languages = csv_list(data.get("languages"))
    if languages:
        left.append(Paragraph("LANGUAGES", styles["sidebar_heading"]))
        left.append(Paragraph(_esc(", ".join(languages)), styles["sidebar_body"]))
    interests = csv_list(data.get("interests"))
    if interests:
        left.append(Paragraph("INTERESTS", styles["sidebar_heading"]))
        left.append(Paragraph(_esc(", ".join(interests)), styles["sidebar_body"]))

    right_theme = {
        **theme,
        "header": "#0f172a",
        "muted": "#475569",
        "accent": theme["accent"],
    }
    right_styles = _base_styles(right_theme, centered=False)
    inner = []
    if data.get("summary"):
        inner.append(_heading("Professional Summary", right_styles, theme))
        inner.append(Paragraph(_esc(data["summary"]), right_styles["body"]))
    exp_blocks = [
        _experience_block(item, right_styles) for item in data.get("experience") or []
    ]
    exp_blocks = [block for block in exp_blocks if block]
    if exp_blocks:
        inner.append(_heading("Work Experience", right_styles, theme))
        inner.extend(exp_blocks)
    proj_blocks = [_project_block(item, right_styles) for item in data.get("projects") or []]
    proj_blocks = [block for block in proj_blocks if block]
    if proj_blocks:
        inner.append(_heading("Projects", right_styles, theme))
        inner.extend(proj_blocks)
    edu_blocks = [_education_block(item, right_styles) for item in data.get("education") or []]
    edu_blocks = [block for block in edu_blocks if block]
    if edu_blocks:
        inner.append(_heading("Education", right_styles, theme))
        inner.extend(edu_blocks)
    cert_lines = _simple_lines(
        data.get("certifications") or [], "name", ("issuer", "year"), right_styles
    )
    if cert_lines:
        inner.append(_heading("Certifications", right_styles, theme))
        inner.extend(cert_lines)
    ach_lines = _simple_lines(
        data.get("achievements") or [], "title", ("description",), right_styles
    )
    if ach_lines:
        inner.append(_heading("Achievements", right_styles, theme))
        inner.extend(ach_lines)
    for item in data.get("custom_sections") or []:
        if entry_has_content(item):
            inner.append(_heading(item.get("title") or "Additional", right_styles, theme))
            inner.append(Paragraph(_esc(item.get("content") or ""), right_styles["body"]))

    table = Table(
        [[left, inner or [Spacer(1, 12)]]],
        colWidths=[sidebar_w, main_w],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), _hex(theme["sidebar"])),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, 0), 12),
                ("RIGHTPADDING", (0, 0), (0, 0), 10),
                ("LEFTPADDING", (1, 0), (1, 0), 14),
                ("RIGHTPADDING", (1, 0), (1, 0), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
            ]
        )
    )
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=0,
        rightMargin=10 * mm,
        topMargin=0,
        bottomMargin=12 * mm,
        title=data.get("full_name") or "Resume",
        author=data.get("full_name") or "",
    )
    doc.build([table], onFirstPage=_page_number, onLaterPages=_page_number)


def _generate_legacy_pdf(resume, output_file):
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    story = []
    theme = resume["theme"]
    sections = resume["sections"]
    header = Paragraph(
        "<font color='%s'><b>Professional Resume</b></font>" % theme["primary"],
        styles["Title"],
    )
    story.append(header)
    story.append(Spacer(1, 16))
    for section in sections.values():
        story.append(Paragraph("<b>%s</b>" % _esc(section["title"]), styles["Heading2"]))
        story.append(Spacer(1, 6))
        content = section["content"]
        if isinstance(content, list):
            if not content:
                continue
            for item in content:
                story.append(Paragraph("• " + _esc(item), styles["BodyText"]))
        else:
            text = str(content).strip()
            if text and text != "Professional summary not available.":
                story.append(Paragraph(_esc(text), styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)
