# zzTakeoff Logo as base64 encoded PNG
# This allows the logo to be embedded in the application without external files

import base64
from io import BytesIO
from PIL import Image
import tkinter as tk

# Base64 encoded logo data (will be populated with actual image)
LOGO_DATA = ""

def get_logo_image(width=None, height=None):
    """
    Get the zzTakeoff logo as a PhotoImage
    Args:
        width: Target width (maintains aspect ratio if only width given)
        height: Target height (maintains aspect ratio if only height given)
    """
    if not LOGO_DATA:
        return None

    try:
        # Decode base64 to image
        image_data = base64.b64decode(LOGO_DATA)
        image = Image.open(BytesIO(image_data))

        # Resize if dimensions specified
        if width or height:
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height

            if width and not height:
                height = int(width / aspect_ratio)
            elif height and not width:
                width = int(height * aspect_ratio)

            image = image.resize((width, height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage for Tkinter
        from PIL import ImageTk
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading logo: {e}")
        return None
