import os
import json
import requests
import re
import unicodedata
from datetime import datetime
from math import pi
from io import BytesIO
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from deep_translator import GoogleTranslator

# A4 dimensions in pixels/points (WeasyPrint uses CSS for layout)
A4_WIDTH = 595
A4_HEIGHT = 842
MARGIN = 40
LINE_HEIGHT = 12

# ------------------ Font Handling ------------------
# WeasyPrint requires the fonts to be accessible via CSS @font-face rules.
# We'll use the same download logic and provide the path in CSS.
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
    "en": ("NotoSans-Regular.ttf", "Noto Sans"),
    # For Urdu, WeasyPrint/Pango handles the complex shaping (Nastaliq) well
    "ur": ("NotoNastaliqUrdu-Regular.ttf", "Noto Nastaliq Urdu")
}

def register_font_for_lang(lang_code="en"):
    """
    Downloads the font if missing. Returns the CSS font-family name.
    (WeasyPrint will find the TTF file via CSS @font-face rules later).
    """
    ttf_file, font_family = FONT_MAP.get(lang_code, FONT_MAP["en"])
    
    if not os.path.exists(ttf_file):
        folder_map = {
            "hi": "NotoSansDevanagari", "bn": "NotoSansBengali", "ta": "NotoSansTamil", 
            "te": "NotoSansTelugu", "ml": "NotoSansMalayalam", "gu": "NotoSansGujarati",
            "kn": "NotoSansKannada", "pa": "NotoSansGurmukhi", "or": "NotoSansOdia",
            "as": "NotoSansBengali", "en": "NotoSans", "ur" : "NotoNastaliqUrdu"
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

# ------------------ Translation Helper (Same) ------------------
def translate_text(text, target_lang):
    if not text:
        return ""
    try:
        # NOTE: Re-enabling translation
        trans_text = GoogleTranslator(source="en", target=target_lang).translate(text)
        return trans_text
    except Exception:
        return text

# ------------------ Helpers for numeric normalization (Same) ------------------
def normalize_number_str(s: str):
    """
    Convert Unicode digits (e.g. Devanagari, Bengali) to ASCII digits,
    remove common thousands separators, normalize dash/minus, and keep only digits, '.' and '-'.
    """
    # ... (Logic is identical to previous version, kept for completeness) ...
    if s is None:
        return ""
    s = str(s).strip()

    normalized_chars = []
    for ch in s:
        try:
            d = unicodedata.digit(ch)
            normalized_chars.append(str(d))
            continue
        except (TypeError, ValueError):
            pass

        if ch in "−–—\u2012\u2013\u2014\u2212":
            normalized_chars.append('-')
            continue

        if ch.isascii() and (ch.isdigit() or ch in ".-"):
            normalized_chars.append(ch)
            continue

        if ch in [",", "\u2009", "\u202f"]:
            continue
        pass

    cleaned = "".join(normalized_chars)

    if cleaned.count('.') > 1:
        parts = cleaned.split('.')
        cleaned = parts[0] + '.' + ''.join(parts[1:])

    if cleaned.count('-') > 1:
        cleaned = cleaned.replace('-', '')
    if '-' in cleaned and not cleaned.startswith('-'):
        cleaned = cleaned.replace('-', '')

    cleaned = cleaned.strip('.').strip()
    return cleaned

# ------------------ HTML/CSS Generation Logic ------------------

COMMON_LABELS = [
    "Health Report Summary", "Confidential Medical Document", "Language",
    "Generated on", "End of Report", "Test", "Result", "Status", 
    "Reference", "Meaning", "Tips", "Chart"
]

def get_translated_labels(lang_code):
    """Translates high-level report components."""
    translated = {}
    for label in COMMON_LABELS:
        translated[label] = translate_text(label, lang_code)
    return translated

def parse_reference_range(reference_range):
    """
    Accepts strings like '11.5 - 15.5' (also Unicode digits/dashes).
    Returns {'normal_min': float, 'normal_max': float} or None.
    (Logic is identical to previous version, kept for completeness)
    """
    if not reference_range:
        return None

    ref = str(reference_range).strip()
    ref = ref.replace('\u2013', '-').replace('\u2014', '-').replace('\u2212', '-').replace('\u2010', '-')
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

def generate_bar_chart_html(test_data, result_value, lang_code):
    """Generates an HTML/SVG snippet for the bar chart."""
    BAR_WIDTH = 220
    BAR_HEIGHT = 12
    
    val_str = normalize_number_str(str(result_value) if result_value is not None else "")
    
    if not val_str:
        return f'<div class="chart-container"><div class="bar-na"></div><span class="label-na">N/A</span></div>'
        
    try:
        numeric_value = float(val_str)
        ranges = parse_reference_range(test_data.get('reference_range', ''))
        
        if not ranges:
            # Placeholder bar with marker
            chart_max = max(numeric_value * 1.2, numeric_value + 1.0)
            value_pct = min(numeric_value, chart_max) / chart_max
            
            # Marker position in px
            marker_pos_x = value_pct * BAR_WIDTH
            
            html = f'''
            <div class="chart-container" style="width: {BAR_WIDTH}px; height: {BAR_HEIGHT+20}px;">
                <div class="bar-na" style="width: {BAR_WIDTH}px; height: {BAR_HEIGHT}px;"></div>
                <div class="marker" style="left: {marker_pos_x}px; height: {BAR_HEIGHT+6}px;"></div>
                <span class="value-label" style="left: {marker_pos_x}px;">{result_value}</span>
            </div>
            '''
            return html

        normal_min, normal_max = ranges['normal_min'], ranges['normal_max']
        if normal_max <= normal_min:
            normal_max = normal_min + max(1.0, abs(normal_min) * 0.1)

        chart_max = max(normal_max * 1.3, numeric_value * 1.2, normal_min + 1.0)
        
        # Calculate widths in percentages
        low_pct = max(0.0, (normal_min / chart_max) * 100)
        normal_pct = max(0.0, ((normal_max - normal_min) / chart_max) * 100)
        
        # Clamp to 100%
        low_pct = min(low_pct, 100)
        normal_pct = min(normal_pct, 100 - low_pct)
        high_pct = max(0.0, 100 - (low_pct + normal_pct))
        
        # Value marker position
        value_pct = min(max(numeric_value, 0.0), chart_max) / chart_max
        marker_pos_x = value_pct * BAR_WIDTH # Position in pixels

        # RTL support: For Urdu, the bar needs to draw right-to-left
        is_rtl = (lang_code == 'ur')

        # Since we use float percentages for width, standard LTR stacking works for layout, 
        # but for RTL scripts, we rely on the parent direction to align the text/marker.
        
        # Generate the segmented bar
        bar_segments = []
        if low_pct > 0.001:
            bar_segments.append(f'<div class="bar-segment low" style="width: {low_pct}%;"></div>')
        if normal_pct > 0.001:
            bar_segments.append(f'<div class="bar-segment normal" style="width: {normal_pct}%;"></div>')
        if high_pct > 0.001:
            # We use flex-grow for the high segment to ensure it fills the remaining space
            bar_segments.append(f'<div class="bar-segment high" style="flex-grow: 1;"></div>')
        
        # Note on RTL: For bar charts, LTR visualization of quantity (low to high) is standard
        # even for RTL text. We only need to adjust the text direction/alignment.
        
        html = f'''
        <div class="chart-container" style="width: {BAR_WIDTH}px; height: {BAR_HEIGHT+20}px;">
            <div class="bar-background" style="width: 100%; height: {BAR_HEIGHT}px; direction: ltr;">
                {''.join(bar_segments)}
            </div>
            <div class="marker" style="left: {marker_pos_x}px; height: {BAR_HEIGHT+6}px;"></div>
            <span class="value-label" style="left: {marker_pos_x}px;">{result_value}</span>
        </div>
        '''
        return html

    except Exception:
        return f'<div class="chart-container"><span style="color: #808080;">Chart Data N/A</span></div>'


def get_css(lang_code, font_family):
    """Generates the CSS style sheet dynamically."""
    
    # Check if font file exists to use in @font-face
    ttf_file = FONT_MAP.get(lang_code, FONT_MAP["en"])[0]
    
    # Determine text direction for the main body
    direction = 'rtl' if lang_code == 'ur' else 'ltr'
    text_align = 'right' if lang_code == 'ur' else 'left'
    
    css = f'''
    /* --- FONT DEFINITIONS --- */
    @font-face {{
        font-family: "{font_family}";
        src: url('{ttf_file}');
        font-weight: normal;
        font-style: normal;
    }}
    @font-face {{
        font-family: "{font_family}";
        src: url('{ttf_file}');
        font-weight: bold;
        font-style: normal;
    }}

    /* --- GLOBAL STYLES --- */
    @page {{
        size: A4;
        margin: {MARGIN}px;
        /* Define named flows for header/footer */
        @top {{
            content: element(header);
        }}
        @bottom {{
            content: element(footer);
        }}
    }}
    
    body {{
        font-family: "{font_family}", sans-serif;
        font-size: 10pt;
        line-height: 1.5;
        direction: {direction}; /* Main body direction */
    }}

    /* --- HEADER/FOOTER --- */
    #page-header {{
        position: running(header);
        border-bottom: 0.5px solid #808080;
        padding-bottom: 8px;
        margin-top: 15px;
    }}
    #page-header h1 {{
        color: #191970;
        font-size: 9pt;
        font-weight: bold;
        margin: 0;
    }}

    #page-footer {{
        position: running(footer);
        font-size: 8pt;
        color: #808080;
    }}
    #page-footer .date {{ float: {text_align}; }}
    #page-footer .page-num {{ float: {'left' if lang_code == 'ur' else 'right'}; }}
    
    /* --- TITLE PAGE --- */
    .title-page {{
        page-break-after: always;
        height: {A4_HEIGHT - 2 * MARGIN}px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }}
    .title-page h1 {{
        font-size: 22pt;
        font-weight: bold;
        color: #191970;
    }}
    .title-page h2 {{
        font-size: 16pt;
        color: #808080;
        margin-bottom: 80px;
    }}
    .info-box {{
        align-self: flex-start;
        margin-top: auto; /* Pushes to bottom */
        font-size: 10pt;
        text-align: {text_align};
    }}
    .info-box b {{ font-weight: bold; }}

    /* --- TEST TABLE STYLES --- */
    .test-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
        border: 0.6px solid #808080;
    }}
    .test-table td {{
        padding: 5px;
        border: 0.25px solid #808080;
        vertical-align: middle;
        text-align: {text_align};
    }}
    .test-key-col {{
        width: 80px;
        font-weight: bold;
        background-color: #f8f8f8;
        text-align: {text_align};
    }}
    .test-table tr:first-child .test-key-col {{ background-color: #eeeeee; }}
    
    /* --- STATUS COLORS --- */
    .status-High {{ color: #FF0000; font-weight: bold; }}
    .status-Low {{ color: #0000FF; font-weight: bold; }}
    .status-Normal, .status-NA {{ color: #008000; font-weight: bold; }}
    
    /* --- BAR CHART STYLES (Flexbox for layout) --- */
    .chart-container {{
        position: relative;
        height: 35px; /* Height for bar + labels */
        margin: 5px 0 15px 0;
        direction: ltr; /* Chart bar visualization is LTR */
    }}
    .bar-background {{
        display: flex;
        flex-direction: row;
        border: 0.25px solid black;
        box-sizing: border-box;
        overflow: hidden;
    }}
    .bar-na {{
        background-color: #f2f2f2;
        border: 0.25px solid #808080;
        box-sizing: border-box;
        width: 220px;
        height: 12px;
    }}
    .bar-segment {{
        height: 100%;
    }}
    .low {{ background-color: #FFC0CB; }} /* Pink */
    .normal {{ background-color: #90EE90; }} /* LightGreen */
    .high {{ background-color: #FFFF99; }} /* LightYellow */

    .marker {{
        position: absolute;
        width: 1.5px;
        top: -3px;
        background-color: #FF0000;
        /* Adjust marker position based on its own width (center) */
        transform: translateX(-50%); 
    }}
    .value-label {{
        position: absolute;
        top: 15px;
        font-size: 7pt;
        color: #FF0000;
        white-space: nowrap;
        transform: translateX(-50%); /* Center text under the marker */
    }}
    .label-na {{
        position: absolute;
        top: 15px;
        font-size: 7pt;
        color: #808080;
        left: 4px;
    }}
    
    '''
    return css

def generate_report_html(translated_data, lang_code, lang_name, labels, font_family):
    """Generates the full HTML content."""
    
    now = datetime.now().strftime('%B %d, %Y')
    
    # --- 1. Header/Footer Template ---
    header_html = f'''
    <div id="page-header">
        <h1>{labels.get("Health Report Summary", "Health Report Summary")}</h1>
    </div>
    '''
    
    footer_html = f'''
    <div id="page-footer">
        <span class="date">{labels.get('Generated on','Generated on')}: {now}</span>
        <span class="page-num">Page <span class="paged-counter"></span></span>
    </div>
    '''

    # --- 2. Title Page ---
    title_page_html = f'''
    <div class="title-page">
        <h1>{labels.get("Health Report Summary", "Health Report Summary")}</h1>
        <h2>{labels.get("Confidential Medical Document", "Confidential Medical Document")}</h2>
        
        <div class="info-box">
            <p><b>{labels.get('Language','Language')}:</b> {lang_name}</p>
            <p><b>{labels.get('Generated on','Generated on')}:</b> {now}</p>
        </div>
    </div>
    '''
    
    # --- 3. Content Sections ---
    content_html = ""
    for test in translated_data.get('tests', []):
        
        status_class = f"status-{test.get('status','NA').title()}"
        
        # Build the table rows dynamically
        rows = [
            (labels.get('Test','Test'), f"<b>{test['name']}</b>", False),
            (labels.get('Result','Result'), f'<span class="{status_class}">{test["value"]} {test.get("unit","").strip()}</span>', False),
            (labels.get('Status','Status'), f'<span class="{status_class}">{test.get("status","N/A")}</span>', False),
            (labels.get('Reference','Reference'), test.get('reference_range','N/A'), False),
            (labels.get('Chart','Chart'), generate_bar_chart_html(test, test['value'], lang_code), True)
        ]
        
        if 'meaning' in test and test['meaning']:
            rows.append((labels.get('Meaning','Meaning'), test['meaning'], False))
        if 'tips' in test and test['tips']:
            rows.append((labels.get('Tips','Tips'), test['tips'], False))

        table_rows_html = ""
        for key, value, is_chart in rows:
            # For the chart row, we need a larger cell to hold the complex HTML
            value_html = f'<div style="text-align: left; direction: ltr;">{value}</div>' if is_chart else value
            
            table_rows_html += f'''
            <tr>
                <td class="test-key-col">{key}:</td>
                <td>{value_html}</td>
            </tr>
            '''

        content_html += f'''
        <table class="test-table">
            <tbody>
                {table_rows_html}
            </tbody>
        </table>
        '''
        
    # --- 4. End of Report ---
    content_html += f'''
    <p style="text-align: center; font-size: 8pt; color: #808080; margin-top: 20px;">
        {labels.get("End of Report", "End of Report")}
    </p>
    '''
    
    # --- 5. Full HTML Document ---
    html_doc = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{labels.get("Health Report Summary")}</title>
    </head>
    <body>
        {header_html}
        {footer_html}
        
        {title_page_html}
        
        <div id="content">
            {content_html}
        </div>
        
    </body>
    </html>
    '''
    return html_doc

# ------------------ WeasyPrint Generator ------------------
def generate_pdf_from_data_weasyprint(report_data, output_pdf_path, lang_code, lang_name, labels, font_family):
    
    # 1. Get CSS and HTML
    css_content = get_css(lang_code, font_family)
    html_content = generate_report_html(report_data, lang_code, lang_name, labels, font_family)
    
    try:
        # 2. Render PDF
        html = HTML(string=html_content)
        css = CSS(string=css_content)
        
        # WeasyPrint requires a FontConfiguration to manage font loading/caching
        font_config = FontConfiguration()
        html.write_pdf(output_pdf_path, stylesheets=[css], font_config=font_config)
        
        return True
    except Exception as e:
        print(f"❌ Error generating PDF with WeasyPrint: {str(e)}")
        # Print a snippet of the generated HTML/CSS for debugging
        # print("--- HTML Snippet ---")
        # print(html_content[:1000]) 
        # print("--- CSS Snippet ---")
        # print(css_content)
        return False

# ------------------ Multi-language PDF Runner (Modified) ------------------
def generate_multilang_reports(json_file, output_folder):
    languages = {
        "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
        "ml": "Malayalam", "gu": "Gujarati", "kn": "Kannada",
        "pa": "Punjabi", "or": "Odia", "as": "Assamese", "ur": "Urdu"
    }

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
    except Exception:
        print(f"❌ Error: Could not load or parse '{json_file}'.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for lang_code, lang_name in languages.items():
        # 1. Get Language-Specific Font Family Name and Register
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
        
        # 4. Generate PDF using WeasyPrint
        success = generate_pdf_from_data_weasyprint(translated_data, output_pdf, lang_code, lang_name, labels, font_family)
        
        if success:
            print(f"✅ Generated {lang_name} report: {output_pdf} using font: {font_family}")
        else:
            print(f"❌ Failed to generate {lang_name} report")

# ------------------ Main (WeasyPrint) ------------------
def main():
    json_file = "health_report_data.json"
    output_folder = "reports_multilang_weasyprint"
    
    if not HTML:
        print("\nExiting. WeasyPrint library (or its underlying dependencies cairo/pango/gi) is missing or could not be loaded.")
        return

    os.makedirs(output_folder, exist_ok=True)

    # Create dummy data file if it doesn't exist (same as previous setup)
    if not os.path.exists(json_file):
        print(f"Creating dummy data file: {json_file}")
        dummy_data = {
            "patient_id": "P12345",
            "tests": [
                {
                    "name": "Hemoglobin",
                    "value": "13.5",
                    "unit": "g/dL",
                    "status": "Normal",
                    "reference_range": "11.5 - 15.5",
                    "meaning": "Hemoglobin is a protein in red blood cells that carries oxygen. Normal levels indicate good oxygen-carrying capacity.",
                    "tips": "Maintain a balanced diet rich in iron and Vitamin C."
                },
                {
                    "name": "Blood Glucose (Fasting)",
                    "value": "125",
                    "unit": "mg/dL",
                    "status": "High",
                    "reference_range": "70 - 100",
                    "meaning": "Elevated fasting glucose suggests possible pre-diabetes or diabetes. High sugar levels can damage blood vessels.",
                    "tips": "Consult a physician immediately. Focus on low-glycemic foods and regular exercise."
                },
                {
                    "name": "Vitamin D",
                    "value": "20",
                    "unit": "ng/mL",
                    "status": "Low",
                    "reference_range": "30 - 100",
                    "meaning": "Low Vitamin D is associated with weak bones and a compromised immune system.",
                    "tips": "Spend more time in the sun (safely) and consider supplements as advised by your doctor."
                }
            ]
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f, indent=4)

    # English PDF first
    print("\n--- Generating English Report ---")
    en_font_family = register_font_for_lang("en")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        labels = get_translated_labels("en")
        success_en = generate_pdf_from_data_weasyprint(report_data, f"{output_folder}/health_report_en.pdf", "en", "English", labels, en_font_family)
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