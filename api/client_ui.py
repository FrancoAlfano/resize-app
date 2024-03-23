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
    if selected_image_paths:
        for image_path in selected_image_paths:
            send_image_to_server(image_path, update_ui)
    else:
        messagebox.showerror("Error", "No images selected")

def select_images():
    global selected_image_paths
    for widget in preview_frame.winfo_children():
        widget.destroy()
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    file_paths = filedialog.askopenfilenames()
    if file_paths:
        selected_image_paths = file_paths

        for image_path in file_paths:
            image = Image.open(image_path)
            thumbnail = image.resize((150, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(thumbnail)

            frame = Frame(preview_frame)
            frame.pack(side="left", padx=10, pady=10)

            label = Label(frame, image=photo)
            label.image = photo
            label.pack()

            title = os.path.basename(image_path)
            title_label = Label(frame, text=title)
            title_label.pack()


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
    selected_label = selected_option.get()
    for label, size in standard_sizes:
        if label == selected_label:
            return size
    return None

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

standard_sizes = [
    ("Instagram (320x320)", "320x320"),
    ("Facebook Desktop (170x170)", "170x170"),
    ("LinkedIn/Twitter (400x400)", "400x400"),
    ("Pinterest (165x165)", "165x165")
]

selected_option = tk.StringVar(value=standard_sizes[0][0])

size_menu = tk.OptionMenu(root, selected_option, *[label for label, size in standard_sizes])
size_menu.pack()

root.mainloop()
