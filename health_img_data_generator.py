from PIL import Image, ImageDraw, ImageFont
import textwrap

# ------------ Input Data ------------
health_data = {
    "patient_info": {
        "name": "ABC",
        "age": 10,
        "sex": "MALE",
    },
    "tests": [
        {"name": "HEMOGLOBIN", "value": "16.2 gm%", "status": "HIGH"},
        {"name": "Total RBC Count", "value": "5.35 mil/cumm", "status": "NORMAL"},
        {"name": "H.CT", "value": "44.2 %", "status": "NORMAL"},
        {"name": "M.C.V", "value": "82.62 fL", "status": "NORMAL"},
        {"name": "M.C.H.", "value": "30.3 pg", "status": "NORMAL"},
        {"name": "M.C.H.C.", "value": "36.7 %", "status": "HIGH"},
        {"name": "R.D.W", "value": "11.8 %", "status": "NORMAL"},
    ]
}

# ------------ Select silhouette based on sex/age ------------
sex = health_data["patient_info"]["sex"].lower()
age = health_data["patient_info"]["age"]

if sex.startswith("m"):
    if age <= 3:
        silhouette = "a4-health/src/assets/baby neutral.png"
    elif age <= 12:
        silhouette = "a4-health/src/assets/baby boy.png"
    elif age <= 20:
        silhouette = "a4-health/src/assets/adult boy.png"
    elif age <= 59:
        silhouette = "a4-health/src/assets/adult man.png"
    else:
        silhouette = "a4-health/src/assets/old man.png"
else:
    if age <= 3:
        silhouette = "a4-health/src/assets/baby neutral.png"
    elif age <= 12:
        silhouette = "a4-health/src/assets/baby girl.png"
    elif age <= 20:
        silhouette = "a4-health/src/assets/adult girl.png"
    elif age <= 59:
        silhouette = "a4-health/src/assets/adult woman.png"
    else:
        silhouette = "a4-health/src/assets/old woman.png"

# ------------ Setup Canvas ------------
W, H = 1000, 1400
bg_color = (244, 247, 249)  # light background
img = Image.new("RGB", (W, H), bg_color)
draw = ImageDraw.Draw(img)

# Fonts (adjust path to system fonts)
title_font = ImageFont.truetype("NotoSans-Regular.ttf", 40)
subtitle_font = ImageFont.truetype("NotoSans-Regular.ttf", 28)
normal_font = ImageFont.truetype("NotoSans-Regular.ttf", 24)
small_font = ImageFont.truetype("NotoSans-Regular.ttf", 20)

# ------------ Header ------------
draw.text((50, 40), "Personalized Summary & Vital Parameters", font=title_font, fill=(44, 62, 80))
draw.rectangle([50, 90, 950, 90], fill=(224, 247, 250))
draw.text((50, 90), "Your Health", font=subtitle_font, fill=(0, 121, 107))

# ------------ Patient Info ------------
draw.text((W//2 - 50, 120), f"{health_data['patient_info']['name']}", font=title_font, fill=(52, 73, 94))
draw.text((W//2 - 60, 170), f"Age: {age}", font=subtitle_font, fill=(127, 140, 141))

# ------------ Load Silhouette ------------
try:
    sil_img = Image.open(silhouette).convert("RGBA")
    sil_img = sil_img.resize((300, 400))
    img.paste(sil_img, (W//2 - 150, 250), sil_img)
except:
    draw.rectangle([W//2 - 150, 250, W//2 + 150, 650], outline="black", width=2)
    draw.text((W//2 - 50, 420), "No Img", font=small_font, fill=(0, 0, 0))

# ------------ Tests (split left/right) ------------
cards = health_data["tests"]
left_cards = cards[::2]
right_cards = cards[1::2]

def draw_card(x, y, test):
    # Card background
    draw.rounded_rectangle([x, y, x+350, y+100], radius=15, fill=(248, 249, 250), outline=(200, 200, 200))
    
    # Status color
    status_color = (40,167,69) if test["status"]=="NORMAL" else (220,53,69) if test["status"]=="HIGH" else (255,193,7)
    
    # Icon placeholder
    draw.ellipse([x+15, y+30, x+55, y+70], fill=(180,180,180))
    
    # Text
    draw.text((x+70, y+20), test["name"], font=small_font, fill=(85,85,85))
    draw.text((x+70, y+45), test["value"], font=normal_font, fill=(34,34,34))
    draw.text((x+70, y+70), test["status"], font=small_font, fill=status_color)

y_start = 700
gap = 120
for i, t in enumerate(left_cards):
    draw_card(50, y_start + i*gap, t)

for i, t in enumerate(right_cards):
    draw_card(W-400, y_start + i*gap, t)

# ------------ Footer ------------
draw.text((W//2 - 220, H-80), "All lab results are subject to clinical interpretation.", font=small_font, fill=(150,150,150))
draw.text((W//2 - 100, H-50), "Consult a physician.", font=small_font, fill=(150,150,150))

# ------------ Save Output ------------
img.save("health_report.png")
print("✅ Saved as health_report.png")
