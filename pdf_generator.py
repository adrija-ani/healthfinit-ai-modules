

# import os
# import json
# import requests
# import re
# from datetime import datetime
# from math import pi
# from io import BytesIO

# # REQUIRED LIBRARIES (from prompt)
# try:
#     import cairo
#     import gi
#     gi.require_version("Pango", "1.0")
#     gi.require_version("PangoCairo", "1.0")
#     from gi.repository import Pango, PangoCairo
# except ImportError:
#     print("❌ Critical Error: Please ensure 'cairo', 'gi' (GObject Introspection), 'Pango', and 'PangoCairo' are installed.")
#     # On many Linux systems, this requires packages like python-gobject, python-cairo, and libpango-1.0-0.
#     cairo, Pango, PangoCairo = None, None, None

# from deep_translator import GoogleTranslator

# # A4 dimensions in points
# A4_WIDTH = 595
# A4_HEIGHT = 842
# MARGIN = 40
# LINE_HEIGHT = 12
# HEADER_HEIGHT = 50
# FOOTER_HEIGHT = 30

# # ------------------ Font Handling ------------------
# # Pango font family names and TTF file names
# FONT_MAP = {
#     "hi": ("NotoSansDevanagari-Regular.ttf", "Noto Sans Devanagari"),
#     "bn": ("NotoSansBengali-Regular.ttf", "Noto Sans Bengali"),
#     "ta": ("NotoSansTamil-Regular.ttf", "Noto Sans Tamil"),
#     "te": ("NotoSansTelugu-Regular.ttf", "Noto Sans Telugu"),
#     "ml": ("NotoSansMalayalam-Regular.ttf", "Noto Sans Malayalam"),
#     "gu": ("NotoSansGujarati-Regular.ttf", "Noto Sans Gujarati"),
#     "kn": ("NotoSansKannada-Regular.ttf", "Noto Sans Kannada"),
#     "pa": ("NotoSansGurmukhi-Regular.ttf", "Noto Sans Gurmukhi"),
#     "or": ("NotoSansOdia-Regular.ttf", "Noto Sans Odia"),
#     "as": ("NotoSansBengali-Regular.ttf", "Noto Sans Bengali"),
#     "en": ("NotoSans-Regular.ttf", "Noto Sans")
# }


# def register_font_for_lang(lang_code="en"):
#     """
#     Downloads the font if missing. Pango relies on system font config 
#     to find the font family name returned here.
#     Returns the Pango font family name string.
#     """
#     ttf_file, font_family = FONT_MAP.get(lang_code, FONT_MAP["en"])
    
#     # Check if the TTF file is downloaded (needed for dynamic demo)
#     if not os.path.exists(ttf_file):
#         folder_map = {
#             "hi": "NotoSansDevanagari", "bn": "NotoSansBengali", "ta": "NotoSansTamil", 
#             "te": "NotoSansTelugu", "ml": "NotoSansMalayalam", "gu": "NotoSansGujarati",
#             "kn": "NotoSansKannada", "pa": "NotoSansGurmukhi", "or": "NotoSansOdia",
#             "as": "NotoSansBengali", "en": "NotoSans"
#         }
#         folder = folder_map.get(lang_code, "NotoSans")
#         url = f"https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/{folder}/{ttf_file}"
#         print(f"⬇️ Downloading font for {lang_code}: {ttf_file}")
#         try:
#             r = requests.get(url, timeout=30)
#             r.raise_for_status()
#             with open(ttf_file, "wb") as f:
#                 f.write(r.content)
#         except requests.exceptions.RequestException as e:
#             print(f"❌ Failed to download font {ttf_file}. Proceeding with fallback: {e}")
#             return FONT_MAP["en"][1]

#     return font_family


# # ------------------ Translation Helper ------------------
# def translate_text(text, target_lang):
#     if not text:
#         return ""
#     try:
#         trans_text = GoogleTranslator(source="en", target=target_lang).translate(text)
#         return trans_text
#     except Exception:
#         return text

# # ------------------ Cairo/Pango Health Report Generator ------------------
# class CairoHealthReportGenerator:
    
#     def __init__(self, font_family="Noto Sans"):
#         self.font_family = font_family
#         self.current_y = MARGIN + HEADER_HEIGHT
#         self.page_num = 1
#         self.ctx = None # cairo.Context
#         self.surface = None # cairo.PDFSurface

#     # --- Utility: Pango Text Rendering ---
#     def draw_pango_text(self, text, x, y, size=10, weight='Normal', color_rgb=(0, 0, 0), align='LEFT', max_width=A4_WIDTH):
        
#         self.ctx.set_source_rgb(*color_rgb)
        
#         # Create Pango layout
#         layout = PangoCairo.create_layout(self.ctx)
        
#         # Set font description
#         font_desc_str = f'{self.font_family} {weight} {size}'
#         layout.set_font_description(Pango.FontDescription(font_desc_str))
        
#         # Handle simple bold tagging for keys (e.g., <b>Test:</b>)
#         if '<b>' in text:
#             layout.set_markup(text, -1)
#         else:
#             layout.set_text(text, -1)
        
#         # Set width for wrapping
#         layout.set_width(int((max_width - x) * Pango.SCALE)) 
#         layout.set_wrap(Pango.WrapMode.WORD)

#         if align == 'CENTER':
#             layout.set_alignment(Pango.Alignment.CENTER)
#         elif align == 'RIGHT':
#             layout.set_alignment(Pango.Alignment.RIGHT)
#         else:
#             layout.set_alignment(Pango.Alignment.LEFT)

#         # Render the text
#         self.ctx.move_to(x, y)
#         PangoCairo.show_layout(self.ctx, layout)
        
#         # Return the height used by the text
#         extents = layout.get_extents()
#         if extents[1].height > 0:
#             height = extents[1].height / Pango.SCALE
#             return height
#         return LINE_HEIGHT
    
#     # --- Utility: Color Map ---
#     def get_status_color(self, status_text):
#         RED = (1, 0, 0)
#         BLUE = (0, 0, 1)
#         GREEN = (0, 0.5, 0)
        
#         status_upper = status_text.upper()
#         if status_upper in ["HIGH", "HOGH", "HIGH", "HIGH"]: 
#             return RED
#         elif status_upper in ["LOW", "LOW"]: 
#             return BLUE
#         else:
#             return GREEN

#     # --- Header/Footer/Page Management ---
#     def start_new_page(self):
#         if self.page_num > 1:
#             self.surface.show_page()
        
#         self.page_num += 1
#         # Set Y position for content below the header
#         self.current_y = MARGIN + HEADER_HEIGHT 
#         self.draw_header_footer()
        
#     def draw_header_footer(self):
        
#         BLUE = (0.1, 0.1, 0.5)
#         GREY = (0.5, 0.5, 0.5)
        
#         # --- Header ---
#         self.ctx.set_source_rgb(*BLUE)
#         self.ctx.set_line_width(0.5)
        
#         # Top line
#         self.ctx.move_to(MARGIN, HEADER_HEIGHT - 10)
#         self.ctx.line_to(A4_WIDTH - MARGIN, HEADER_HEIGHT - 10)
#         self.ctx.stroke()
        
#         # Title text (fixed English title on header for simplicity)
#         self.draw_pango_text("Health Report Summary", MARGIN, 15, 9, 'Bold', BLUE)

#         # --- Footer ---
#         self.ctx.set_source_rgb(*GREY)
        
#         # Date/Page
#         date_str = f"Generated on {datetime.now().strftime('%B %d, %Y')}"
#         self.draw_pango_text(date_str, MARGIN, A4_HEIGHT - 20, 8, color_rgb=GREY)
#         self.draw_pango_text(f"Page {self.page_num}", A4_WIDTH - MARGIN, A4_HEIGHT - 20, 8, color_rgb=GREY, align='RIGHT')


#     # --- Parse reference range ---
#     def parse_reference_range(self, reference_range):
#         if not reference_range:
#             return None
#         match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', reference_range)
#         if match:
#             return {'normal_min': float(match.group(1)), 'normal_max': float(match.group(2))}
#         return None

#     # --- Bar chart (using cairo primitives) ---
#     def draw_bar_chart(self, x_start, y_start, result_value, test_data):
        
#         bar_width, bar_height = 220, 12
        
#         try:
#             val_str = str(result_value).replace(',', '').replace('+', '')
#             if not val_str or val_str.lower() in ['nil', 'negative', 'absent', 'present', 'clear']:
#                 self.draw_pango_text("N/A", x_start, y_start, 10, color_rgb=(0.5, 0.5, 0.5))
#                 return 15
            
#             numeric_value = float(val_str)
#             ranges = test_data.get('ranges') or self.parse_reference_range(test_data.get('reference_range', ''))
#             if not ranges:
#                 self.draw_pango_text("N/A (No range)", x_start, y_start, 10, color_rgb=(0.5, 0.5, 0.5))
#                 return 15

#             normal_min, normal_max = ranges['normal_min'], ranges['normal_max']
#             chart_max = max(normal_max * 1.3, numeric_value * 1.2)
            
#             # Colors
#             PINK = (1.0, 0.8, 0.8)
#             LIGHTGREEN = (0.7, 1.0, 0.7)
#             LIGHTYELLOW = (1.0, 1.0, 0.7)
#             RED = (1.0, 0.0, 0.0)

#             # Calculate widths
#             low_width = (normal_min / chart_max) * bar_width
#             normal_width = ((normal_max - normal_min) / chart_max) * bar_width
            
#             # Draw Bar Background
#             x = x_start
#             self.ctx.set_line_width(0.25)
            
#             # Low
#             if low_width > 0:
#                 self.ctx.rectangle(x, y_start, low_width, bar_height)
#                 self.ctx.set_source_rgb(*PINK)
#                 self.ctx.fill_preserve()
#                 self.ctx.set_source_rgb(0, 0, 0)
#                 self.ctx.stroke()
#                 x += low_width
                
#             # Normal
#             self.ctx.rectangle(x, y_start, normal_width, bar_height)
#             self.ctx.set_source_rgb(*LIGHTGREEN)
#             self.ctx.fill_preserve()
#             self.ctx.set_source_rgb(0, 0, 0)
#             self.ctx.stroke()
#             x += normal_width

#             # High (rest of the bar)
#             high_width = bar_width - (low_width + normal_width)
#             if high_width > 0:
#                 self.ctx.rectangle(x, y_start, high_width, bar_height)
#                 self.ctx.set_source_rgb(*LIGHTYELLOW)
#                 self.ctx.fill_preserve()
#                 self.ctx.set_source_rgb(0, 0, 0)
#                 self.ctx.stroke()
            
#             # Draw Value Marker (Red Line)
#             value_pos_x = x_start + (min(numeric_value, chart_max) / chart_max) * bar_width
#             self.ctx.set_source_rgb(*RED)
#             self.ctx.set_line_width(1.5)
#             self.ctx.move_to(value_pos_x, y_start - 3)
#             self.ctx.line_to(value_pos_x, y_start + bar_height + 3)
#             self.ctx.stroke()
            
#             # Draw Value Text
#             self.draw_pango_text(f"{result_value}", value_pos_x - 10, y_start + bar_height + 5, 7, color_rgb=RED)

#             return 35 # Height used by the chart
            
#         except Exception:
#             self.draw_pango_text("N/A", x_start, y_start, 10, color_rgb=(0.5, 0.5, 0.5))
#             return 15

#     # --- Test section (Manual Table Drawing) ---
#     def draw_test_section(self, test_data, labels):
        
#         CELL_MARGIN = 5
#         KEY_WIDTH = 80
#         VALUE_WIDTH = A4_WIDTH - 2 * MARGIN - KEY_WIDTH - 2 * CELL_MARGIN
        
#         # Row data: (Key label, Value content, Status related, Chart required)
#         rows = [
#             (labels.get('Test','Test'), test_data['name'], False, False),
#             (labels.get('Result','Result'), f"{test_data['value']} {test_data.get('unit','')}", True, False),
#             (labels.get('Status','Status'), test_data['status'], True, False),
#             (labels.get('Reference','Reference'), test_data.get('reference_range','N/A'), False, False),
#             (labels.get('Chart','Chart'), test_data['value'], False, True)
#         ]
        
#         if 'meaning' in test_data and test_data['meaning']:
#             rows.append((labels.get('Meaning','Meaning'), test_data['meaning'], False, False))
#         if 'tips' in test_data and test_data['tips']:
#             rows.append((labels.get('Tips','Tips'), test_data['tips'], False, False))

#         # --- 1. Calculate Table Height ---
#         total_height = 0
#         row_heights = []
        
#         for key, value, is_status, is_chart in rows:
#             if is_chart:
#                 height = 35 + 2 * CELL_MARGIN
#             else:
#                 # Use a temporary layout to measure wrapping height
#                 temp_layout = PangoCairo.create_layout(self.ctx)
#                 # Setting text/markup is necessary for measurement
#                 if '<b>' in key: temp_layout.set_markup(value, -1)
#                 else: temp_layout.set_text(value, -1)
#                 temp_layout.set_font_description(Pango.FontDescription(f'{self.font_family} Normal 10'))
#                 temp_layout.set_width(int(VALUE_WIDTH * Pango.SCALE)) 
#                 temp_layout.set_wrap(Pango.WrapMode.WORD)
                
#                 pango_height = temp_layout.get_extents()[1].height / Pango.SCALE
#                 height = max(LINE_HEIGHT, pango_height) + 2 * CELL_MARGIN
            
#             row_heights.append(height)
#             total_height += height

#         # --- 2. Check Page Break ---
#         if self.current_y + total_height + 15 > A4_HEIGHT - FOOTER_HEIGHT - MARGIN:
#             self.start_new_page()
            
#         # --- 3. Draw Table Structure ---
#         table_x = MARGIN
#         table_y = self.current_y
#         current_y_pos = table_y
        
#         # Outer box
#         self.ctx.set_line_width(0.6)
#         self.ctx.set_source_rgb(0.5, 0.5, 0.5) 
#         self.ctx.rectangle(table_x, table_y, A4_WIDTH - 2 * MARGIN, total_height)
#         self.ctx.stroke()
        
#         # Inner grid setup
#         self.ctx.set_line_width(0.25)
#         self.ctx.set_source_rgb(0.8, 0.8, 0.8)

#         # --- 4. Draw Rows and Content ---
#         for i, ((key, value, is_status, is_chart), row_h) in enumerate(zip(rows, row_heights)):
            
#             # Draw Row Separator (Inner Grid)
#             self.ctx.move_to(table_x, current_y_pos + row_h)
#             self.ctx.line_to(A4_WIDTH - MARGIN, current_y_pos + row_h)
#             self.ctx.stroke()
            
#             # Draw Key-Value Separator (Inner Grid)
#             self.ctx.move_to(table_x + KEY_WIDTH, current_y_pos)
#             self.ctx.line_to(table_x + KEY_WIDTH, current_y_pos + row_h)
#             self.ctx.stroke()
            
#             # Key column background for the first row (Header)
#             if i == 0:
#                 self.ctx.rectangle(table_x, current_y_pos, KEY_WIDTH, row_h)
#                 self.ctx.set_source_rgb(0.95, 0.95, 0.95)
#                 self.ctx.fill()
#                 self.ctx.set_source_rgb(0.8, 0.8, 0.8) 
#                 self.ctx.rectangle(table_x, current_y_pos, KEY_WIDTH, row_h)
#                 self.ctx.stroke()

#             # 1. Draw Key Text (Bold using Pango markup)
#             self.draw_pango_text(f"<b>{key}:</b>", 
#                                  table_x + CELL_MARGIN, current_y_pos + CELL_MARGIN, 10, 'Bold')
            
#             # 2. Draw Value Content
#             value_x = table_x + KEY_WIDTH + CELL_MARGIN
#             value_y = current_y_pos + CELL_MARGIN
            
#             if is_chart:
#                 self.draw_bar_chart(value_x, value_y, value, test_data)
#             elif is_status:
#                 color_rgb = self.get_status_color(value)
#                 self.draw_pango_text(value, value_x, value_y, 10, 'Bold', color_rgb=color_rgb, max_width=A4_WIDTH - MARGIN)
#             else:
#                 self.draw_pango_text(value, value_x, value_y, 10, max_width=A4_WIDTH - MARGIN)
                
#             current_y_pos += row_h

#         self.current_y = current_y_pos + 15 # Spacer after table


#     # --- Generate PDF from data ---
#     def generate_pdf_from_data(self, report_data, output_pdf_path, lang_name="English", labels=None):
#         if labels is None:
#             labels = {label: label for label in COMMON_LABELS}
            
#         try:
#             # 1. Setup Cairo Surface and Context
#             self.surface = cairo.PDFSurface(output_pdf_path, A4_WIDTH, A4_HEIGHT)
#             self.ctx = cairo.Context(self.surface)
            
#             self.page_num = 1
            
#             # --- Dedicated First Page for Titles (Page 1) ---
            
#             # Set Y position for titles (centered vertically)
#             self.current_y = A4_HEIGHT
            
#             # 1a. Draw Titles
#             report_title = labels.get("Health Report Summary")
#             sub_title = labels.get("Confidential Medical Document")
#             self.start_new_page()
            
#             self.draw_pango_text(report_title, A4_WIDTH-600, self.current_y, 22, 'Bold', (0.1, 0.14, 0.5), 'CENTER', max_width=A4_WIDTH)
#             self.current_y += 40
#             self.draw_pango_text(sub_title, A4_WIDTH-600, self.current_y, 16, 'Normal', (0.5, 0.5, 0.5), 'CENTER', max_width=A4_WIDTH)
#             self.current_y += 30
            
#             # 1b. Language and Generated Info (at bottom of first page)
#             lang_label = labels.get('Language','Language')
#             generated_label = labels.get('Generated on','Generated on')
            
#             # Place this info near the bottom, before the footer area
#             info_y = A4_HEIGHT - 100
#             self.draw_pango_text(f"<b>{lang_label}:</b> {lang_name}", MARGIN, info_y, 10, 'Normal', max_width=A4_WIDTH)
#             info_y += 15
#             self.draw_pango_text(f"<b>{generated_label}:</b> {datetime.now().strftime('%B %d, %Y')}", MARGIN, info_y, 10, 'Normal', max_width=A4_WIDTH)
            
#             # Draw the header/footer (Page 1)
#             self.draw_header_footer()
            
#             # --- Start Second Page for Content (Page 2 onwards) ---
#             self.start_new_page() # Increments page_num to 2 and draws header/footer
            
#             # 3. Draw Test Sections
#             for test in report_data.get('tests', []):
#                 self.draw_test_section(test, labels)
            
#             # 4. End of Report
#             end_label = labels.get("End of Report", "End of Report")
#             self.draw_pango_text(end_label, A4_WIDTH / 2, self.current_y + 10, 8, 'Normal', (0.5, 0.5, 0.5), 'CENTER', max_width=A4_WIDTH)
            
#             # 5. Finalize PDF
#             self.surface.finish()
#             return True
            
#         except Exception as e:
#             print(f"❌ Error generating PDF: {str(e)}")
#             return False

# COMMON_LABELS = [
#     "Health Report Summary", "Confidential Medical Document", "Language",
#     "Generated on", "End of Report", "Test", "Result", "Status", 
#     "Reference", "Meaning", "Tips", "Chart"
# ]

# def get_translated_labels(lang_code):
#     """Translates high-level report components."""
#     translated = {}
#     for label in COMMON_LABELS:
#         #translated[label] = translate_text(label, lang_code)
#         translated[label] = label
#     return translated

# # ------------------ Multi-language PDF Runner ------------------
# def generate_multilang_reports(json_file, output_folder):
#     languages = {
#         "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
#         "ml": "Malayalam", "gu": "Gujarati", "kn": "Kannada",
#         "pa": "Punjabi", "or": "Odia", "as": "Assamese"
#     }

#     try:
#         with open(json_file, 'r', encoding='utf-8') as f:
#             report_data = json.load(f)
#     except Exception:
#         print(f"❌ Error: Could not load or parse '{json_file}'.")
#         return

#     os.makedirs(output_folder, exist_ok=True)

#     for lang_code, lang_name in languages.items():
#         # 1. Get Language-Specific Font Family Name
#         font_family = register_font_for_lang(lang_code)

#         # 2. Get Translated Labels (titles)
#         labels = get_translated_labels(lang_code)

#         # 3. Translate test data content
#         translated_data = {"tests": []}
#         for test in report_data.get("tests", []):
#             translated_test = {
#                 "name": translate_text(test["name"], lang_code),
#                 "value": test["value"],
#                 "unit": test.get("unit", ""),
#                 "status": translate_text(test.get("status", ""), lang_code),
#                 "reference_range": test.get("reference_range", ""),
#                 "meaning": translate_text(test.get("meaning", ""), lang_code) if test.get("meaning") else "",
#                 "tips": translate_text(test.get("tips", ""), lang_code) if test.get("tips") else ""
#             }
#             translated_data["tests"].append(translated_test)

#         output_pdf = f"{output_folder}/health_report_{lang_code}.pdf"
        
#         # 4. Generate PDF using Cairo/Pango
#         generator = CairoHealthReportGenerator(font_family=font_family)
#         success = generator.generate_pdf_from_data(translated_data, output_pdf, lang_name, labels)
        
#         if success:
#             print(f"✅ Generated {lang_name} report: {output_pdf} using font: {font_family}")
#         else:
#             print(f"❌ Failed to generate {lang_name} report")

# # ------------------ Main ------------------
# def main():
#     json_file = "health_report_data.json"
#     output_folder = "reports_multilang"
    
#     if not all([cairo, Pango, PangoCairo]):
#         print("\nExiting. Cairo/Pango (GObject Introspection) libraries are missing or could not be loaded.")
#         return

#     os.makedirs(output_folder, exist_ok=True)

#     # --- Dummy JSON Creation if needed ---
#     if not os.path.exists(json_file):
#         print(f"Creating dummy '{json_file}'.")
#         dummy_data = {
#             "tests": [
#                 {
#                     "name": "Hemoglobin",
#                     "value": "13.5",
#                     "unit": "g/dL",
#                     "status": "NORMAL",
#                     "reference_range": "11.5 - 15.5",
#                     "meaning": "Hemoglobin is the protein in red blood cells that carries oxygen.",
#                     "tips": "Maintain a balanced diet rich in iron and B vitamins."
#                 },
#                 {
#                     "name": "Blood Glucose (Fasting)",
#                     "value": "110",
#                     "unit": "mg/dL",
#                     "status": "HIGH",
#                     "reference_range": "70 - 100",
#                     "meaning": "Elevated fasting glucose can indicate pre-diabetes or diabetes.",
#                     "tips": "Consult a doctor. Increase physical activity and reduce sugar intake."
#                 },
#                 {
#                     "name": "Cholesterol (Total)",
#                     "value": "225",
#                     "unit": "mg/dL",
#                     "status": "HIGH",
#                     "reference_range": "0 - 200",
#                     "meaning": "High cholesterol increases risk of heart disease.",
#                     "tips": "Reduce saturated and trans fats. Exercise regularly."
#                 },
#                 {
#                     "name": "Vitamin D",
#                     "value": "18",
#                     "unit": "ng/mL",
#                     "status": "LOW",
#                     "reference_range": "30 - 100",
#                     "meaning": "Low Vitamin D can lead to bone density issues.",
#                     "tips": "Get sun exposure and consider supplements."
#                 }
#             ]
#         }
#         with open(json_file, 'w', encoding='utf-8') as f:
#             json.dump(dummy_data, f, indent=4)
#     # --- End Dummy JSON ---

#     # English PDF first
#     print("\n--- Generating English Report ---")
#     en_font_family = register_font_for_lang("en")
#     try:
#         with open(json_file, 'r', encoding='utf-8') as f:
#             report_data = json.load(f)
#         generator_en = CairoHealthReportGenerator(font_family=en_font_family)
#         success_en = generator_en.generate_pdf_from_data(report_data, f"{output_folder}/health_report_en.pdf", "English")
#         if success_en:
#             print(f"✅ Generated English report: {output_folder}/health_report_en.pdf using font: {en_font_family}")
#     except Exception as e:
#         print(f"Exiting main: Could not load or process '{json_file}'. Error: {e}")
#         return

#     # Generate multi-language reports
#     print("\n--- Generating Multi-Language Reports ---")
#     generate_multilang_reports(json_file, output_folder)

# if __name__ == "__main__":
#     main()

import os
import json
import requests
import re
import unicodedata
from datetime import datetime
from math import pi
from io import BytesIO

# REQUIRED LIBRARIES (from prompt)
try:
    import cairo
    import gi
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo
except ImportError:
    print("❌ Critical Error: Please ensure 'cairo', 'gi' (GObject Introspection), 'Pango', and 'PangoCairo' are installed.")
    # On many Linux systems, this requires packages like python-gobject, python-cairo, and libpango-1.0-0.
    cairo, Pango, PangoCairo = None, None, None

from deep_translator import GoogleTranslator

# A4 dimensions in points
A4_WIDTH = 595
A4_HEIGHT = 842
MARGIN = 40
LINE_HEIGHT = 12
HEADER_HEIGHT = 50
FOOTER_HEIGHT = 30

# ------------------ Font Handling ------------------
# Pango font family names and TTF file names
FONT_MAP = {
    "hi": ("NotoSansDevanagari-Regular.ttf", "Noto Sans Devanagari"),
    "bn": ("NotoSansBengali-Regular.ttf", "Noto Sans Bengali"),
    "ta": ("NotoSansTamil-Regular.ttf", "Noto Sans Tamil"),
    "te": ("NotoSansTelugu-Regular.ttf", "Noto Sans Telugu"),
    "ml": ("NotoSansMalayalam-Regular.ttf", "Noto Sans Malayalam"),
    "gu": ("NotoSansGujarati-Regular.ttf", "Noto Sans Gujarati"),
    "kn": ("NotoSansKannada-Regular.ttf", "Noto Sans Kannada"),
    "pa": ("NotoSansGurmukhi-Regular.ttf", "Noto Sans Gurmukhi"),
    "or": ("NotoSansOdia-Regular.ttf", "Noto Sans Odia"),
    "as": ("NotoSansBengali-Regular.ttf", "Noto Sans Bengali"),
    "en": ("NotoSans-Regular.ttf", "Noto Sans")
}


def register_font_for_lang(lang_code="en"):
    """
    Downloads the font if missing. Pango relies on system font config 
    to find the font family name returned here.
    Returns the Pango font family name string.
    """
    ttf_file, font_family = FONT_MAP.get(lang_code, FONT_MAP["en"])
    
    # Check if the TTF file is downloaded (needed for dynamic demo)
    if not os.path.exists(ttf_file):
        folder_map = {
            "hi": "NotoSansDevanagari", "bn": "NotoSansBengali", "ta": "NotoSansTamil", 
            "te": "NotoSansTelugu", "ml": "NotoSansMalayalam", "gu": "NotoSansGujarati",
            "kn": "NotoSansKannada", "pa": "NotoSansGurmukhi", "or": "NotoSansOdia",
            "as": "NotoSansBengali", "en": "NotoSans"
        }
        folder = folder_map.get(lang_code, "NotoSans")
        url = f"https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/{folder}/{ttf_file}"
        print(f"⬇️ Downloading font for {lang_code}: {ttf_file}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(ttf_file, "wb") as f:
                f.write(r.content)
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download font {ttf_file}. Proceeding with fallback: {e}")
            return FONT_MAP["en"][1]

    return font_family


# ------------------ Translation Helper ------------------
def translate_text(text, target_lang):
    if not text:
        return ""
    try:
        trans_text = GoogleTranslator(source="en", target=target_lang).translate(text)
        return trans_text
    except Exception:
        return text

# ------------------ Helpers for numeric normalization ------------------
def normalize_number_str(s: str):
    """
    Convert Unicode digits (e.g. Devanagari, Bengali) to ASCII digits,
    remove common thousands separators, normalize dash/minus, and keep only digits, '.' and '-'.
    Returns normalized ASCII string or empty string if nothing numeric found.
    """
    if s is None:
        return ""
    s = str(s).strip()

    normalized_chars = []
    for ch in s:
        # Try numeric digit conversion for many Unicode digit blocks
        try:
            d = unicodedata.digit(ch)
            normalized_chars.append(str(d))
            continue
        except (TypeError, ValueError):
            pass

        # Normalize various dash/minus characters to ASCII '-'
        if ch in "−–—\u2012\u2013\u2014\u2212":
            normalized_chars.append('-')
            continue

        # Accept ASCII digits and dot/minus
        if ch.isascii() and (ch.isdigit() or ch in ".-"):
            normalized_chars.append(ch)
            continue

        # Ignore common thousands separators
        if ch in [",", "\u2009", "\u202f"]:
            continue

        # ignore other characters (units, letters, whitespace)
        pass

    cleaned = "".join(normalized_chars)

    # If multiple dots, collapse to single dot (keep first)
    if cleaned.count('.') > 1:
        parts = cleaned.split('.')
        cleaned = parts[0] + '.' + ''.join(parts[1:])

    # Remove stray hyphens not leading
    if cleaned.count('-') > 1:
        # keep only one leading hyphen if present
        cleaned = cleaned.replace('-', '')
    if '-' in cleaned and not cleaned.startswith('-'):
        cleaned = cleaned.replace('-', '')

    cleaned = cleaned.strip('.').strip()
    return cleaned

# ------------------ Cairo/Pango Health Report Generator ------------------
class CairoHealthReportGenerator:
    
    def __init__(self, font_family="Noto Sans"):
        self.font_family = font_family
        self.current_y = MARGIN + HEADER_HEIGHT
        self.page_num = 1
        self.ctx = None # cairo.Context
        self.surface = None # cairo.PDFSurface

    # --- Utility: Pango Text Rendering ---
    def draw_pango_text(self, text, x, y, size=10, weight='Normal', color_rgb=(0, 0, 0), align='LEFT', max_width=A4_WIDTH):
        
        self.ctx.set_source_rgb(*color_rgb)
        
        # Create Pango layout
        layout = PangoCairo.create_layout(self.ctx)
        
        # Set font description
        font_desc_str = f'{self.font_family} {weight} {size}'
        layout.set_font_description(Pango.FontDescription(font_desc_str))
        
        # Handle simple bold tagging for keys (e.g., <b>Test:</b>)
        try:
            if isinstance(text, str) and ('<' in text and '>' in text):
                # assume markup safe — Pango will raise if markup invalid
                layout.set_markup(text, -1)
            else:
                layout.set_text(str(text), -1)
        except Exception:
            # fallback to plain text if markup fails
            layout.set_text(re.sub(r'<[^>]+>', '', str(text)), -1)
        
        # Set width for wrapping
        layout.set_width(int((max_width - x) * Pango.SCALE)) 
        layout.set_wrap(Pango.WrapMode.WORD)

        if align == 'CENTER':
            layout.set_alignment(Pango.Alignment.CENTER)
        elif align == 'RIGHT':
            layout.set_alignment(Pango.Alignment.RIGHT)
        else:
            layout.set_alignment(Pango.Alignment.LEFT)

        # Render the text
        self.ctx.move_to(x, y)
        PangoCairo.show_layout(self.ctx, layout)
        
        # Return the height used by the text
        extents = layout.get_extents()
        if extents[1].height > 0:
            height = extents[1].height / Pango.SCALE
            return height
        return LINE_HEIGHT
    
    # --- Utility: Color Map ---
    def get_status_color(self, status_text):
        RED = (1, 0, 0)
        BLUE = (0, 0, 1)
        GREEN = (0, 0.5, 0)
        
        try:
            status_upper = status_text.upper()
        except Exception:
            status_upper = ""
        if status_upper in ["HIGH", "HOGH"]:
            return RED
        elif status_upper in ["LOW"]:
            return BLUE
        else:
            return GREEN

    # --- Header/Footer/Page Management ---
    def start_new_page(self):
        if self.page_num > 1:
            self.surface.show_page()
        
        self.page_num += 1
        # Set Y position for content below the header
        self.current_y = MARGIN + HEADER_HEIGHT 
        self.draw_header_footer()
        
    def draw_header_footer(self):
        
        BLUE = (0.1, 0.1, 0.5)
        GREY = (0.5, 0.5, 0.5)
        
        # --- Header ---
        self.ctx.set_source_rgb(*BLUE)
        self.ctx.set_line_width(0.5)
        
        # Top line
        self.ctx.move_to(MARGIN, HEADER_HEIGHT - 10)
        self.ctx.line_to(A4_WIDTH - MARGIN, HEADER_HEIGHT - 10)
        self.ctx.stroke()
        
        # Title text (fixed English title on header for simplicity)
        self.draw_pango_text("Health Report Summary", MARGIN, 15, 9, 'Bold', BLUE)

        # --- Footer ---
        self.ctx.set_source_rgb(*GREY)
        
        # Date/Page
        date_str = f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        self.draw_pango_text(date_str, MARGIN, A4_HEIGHT - 20, 8, color_rgb=GREY)
        self.draw_pango_text(f"Page {self.page_num}", A4_WIDTH - MARGIN, A4_HEIGHT - 20, 8, color_rgb=GREY, align='RIGHT')


    # --- Parse reference range (robust) ---
    def parse_reference_range(self, reference_range):
        """
        Accepts strings like '11.5 - 15.5' (also Unicode digits/dashes).
        Returns {'normal_min': float, 'normal_max': float} or None.
        """
        if not reference_range:
            return None

        ref = str(reference_range).strip()
        # normalize dash variants to ASCII hyphen
        ref = ref.replace('\u2013', '-').replace('\u2014', '-').replace('\u2212', '-').replace('\u2010', '-')
        # flexible regex capturing groups with possible localized digits/commas/dots
        match = re.search(r'([0-9\-\.,\u2009\u202f\u0966-\u096F\u09E6-\u09EF\u0BE6-\u0BEF\u0C66-\u0C6F\u0CE6-\u0CEF\u0AE6-\u0AEF\u0B66-\u0B6F\u0D66-\u0D6F\u0660-\u0669]+)\s*[-–—]\s*([0-9\-\.,\u2009\u202f\u0966-\u096F\u09E6-\u09EF\u0BE6-\u0BEF\u0C66-\u0C6F\u0CE6-\u0CEF\u0AE6-\u0AEF\u0B66-\u0B6F\u0D66-\u0D6F\u0660-\u0669]+)', ref)
        if match:
            a_raw, b_raw = match.group(1), match.group(2)
            a_norm = normalize_number_str(a_raw)
            b_norm = normalize_number_str(b_raw)
            try:
                a_val = float(a_norm) if a_norm != "" else None
                b_val = float(b_norm) if b_norm != "" else None
                if a_val is not None and b_val is not None:
                    normal_min, normal_max = min(a_val, b_val), max(a_val, b_val)
                    return {'normal_min': float(normal_min), 'normal_max': float(normal_max)}
            except Exception:
                return None
        return None

    # --- Bar chart (robust) ---
    def draw_bar_chart(self, x_start, y_start, result_value, test_data):
        
        bar_width, bar_height = 220, 12
        
        try:
            # Normalize result value (handles localized numerals & stray chars)
            val_str_raw = str(result_value) if result_value is not None else ""
            val_str = normalize_number_str(val_str_raw)
            if not val_str:
                # Draw placeholder "N/A" bar
                self.ctx.set_source_rgb(0.95, 0.95, 0.95)
                self.ctx.rectangle(x_start, y_start, bar_width, bar_height)
                self.ctx.fill_preserve()
                self.ctx.set_source_rgb(0.7, 0.7, 0.7)
                self.ctx.set_line_width(0.25)
                self.ctx.stroke()
                self.draw_pango_text("N/A", x_start + 4, y_start + bar_height + 4, 7, color_rgb=(0.5, 0.5, 0.5))
                return bar_height + 20
            
            numeric_value = float(val_str)
            ranges = None
            if isinstance(test_data.get('ranges'), dict):
                ranges = test_data.get('ranges')
            else:
                ranges = self.parse_reference_range(test_data.get('reference_range', ''))
            
            # If no ranges, draw placeholder bar but still show marker
            if not ranges:
                self.ctx.set_line_width(0.25)
                self.ctx.rectangle(x_start, y_start, bar_width, bar_height)
                self.ctx.set_source_rgb(0.95, 0.95, 0.95)
                self.ctx.fill_preserve()
                self.ctx.set_source_rgb(0.7, 0.7, 0.7)
                self.ctx.stroke()

                chart_max = max(numeric_value * 1.2, numeric_value + 1.0)
                value_pos_x = x_start + (min(numeric_value, chart_max) / chart_max) * bar_width
                self.ctx.set_source_rgb(1.0, 0.0, 0.0)
                self.ctx.set_line_width(1.2)
                self.ctx.move_to(value_pos_x, y_start - 3)
                self.ctx.line_to(value_pos_x, y_start + bar_height + 3)
                self.ctx.stroke()
                self.draw_pango_text(f"{result_value}", value_pos_x - 10, y_start + bar_height + 5, 7, color_rgb=(1, 0, 0))
                return bar_height + 25

            normal_min, normal_max = ranges['normal_min'], ranges['normal_max']
            if normal_max <= normal_min:
                normal_max = normal_min + max(1.0, abs(normal_min) * 0.1)

            chart_max = max(normal_max * 1.3, numeric_value * 1.2, normal_min + 1.0)
            
            # Colors
            PINK = (1.0, 0.8, 0.8)
            LIGHTGREEN = (0.7, 1.0, 0.7)
            LIGHTYELLOW = (1.0, 1.0, 0.7)
            RED = (1.0, 0.0, 0.0)

            # Calculate widths (with clamping)
            low_width = max(0.0, (normal_min / chart_max) * bar_width)
            normal_width = max(0.0, ((normal_max - normal_min) / chart_max) * bar_width)
            low_width = min(low_width, bar_width)
            normal_width = min(normal_width, bar_width - low_width)
            high_width = max(0.0, bar_width - (low_width + normal_width))

            # Draw Bar Background
            x = x_start
            self.ctx.set_line_width(0.25)
            
            # Low
            if low_width > 0.001:
                self.ctx.rectangle(x, y_start, low_width, bar_height)
                self.ctx.set_source_rgb(*PINK)
                self.ctx.fill_preserve()
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.stroke()
                x += low_width
                
            # Normal
            if normal_width > 0.001:
                self.ctx.rectangle(x, y_start, normal_width, bar_height)
                self.ctx.set_source_rgb(*LIGHTGREEN)
                self.ctx.fill_preserve()
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.stroke()
                x += normal_width

            # High (rest of the bar)
            if high_width > 0.001:
                self.ctx.rectangle(x, y_start, high_width, bar_height)
                self.ctx.set_source_rgb(*LIGHTYELLOW)
                self.ctx.fill_preserve()
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.stroke()
            
            # Draw Value Marker (Red Line)
            value_pos_x = x_start + (min(max(numeric_value, 0.0), chart_max) / chart_max) * bar_width
            self.ctx.set_source_rgb(*RED)
            self.ctx.set_line_width(1.5)
            self.ctx.move_to(value_pos_x, y_start - 3)
            self.ctx.line_to(value_pos_x, y_start + bar_height + 3)
            self.ctx.stroke()
            
            # Draw Value Text (avoid clipping off right edge)
            text_x = value_pos_x - 10
            if text_x + 40 > A4_WIDTH - MARGIN:
                text_x = A4_WIDTH - MARGIN - 40
            self.draw_pango_text(f"{result_value}", text_x, y_start + bar_height + 5, 7, color_rgb=RED)

            return bar_height + 25 # Height used by the chart
            
        except Exception:
            self.draw_pango_text("N/A", x_start, y_start, 10, color_rgb=(0.5, 0.5, 0.5))
            return 15

    # --- Test section (Manual Table Drawing) ---
    def draw_test_section(self, test_data, labels):
        
        CELL_MARGIN = 5
        KEY_WIDTH = 80
        VALUE_WIDTH = A4_WIDTH - 2 * MARGIN - KEY_WIDTH - 2 * CELL_MARGIN
        
        # Row data: (Key label, Value content, Status related, Chart required)
        rows = [
            (labels.get('Test','Test'), test_data['name'], False, False),
            (labels.get('Result','Result'), f"{test_data['value']} {test_data.get('unit','')}".strip(), True, False),
            (labels.get('Status','Status'), test_data.get('status',''), True, False),
            (labels.get('Reference','Reference'), test_data.get('reference_range','N/A'), False, False),
            (labels.get('Chart','Chart'), test_data['value'], False, True)
        ]
        
        if 'meaning' in test_data and test_data['meaning']:
            rows.append((labels.get('Meaning','Meaning'), test_data['meaning'], False, False))
        if 'tips' in test_data and test_data['tips']:
            rows.append((labels.get('Tips','Tips'), test_data['tips'], False, False))

        # --- 1. Calculate Table Height ---
        total_height = 0
        row_heights = []
        
        for key, value, is_status, is_chart in rows:
            if is_chart:
                height = 35 + 2 * CELL_MARGIN
            else:
                # Use a temporary layout to measure wrapping height
                temp_layout = PangoCairo.create_layout(self.ctx)
                # Now decide whether to set markup or plain text based on the VALUE content
                try:
                    if isinstance(value, str) and ('<' in value and '>' in value):
                        temp_layout.set_markup(value, -1)
                    else:
                        temp_layout.set_text(str(value), -1)
                except Exception:
                    # fallback plain text if markup fails
                    temp_layout.set_text(re.sub(r'<[^>]+>', '', str(value)), -1)

                temp_layout.set_font_description(Pango.FontDescription(f'{self.font_family} Normal 10'))
                temp_layout.set_width(int(VALUE_WIDTH * Pango.SCALE))
                temp_layout.set_wrap(Pango.WrapMode.WORD)
                
                pango_height = temp_layout.get_extents()[1].height / Pango.SCALE
                height = max(LINE_HEIGHT, pango_height) + 2 * CELL_MARGIN
            
            row_heights.append(height)
            total_height += height

        # --- 2. Check Page Break ---
        if self.current_y + total_height + 15 > A4_HEIGHT - FOOTER_HEIGHT - MARGIN:
            self.start_new_page()
            
        # --- 3. Draw Table Structure ---
        table_x = MARGIN
        table_y = self.current_y
        current_y_pos = table_y
        
        # Outer box
        self.ctx.set_line_width(0.6)
        self.ctx.set_source_rgb(0.5, 0.5, 0.5) 
        self.ctx.rectangle(table_x, table_y, A4_WIDTH - 2 * MARGIN, total_height)
        self.ctx.stroke()
        
        # Inner grid setup
        self.ctx.set_line_width(0.25)
        self.ctx.set_source_rgb(0.8, 0.8, 0.8)

        # --- 4. Draw Rows and Content ---
        for i, ((key, value, is_status, is_chart), row_h) in enumerate(zip(rows, row_heights)):
            
            # Draw Row Separator (Inner Grid)
            self.ctx.move_to(table_x, current_y_pos + row_h)
            self.ctx.line_to(A4_WIDTH - MARGIN, current_y_pos + row_h)
            self.ctx.stroke()
            
            # Draw Key-Value Separator (Inner Grid)
            self.ctx.move_to(table_x + KEY_WIDTH, current_y_pos)
            self.ctx.line_to(table_x + KEY_WIDTH, current_y_pos + row_h)
            self.ctx.stroke()
            
            # Key column background for the first row (Header)
            if i == 0:
                self.ctx.rectangle(table_x, current_y_pos, KEY_WIDTH, row_h)
                self.ctx.set_source_rgb(0.95, 0.95, 0.95)
                self.ctx.fill()
                self.ctx.set_source_rgb(0.8, 0.8, 0.8) 
                self.ctx.rectangle(table_x, current_y_pos, KEY_WIDTH, row_h)
                self.ctx.stroke()

            # 1. Draw Key Text (Bold using Pango markup)
            self.draw_pango_text(f"<b>{key}:</b>", 
                                 table_x + CELL_MARGIN, current_y_pos + CELL_MARGIN, 10, 'Bold')
            
            # 2. Draw Value Content
            value_x = table_x + KEY_WIDTH + CELL_MARGIN
            value_y = current_y_pos + CELL_MARGIN
            
            if is_chart:
                self.draw_bar_chart(value_x, value_y, value, test_data)
            elif is_status:
                color_rgb = self.get_status_color(value)
                self.draw_pango_text(value, value_x, value_y, 10, 'Bold', color_rgb=color_rgb, max_width=A4_WIDTH - MARGIN)
            else:
                self.draw_pango_text(value, value_x, value_y, 10, max_width=A4_WIDTH - MARGIN)
                
            current_y_pos += row_h

        self.current_y = current_y_pos + 15 # Spacer after table


    # --- Generate PDF from data ---
    def generate_pdf_from_data(self, report_data, output_pdf_path, lang_name="English", labels=None):
        if labels is None:
            labels = {label: label for label in COMMON_LABELS}
            
        try:
            # 1. Setup Cairo Surface and Context
            self.surface = cairo.PDFSurface(output_pdf_path, A4_WIDTH, A4_HEIGHT)
            self.ctx = cairo.Context(self.surface)
            
            self.page_num = 1
            
            # --- Dedicated First Page for Titles (Page 1) ---
            
            # Set Y position for titles (centered vertically)
            self.current_y = A4_HEIGHT
            
            # 1a. Draw Titles
            report_title = labels.get("Health Report Summary")
            sub_title = labels.get("Confidential Medical Document")
            self.start_new_page()
            
            self.draw_pango_text(report_title, A4_WIDTH-600, self.current_y, 22, 'Bold', (0.1, 0.14, 0.5), 'CENTER', max_width=A4_WIDTH)
            self.current_y += 40
            self.draw_pango_text(sub_title, A4_WIDTH-600, self.current_y, 16, 'Normal', (0.5, 0.5, 0.5), 'CENTER', max_width=A4_WIDTH)
            self.current_y += 30
            
            # 1b. Language and Generated Info (at bottom of first page)
            lang_label = labels.get('Language','Language')
            generated_label = labels.get('Generated on','Generated on')
            
            # Place this info near the bottom, before the footer area
            info_y = A4_HEIGHT - 100
            self.draw_pango_text(f"<b>{lang_label}:</b> {lang_name}", MARGIN, info_y, 10, 'Normal', max_width=A4_WIDTH)
            info_y += 15
            self.draw_pango_text(f"<b>{generated_label}:</b> {datetime.now().strftime('%B %d, %Y')}", MARGIN, info_y, 10, 'Normal', max_width=A4_WIDTH)
            
            # Draw the header/footer (Page 1)
            self.draw_header_footer()
            
            # --- Start Second Page for Content (Page 2 onwards) ---
            self.start_new_page() # Increments page_num to 2 and draws header/footer
            
            # 3. Draw Test Sections
            for test in report_data.get('tests', []):
                self.draw_test_section(test, labels)
            
            # 4. End of Report
            end_label = labels.get("End of Report", "End of Report")
            self.draw_pango_text(end_label, A4_WIDTH / 2, self.current_y + 10, 8, 'Normal', (0.5, 0.5, 0.5), 'CENTER', max_width=A4_WIDTH)
            
            # 5. Finalize PDF
            self.surface.finish()
            return True
            
        except Exception as e:
            print(f"❌ Error generating PDF: {str(e)}")
            return False

COMMON_LABELS = [
    "Health Report Summary", "Confidential Medical Document", "Language",
    "Generated on", "End of Report", "Test", "Result", "Status", 
    "Reference", "Meaning", "Tips", "Chart"
]

def get_translated_labels(lang_code):
    """Translates high-level report components."""
    translated = {}
    for label in COMMON_LABELS:
        #translated[label] = translate_text(label, lang_code)
        translated[label] = label
    return translated

# ------------------ Multi-language PDF Runner ------------------
def generate_multilang_reports(json_file, output_folder):
    languages = {
        "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
        "ml": "Malayalam", "gu": "Gujarati", "kn": "Kannada",
        "pa": "Punjabi", "or": "Odia", "as": "Assamese"
    }

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
    except Exception:
        print(f"❌ Error: Could not load or parse '{json_file}'.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for lang_code, lang_name in languages.items():
        # 1. Get Language-Specific Font Family Name
        font_family = register_font_for_lang(lang_code)

        # 2. Get Translated Labels (titles)
        labels = get_translated_labels(lang_code)

        # 3. Translate test data content
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
        
        # 4. Generate PDF using Cairo/Pango
        generator = CairoHealthReportGenerator(font_family=font_family)
        success = generator.generate_pdf_from_data(translated_data, output_pdf, lang_name, labels)
        
        if success:
            print(f"✅ Generated {lang_name} report: {output_pdf} using font: {font_family}")
        else:
            print(f"❌ Failed to generate {lang_name} report")

# ------------------ Main ------------------
def main():
    json_file = "health_report_data.json"
    output_folder = "reports_multilang_new"
    
    if not all([cairo, Pango, PangoCairo]):
        print("\nExiting. Cairo/Pango (GObject Introspection) libraries are missing or could not be loaded.")
        return

    os.makedirs(output_folder, exist_ok=True)

    # English PDF first
    print("\n--- Generating English Report ---")
    en_font_family = register_font_for_lang("en")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        generator_en = CairoHealthReportGenerator(font_family=en_font_family)
        success_en = generator_en.generate_pdf_from_data(report_data, f"{output_folder}/health_report_en.pdf", "English")
        if success_en:
            print(f"✅ Generated English report: {output_folder}/health_report_en.pdf using font: {en_font_family}")
    except Exception as e:
        print(f"Exiting main: Could not load or process '{json_file}'. Error: {e}")
        return

    # Generate multi-language reports
    print("\n--- Generating Multi-Language Reports ---")
    generate_multilang_reports(json_file, output_folder)

if __name__ == "__main__":
    main()
