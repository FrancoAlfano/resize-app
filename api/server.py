import multiprocessing
from PIL import Image
import threading
import socket
import io

process_count = 0

def process_image(data, output_size):
    image = Image.open(io.BytesIO(data))
    resized_image = image.resize(output_size)
    buffer = io.BytesIO()
    resized_image.save(buffer, format='JPEG')
    print('Image processed')
    return buffer.getvalue()

def handle_client(connection, process_counter):
    global process_count
    try:
        received_data = b''
        while True:
            part = connection.recv(4096)
            if not part:
                break
            received_data += part

        if not received_data:
            print("No data received")
            return

        output_size = (1024, 768)

        process = multiprocessing.Process(target=process_image, args=(received_data, output_size))
        process.start()
        process.join()

        with process_counter.get_lock():
            process_counter.value += 1
            process_count = process_counter.value

        processed_image = process_image(received_data, output_size)
        connection.sendall(processed_image)

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connection.close()
        print(f"Total processes created: {process_count}")

def start_server(host='127.0.0.1', port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    process_counter = multiprocessing.Value('i', 0)

    print(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, process_counter))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()
