
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper

# ==== SETTINGS ====
input_txt = r"C:\Users\Usuario\Documents\random\emofile.txt"
output_pdf = "hebrew_wrapped_fixed.pdf"
font_path = "arial.ttf"
font_name = "HebrewFont"
font_size = 14

# Page settings
page_width, page_height = 595.27, 841.89  # A4 in points
right_margin = 40
left_margin = 40
top_margin = 40
line_spacing = 18

# Register Hebrew font
pdfmetrics.registerFont(TTFont(font_name, font_path))

# Read text
with open(input_txt, "r", encoding="utf-8") as f:
    text = f.read()

# Prepare text for RTL display
reshaped = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped)

# Split into words
words = bidi_text.split(" ")

# Start PDF
c = canvas.Canvas(output_pdf, pagesize=(page_width, page_height))
c.setFont(font_name, font_size)

x_start = page_width - right_margin
y = page_height - top_margin

line_words = []
line_width = 0
max_width = page_width - left_margin - right_margin

for word in words:
    w_width = pdfmetrics.stringWidth(word + " ", font_name, font_size)
    if line_width + w_width > max_width:
        # Draw the current line (right-aligned)
        line_text = " ".join(line_words)
        c.drawRightString(x_start, y, line_text)
        y -= line_spacing
        line_words = [word]
        line_width = w_width
    else:
        line_words.append(word)
        line_width += w_width

# Draw the last line
if line_words:
    c.drawRightString(x_start, y, " ".join(line_words))

c.save()
print(f"✅ Fixed Hebrew wrapping PDF saved as: {output_pdf}")
