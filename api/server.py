import socketserver
import threading
import os
from PIL import Image, ImageFilter, ImageEnhance

def process_image(image_path='/home/franco/Downloads/mario/mario.jpg', output_folder='.', custom_size=None, filter_type=None, overlay_image=None, transparency=None):
    img = Image.open(image_path)

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
    return output_path

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        image_data = self.request.recv(1024).strip()  # Receive image data
        image_path = "temp.png"
        with open(image_path, "wb") as f:
            f.write(image_data)

        output_folder = "images"
        os.makedirs(output_folder, exist_ok=True)

        thread = threading.Thread(target=process_image, args=(image_path, output_folder))
        thread.start()

        self.request.sendall(b"Image processed and saved successfully")

HOST, PORT = "localhost", 9999

with socketserver.ThreadingTCPServer((HOST, PORT), TCPHandler) as server:
    print("Server started")
    server.serve_forever()
