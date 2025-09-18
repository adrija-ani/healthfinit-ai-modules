# import json
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# from reportlab.graphics.shapes import Drawing, Rect, String
# from reportlab.graphics import renderPDF
# from reportlab.platypus.flowables import Flowable
# from datetime import datetime
# import os

# class ChartFlowable(Flowable):
#     def __init__(self, drawing):
#         Flowable.__init__(self)
#         self.drawing = drawing
#         self.width = drawing.width
#         self.height = drawing.height

#     def draw(self):
#         renderPDF.draw(self.drawing, self.canv, 0, 0)

# class HealthReportGenerator:
#     def __init__(self):
#         self.styles = getSampleStyleSheet()
#         self.setup_custom_styles()
    
#     def setup_custom_styles(self):
#         self.title_style = ParagraphStyle(
#             'Title',
#             parent=self.styles['Heading1'],
#             fontSize=20,
#             textColor=colors.black,
#             alignment=TA_CENTER,
#             spaceAfter=20,
#             fontName='Helvetica-Bold'
#         )
        
#         self.test_name_style = ParagraphStyle(
#             'TestName',
#             parent=self.styles['Heading2'],
#             fontSize=16,
#             textColor=colors.darkblue,
#             alignment=TA_LEFT,
#             spaceBefore=15,
#             spaceAfter=8,
#             fontName='Helvetica-Bold'
#         )
        
#         self.result_style = ParagraphStyle(
#             'Result',
#             parent=self.styles['Normal'],
#             fontSize=12,
#             textColor=colors.black,
#             alignment=TA_LEFT,
#             spaceAfter=4,
#             fontName='Helvetica'
#         )
        
#         self.status_high_style = ParagraphStyle(
#             'StatusHigh',
#             parent=self.styles['Normal'],
#             fontSize=12,
#             textColor=colors.red,
#             alignment=TA_LEFT,
#             spaceAfter=10,
#             fontName='Helvetica-Bold'
#         )
        
#         self.status_low_style = ParagraphStyle(
#             'StatusLow',
#             parent=self.styles['Normal'],
#             fontSize=12,
#             textColor=colors.blue,
#             alignment=TA_LEFT,
#             spaceAfter=10,
#             fontName='Helvetica-Bold'
#         )
        
#         self.status_normal_style = ParagraphStyle(
#             'StatusNormal',
#             parent=self.styles['Normal'],
#             fontSize=12,
#             textColor=colors.green,
#             alignment=TA_LEFT,
#             spaceAfter=10,
#             fontName='Helvetica-Bold'
#         )
        
#         self.meaning_style = ParagraphStyle(
#             'Meaning',
#             parent=self.styles['Normal'],
#             fontSize=10,
#             textColor=colors.darkslategray,
#             alignment=TA_LEFT,
#             spaceAfter=6,
#             fontName='Helvetica',
#             leftIndent=10
#         )
        
#         self.tips_style = ParagraphStyle(
#             'Tips',
#             parent=self.styles['Normal'],
#             fontSize=10,
#             textColor=colors.darkgreen,
#             alignment=TA_LEFT,
#             spaceAfter=15,
#             fontName='Helvetica',
#             leftIndent=10
#         )
    
#     def parse_reference_range(self, reference_range):
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
    
#     def create_bar_chart(self, test_name, result_value, unit, test_data):
#         drawing = Drawing(400, 60)
        
#         bar_width = 280
#         bar_height = 15
#         bar_x = 60
#         bar_y = 25
        
#         try:
#             clean_value = str(result_value).replace(',', '').replace(' ', '').replace('+', '').replace('(', '').replace(')', '')
#             if not clean_value or clean_value.lower() in ['nil', 'negative', 'absent', 'present', 'clear', 'acidic', 'occasional']:
#                 return None
                
#             numeric_value = float(clean_value)
#             ranges = None
            
#             if 'ranges' in test_data and test_data['ranges'] and 'normal_min' in test_data['ranges']:
#                 ranges = test_data['ranges']
#             elif 'reference_range' in test_data and test_data['reference_range']:
#                 ranges = self.parse_reference_range(test_data['reference_range'])
            
#             if not ranges or 'normal_min' not in ranges or 'normal_max' not in ranges:
#                 return None
                
#             normal_min = float(ranges['normal_min'])
#             normal_max = float(ranges['normal_max'])
            
#             chart_max = max(normal_max * 1.3, numeric_value * 1.1)
#             if chart_max == 0:
#                 chart_max = 100
            
#             low_width = (normal_min / chart_max) * bar_width
#             normal_width = ((normal_max - normal_min) / chart_max) * bar_width
#             high_width = bar_width - low_width - normal_width
            
#             if low_width > 0:
#                 drawing.add(Rect(bar_x, bar_y, low_width, bar_height, 
#                                fillColor=colors.pink, strokeColor=colors.black, strokeWidth=0.5))
            
#             drawing.add(Rect(bar_x + low_width, bar_y, normal_width, bar_height, 
#                            fillColor=colors.lightgreen, strokeColor=colors.black, strokeWidth=0.5))
            
#             if high_width > 0:
#                 drawing.add(Rect(bar_x + low_width + normal_width, bar_y, high_width, bar_height, 
#                                fillColor=colors.lightyellow, strokeColor=colors.black, strokeWidth=0.5))
            
#             drawing.add(String(bar_x, bar_y - 8, f"<{normal_min}", fontSize=7, fillColor=colors.black))
#             drawing.add(String(bar_x + low_width + 5, bar_y - 8, f"{normal_min}-{normal_max}", fontSize=7, fillColor=colors.black))
#             if high_width > 10:
#                 drawing.add(String(bar_x + low_width + normal_width + 5, bar_y - 8, f">{normal_max}", fontSize=7, fillColor=colors.black))
            
#             value_pos = bar_x + (min(numeric_value, chart_max) / chart_max) * bar_width
#             drawing.add(Rect(value_pos - 1, bar_y - 3, 2, bar_height + 6, 
#                            fillColor=colors.red, strokeColor=colors.red))
            
#             drawing.add(String(value_pos - 10, bar_y + bar_height + 5, 
#                              f"You: {result_value}", fontSize=7, fillColor=colors.red))
            
#             return drawing
        
#         except (ValueError, TypeError, KeyError):
#             return None
    
#     def create_test_section(self, test_data):
#         elements = []
        
#         test_name = Paragraph(test_data['name'], self.test_name_style)
#         elements.append(test_name)
        
#         result_text = f"<b>Result:</b> {test_data['value']} {test_data.get('unit', '')}"
#         result = Paragraph(result_text, self.result_style)
#         elements.append(result)
        
#         status = test_data.get('status', 'UNKNOWN')
#         if status == "HIGH":
#             status_para = Paragraph(f"<b>Status:</b> {status}", self.status_high_style)
#         elif status == "LOW":
#             status_para = Paragraph(f"<b>Status:</b> {status}", self.status_low_style)
#         else:
#             status_para = Paragraph(f"<b>Status:</b> {status}", self.status_normal_style)
#         elements.append(status_para)
        
#         chart = self.create_bar_chart(
#             test_data['name'], 
#             test_data['value'], 
#             test_data.get('unit', ''),
#             test_data
#         )
#         if chart:
#             chart_flowable = ChartFlowable(chart)
#             elements.append(chart_flowable)
#             elements.append(Spacer(1, 0.05*inch))
        
#         if 'meaning' in test_data and test_data['meaning']:
#             meaning_text = f"<b>Meaning:</b> {test_data['meaning']}"
#             meaning = Paragraph(meaning_text, self.meaning_style)
#             elements.append(meaning)
        
#         if 'tips' in test_data and test_data['tips']:
#             tips_text = f"<b>Tips:</b> {test_data['tips']}"
#             tips = Paragraph(tips_text, self.tips_style)
#             elements.append(tips)
        
#         elements.append(Spacer(1, 0.3*inch))
        
#         return elements
    
#     def generate_pdf(self, json_file_path, output_pdf_path):
#         try:
#             with open(json_file_path, 'r', encoding='utf-8') as f:
#                 report_data = json.load(f)
            
#             doc = SimpleDocTemplate(output_pdf_path, pagesize=A4, 
#                                   topMargin=0.75*inch, bottomMargin=0.75*inch,
#                                   leftMargin=0.75*inch, rightMargin=0.75*inch)
            
#             story = []
            
#             title = Paragraph("Health Report Summary", self.title_style)
#             story.append(title)
            
#             date_style = ParagraphStyle(
#                 'Date',
#                 parent=self.styles['Normal'],
#                 fontSize=10,
#                 alignment=TA_CENTER,
#                 spaceAfter=20
#             )
#             date_para = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", date_style)
#             story.append(date_para)
#             story.append(Spacer(1, 0.3*inch))
            
#             tests = report_data.get('tests', [])
#             for i, test in enumerate(tests):
#                 test_elements = self.create_test_section(test)
#                 story.extend(test_elements)
                
#                 if i < len(tests) - 1:
#                     story.append(Spacer(1, 0.2*inch))
            
#             doc.build(story)
#             return True
            
#         except Exception as e:
#             print(f"Error generating PDF: {str(e)}")
#             return False

# def main():
#     json_file = "health_report_data.json"
#     output_pdf = "health_report_summary_test.pdf"
    
#     generator = HealthReportGenerator()
#     success = generator.generate_pdf(json_file, output_pdf)
    
#     if success:
#         print(f"Health report PDF generated successfully: {output_pdf}")
#     else:
#         print("Failed to generate PDF")

# if __name__ == "__main__":
#     main()

import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from datetime import datetime


# --- Chart Flowable Wrapper ---
class ChartFlowable(Flowable):
    def __init__(self, drawing):
        Flowable.__init__(self)
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)


# --- Health Report Generator ---
class HealthReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Define custom styles for different sections"""
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor("#1A237E"),
            alignment=1,  # Center
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )

        self.sub_title_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=1,
            spaceAfter=30
        )

        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor("#0D47A1"),
            alignment=0,  # Left
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )

        self.normal_text = ParagraphStyle(
            'NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=0,
            spaceAfter=4,
            fontName='Helvetica'
        )

        self.status_high = ParagraphStyle(
            'StatusHigh',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        )

        self.status_low = ParagraphStyle(
            'StatusLow',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.blue,
            fontName='Helvetica-Bold'
        )

        self.status_normal = ParagraphStyle(
            'StatusNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.green,
            fontName='Helvetica-Bold'
        )

        self.footnote_style = ParagraphStyle(
            'Footnote',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1,
            spaceBefore=20
        )

    def parse_reference_range(self, reference_range):
        """Parse string ranges like 70-110 into dict"""
        import re
        if not reference_range:
            return None

        range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', reference_range)
        if range_match:
            return {
                'normal_min': float(range_match.group(1)),
                'normal_max': float(range_match.group(2))
            }
        return None

    def create_bar_chart(self, result_value, test_data):
        """Create a bar chart visualization for the test"""
        drawing = Drawing(300, 50)
        bar_width, bar_height = 220, 12
        bar_x, bar_y = 50, 20

        try:
            clean_value = str(result_value).replace(',', '').replace('+', '')
            if not clean_value or clean_value.lower() in [
                'nil', 'negative', 'absent', 'present', 'clear'
            ]:
                return None

            numeric_value = float(clean_value)

            # Determine normal ranges
            ranges = test_data.get('ranges') or self.parse_reference_range(
                test_data.get('reference_range', '')
            )
            if not ranges:
                return None

            normal_min, normal_max = ranges['normal_min'], ranges['normal_max']
            chart_max = max(normal_max * 1.3, numeric_value * 1.2)

            # Low - Normal - High regions
            low_width = (normal_min / chart_max) * bar_width
            normal_width = ((normal_max - normal_min) / chart_max) * bar_width
            high_width = bar_width - low_width - normal_width

            if low_width > 0:
                drawing.add(Rect(bar_x, bar_y, low_width, bar_height,
                                 fillColor=colors.pink, strokeColor=colors.black, strokeWidth=0.25))
            drawing.add(Rect(bar_x + low_width, bar_y, normal_width, bar_height,
                             fillColor=colors.lightgreen, strokeColor=colors.black, strokeWidth=0.25))
            if high_width > 0:
                drawing.add(Rect(bar_x + low_width + normal_width, bar_y, high_width, bar_height,
                                 fillColor=colors.lightyellow, strokeColor=colors.black, strokeWidth=0.25))

            # Mark value
            value_pos = bar_x + (min(numeric_value, chart_max) / chart_max) * bar_width
            drawing.add(Rect(value_pos - 1, bar_y - 3, 2, bar_height + 6,
                             fillColor=colors.red, strokeColor=colors.red))
            drawing.add(String(value_pos - 10, bar_y + bar_height + 5,
                               f"{result_value}", fontSize=7, fillColor=colors.red))
            return drawing

        except Exception:
            return None

    def create_test_section(self, test_data):
        """Builds a standardized table for each test"""
        elements = []

        # Status field
        status = test_data.get('status', 'UNKNOWN')
        if status == "HIGH":
            status_para = Paragraph("HIGH", self.status_high)
        elif status == "LOW":
            status_para = Paragraph("LOW", self.status_low)
        else:
            status_para = Paragraph("NORMAL", self.status_normal)

        # Chart
        chart = self.create_bar_chart(test_data['value'], test_data)
        chart_flowable = ChartFlowable(chart) if chart else Paragraph("N/A", self.normal_text)

        # Build structured table
        table_data = [
            [Paragraph("<b>Test:</b>", self.normal_text),
             Paragraph(test_data['name'], self.normal_text)],
            [Paragraph("<b>Result:</b>", self.normal_text),
             Paragraph(f"{test_data['value']} {test_data.get('unit', '')}", self.normal_text)],
            [Paragraph("<b>Status:</b>", self.normal_text), status_para],
            [Paragraph("<b>Reference:</b>", self.normal_text),
             Paragraph(test_data.get('reference_range', 'N/A'), self.normal_text)],
            [Paragraph("<b>Chart:</b>", self.normal_text), chart_flowable]
        ]

        if 'meaning' in test_data and test_data['meaning']:
            table_data.append([Paragraph("<b>Meaning:</b>", self.normal_text),
                               Paragraph(test_data['meaning'], self.normal_text)])

        if 'tips' in test_data and test_data['tips']:
            table_data.append([Paragraph("<b>Tips:</b>", self.normal_text),
                               Paragraph(test_data['tips'], self.normal_text)])

        table = Table(table_data, colWidths=[80, 380])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.6, colors.grey),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))
        return elements

    def add_header_footer(self, canvas, doc):
        """Header and footer for every page"""
        canvas.saveState()
        # Header
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor("#1A237E"))
        canvas.drawString(30, A4[1] - 30, "Health Report Summary")
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(30, 20, f"Generated on {datetime.now().strftime('%B %d, %Y')}")
        canvas.drawRightString(A4[0] - 30, 20, f"Page {doc.page}")
        canvas.restoreState()

    def generate_pdf(self, json_file_path, output_pdf_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            doc = SimpleDocTemplate(output_pdf_path, pagesize=A4,
                                    topMargin=0.8 * inch, bottomMargin=0.8 * inch,
                                    leftMargin=0.75 * inch, rightMargin=0.75 * inch)

            story = []

            # --- Cover Page ---
            story.append(Spacer(1, 2 * inch))
            story.append(Paragraph("Health Report Summary", self.title_style))
            story.append(Paragraph("Confidential Medical Document", self.sub_title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}",
                                   self.normal_text))
            story.append(PageBreak())

            # --- Test Sections ---
            tests = report_data.get('tests', [])
            for test in tests:
                story.extend(self.create_test_section(test))

            story.append(Paragraph("End of Report", self.footnote_style))

            doc.build(story, onFirstPage=self.add_header_footer,
                      onLaterPages=self.add_header_footer)
            return True

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False


# --- Main Execution ---
def main():
    json_file = "health_report_data.json"
    output_pdf = "health_report_summary_test.pdf"

    generator = HealthReportGenerator()
    success = generator.generate_pdf(json_file, output_pdf)

    if success:
        print(f"✅ Health report PDF generated successfully: {output_pdf}")
    else:
        print("❌ Failed to generate PDF")


if __name__ == "__main__":
    main()
