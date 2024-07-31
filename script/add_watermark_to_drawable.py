from PIL import Image, ImageDraw, ImageFont
import os
from collections import Counter

# Path to the directory containing images
root_dir = '../src/main/res/drawable-hdpi'

# Function to calculate font size based on image size
def calculate_font_size(image, desired_width_fraction=0.1):
    image_width, image_height = image.size
    return max(1, int(desired_width_fraction * min(image_width, image_height)))  # For example, 10% of image width

def find_least_used_palette_color(image):
    if image.mode != 'P':
        # If the image is not in palette mode, return a default color
        return "black"

    palette = image.getpalette()  # Get the palette
    color_counts = Counter(image.getdata())  # Count color usage
    color_counts = {k: v for k, v in color_counts.items() if k < len(palette) // 3}  # Filter out invalid colors
    least_used_color = min(color_counts, key=color_counts.get)  # Find least used color
    return least_used_color

for filename in os.listdir(root_dir):
    if filename.endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
        img_path = os.path.join(root_dir, filename)
        with Image.open(img_path) as img:
            least_used_color = find_least_used_palette_color(img)
            draw = ImageDraw.Draw(img)

            font = ImageFont.load_default(calculate_font_size(img))

            position = (10, 10)
            draw.text(position, "Test", font=font, fill=least_used_color)
            img.save(img_path)
