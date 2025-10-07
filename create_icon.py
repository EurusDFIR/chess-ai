#!/usr/bin/env python3
"""
Create a simple chess icon for the application
Requires: pip install pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_icon():
    """Create a simple chess piece icon"""
    # Create image (256x256 for high quality icon)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circle background
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(41, 98, 157),  # Blue
                 outline=(255, 255, 255), 
                 width=8)
    
    # Draw simplified chess piece (knight)
    # Simple geometric approximation
    piece_color = (255, 255, 255)
    
    # Knight head (simplified)
    points = [
        (size//2 - 30, size//2 + 40),  # Base left
        (size//2 - 30, size//2 - 20),  # Neck left
        (size//2 - 10, size//2 - 60),  # Head top left
        (size//2 + 20, size//2 - 50),  # Ear
        (size//2 + 25, size//2 - 30),  # Head top right
        (size//2 + 30, size//2),       # Nose
        (size//2 + 30, size//2 + 40),  # Base right
    ]
    
    draw.polygon(points, fill=piece_color, outline=(200, 200, 200), width=3)
    
    # Add eye
    draw.ellipse([size//2 + 5, size//2 - 35, size//2 + 15, size//2 - 25], 
                 fill=(41, 98, 157))
    
    # Save as ICO
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_path = 'src/gui/assets/icon.ico'
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    
    # Save ICO with multiple sizes
    img.save(icon_path, format='ICO', sizes=icon_sizes)
    print(f"✅ Icon created: {icon_path}")
    
    # Also save as PNG for reference
    img.save('src/gui/assets/icon.png', format='PNG')
    print(f"✅ PNG created: src/gui/assets/icon.png")
    
    return icon_path

if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("📦 Installing Pillow...")
        import subprocess
        subprocess.run(['pip', 'install', 'pillow'])
        from PIL import Image, ImageDraw
    
    create_simple_icon()
    print("\n🎨 Icon ready for PyInstaller!")
