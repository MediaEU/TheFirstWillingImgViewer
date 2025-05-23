
# GNU GENERAL PUBLIC LICENSE
# Version 2, June 1991


import tkinter as tk


class ToolTip:
    def __init__(self, widget, text, 
                 x_offset=10, y_offset=5, margin=2):
        """
        widget     — the widget to attach to
        text       — tooltip text
        x_offset   — horizontal distance from widget (px)
        y_offset   — vertical distance from widget (px)
        margin     — minimum gap from window edges (px)
        """
        self.widget   = widget
        self.text     = text
        self.x_off    = x_offset
        self.y_off    = y_offset
        self.margin   = margin
        self.tw       = None

        widget.bind("<Enter>", self.show, add='+')
        widget.bind("<Leave>", self.hide, add='+')

    def show(self, event=None):
        if self.tw or not self.text:
            return

        # parent window geometry
        win = self.widget.winfo_toplevel()
        win_x = win.winfo_rootx()
        win_y = win.winfo_rooty()
        win_w = win.winfo_width()
        win_h = win.winfo_height()

        # widget absolute position
        wx = self.widget.winfo_rootx()
        wy = self.widget.winfo_rooty()
        wh = self.widget.winfo_height()

        # create tooltip window
        self.tw = tw = tk.Toplevel(win)
        tw.wm_overrideredirect(True)
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1, font=("tahoma", 10))
        label.pack(ipadx=4, ipady=2)
        tw.update_idletasks()

        tw_w = tw.winfo_width()
        tw_h = tw.winfo_height()

        # default: below widget
        x = wx + self.x_off
        y = wy + wh + self.y_off

        # if it would go past bottom of window, flip above
        if y + tw_h + self.margin > win_y + win_h:
            y = wy - tw_h - self.y_off

        # if it would go past right edge, shift left
        if x + tw_w + self.margin > win_x + win_w:
            x = (win_x + win_w) - tw_w - self.margin

        # if it would go past left edge, clamp to left margin
        if x < win_x + self.margin:
            x = win_x + self.margin

        tw.wm_geometry(f"+{x}+{y}")

    def hide(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None