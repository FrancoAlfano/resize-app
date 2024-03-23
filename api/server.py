import asyncio
import concurrent.futures
from PIL import Image
import io

def process_image(data, output_size):
    image = Image.open(io.BytesIO(data))
    resized_image = image.resize(output_size)
    buffer = io.BytesIO()
    format = image.format if image.format else 'JPEG'
    resized_image.save(buffer, format)
    return buffer.getvalue()

async def handle_client(reader, writer):
    size_header = await reader.readline()
    selected_size_str = size_header.decode().strip()
    selected_size = tuple(map(int, selected_size_str.split('x')))

    data = b''
    try:
        while True:
            part = await reader.read(4096)
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
                pool, process_image, data, selected_size
            )

        writer.write(processed_image)
        await writer.drain()
        writer.close()
    except Exception as e:
        print(f"Error processing image: {e}")
        writer.close()



async def main(host='127.0.0.1', port=8080):
    server = await asyncio.start_server(handle_client, host, port)
    print(f'Server listening on {host}:{port}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
