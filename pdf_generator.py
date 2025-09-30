# import json
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, Image
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.graphics.shapes import Drawing, Rect, String
# from reportlab.graphics import renderPDF
# from datetime import datetime
# from deep_translator import GoogleTranslator

# def translate_text(text, target_lang):
#     try:
#         return GoogleTranslator(source='en', target=target_lang).translate(text)
#     except Exception as e:
#         return text


# # --- Chart Flowable Wrapper ---
# class ChartFlowable(Flowable):
#     def __init__(self, drawing):
#         Flowable.__init__(self)
#         self.drawing = drawing
#         self.width = drawing.width
#         self.height = drawing.height

#     def draw(self):
#         renderPDF.draw(self.drawing, self.canv, 0, 0)


# # --- Health Report Generator ---
# class HealthReportGenerator:
#     def __init__(self, logo_path="healthfinit-ai-modules/logo_img.png"):
#         self.styles = getSampleStyleSheet()
#         self.setup_custom_styles()
#         self.logo_path = logo_path

#     def setup_custom_styles(self):
#         """Define custom styles for different sections"""
#         self.title_style = ParagraphStyle(
#             'Title',
#             parent=self.styles['Heading1'],
#             fontSize=22,
#             textColor=colors.HexColor("#1A237E"),
#             alignment=1,  # Center
#             spaceAfter=20,
#             fontName='Helvetica-Bold'
#         )

#         self.sub_title_style = ParagraphStyle(
#             'Subtitle',
#             parent=self.styles['Normal'],
#             fontSize=12,
#             textColor=colors.grey,
#             alignment=1,
#             spaceAfter=30
#         )

#         self.section_header_style = ParagraphStyle(
#             'SectionHeader',
#             parent=self.styles['Heading2'],
#             fontSize=14,
#             textColor=colors.HexColor("#0D47A1"),
#             alignment=0,  # Left
#             spaceBefore=12,
#             spaceAfter=6,
#             fontName='Helvetica-Bold'
#         )

#         self.normal_text = ParagraphStyle(
#             'NormalText',
#             parent=self.styles['Normal'],
#             fontSize=10,
#             textColor=colors.black,
#             alignment=0,
#             spaceAfter=4,
#             fontName='Helvetica'
#         )

#         self.status_high = ParagraphStyle(
#             'StatusHigh',
#             parent=self.styles['Normal'],
#             fontSize=10,
#             textColor=colors.red,
#             fontName='Helvetica-Bold'
#         )

#         self.status_low = ParagraphStyle(
#             'StatusLow',
#             parent=self.styles['Normal'],
#             fontSize=10,
#             textColor=colors.blue,
#             fontName='Helvetica-Bold'
#         )

#         self.status_normal = ParagraphStyle(
#             'StatusNormal',
#             parent=self.styles['Normal'],
#             fontSize=10,
#             textColor=colors.green,
#             fontName='Helvetica-Bold'
#         )

#         self.footnote_style = ParagraphStyle(
#             'Footnote',
#             parent=self.styles['Normal'],
#             fontSize=8,
#             textColor=colors.grey,
#             alignment=1,
#             spaceBefore=20
#         )

#     def parse_reference_range(self, reference_range):
#         """Parse string ranges like 70-110 into dict"""
#         import re
#         if not reference_range:
#             return None

#         range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', reference_range)
#         if range_match:
#             return {
#                 'normal_min': float(range_match.group(1)),
#                 'normal_max': float(range_match.group(2))
#             }
#         return None

#     def create_bar_chart(self, result_value, test_data):
#         """Create a bar chart visualization for the test"""
#         drawing = Drawing(300, 50)
#         bar_width, bar_height = 220, 12
#         bar_x, bar_y = 50, 20

#         try:
#             clean_value = str(result_value).replace(',', '').replace('+', '')
#             if not clean_value or clean_value.lower() in [
#                 'nil', 'negative', 'absent', 'present', 'clear'
#             ]:
#                 return None

#             numeric_value = float(clean_value)

#             # Determine normal ranges
#             ranges = test_data.get('ranges') or self.parse_reference_range(
#                 test_data.get('reference_range', '')
#             )
#             if not ranges:
#                 return None

#             normal_min, normal_max = ranges['normal_min'], ranges['normal_max']
#             chart_max = max(normal_max * 1.3, numeric_value * 1.2)

#             # Low - Normal - High regions
#             low_width = (normal_min / chart_max) * bar_width
#             normal_width = ((normal_max - normal_min) / chart_max) * bar_width
#             high_width = bar_width - low_width - normal_width

#             if low_width > 0:
#                 drawing.add(Rect(bar_x, bar_y, low_width, bar_height,
#                                  fillColor=colors.pink, strokeColor=colors.black, strokeWidth=0.25))
#             drawing.add(Rect(bar_x + low_width, bar_y, normal_width, bar_height,
#                              fillColor=colors.lightgreen, strokeColor=colors.black, strokeWidth=0.25))
#             if high_width > 0:
#                 drawing.add(Rect(bar_x + low_width + normal_width, bar_y, high_width, bar_height,
#                                  fillColor=colors.lightyellow, strokeColor=colors.black, strokeWidth=0.25))

#             # Mark value
#             value_pos = bar_x + (min(numeric_value, chart_max) / chart_max) * bar_width
#             drawing.add(Rect(value_pos - 1, bar_y - 3, 2, bar_height + 6,
#                              fillColor=colors.red, strokeColor=colors.red))
#             drawing.add(String(value_pos - 10, bar_y + bar_height + 5,
#                                f"{result_value}", fontSize=7, fillColor=colors.red))
#             return drawing

#         except Exception:
#             return None

#     def create_test_section(self, test_data):
#         """Builds a standardized table for each test"""
#         elements = []

#         # Status field
#         status = test_data.get('status', 'UNKNOWN')
#         if status == "HIGH":
#             status_para = Paragraph("HIGH", self.status_high)
#         elif status == "LOW":
#             status_para = Paragraph("LOW", self.status_low)
#         else:
#             status_para = Paragraph("NORMAL", self.status_normal)

#         # Chart
#         chart = self.create_bar_chart(test_data['value'], test_data)
#         chart_flowable = ChartFlowable(chart) if chart else Paragraph("N/A", self.normal_text)

#         # Build structured table
#         table_data = [
#             [Paragraph("<b>Test:</b>", self.normal_text),
#              Paragraph(test_data['name'], self.normal_text)],
#             [Paragraph("<b>Result:</b>", self.normal_text),
#              Paragraph(f"{test_data['value']} {test_data.get('unit', '')}", self.normal_text)],
#             [Paragraph("<b>Status:</b>", self.normal_text), status_para],
#             [Paragraph("<b>Reference:</b>", self.normal_text),
#              Paragraph(test_data.get('reference_range', 'N/A'), self.normal_text)],
#             [Paragraph("<b>Chart:</b>", self.normal_text), chart_flowable]
#         ]

#         if 'meaning' in test_data and test_data['meaning']:
#             table_data.append([Paragraph("<b>Meaning:</b>", self.normal_text),
#                                Paragraph(test_data['meaning'], self.normal_text)])

#         if 'tips' in test_data and test_data['tips']:
#             table_data.append([Paragraph("<b>Tips:</b>", self.normal_text),
#                                Paragraph(test_data['tips'], self.normal_text)])

#         table = Table(table_data, colWidths=[80, 380])
#         table.setStyle(TableStyle([
#             ('BOX', (0, 0), (-1, -1), 0.6, colors.grey),
#             ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#             ('LEFTPADDING', (0, 0), (-1, -1), 6),
#             ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#             ('TOPPADDING', (0, 0), (-1, -1), 4),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
#         ]))

#         elements.append(table)
#         elements.append(Spacer(1, 0.25 * inch))
#         return elements

#     def add_header_footer(self, canvas, doc):
#         """Header and footer for every page"""
#         canvas.saveState()

#         # --- Add Image on Top ---
#         try:
#             img_width = 240  # adjust size
#             img_height = 30
#             x = (A4[0]) / 2
#             y = A4[1] - 30               # from top margin
#             canvas.drawImage(self.logo_path, x, y, width=img_width, height=img_height, preserveAspectRatio=True)
#         except Exception as e:
#             print(f"⚠️ Could not load image: {e}")

#         # Header
#         canvas.setFont('Helvetica-Bold', 9)
#         canvas.setFillColor(colors.HexColor("#1A237E"))
#         canvas.drawString(30, A4[1] - 30, "Health Report Summary")
#         # Footer
#         canvas.setFont('Helvetica', 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawString(30, 20, f"Generated on {datetime.now().strftime('%B %d, %Y')}")
#         canvas.drawRightString(A4[0] - 30, 20, f"Page {doc.page}")
#         canvas.restoreState()

#     def generate_pdf(self, json_file_path, output_pdf_path):
#         try:
#             with open(json_file_path, 'r', encoding='utf-8') as f:
#                 report_data = json.load(f)

#             doc = SimpleDocTemplate(output_pdf_path, pagesize=A4,
#                                     topMargin=0.8 * inch, bottomMargin=0.8 * inch,
#                                     leftMargin=0.75 * inch, rightMargin=0.75 * inch)

#             story = []

#             # --- Cover Page ---
#             story.append(Spacer(1, 2 * inch))
#             story.append(Paragraph("Health Report Summary", self.title_style))
#             story.append(Paragraph("Confidential Medical Document", self.sub_title_style))
#             story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}",
#                                    self.normal_text))
#             story.append(PageBreak())

#             # --- Test Sections ---
#             tests = report_data.get('tests', [])
#             for test in tests:
#                 story.extend(self.create_test_section(test))

#             story.append(Paragraph("End of Report", self.footnote_style))

#             doc.build(story, onFirstPage=self.add_header_footer,
#                       onLaterPages=self.add_header_footer)
#             return True

#         except Exception as e:
#             print(f"Error generating PDF: {str(e)}")
#             return False


# # --- Main Execution ---
# def main():
#     json_file = "healthfinit-ai-modules/health_report_data.json"
#     output_pdf = "healthfinit-ai-modules/health_report_summary_test.pdf"

#     generator = HealthReportGenerator(logo_path="healthfinit-ai-modules/logo_img.png")
#     success = generator.generate_pdf(json_file, output_pdf)

#     if success:
#         print(f"✅ Health report PDF generated successfully: {output_pdf}")
#     else:
#         print("❌ Failed to generate PDF")


# if __name__ == "__main__":
#     main()

# -*- coding: utf-8 -*-
import os
import json
import requests
import re
from datetime import datetime
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from deep_translator import GoogleTranslator

# ------------------ Chart Flowable ------------------
class ChartFlowable(Flowable):
    def __init__(self, drawing):
        Flowable.__init__(self)
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)

# ------------------ Font Handling ------------------
FONT_MAP = {
    "hi": ("NotoSansDevanagari-Regular.ttf", "NotoSansDevanagari"),
    "bn": ("NotoSansBengali-Regular.ttf", "NotoSansBengali"),
    "ta": ("NotoSansTamil-Regular.ttf", "NotoSansTamil"),
    "te": ("NotoSansTelugu-Regular.ttf", "NotoSansTelugu"),
    "ml": ("NotoSansMalayalam-Regular.ttf", "NotoSansMalayalam"),
    "gu": ("NotoSansGujarati-Regular.ttf", "NotoSansGujarati"),
    "kn": ("NotoSansKannada-Regular.ttf", "NotoSansKannada"),
    "pa": ("NotoSansGurmukhi-Regular.ttf", "NotoSansGurmukhi"),
    "or": ("NotoSansOdia-Regular.ttf", "NotoSansOdia"),
    "as": ("NotoSansBengali-Regular.ttf", "NotoSansAssamese"),
    "en": ("NotoSans-Regular.ttf", "NotoSans")
}


def register_font_for_lang(lang_code="en"):
    ttf_file, font_name = FONT_MAP.get(lang_code, FONT_MAP["en"])
    if not os.path.exists(ttf_file):
        folder_map = {
            "hi": "NotoSansDevanagari",
            "bn": "NotoSansBengali",
            "ta": "NotoSansTamil",
            "te": "NotoSansTelugu",
            "ml": "NotoSansMalayalam",
            "gu": "NotoSansGujarati",
            "kn": "NotoSansKannada",
            "pa": "NotoSansGurmukhi",
            "or": "NotoSansOdia",
            "as": "NotoSansBengali",
            "en": "NotoSans"
        }
        folder = folder_map.get(lang_code, "NotoSans")
        url = f"https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/{folder}/{ttf_file}"
        r = requests.get(url)
        with open(ttf_file, "wb") as f:
            f.write(r.content)
    pdfmetrics.registerFont(TTFont(font_name, ttf_file))
    return font_name

# ------------------ Translation Helper ------------------
def translate_text(text, target_lang):
    if not text:
        return ""
    try:
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except Exception as e:
        print(f"⚠️ Translation failed for '{text[:30]}...': {e}")
        return text

# ------------------ Health Report Generator ------------------
class HealthReportGenerator:
    def __init__(self, logo_path=None, font_name="NotoFont"):
        self.styles = getSampleStyleSheet()
        self.logo_path = logo_path
        self.font_name = font_name
        self.setup_custom_styles()

    def setup_custom_styles(self):
        self.title_style = ParagraphStyle('Title', parent=self.styles['Heading1'],
                                          fontSize=22, textColor=colors.HexColor("#1A237E"),
                                          alignment=1, spaceAfter=20, fontName=self.font_name)
        self.sub_title_style = ParagraphStyle('Subtitle', parent=self.styles['Normal'],
                                              fontSize=12, textColor=colors.grey,
                                              alignment=1, spaceAfter=30, fontName=self.font_name)
        self.section_header_style = ParagraphStyle('SectionHeader', parent=self.styles['Heading2'],
                                                   fontSize=14, textColor=colors.HexColor("#0D47A1"),
                                                   alignment=0, spaceBefore=12, spaceAfter=6,
                                                   fontName=self.font_name)
        self.normal_text = ParagraphStyle('NormalText', parent=self.styles['Normal'],
                                          fontSize=10, textColor=colors.black,
                                          alignment=0, spaceAfter=4, fontName=self.font_name)
        self.status_high = ParagraphStyle('StatusHigh', parent=self.styles['Normal'],
                                          fontSize=10, textColor=colors.red, fontName=self.font_name)
        self.status_low = ParagraphStyle('StatusLow', parent=self.styles['Normal'],
                                         fontSize=10, textColor=colors.blue, fontName=self.font_name)
        self.status_normal = ParagraphStyle('StatusNormal', parent=self.styles['Normal'],
                                            fontSize=10, textColor=colors.green, fontName=self.font_name)
        self.footnote_style = ParagraphStyle('Footnote', parent=self.styles['Normal'],
                                             fontSize=8, textColor=colors.grey,
                                             alignment=1, spaceBefore=20, fontName=self.font_name)

    # ------------------ Parse reference range ------------------
    def parse_reference_range(self, reference_range):
        if not reference_range:
            return None
        match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', reference_range)
        if match:
            return {'normal_min': float(match.group(1)), 'normal_max': float(match.group(2))}
        return None

    # ------------------ Bar chart ------------------
    def create_bar_chart(self, result_value, test_data):
        drawing = Drawing(300, 50)
        bar_width, bar_height = 220, 12
        bar_x, bar_y = 50, 20

        try:
            val_str = str(result_value).replace(',', '').replace('+', '')
            if not val_str or val_str.lower() in ['nil', 'negative', 'absent', 'present', 'clear']:
                return None

            numeric_value = float(val_str)
            ranges = test_data.get('ranges') or self.parse_reference_range(test_data.get('reference_range', ''))
            if not ranges:
                return None

            normal_min, normal_max = ranges['normal_min'], ranges['normal_max']
            chart_max = max(normal_max * 1.3, numeric_value * 1.2)

            low_width = (normal_min / chart_max) * bar_width
            normal_width = ((normal_max - normal_min) / chart_max) * bar_width
            high_width = bar_width - low_width - normal_width

            if low_width > 0:
                drawing.add(Rect(bar_x, bar_y, low_width, bar_height, fillColor=colors.pink, strokeColor=colors.black, strokeWidth=0.25))
            drawing.add(Rect(bar_x + low_width, bar_y, normal_width, bar_height, fillColor=colors.lightgreen, strokeColor=colors.black, strokeWidth=0.25))
            if high_width > 0:
                drawing.add(Rect(bar_x + low_width + normal_width, bar_y, high_width, bar_height, fillColor=colors.lightyellow, strokeColor=colors.black, strokeWidth=0.25))

            value_pos = bar_x + (min(numeric_value, chart_max) / chart_max) * bar_width
            drawing.add(Rect(value_pos - 1, bar_y - 3, 2, bar_height + 6, fillColor=colors.red, strokeColor=colors.red))
            drawing.add(String(value_pos - 10, bar_y + bar_height + 5, f"{result_value}", fontName=self.font_name, fontSize=7, fillColor=colors.red))
            return drawing

        except Exception:
            return None

    # ------------------ Test section ------------------
    def create_test_section(self, test_data, labels):
        elements = []
        status = test_data.get('status', 'UNKNOWN')
        if status.upper() == "HIGH":
            status_para = Paragraph(status, self.status_high)
        elif status.upper() == "LOW":
            status_para = Paragraph(status, self.status_low)
        else:
            status_para = Paragraph(status, self.status_normal)

        chart = self.create_bar_chart(test_data['value'], test_data)
        chart_flowable = ChartFlowable(chart) if chart else Paragraph("N/A", self.normal_text)

        table_data = [
            [Paragraph(f"<b>{labels.get('Test','Test')}:</b>", self.normal_text), Paragraph(test_data['name'], self.normal_text)],
            [Paragraph(f"<b>{labels.get('Result','Result')}:</b>", self.normal_text), Paragraph(f"{test_data['value']} {test_data.get('unit','')}", self.normal_text)],
            [Paragraph(f"<b>{labels.get('Status','Status')}:</b>", self.normal_text), status_para],
            [Paragraph(f"<b>{labels.get('Reference','Reference')}:</b>", self.normal_text), Paragraph(test_data.get('reference_range','N/A'), self.normal_text)],
            [Paragraph(f"<b>{labels.get('Chart','Chart')}:</b>", self.normal_text), chart_flowable]
        ]

        if 'meaning' in test_data and test_data['meaning']:
            table_data.append([Paragraph(f"<b>{labels.get('Meaning','Meaning')}:</b>", self.normal_text), Paragraph(test_data['meaning'], self.normal_text)])
        if 'tips' in test_data and test_data['tips']:
            table_data.append([Paragraph(f"<b>{labels.get('Tips','Tips')}:</b>", self.normal_text), Paragraph(test_data['tips'], self.normal_text)])

        table = Table(table_data, colWidths=[80, 380])
        table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.6, colors.grey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))
        return elements


    # ------------------ Header/Footer ------------------
    def add_header_footer(self, canvas, doc):
        canvas.saveState()
        # --- Add Image on Top ---
        try:
            img_width = 240  # adjust size
            img_height = 30
            x = (A4[0]) / 2
            y = A4[1] - 30               # from top margin
            canvas.drawImage(self.logo_path, x, y, width=img_width, height=img_height, preserveAspectRatio=True)
        except Exception as e:
            print(f"⚠️ Could not load image: {e}")
        canvas.setFont(self.font_name, 9)
        canvas.setFillColor(colors.HexColor("#1A237E"))
        canvas.drawString(30, A4[1] - 30, "Health Report Summary")
        canvas.setFont(self.font_name, 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(30, 20, f"Generated on {datetime.now().strftime('%B %d, %Y')}")
        canvas.drawRightString(A4[0] - 30, 20, f"Page {doc.page}")
        canvas.restoreState()

    # ------------------ Generate PDF from data ------------------
    def generate_pdf_from_data(self, report_data, output_pdf_path, lang_name="English", labels=None):
        if labels is None:
            labels = {label: label for label in COMMON_LABELS}
        try:
            doc = SimpleDocTemplate(output_pdf_path, pagesize=A4,
                                    topMargin=0.8*inch, bottomMargin=0.8*inch,
                                    leftMargin=0.75*inch, rightMargin=0.75*inch)
            story = []
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph(labels.get("Health Report Summary", "Health Report Summary"), self.title_style))
            story.append(Paragraph(labels.get("Confidential Medical Document", "Confidential Medical Document"), self.sub_title_style))
            story.append(Paragraph(f"{labels.get('Language','Language')}: {lang_name}", self.normal_text))
            story.append(Paragraph(f"{labels.get('Generated on','Generated on')}: {datetime.now().strftime('%B %d, %Y')}", self.normal_text))
            story.append(PageBreak())
            for test in report_data.get('tests', []):
                story.extend(self.create_test_section(test, labels))
            story.append(Paragraph(labels.get("End of Report", "End of Report"), self.footnote_style))
            doc.build(story, onFirstPage=self.add_header_footer, onLaterPages=self.add_header_footer)
            return True
        except Exception as e:
            print(f"❌ Error generating PDF: {str(e)}")
            return False

COMMON_LABELS = [
    "Health Report Summary",
    "Confidential Medical Document",
    "Language",
    "Generated on",
    "End of Report",
    "Test",
    "Result",
    "Status",
    "Reference",
    "Meaning",
    "Tips",
    "Chart"
]

def get_translated_labels(lang_code):
    translated = {}
    for label in COMMON_LABELS:
        translated[label] = translate_text(label, lang_code)
    return translated

# ------------------ Multi-language PDF Runner ------------------
def generate_multilang_reports(json_file, output_folder, logo_path=None):
    languages = {
        "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
        "ml": "Malayalam", "gu": "Gujarati", "kn": "Kannada",
        "pa": "Punjabi", "or": "Odia", "as": "Assamese"
    }

    with open(json_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    os.makedirs(output_folder, exist_ok=True)

    for lang_code, lang_name in languages.items():
        font_name = register_font_for_lang(lang_code)

        # Translate common labels
        labels = get_translated_labels(lang_code)

        # Translate test data
        translated_data = {"tests": []}
        for test in report_data.get("tests", []):
            translated_test = {
                "name": translate_text(test["name"], lang_code),
                "value": test["value"],
                "unit": test.get("unit", ""),
                "status": translate_text(test.get("status", ""), lang_code),
                "reference_range": test.get("reference_range", ""),
                "meaning": translate_text(test.get("meaning", ""), lang_code) if test.get("meaning") else "",
                "tips": translate_text(test.get("tips", ""), lang_code) if test.get("tips") else ""
            }
            translated_data["tests"].append(translated_test)

        output_pdf = f"{output_folder}/health_report_{lang_code}.pdf"
        generator = HealthReportGenerator(logo_path=logo_path, font_name=font_name)
        success = generator.generate_pdf_from_data(translated_data, output_pdf, lang_name, labels)
        if success:
            print(f"✅ Generated {lang_name} report: {output_pdf}")
        else:
            print(f"❌ Failed to generate {lang_name} report")

# ------------------ Main ------------------
def main():
    json_file = "healthfinit-ai-modules/health_report_data.json"  # path to your input JSON
    output_folder = "healthfinit-ai-modules/reports"
    logo_path = "healthfinit-ai-modules/logo_img.png"  # optional

    # English PDF first
    font_name = register_font_for_lang("en")
    generator = HealthReportGenerator(logo_path=logo_path, font_name=font_name)
    with open(json_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    generator.generate_pdf_from_data(report_data, f"{output_folder}/health_report_en.pdf", "English")

    # Generate multi-language reports
    generate_multilang_reports(json_file, output_folder, logo_path)

if __name__ == "__main__":
    main()
