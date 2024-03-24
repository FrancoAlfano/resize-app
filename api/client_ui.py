from tkinter import Tk, Label, Button, filedialog, messagebox, Scrollbar, Frame, Canvas, ttk
import tkinter as tk
from PIL import Image, ImageTk
import threading
import socket
import io
import os

def send_image_to_server(image_path, callback):
    def thread_target():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', 8080))
            selected_size_str = get_selected_size() + '\n'
            sock.sendall(selected_size_str.encode())
            with open(image_path, 'rb') as f:
                bytes_read = f.read(10024)
                while bytes_read:
                    sock.sendall(bytes_read)
                    bytes_read = f.read(10024)

            sock.shutdown(socket.SHUT_WR)

            received_data = b''
            while True:
                part = sock.recv(10024)
                if not part:
                    break
                received_data += part

            root.after(0, callback, received_data, image_path)

    threading.Thread(target=thread_target).start()

def update_ui(image_data, image_path):
    if not image_data:
        print(f"Failed to process {image_path}")
        return

    image = Image.open(io.BytesIO(image_data))
    photo = ImageTk.PhotoImage(image)

    frame = Frame(scrollable_frame)
    frame.pack()

    label = Label(frame, image=photo)
    label.image = photo
    label.pack(side="left")

    title = os.path.basename(image_path)
    Label(frame, text=title).pack(side="left")

    download_button = Button(frame, text="Download", command=lambda: download_image(image_data, image_path))
    download_button.pack(side="right")

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
        send_image_to_server(image_path, update_ui)


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


def download_image(image_data, image_path):
    original_name, original_extension = os.path.splitext(os.path.basename(image_path))
    image = Image.open(io.BytesIO(image_data))
    new_size = f"{image.width}x{image.height}"

    new_file_name = f"{original_name}_{new_size}{original_extension}"

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
        for label, size in standard_sizes:
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

standard_sizes = [
    ("Instagram (320x320)", "320x320"),
    ("Facebook Desktop (170x170)", "170x170"),
    ("LinkedIn/Twitter (400x400)", "400x400"),
    ("Pinterest (165x165)", "165x165"),
    ("Twitter Post (1024x512)", "1024x512"),
    ("Facebook Post (1200x630)", "1200x630"),
    ("Instagram Story (1080x1920)", "1080x1920"),
    ("YouTube Thumbnail (1280x720)", "1280x720"),
    ("LinkedIn Post Square (1200x1200)", "1200x1200"),
    ("LinkedIn Post Portrait (1080x1350)", "1080x1350"),
    ("Web Banner (468x60)", "468x60"),
    ("Web Leaderboard (728x90)", "728x90"),
    ("Medium Rectangle (300x250)", "300x250"),
    ("Large Rectangle (336x280)", "336x280"),
    ("Skyscraper (120x600)", "120x600"),
    ("Smartphone (1170x2532)", "1170x2532"),
    ("Tablet (1620x2160)", "1620x2160"),
    ("Desktop Wallpaper HD (1920x1080)", "1920x1080"),
    ("Desktop Wallpaper 4K (3840x2160)", "3840x2160"),
    ("Business Card (1050x600)", "1050x600"),
    ("Postcard (1800x1200)", "1800x1200"),
    ("Flyer (2550x3300)", "2550x3300"),
    ("Poster (7200x10800)", "7200x10800"),
    ("Photography Small (640x480)", "640x480"),
    ("Photography Medium (800x600)", "800x600"),
    ("Photography Large (1024x768)", "1024x768"),
    ("Full-Size (2048x1536)", "2048x1536")
]

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
root.geometry("1000x800")

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
size_menu = ttk.OptionMenu(size_frame, selected_option, "Instagram (320x320)", *[label for label, _ in standard_sizes])
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

info_frame = tk.Frame(root, bg='#f0f0f0')
info_frame.pack(fill=tk.X, padx=10, pady=20)

info_text = ('\n----------------------------------------INFOMATION----------------------------------------\n\n'
             'The exact size will transform the image to those exact dimensions, '
             'regardless of the aspect ratio.\n\n\n'
             'The custom size will transform the image to the closest possible dimensions '
             'while keeping the aspect ratio intact.')

wrap_length = 500

info_label = tk.Label(info_frame, text=info_text, font=('Helvetica', 12), wraplength=wrap_length, justify='left', bg='#f0f0f0')
info_label.pack(side=tk.LEFT, fill=tk.X)



root.mainloop()
