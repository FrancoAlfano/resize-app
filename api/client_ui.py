import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageFilter, ImageEnhance, ImageTk

def load_image():
    filename = filedialog.askopenfilename()
    if filename:
        img = Image.open(filename)
        img = img.resize((300, 300))
        photo = ImageTk.PhotoImage(img)
        label_img.config(image=photo)
        label_img.image = photo
        global image_path
        image_path = filename

def process_image(image_path='/home/franco/Downloads/mario/mario.jpg', output_folder='.', custom_size=None, filter_type=None, overlay_image=None, transparency=100):
    img = Image.open(image_path)
    print('processing')
    print(img.width, img.height)

    if custom_size:
        width, height = custom_size
        img = img.resize((width, height), Image.ANTIALIAS)

    if filter_type:
        if filter_type == "blur":
            img = img.filter(ImageFilter.BLUR)
        elif filter_type == "grayscale":
            img = img.convert("L")

    if overlay_image:
        overlay = Image.open(overlay_image)
        if transparency is not None:
            overlay = overlay.convert("RGBA")
            overlay = ImageEnhance.Brightness(overlay).enhance(transparency)
        img.paste(overlay, (0, 0), overlay)

    output_path = os.path.join(output_folder, f"{img.width}x{img.height}_processed.png")
    img.save(output_path)
    print('saved')
    return output_path

root = tk.Tk()
root.title("Resize-app")

btn_load = tk.Button(root, text="Load Image", command=load_image)
btn_load.pack()

label_img = tk.Label(root)
label_img.pack()

btn_process = tk.Button(root, text="Process Image", command=process_image())
btn_process.pack()

image_path = None

root.mainloop()
