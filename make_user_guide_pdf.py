from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# Define PDF filename
pdf_filename = "pota_user_guide.pdf"
doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40,
)
story = []

# Styles setup
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Heading1"],
    fontSize=16,
    spaceAfter=12,
    textColor="#1e1e2e",
    fontName="Helvetica-Bold",
)
heading_style = ParagraphStyle(
    "SectionHeading",
    parent=styles["Heading2"],
    fontSize=12,
    spaceBefore=10,
    spaceAfter=6,
    textColor="#2563eb",
    fontName="Helvetica-Bold",
)
body_style = ParagraphStyle(
    "BodyText",
    parent=styles["Normal"],
    fontSize=9.5,
    spaceAfter=6,
    leading=13,
    textColor="#334155",
)
bullet_style = ParagraphStyle(
    "BulletText",
    parent=body_style,
    leftIndent=15,
    spaceAfter=4,
)

# Document Header
story.append(
    Paragraph("POTA FT-8 / FT-4 Companion Logger — End User Guide", title_style)
)
story.append(
    Paragraph(
        "A lightweight, modern desktop companion app designed to run alongside"
        " WSJT-X during Parks on the Air (POTA) activations.",
        body_style,
    )
)
story.append(Spacer(1, 8))

# Section 1: Overview
story.append(Paragraph("1. Interface Overview", heading_style))
story.append(
    Paragraph(
        "<b>Top Header:</b> Contains the application title, a live progress"
        " counter (e.g., Contacts: 0 / 10), and the <b>Export POTA ADIF</b>"
        " button.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "<b>Middle Controls:</b> Features the <b>My Park</b> input field (where"
        " you enter your park reference like K-1234) and a <b>Mode</b> selection"
        " drop-down menu (FT-8 or FT-4).",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "<b>Contact Table:</b> Real-time table displaying Callsign, Band, Mode,"
        " Time UTC, Sent report, Rcvd report, and Park reference for every"
        " logged contact.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "<b>Footer:</b> Displays the live file path status and the <b>Locate Log"
        " File</b> button for custom WSJT-X log configurations.",
        bullet_style,
    )
)
story.append(Spacer(1, 6))

# Section 2: Getting Started
story.append(Paragraph("2. Getting Started & Setup", heading_style))
story.append(
    Paragraph(
        "<b>1. Set Your Park Reference:</b> Before operating, type your target"
        " park number into the <i>My Park</i> box (e.g., K-1234).",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "<b>2. Select Your Mode:</b> Choose either <b>FT-8</b> or <b>FT-4</b>"
        " from the mode drop-down list to match your current radio operation.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "<b>3. Verify WSJT-X Connection:</b> The app automatically checks the"
        " standard default WSJT-X log directory for your operating system.",
        bullet_style,
    )
)
story.append(Spacer(1, 6))

# Section 3: Custom Log Locations
story.append(Paragraph("3. Using Custom Log Paths", heading_style))
story.append(
    Paragraph(
        "If WSJT-X saves your logs in a custom directory or file name:",
        body_style,
    )
)
story.append(
    Paragraph(
        "• Click the <b>Locate Log File</b> button in the bottom right corner.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "• Select your target ADIF log file using the file browser dialog.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "• The app will automatically save your choice to a <b>config.txt</b>"
        " file so it remembers the path on future startups.",
        bullet_style,
    )
)
story.append(Spacer(1, 6))

# Section 4: Live Logging & Activation
story.append(
    Paragraph("4. Live Logging & Activation Tracking", heading_style)
)
story.append(
    Paragraph(
        "• <b>Real-Time Sync:</b> Every time you complete a QSO and click 'OK'"
        " in the WSJT-X logging window, the contact automatically streams into"
        " the companion app window instantly.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "• <b>Activation Milestone:</b> The contact counter badge tracks your"
        " progress toward the required 10 contacts. The moment your count hits"
        " <b>10</b>, a congratulatory pop-up message will appear confirming"
        " your activation success!",
        bullet_style,
    )
)
story.append(Spacer(1, 6))

# Section 5: Exporting for POTA
story.append(Paragraph("5. Exporting Your Log for POTA Upload", heading_style))
story.append(
    Paragraph(
        "Once your activation is complete and you are ready to submit your"
        " logs:",
        body_style,
    )
)
story.append(
    Paragraph(
        "• Click the <b>Export POTA ADIF</b> button at the top right.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "• A save window will open with the default name <b>ft8_data.adif</b>"
        " pre-populated.",
        bullet_style,
    )
)
story.append(
    Paragraph(
        "• Choose your destination folder and click Save. The file will format"
        " all contacts with the necessary POTA tags (<MY_SIG:POTA> and your"
        " park reference) ready for direct upload on the POTA website.",
        bullet_style,
    )
)

# Build PDF document
doc.build(story)
print(f"Success! User guide generated: {pdf_filename}")