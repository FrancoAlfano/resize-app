import socketserver
import threading
import os
from PIL import Image

def process_image(image_data, output_folder):
    try:
        if image_data:
            image_path = os.path.join(output_folder, "temp_image.png")
            with open(image_path, "wb") as f:
                f.write(image_data)

            if os.path.exists(image_path):
                print("Image file saved successfully:", image_path)

                img = Image.open(image_path)
                img = img.resize((300, 300))
                output_path = os.path.join(output_folder, "processed_image.png")
                img.save(output_path)

                return output_path
            else:
                print("Error: Image file not saved")
                return None
        else:
            print("Error: No image data received")
            return None

    except Exception as e:
        print("Error processing image:", e)
        return None

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        image_data = b""
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            image_data += data

        output_folder = "images"
        os.makedirs(output_folder, exist_ok=True)

        thread = threading.Thread(target=process_image, args=(image_data, output_folder))
        thread.start()
        thread.join()

        self.request.sendall(b"Image processed and saved successfully")

HOST, PORT = "localhost", 9999

with socketserver.ThreadingTCPServer((HOST, PORT), TCPHandler) as server:
    print("Server started")
    server.serve_forever()
