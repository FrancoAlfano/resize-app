from tkinter import Tk, Label, Button, filedialog, messagebox, Scrollbar, Frame, Canvas, ttk
from client import send_image_to_server
from config import STANDARD_SIZES
from filter import apply_filter
from PIL import Image, ImageTk
import tkinter as tk
import os
import io


def update_ui(image_data, image_path):
    if not image_data:
        print(f"Failed to process {image_path}")
        return

    max_display_size = (500, 500)

    img_frame = Frame(scrollable_frame)
    img_frame.pack(fill='x', expand=True, padx=5, pady=5)

    image = Image.open(io.BytesIO(image_data))

    if filter_var.get() != 'None':
        image = apply_filter(image, filter_var.get().lower(), transparency_slider.get())

    if image.size[0] > max_display_size[0] or image.size[1] > max_display_size[1]:
        image.thumbnail(max_display_size, Image.LANCZOS)

    photo = ImageTk.PhotoImage(image)

    label = Label(img_frame, image=photo)
    label.image = photo
    label.pack(side="left", padx=5, pady=5)

    title_label = Label(img_frame, text=os.path.basename(image_path))
    title_label.pack(side="top")

    download_button = Button(img_frame, text="Download", command=lambda: download_image(image_data, image_path, filter_var.get().lower()))
    download_button.pack(side="bottom")

    canvas.configure(scrollregion=canvas.bbox("all"))


def process_images():
    if not selected_image_paths:
        messagebox.showerror("Error", "No images selected")
        return

    selected_size_str = get_selected_size()
    if selected_size_str.startswith("exact:"):
        response = messagebox.askyesnocancel("Exact Size Selected",
                                        "An exact size is selected, "+
                                        "the aspect ratio may not be maintained. Continue?")
        if response is not True:
            return

    for image_path in selected_image_paths:
        send_image_to_server(image_path, update_ui, get_selected_size)


def select_images():
    clear_images()
    global selected_image_paths

    file_paths = filedialog.askopenfilenames()
    try:
        if file_paths:
            selected_image_paths = file_paths

            for widget in preview_frame.winfo_children():
                widget.destroy()

            preview_canvas = Canvas(preview_frame, bg='#f0f0f0', height=200)
            preview_scrollbar = Scrollbar(preview_frame,orient="horizontal", command=preview_canvas.xview)
            preview_canvas.configure(xscrollcommand=preview_scrollbar.set)

            scrollable_preview_frame = Frame(preview_canvas, bg='#f0f0f0')
            preview_canvas.create_window((0, 0), window=scrollable_preview_frame, anchor="nw")

            scrollable_preview_frame.bind("<Configure>", lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all")))
            preview_scrollbar.pack(side="bottom", fill="x")
            preview_canvas.pack(side="top", fill="both", expand=True)

            for image_path in file_paths:
                image = Image.open(image_path)
                aspect_ratio = min(100 / image.width, 100 / image.height)
                new_width = int(image.width * aspect_ratio)
                new_height = int(image.height * aspect_ratio)
                thumbnail = image.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(thumbnail)

                frame = Frame(scrollable_preview_frame)
                frame.pack(side="left", padx=10, pady=10)

                label = Label(frame, image=photo)
                label.image = photo
                label.pack()

                title = os.path.basename(image_path)
                title_label = Label(frame, text=title, bg='#f0f0f0')
                title_label.pack()
    except Exception as e:
        selected_image_paths = []
        messagebox.showerror("Error", f"Invalid format {e}")


def download_image(image_data, image_path, filter_name=None):
    original_name, original_extension = os.path.splitext(os.path.basename(image_path))
    image = Image.open(io.BytesIO(image_data))
    new_size = f"{image.width}x{image.height}"

    filter_suffix = f"_{filter_name}" if filter_name and filter_name != 'none' else ""
    new_file_name = f"{original_name}{filter_suffix}_{new_size}{original_extension}"

    filetypes = [("Image files", f"*{original_extension}"), ("All files", "*.*")]

    save_path = filedialog.asksaveasfilename(
        initialfile=new_file_name,
        defaultextension=original_extension,
        filetypes=filetypes
    )
    if save_path:
        with open(save_path, "wb") as f:
            f.write(image_data)


def get_selected_size():
    exact_width = exact_width_entry.get()
    exact_height = exact_height_entry.get()
    custom_width = custom_width_entry.get()
    custom_height = custom_height_entry.get()

    if exact_width and exact_height:
        width = int(exact_width)
        height = int(exact_height)
        selected_size = f"exact:{width}x{height}"
        return selected_size
    elif custom_width and custom_height:
        width = int(custom_width)
        height = int(custom_height)
        selected_size = f"{width}x{height}"
        return selected_size
    else:
        selected_label = selected_option.get()
        for label, size in STANDARD_SIZES:
            if label == selected_label:
                return size
    return None


def clear_images():
    global selected_image_paths
    selected_image_paths = []
    for widget in preview_frame.winfo_children():
        widget.destroy()
    for widget in scrollable_frame.winfo_children():
        widget.destroy()


def apply_style():
    style = ttk.Style()
    style.theme_use('clam')

    style.configure('TButton', font=('Helvetica', 12, 'bold'), borderwidth=1, background='#005792', foreground='white')
    style.map('TButton',
              background=[('active', '#0073a8'), ('disabled', '#a3a3a3')],
              foreground=[('active', 'white'), ('disabled', '#dedede')],
              relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

    style.configure('TLabel', font=('Helvetica', 12, 'bold'), background='#f0f0f0', foreground='#333333')

    style.configure('TEntry', font=('Helvetica', 12, 'bold'), borderwidth=1, relief="solid")

    style.configure('TFrame', background='#f0f0f0')

    style.configure('Vertical.TScrollbar', gripcount=0, background='#005792', troughcolor='#f0f0f0', bordercolor='#005792', arrowcolor='white')
    style.configure('Horizontal.TScrollbar', gripcount=0, background='#005792', troughcolor='#f0f0f0', bordercolor='#005792', arrowcolor='white')

    root.option_add("*Font", "Helvetica 12")

root = Tk()
root.title("Resize-app")
root.geometry("1199x870")

apply_style()

selected_image_paths = []

canvas = Canvas(root, bg='#f0f0f0')
scrollbar = Scrollbar(root, command=canvas.yview)
scrollable_frame = Frame(canvas, bg='#f0f0f0')

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

preview_frame = Frame(root, bg='#f0f0f0')
preview_frame.pack(fill="x", pady=(10, 20))

button_frame = ttk.Frame(root, padding="10", style='TFrame')
button_frame.pack(fill='x', expand=False)

button_select = ttk.Button(button_frame, text="Select Images", command=select_images)
button_select.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

button_process = ttk.Button(button_frame, text="Process Images", command=process_images)
button_process.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

button_clear = ttk.Button(button_frame, text="Clear Images", command=clear_images)
button_clear.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

size_frame = Frame(root, bg='#f0f0f0')
size_frame.pack(pady=(0, 20))

size_menu_label = ttk.Label(size_frame, text="Select Size:")
size_menu_label.pack(side="left", padx=(0, 10))

selected_option = tk.StringVar()
selected_option.set("Instagram (320x320)")
size_menu = ttk.OptionMenu(size_frame, selected_option, "Instagram (320x320)", *[label for label, _ in STANDARD_SIZES])
size_menu.pack(side="left")

exact_size_frame = tk.Frame(root)
exact_size_frame.pack(fill=tk.X, padx=10, pady=5)

exact_size_label = tk.Label(exact_size_frame, text="Exact Size:")
exact_size_label.pack(side=tk.LEFT)

exact_width_label = tk.Label(exact_size_frame, text="Width:")
exact_width_label.pack(side=tk.LEFT)

exact_width_entry = tk.Entry(exact_size_frame, width=5)
exact_width_entry.pack(side=tk.LEFT, padx=(0, 10))

exact_height_label = tk.Label(exact_size_frame, text="Height:")
exact_height_label.pack(side=tk.LEFT)

exact_height_entry = tk.Entry(exact_size_frame, width=5)
exact_height_entry.pack(side=tk.LEFT)

custom_size_frame = tk.Frame(root)
custom_size_frame.pack(fill=tk.X, padx=10, pady=5)

custom_size_label = tk.Label(custom_size_frame, text="Custom Size:")
custom_size_label.pack(side=tk.LEFT)

custom_width_label = tk.Label(custom_size_frame, text="Width:")
custom_width_label.pack(side=tk.LEFT)

custom_width_entry = tk.Entry(custom_size_frame, width=5)
custom_width_entry.pack(side=tk.LEFT, padx=(0, 10))

custom_height_label = tk.Label(custom_size_frame, text="Height:")
custom_height_label.pack(side=tk.LEFT)

custom_height_entry = tk.Entry(custom_size_frame, width=5)
custom_height_entry.pack(side=tk.LEFT)

filter_frame = tk.Frame(root)
filter_frame.pack(fill=tk.X, padx=10, pady=5)

filter_label = tk.Label(filter_frame, text="Select Filter:")
filter_label.pack(side=tk.LEFT)

filter_var = tk.StringVar()
filter_var.set("None")
filter_options = ['None', 'Red', 'Green', 'Blue', 'Black and White']
filter_menu = tk.OptionMenu(filter_frame, filter_var, *filter_options)
filter_menu.pack(side=tk.LEFT, padx=10)

transparency_label = tk.Label(filter_frame, text="Transparency:")
transparency_label.pack(side=tk.LEFT, padx=10)

transparency_slider = tk.Scale(filter_frame, from_=1, to=10, resolution=1, orient=tk.HORIZONTAL)
transparency_slider.set(10)

transparency_slider.pack(side=tk.LEFT)

info_frame = tk.Frame(root, bg='#f0f0f0')
info_frame.pack(fill=tk.X, padx=10, pady=20)

info_text = ('\n----------------------------------------INFOMATION----------------------------------------\n\n'
             'The Exact Size will transform the image to those exact dimensions, '
             'regardless of the aspect ratio.\n\n\n'
             'The Custom Size will transform the image to the closest possible dimensions '
             'while keeping the aspect ratio intact.\n\n\n'
             'The Color Filter allows you to select a color filter to apply a specific hue.\n\n\n'
             'Transparency Slider allows you to adjust the intensity of the color,\n'
             'from 1 (least visible) to 10 (most visible).')

wrap_length = 500

info_label = tk.Label(info_frame, text=info_text, font=('Helvetica', 12), wraplength=wrap_length, justify='left', bg='#f0f0f0')
info_label.pack(side=tk.LEFT, fill=tk.X)



root.mainloop()
