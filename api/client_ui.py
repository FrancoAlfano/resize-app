from tkinter import filedialog, Label, Button
import tkinter as tk
import socket
from PIL import Image, ImageTk

def send_image(image_path, server_host, server_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_host, server_port))

            with open(image_path, "rb") as f:
                image_data = f.read()

            client_socket.sendall(image_data)

            response = client_socket.recv(1024)
            print("Server response:", response.decode())

    except Exception as e:
        print("Error:", e)

def choose_image():
    filename = filedialog.askopenfilename()
    if filename:
        img = Image.open(filename)
        img = img.resize((300, 300))
        photo = ImageTk.PhotoImage(img)
        img_preview.config(image=photo)
        img_preview.image = photo
        img_path.set(filename)

def process_image():
    image_path = img_path.get()
    if image_path:
        send_image(image_path, "localhost", 9999)

root = tk.Tk()
root.title("Resize-app")
root.geometry("800x800")

img_preview = Label(root)
img_preview.pack()

btn_choose_image = Button(root, text="Choose Image", command=choose_image)
btn_choose_image.pack()

img_path = tk.StringVar()

btn_process_image = Button(root, text="Process Image", command=process_image)
btn_process_image.pack()

root.mainloop()
