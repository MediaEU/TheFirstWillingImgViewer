Goal: To create a simple image viewer that is focused on simplicity, unlike Windows 10's default bullshit viewer.

Image format supported:
    "*.jpg *.jpeg *.png *.bmp *.gif *.avif"

Dependencies:
    Tkinter
    PIL
    pillow_avif  # AVIF plugin

To use it with Windows file browser:
    Right-click an image file → Open with → Choose another app → More apps → Look for another app on this PC.
    Select the .bat file below.

Create .bat script and store it where you want.

    @echo off
    python "path_to_tfwiv\TheFirstWillingImgViewer\tfwiv.py" %1
