from client_config import SERVER_ADDRESS, SERVER_PORT
import threading
import socket

def send_image_to_server(image_path, callback, get_selected_size, get_selected_filter, get_selected_alpha):
    def thread_target():
        addrinfo = socket.getaddrinfo(SERVER_ADDRESS, SERVER_PORT, socket.AF_UNSPEC, socket.SOCK_STREAM)
        af, socktype, proto, canonname, sa = addrinfo[0]
        with socket.socket(af, socktype, proto) as sock:
            sock.connect(sa)
            selected_size_str = get_selected_size() + '\n'
            selected_filter_str = get_selected_filter() + '\n'
            selected_alpha_str = str(get_selected_alpha()) + '\n'
            sock.sendall(selected_size_str.encode())
            sock.sendall(selected_filter_str.encode())
            sock.sendall(selected_alpha_str.encode())
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

            callback(received_data, image_path)

    threading.Thread(target=thread_target).start()

