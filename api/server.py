from server_config import HOST, PORT, FAMILY, FLAGS, BUFFER_SIZE
from image_processing import process_image
import concurrent.futures
import asyncio


async def handle_client(reader, writer):
    size_header = await reader.readline()
    selected_size_str = size_header.decode().strip()

    if selected_size_str.startswith('exact:'):
        is_exact = True
        selected_size_str = selected_size_str.replace('exact:', '', 1)
    else:
        is_exact = False

    selected_size = tuple(map(int, selected_size_str.split('x')))

    data = b''
    try:
        while True:
            part = await reader.read(BUFFER_SIZE)
            if not part:
                break
            data += part

        if not data:
            print("No data received")
            writer.close()
            return

        loop = asyncio.get_running_loop()
        with concurrent.futures.ProcessPoolExecutor() as pool:
            processed_image = await loop.run_in_executor(
                pool, process_image, data, selected_size, is_exact
            )

        writer.write(processed_image)
        await writer.drain()
        writer.close()
    except Exception as e:
        print(f"Error processing image: {e}")
        writer.close()


async def main():
    server = await asyncio.start_server(
        handle_client, HOST, PORT, family=FAMILY, flags=FLAGS)
    print(f'Server listening on {HOST}:{PORT}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    print("Starting server")
    asyncio.run(main())
