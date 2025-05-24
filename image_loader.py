

import os
from PIL import Image, ImageTk

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

def load_image(filename, subfolder=None, size=None):
    """
    Load an image from assets folder, optionally from a subfolder.
    
    :param filename: str - The image filename (e.g., 'zoom_in.png')
    :param subfolder: str or None - Subfolder inside assets (e.g., 'icons')
    :return: PhotoImage object for Tkinter
    """
    if subfolder:
        path = os.path.join(ASSETS_DIR, subfolder, filename)
    else:
        path = os.path.join(ASSETS_DIR, filename)
    img = Image.open(path)
    
    try:
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {filename} from {subfolder or 'root assets'}: {e}")
        return None
    