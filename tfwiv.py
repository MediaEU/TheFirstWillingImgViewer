
# GNU GENERAL PUBLIC LICENSE
# Version 2, June 1991

import os
from tkinter import (
    Tk, Label, Button, Entry, Scale, HORIZONTAL,
    filedialog, Canvas, Toplevel, Frame, LabelFrame, Scrollbar
)
from tkinter import ttk
import tkinter.font as tkFont
from tooltip import ToolTip
from PIL import Image, ImageTk, ImageOps


class TheFirstWillingImgViewer:
    def __init__(self, root):
        self.root = root
        self.root["background"] = "gray15"
        self.root.title("Image Explorer")
        self.root.grid_columnconfigure((0), weight=1)
        # self.root.grid_columnconfigure((1), weight=0)
        self.root.grid_rowconfigure((0), weight=1)
        self.root.grid_rowconfigure((1), weight=0)
        

        self.custom_font = tkFont.Font(family="Arial", size=10, weight=tkFont.BOLD)
        self.custom_font2 = tkFont.Font(family="Arial", size=16, weight=tkFont.BOLD)
        self.custom_font_bold = tkFont.Font(size=10, weight=tkFont.BOLD)
        self.style_button = {
            "font": self.custom_font_bold,
            "relief": "flat",
            "bg": "gray20",
            "fg": "SlateGray1",
            "activebackground": "darkgreen",
            "activeforeground": "white"}

        self.zoom_job = None
        self.image_paths = []
        self.current_index = 0
        self.original_image = None
        self.display_image = None
        self.zoom = 1.0
        self.image_id = None
        self.drag_data = {"x": 0, "y": 0}
        self.rotation = 0
        self.clockwise_bool = False
        # Track widgets to hide/show
        self.widgets_to_toggle = []
        self.containers()
        self.setup_ui()
        self.setup_bindings()


    def containers(self):
        self.bottom = Frame(self.root)
        self.bottom.grid(row=1, column=0, columnspan=2)
        self.widgets_to_toggle.append(self.bottom)

    def setup_ui(self):      
        self.frame_canvvas = Frame(self.root, bg="gray15")
        self.frame_canvvas.grid(row=0, column=0, columnspan=3, sticky="wesn")
        self.frame_canvvas.grid_columnconfigure(0, weight=1)
        self.frame_canvvas.grid_rowconfigure((0), weight=1)
        
        # Canvas
        self.canvas = Canvas(self.frame_canvvas, #width=800, 
                             bg="black", 
                             highlightbackground="black", 
                             highlightthickness=2)
        self.canvas.grid(row=0, column=0, sticky="wesn")

        # Control frame
        self.control_frame = Frame(self.bottom, background="gray15")
        self.control_frame.grid(column=0, row=0, sticky="wesn")
        self.widgets_to_toggle.append(self.control_frame)

        main_frame_controls = Frame(self.control_frame, background="gray15")
        main_frame_controls.grid(row=0, column=0, sticky="we", padx=10)
        # Buttons and other controls
        self.zoom_label = Label(main_frame_controls, 
                                text="Zoom: 100%", 
                                width=10,
                                bg="gray15",
                                fg="cyan",
                                font=self.custom_font)
        self.zoom_label.grid(row=0, column=0, padx=6)

        open_dir = Button(main_frame_controls, 
                          text="Open Folder", 
                          command=self.open_folder,
                          **self.style_button)
        self.add_hover_effect(open_dir)

        ToolTip(open_dir, "Open directory")
        open_dir.grid(row=0, column=1, padx=6)
        preview = Button(main_frame_controls, 
                         text="Preview All", 
                         command=self.open_preview_window,
                         **self.style_button)
        self.add_hover_effect(preview)
        preview.grid(row=0, column=2)
        previous = Button(main_frame_controls, 
                          text="Previous", 
                          command=self.prev_image,
                          **self.style_button)
        self.add_hover_effect(previous)
        previous.grid(row=0, column=3, padx=6)
        next_img = Button(main_frame_controls, 
                          text="Next", 
                          command=self.next_image,
                          **self.style_button)
        self.add_hover_effect(next_img)
        next_img.grid(row=0, column=4)
        

        #Zoom Frame
        main_frame_zoom = Frame(self.control_frame, background="gray15")
        main_frame_zoom.grid(row=0, column=1, sticky="wesn")
        labelframe = LabelFrame(main_frame_zoom, 
                                text=" Zoom ", 
                                background="gray15", 
                                foreground="cyan")
        labelframe.grid(row=0, column=0, ipady=4)

        frame_zoom = Frame(labelframe, background="gray15")
        frame_zoom.grid(row=0, column=0)
        zoom_in = Button(frame_zoom, 
                         text="Zoom In", 
                         command=lambda: self.scale_image(1.2),
                         **self.style_button)
        self.add_hover_effect(zoom_in, hover_bg="green", hover_fg="white")
        ToolTip(zoom_in, "Zoom In")
        zoom_in.grid(row=0, column=0, padx=6)
        zoom_out = Button(frame_zoom, 
                          text="Zoom Out", 
                          command=lambda: self.scale_image(0.8),
                          **self.style_button)
        self.add_hover_effect(zoom_out, hover_bg="green", hover_fg="white")
        ToolTip(zoom_out, "Zoom Out")
        zoom_out.grid(row=0, column=1)
        fitscreen = Button(frame_zoom, 
                           text="Fit to Screen", 
                           command=self.fit_to_screen,
                           **self.style_button)
        self.add_hover_effect(fitscreen, hover_bg="green", hover_fg="white")
        ToolTip(fitscreen, "Fit to Screen")
        fitscreen.grid(row=0, column=2, padx=6)
        reset_zoom = Button(frame_zoom, 
                            text="Reset Zoom", 
                            command=self.reset_zoom,
                            **self.style_button)
        self.add_hover_effect(reset_zoom, hover_bg="green", hover_fg="white")
        ToolTip(reset_zoom, "Reset Zoom")
        reset_zoom.grid(row=0, column=3)
        self.zoom_entry = Entry(frame_zoom, 
                                width=6,
                                highlightbackground="crimson", 
                                relief="groove",
                                font=self.custom_font_bold,
                                background="gray20",
                                fg="SlateGray1")
        self.zoom_entry.insert(0, "100")
        self.zoom_entry.grid(row=0, column=4, padx=(12,0))
        set_zoom = Button(frame_zoom, 
                          text="Set", 
                          width=3,
                          command=self.set_custom_zoom, 
                          relief="flat",
                          font=self.custom_font_bold,
                          fg="springgreen",
                          bg="gray15")
        self.add_hover_effect(set_zoom, hover_bg="orange", hover_fg="white", normal_bg="gray15", normal_fg="springgreen")
        ToolTip(set_zoom, "Set explicit zoom %")                  
        set_zoom.grid(row=0, column=5)
        

        #Align Frame
        main_frame_align = Frame(self.control_frame, background="gray15")
        main_frame_align.grid(row=0, column=2, sticky="wesn", padx=10)
        labelframe_align = LabelFrame(main_frame_align, 
                                      text=" Align ",
                                      background="gray15", 
                                      foreground="cyan")
        labelframe_align.grid(row=0, column=0, ipady=4, ipadx=4)
        frame_align = Frame(labelframe_align, 
                            background="gray15")
        frame_align.pack()
        align_left = Button(frame_align, 
                            text="🠈", 
                            command=self.align_left, 
                            font=self.custom_font,
                            foreground="yellow", 
                            background="gray20",
                            width=3,
                            relief="flat")
        align_left.grid(row=0, column=0)
        self.add_hover_effect(align_left, hover_bg="orange", hover_fg="white", normal_bg="gray15", normal_fg="yellow")
        ToolTip(align_left, "Left side")
        align_center = Button(frame_align, 
                              text="⬌", 
                              command=self.center_image,
                              font=self.custom_font,
                              foreground="yellow", 
                              background="gray20",
                              width=3,
                              relief="flat")
        align_center.grid(row=0, column=1)
        self.add_hover_effect(align_center, hover_bg="orange", hover_fg="white", normal_bg="gray15", normal_fg="yellow")
        ToolTip(align_center, "Center")
        align_right = Button(frame_align, 
                             text="🠊", 
                             command=self.align_right,
                             font=self.custom_font,
                             foreground="yellow", 
                             background="gray20",
                             width=3,
                             relief="flat")
        align_right.grid(row=0, column=2)
        self.add_hover_effect(align_right, hover_bg="orange", hover_fg="white", normal_bg="gray15", normal_fg="yellow")
        ToolTip(align_right, "Right side")


        # Zoom slider
        main_frame_slider = Frame(self.control_frame, bg="gray15", width=200)
        main_frame_slider.grid(row=0, column=3, sticky="wesn", padx=10)
        self.zoom_slider = Scale(main_frame_slider, 
                                 from_=10, 
                                 to=300, 
                                 orient=HORIZONTAL,
                                 label="Zoom %", 
                                 command=self.slider_zoom,
                                 bg="gray15",
                                 fg="SlateGray1",
                                 troughcolor="gray20",
                                 borderwidth=0,
                                 border=0,
                                 highlightthickness=0)
        self.zoom_slider.set(100)
        self.zoom_slider.grid(sticky="wesn")

        # Rotation widget
        self.rotate_slider = Scale(main_frame_slider, 
                                   from_=0, to=360, 
                                   orient=HORIZONTAL,
                                   label="Rotate°", 
                                   command=self.set_rotation,
                                   bg="gray15",
                                   fg="SlateGray1",
                                   relief="flat",
                                   troughcolor="gray20",
                                   borderwidth=0,
                                   border=0,
                                   highlightthickness=0)
        self.rotate_slider.set(0)
        self.rotate_slider.grid(row=0, column=1, sticky="wesn", padx=4)

        self.bt_clockwise = Button(main_frame_slider, command=self.clockwise,
                                   text="Clk",
                                   bg="gray20",
                                   fg="SlateGray1",
                                   relief="flat")
        self.bt_clockwise.grid(row=0, column=2)
        ToolTip(self.bt_clockwise, "Rotate clockwise")


        # Hide Frame
        self.hide_frame = Frame(self.root, bg="gray15")
        self.hide_frame.grid(row=1, column=2, sticky="e")
        self.widgets_to_toggle.append(self.hide_frame)
        # Hide button on far right of control_frame
        hide = Button(self.hide_frame, 
               text="↧", 
               command=self.hide_widgets, 
               relief="flat",
               bg="gray20",
               fg="crimson",
               font=self.custom_font2)
        hide.grid(row=0, column=0, sticky="e")
        ToolTip(hide, "Hide Bar")

    def setup_bindings(self):
        self.canvas.bind("<MouseWheel>", self.mouse_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)

    def clockwise(self):
        self.clockwise_bool = not self.clockwise_bool
        color = self.bt_clockwise.cget('bg')
        print(color)
        if self.bt_clockwise.cget('bg') == 'gray20':
            self.bt_clockwise.configure(background="red")
        else:
            self.bt_clockwise.configure(background="gray20")


    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_paths = sorted([
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
            ])
            self.current_index = 0
            self.load_image()

    def load_image(self):
        if not self.image_paths:
            return

        path = self.image_paths[self.current_index]
        self.original_image = Image.open(path)
        self.zoom = 1.0
        self.rotation = 0
        self.zoom_slider.set(100)
        self.rotate_slider.set(0)
        self.display_scaled_image()
        self.update_zoom_label()

    def display_scaled_image(self):
        if not self.original_image:
            return

        # Apply rotation
        img = self.original_image.rotate(self.rotation, expand=True)
        # Resize
        size = (int(img.width * self.zoom), int(img.height * self.zoom))
        img = img.resize(size, Image.Resampling.LANCZOS)

        self.display_image = ImageTk.PhotoImage(img)

        # Preserve position
        if self.image_id is None:
            self.image_id = self.canvas.create_image(400, 300, image=self.display_image, anchor="center")
        else:
            coords = self.canvas.coords(self.image_id)
            self.canvas.delete(self.image_id)
            self.image_id = self.canvas.create_image(*coords, image=self.display_image, anchor="center")

    def next_image(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.load_image()

    def prev_image(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.load_image()

    def scale_image(self, factor):
        self.zoom *= factor
        self.zoom = max(0.1, min(self.zoom, 10.0))
        self.zoom_slider.set(int(self.zoom * 100))
        self.display_scaled_image()
        self.update_zoom_label()

    def mouse_zoom(self, event):
        step = 0.05
        factor = 1 + step if event.delta > 0 else 1 - step
        self.scale_image(factor)

    def slider_zoom(self, value):
        self.zoom = int(value) / 100.0
        self.display_scaled_image()
        self.update_zoom_label()

    def set_custom_zoom(self):
        try:
            value = float(self.zoom_entry.get())
            self.zoom = value / 100
            self.zoom = max(0.1, min(self.zoom, 10.0))
            self.zoom_slider.set(int(self.zoom * 100))
            self.display_scaled_image()
            self.update_zoom_label()
        except ValueError:
            self.zoom_entry.delete(0, "end")
            self.zoom_entry.insert(0, str(int(self.zoom * 100)))

    def reset_zoom(self):
        self.zoom = 1.0
        self.zoom_slider.set(100)
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, "100")
        self.display_scaled_image()
        self.update_zoom_label()

    def set_rotation(self, value):
        try:
            angle = float(value)
        except ValueError:
            return
        if self.clockwise_bool:
            angle = -angle
        self.rotation = angle
        self.display_scaled_image()

    def update_zoom_label(self):
        percent = int(self.zoom * 100)
        self.zoom_label.config(text=f"Zoom: {percent}%")

    def fit_to_screen(self):
        if not self.original_image:
            return

        # Compute the fit zoom factor
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        img_w, img_h = self.original_image.size
        self.zoom = min(canvas_w / img_w, canvas_h / img_h)

        self.zoom_slider.set(int(self.zoom * 100))
        # Redraw at the current coords (so existing panning stays until we recenter)
        self.display_scaled_image()
        self.update_zoom_label()

        # Now recenter this one time
        center_x = canvas_w // 2
        center_y = canvas_h // 2
        self.canvas.coords(self.image_id, center_x, center_y)


    def on_drag_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_move(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.image_id, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def open_preview_window(self):
        if not self.image_paths:
            return

        preview = Toplevel(self.root)
        preview.title("Image Preview Grid")

        # Create canvas and scrollbar
        canvas = Canvas(preview)
        scrollbar = Scrollbar(preview, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the canvas
        frame = Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", self.on_frame_configure)
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        row = col = 0
        max_col = 5
        thumb_size = (120, 120)

        for idx, path in enumerate(self.image_paths):
            thumb = self.create_thumbnail(path, thumb_size)
            lbl = Label(frame, image=thumb, cursor="hand2")
            lbl.image = thumb
            lbl.grid(row=row, column=col, padx=5, pady=5)
            lbl.bind("<Button-1>", lambda e, i=idx: self.load_from_preview(i))

            col += 1
            if col >= max_col:
                col = 0
                row += 1
        self.canvas_preview = canvas

    # Configure scrolling region
    def on_frame_configure(self, event):
        self.canvas_preview.configure(scrollregion=self.canvas_preview.bbox("all"))
    
    # Optional: enable scrolling with the mouse wheel
    def _on_mousewheel(self, event):
        self.canvas_preview.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_thumbnail(self, path, size):
        img = Image.open(path)
        img.thumbnail(size)
        return ImageTk.PhotoImage(img)

    def load_from_preview(self, index):
        self.current_index = index
        self.load_image()

    def center_image(self):
        """Move the current image to the exact center of the canvas."""
        if self.image_id is None:
            return
        # Get canvas dimensions
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # Compute center
        cx, cy = w // 2, h // 2
        # Reposition image
        self.canvas.coords(self.image_id, cx, cy)

    def hide_widgets(self):
        # Remove all toggle widgets from view
        for w in self.widgets_to_toggle:
            # w.pack_forget()
            w.grid_remove()

        # Hide/Show bar
        self.show_button = Button(self.root, text="↥", 
                                  command=self.show_widgets, 
                                  background="grey5", 
                                  foreground="cyan", 
                                  relief="flat",
                                  font=self.custom_font)
        # use place so it sits in the bottom-right corner
        self.show_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def show_widgets(self):
        # Remove the Show button
        self.show_button.destroy()

        #No need to grid it manually if you use grid_forget before you can just grid() it again
        for w in self.widgets_to_toggle:
            w.grid()  # Re-show them in their previous grid position

    def align_left(self):
        """Align image to the left edge of the canvas, vertically centered."""
        if self.image_id is None:
            return
        # get current canvas height
        ch = self.canvas.winfo_height()
        # compute y to center vertically
        y = ch // 2
        # compute half of displayed image width
        iw = self.display_image.width() // 2
        # set x so left edge of image sits at 0
        self.canvas.coords(self.image_id, iw, y)

    def align_right(self):
        """Align image to the right edge of the canvas, vertically centered."""
        if self.image_id is None:
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        y = ch // 2
        iw = self.display_image.width() // 2
        # set x so right edge of image sits at canvas width
        self.canvas.coords(self.image_id, cw - iw, y)

    def add_hover_effect(self, widget, 
                        hover_bg='OrangeRed3', hover_fg='white', 
                        # normal_bg='SystemButtonFace', normal_fg='black'):
                        normal_bg='gray20', normal_fg='SlateGray1'):
        def on_enter(event):
            event.widget.config(bg=hover_bg, fg=hover_fg)

        def on_leave(event):
            event.widget.config(bg=normal_bg, fg=normal_fg)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)


if __name__ == "__main__":
    root = Tk()
    root.geometry("1400x800")
    app = ImageExplorer(root)
    root.mainloop()
