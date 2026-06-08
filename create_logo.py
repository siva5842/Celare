from PIL import Image, ImageDraw, ImageFont

# Create a dark background image
img = Image.new('RGB', (200, 80), color='#0E1117')
draw = ImageDraw.Draw(img)

# Try to use a system font; if not available, use default
try:
    font = ImageFont.truetype("arial.ttf", 32)
except:
    font = ImageFont.load_default()

# Draw text
text = "Celare"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (img.width - text_width) / 2
y = (img.height - text_height) / 2 - bbox[1]

# Draw with a green accent color
draw.text((x, y), text, font=font, fill='#00FF88')

# Save the logo
img.save('logo.png')
print("logo.png created!")
