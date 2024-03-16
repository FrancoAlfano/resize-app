from tkinter import Tk, Label, Button, filedialog, messagebox, Scrollbar, Frame, Canvas
from PIL import Image, ImageTk
import socket
import io
import os

def send_image_to_server(image_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('127.0.0.1', 8080))
        with open(image_path, 'rb') as f:
            bytes_read = f.read(1024)
            while bytes_read:
                sock.sendall(bytes_read)
                bytes_read = f.read(1024)

        sock.shutdown(socket.SHUT_WR)

        received_data = b''
        while True:
            part = sock.recv(1024)
            if not part:
                break
            received_data += part

        return received_data

def download_image(image_data):
    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG images", "*.jpg")])
    if save_path:
        with open(save_path, "wb") as f:
            f.write(image_data)

def select_images():
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        global selected_image_paths
        selected_image_paths = file_paths

        for widget in preview_frame.winfo_children():
            widget.destroy()

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

def process_images():
    if selected_image_paths:
        for image_path in selected_image_paths:
            image_data = send_image_to_server(image_path)
            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)

            frame = Frame(scrollable_frame)
            frame.pack()

            label = Label(frame, image=photo)
            label.image = photo
            label.pack(side="left")

            button = Button(frame, text="Download", command=lambda data=image_data: download_image(data))
            button.pack(side="right")

            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
    else:
        messagebox.showerror("Error", "No images selected")

root = Tk()
root.title("Resize-app")
root.geometry("1500x1500")

selected_image_paths = []

canvas = Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = Scrollbar(root, command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

scrollable_frame = Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

preview_frame = Frame(root)
preview_frame.pack()

button_select = Button(root, text="Select Images", command=select_images)
button_select.pack()

button_process = Button(root, text="Process Images", command=process_images)
button_process.pack()

root.mainloop()
