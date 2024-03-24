from tkinter import Tk, Label, Button, filedialog, messagebox, Scrollbar, Frame, Canvas
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
    if selected_size_str.startswith("custom:"):
        response = messagebox.askyesnocancel("Custom Size Selected",
                                        "A custom size is selected, "+
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

            for image_path in file_paths:
                image = Image.open(image_path)
                aspect_ratio = min(100 / image.width, 100 / image.height)
                new_width = int(image.width * aspect_ratio)
                new_height = int(image.height * aspect_ratio)
                thumbnail = image.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(thumbnail)

                frame = Frame(preview_frame)
                frame.pack(side="left", padx=10, pady=10)

                label = Label(frame, image=photo)
                label.image = photo
                label.pack()

                title = os.path.basename(image_path)
                title_label = Label(frame, text=title)
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
    width = width_entry.get()
    height = height_entry.get()

    if width and height:
        width = int(width)
        height = int(height)

        selected_size = f"custom:{width}x{height}"
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

root = Tk()
root.title("Resize-app")
root.geometry("1500x1500")

selected_image_paths = []

canvas = Canvas(root)
scrollbar = Scrollbar(root, command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

preview_frame = Frame(root)
preview_frame.pack()

button_select = Button(root, text="Select Images", command=select_images)
button_select.pack()

button_process = Button(root, text="Process Images", command=process_images)
button_process.pack()

button_clear = Button(root, text="clear Images", command=clear_images)
button_clear.pack()

standard_sizes = [
    ("Instagram (320x320)", "320x320"),
    ("Facebook Desktop (170x170)", "170x170"),
    ("LinkedIn/Twitter (400x400)", "400x400"),
    ("Pinterest (165x165)", "165x165")
]

selected_option = tk.StringVar(value=standard_sizes[0][0])

size_menu = tk.OptionMenu(root, selected_option, *[label for label, size in standard_sizes])
size_menu.pack()

custom_size_frame = tk.Frame(root)
custom_size_frame.pack(fill=tk.X, padx=10, pady=5)

custom_size_label = tk.Label(custom_size_frame, text="Custom Size:")
custom_size_label.pack(side=tk.LEFT)

width_label = tk.Label(custom_size_frame, text="Width:")
width_label.pack(side=tk.LEFT)

width_entry = tk.Entry(custom_size_frame, width=5)
width_entry.pack(side=tk.LEFT, padx=(0, 10))

height_label = tk.Label(custom_size_frame, text="Height:")
height_label.pack(side=tk.LEFT)

height_entry = tk.Entry(custom_size_frame, width=5)
height_entry.pack(side=tk.LEFT)

root.mainloop()
