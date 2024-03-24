import asyncio
import concurrent.futures
from PIL import Image
import io

def process_image(data, output_size, is_custom=False):
    image = Image.open(io.BytesIO(data))
    if not is_custom:
        original_aspect_ratio = image.width / image.height
        target_width, target_height = output_size
        target_aspect_ratio = target_width / target_height

        if target_aspect_ratio > original_aspect_ratio:
            new_height = target_height
            new_width = int(new_height * original_aspect_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / original_aspect_ratio)

        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    else:
        resized_image = image.resize(output_size, Image.LANCZOS)

    buffer = io.BytesIO()
    format = image.format if image.format else 'JPEG'
    resized_image.save(buffer, format)
    return buffer.getvalue()


async def handle_client(reader, writer):
    size_header = await reader.readline()
    selected_size_str = size_header.decode().strip()

    if selected_size_str.startswith('custom:'):
        is_custom = True
        selected_size_str = selected_size_str.replace('custom:', '', 1)
    else:
        is_custom = False

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
                pool, process_image, data, selected_size, is_custom
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
