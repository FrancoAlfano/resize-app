from tkinter import Tk, Label, Button, filedialog, messagebox
from PIL import Image, ImageTk
import socket
import io

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

def select_images():
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        global selected_image_paths
        selected_image_paths = file_paths
        image = Image.open(file_paths[0])
        preview_image = image.resize((300, 300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(preview_image)
        label.config(image=photo)
        label.image = photo

def process_images():
    if selected_image_paths:
        for image_path in selected_image_paths:
            image_data = send_image_to_server(image_path)
            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
            root.update()
    else:
        messagebox.showerror("Error", "No images selected")

root = Tk()
root.title("Resize-app")
root.geometry("1000x1000")

window_width = 1000
window_height = 1000
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

label = Label(root)
label.pack()

button_select = Button(root, text="Select Images", command=select_images)
button_select.pack()

button_process = Button(root, text="Process Images", command=process_images)
button_process.pack()

selected_image_paths = []

root.mainloop()
