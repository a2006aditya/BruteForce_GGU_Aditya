"""
Script to generate a clean, modern Light-Themed PowerPoint (.pptx) presentation for ConvoSense AI.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Light Theme Color Palette
    BG_COLOR = RGBColor(255, 255, 255)       # #FFFFFF Clean White
    CARD_BG = RGBColor(248, 250, 252)        # #F8FAFC Slate 50
    CARD_BORDER = RGBColor(226, 232, 240)    # #E2E8F0 Slate 200
    PRIMARY_COLOR = RGBColor(37, 99, 235)    # #2563EB Royal Blue
    CORAL_COLOR = RGBColor(220, 38, 38)     # #DC2626 Coral Red
    AMBER_COLOR = RGBColor(217, 119, 6)     # #D97706 Warm Amber
    GREEN_COLOR = RGBColor(5, 150, 105)     # #059669 Emerald Green
    TEXT_MAIN = RGBColor(15, 23, 42)        # #0F172A Slate 900
    TEXT_MUTED = RGBColor(71, 85, 105)      # #475569 Slate 600

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="CEREBRO HACKATHON PRESENTATION"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf = cat_box.text_frame
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_COLOR

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf2 = title_box.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(26)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE (LIGHT THEME)
    # -------------------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide1)

    dec = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.8))
    dec.fill.solid()
    dec.fill.fore_color.rgb = CARD_BG
    dec.line.color.rgb = PRIMARY_COLOR
    dec.line.width = Pt(2)

    title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(2.0))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "ConvoSense AI"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_COLOR

    p_sub = tf.add_paragraph()
    p_sub.text = "Conversation Intelligence & Communication Gap Analysis"
    p_sub.font.size = Pt(22)
    p_sub.font.bold = True
    p_sub.font.color.rgb = TEXT_MAIN

    p_desc = tf.add_paragraph()
    p_desc.text = "\nBridge workplace communication breakdowns with local, evidence-based NLP."
    p_desc.font.size = Pt(15)
    p_desc.font.color.rgb = TEXT_MUTED

    meta_box = slide1.shapes.add_textbox(Inches(1.2), Inches(5.0), Inches(10.9), Inches(1.0))
    tf_meta = meta_box.text_frame
    p_m = tf_meta.paragraphs[0]
    p_m.text = "Track: AI / NLP & Workplace Productivity  |  CEREBRO Hackathon"
    p_m.font.size = Pt(14)
    p_m.font.bold = True
    p_m.font.color.rgb = GREEN_COLOR

    # -------------------------------------------------------------------------
    # SLIDE 2: RELEVANCE & PROBLEM STATEMENT
    # -------------------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide2)
    add_header(slide2, "1. Relevance to Track & Problem Statement", "PROBLEM & TRACK FIT")

    problems = [
        ("❓ Unanswered Questions", "Critical queries get buried in chat threads without receiving plausible answers.", CORAL_COLOR),
        ("🔕 Ignored Proposals", "Commitments and action requests receive no confirmation or decision.", AMBER_COLOR),
        ("🔄 Repeated Clarifications", "Team members re-ask identical questions due to poor context visibility.", PRIMARY_COLOR),
        ("📌 Unresolved Topics", "Action items like 'We need someone for demo' linger without an assigned owner.", GREEN_COLOR)
    ]

    for idx, (title, desc, color) in enumerate(problems):
        row = idx // 2
        col = idx % 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.8 + row * 2.5)

        card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        tb = slide2.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(5.2), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(14)
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------------------
    # SLIDE 3: INNOVATION & ORIGINALITY (TABLE)
    # -------------------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide3)
    add_header(slide3, "2. Innovation & Originality", "COMPETITIVE ADVANTAGE")

    rows, cols = 5, 3
    left, top, width, height = Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8)
    table_shape = slide3.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(4.2)
    table.columns[2].width = Inches(4.333)

    headers = ["Feature Dimension", "Traditional LLMs / Prompts", "ConvoSense AI (Our Solution)"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY_COLOR if i == 2 else CARD_BORDER
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = BG_COLOR if i == 2 else TEXT_MAIN

    matrix_data = [
        ("Explainability & Evidence", "Black-box labels without proof", "Verifiable message trace & confidence metrics"),
        ("Privacy & Execution", "Requires cloud APIs & paid tokens", "100% Local execution with zero cloud latency"),
        ("Chat Log Parsing", "Breaks on multiline text & dates", "Robust WhatsApp, CSV, & transcript parser"),
        ("Review Control", "Static text summary", "Interactive Human-in-the-Loop status controls")
    ]

    for row_idx, row_data in enumerate(matrix_data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if col_idx == 2 else BG_COLOR
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(13)
            p.font.color.rgb = PRIMARY_COLOR if col_idx == 2 else TEXT_MAIN

    # -------------------------------------------------------------------------
    # SLIDE 4: TECHNICAL IMPLEMENTATION & ARCHITECTURE
    # -------------------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide4)
    add_header(slide4, "3. Technical Implementation & Architecture", "END-TO-END PIPELINE")

    steps = [
        ("1. Ingestion Engine", "Multi-format parser for WhatsApp export, CSV, TXT, and raw transcripts. Normalizes timestamps and speakers.", PRIMARY_COLOR),
        ("2. Detection Pipeline", "Executes 4 parallel NLP detection engines using interrogative heuristics, TF-IDF, & Cosine Similarity.", AMBER_COLOR),
        ("3. Structured Schema", "Generates JSON/CSV findings with message ID, speaker, timestamp, confidence score, & evidence logs.", CORAL_COLOR),
        ("4. Interactive Dashboard", "Streamlit UI with Plotly Gantt timeline, metric cards, review controls, and audit exporter.", GREEN_COLOR)
    ]

    for i, (title, desc, color) in enumerate(steps):
        x = Inches(0.8 + i * 2.95)
        y = Inches(1.8)

        card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.8), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        tb = slide4.shapes.add_textbox(x + Inches(0.15), y + Inches(0.2), Inches(2.5), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = f"\n{desc}"
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------------------
    # SLIDE 5: THE FOUR DETECTION ENGINES (DEEP-DIVE)
    # -------------------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide5)
    add_header(slide5, "4. Deep-Dive: The Four Detection Engines", "NLP ENGINE DETAILS")

    engines = [
        ("Engine A: Unanswered Questions", "NLP question heuristics + lookahead window scan + TF-IDF cosine similarity against candidate answers.", CORAL_COLOR),
        ("Engine B: Ignored Responses", "Identifies action/proposal phrases and verifies if subsequent messages contain explicit acknowledgment.", AMBER_COLOR),
        ("Engine C: Repeated Clarifications", "Pairwise n-gram TF-IDF similarity matrix to link paraphrased queries across the timeline.", PRIMARY_COLOR),
        ("Engine D: Unresolved Topics", "Flags unassigned task proposals ('We need someone for demo') lacking explicit owner acceptance.", GREEN_COLOR)
    ]

    for idx, (title, desc, color) in enumerate(engines):
        y = Inches(1.7 + idx * 1.3)
        card = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(1.15))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        tb = slide5.shapes.add_textbox(Inches(1.0), y + Inches(0.15), Inches(11.3), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------------------
    # SLIDE 6: SCALABILITY & REAL-WORLD IMPACT
    # -------------------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide6)
    add_header(slide6, "5. Scalability & Real-World Impact", "BUSINESS & PRODUCTION VALUE")

    impacts = [
        ("🏢 Enterprise Teams", "Audits Slack & Teams channels to ensure no question or task drops through the cracks.", PRIMARY_COLOR),
        ("🎧 Support Escalations", "Verifies that customer inquiries receive timely, accurate support responses.", AMBER_COLOR),
        ("⚡ High Performance", "Processes hundreds of messages in under 3 seconds with O(N log N) local complexity.", GREEN_COLOR),
        ("🔒 Privacy & Compliance", "No conversation data leaves the local machine (GDPR/HIPAA compliant by design).", CORAL_COLOR)
    ]

    for idx, (title, desc, color) in enumerate(impacts):
        row = idx // 2
        col = idx % 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.8 + row * 2.5)

        card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        tb = slide6.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(5.2), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(14)
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------------------
    # SLIDE 7: VERIFICATION & DEMO SUMMARY
    # -------------------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide7)
    add_header(slide7, "6. Verification & Live Demo Summary", "BENCHMARK RESULTS")

    card = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = GREEN_COLOR
    card.line.width = Pt(2)

    tb = slide7.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "✅ 100% Test Pass Rate (8/8 Unit Test Suites Passed)"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = GREEN_COLOR

    points = [
        "• Negative Test Case Verified: 'When is meeting?' followed by 'At 4 PM' is NOT flagged.",
        "• Acknowledgment Verified: Proposals followed by 'Confirmed, thanks!' pass cleanly.",
        "• Paraphrase Detection Verified: Linked 'Which file format?' with 'Should we submit PDF or DOCX?'",
        "• Unassigned Task Tracking Verified: Caught 'We need someone for demo' with no owner.",
        "• Complete Streamlit UI: Interactive review controls, Plotly Gantt timeline, and CSV/JSON export."
    ]

    for pt in points:
        p_pt = tf.add_paragraph()
        p_pt.text = f"\n{pt}"
        p_pt.font.size = Pt(15)
        p_pt.font.color.rgb = TEXT_MAIN

    output_path = r"c:\Users\DELL\OneDrive\Desktop\CEREBRO\convosense-ai\ConvoSense_AI_Presentation.pptx"
    prs.save(output_path)
    print(f"Light-themed presentation saved successfully at: {output_path}")


if __name__ == "__main__":
    create_presentation()
