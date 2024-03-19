import asyncio

async def handle_client(reader, writer):
    try:
        data = await reader.read(4096)
        print(f"Received data: {data}")

        if not data:
            print("No data received")
            return

        writer.write(b'OK')
        await writer.drain()
        print("Response sent")

    finally:
        writer.close()
        await writer.wait_closed()
        print("Connection closed")

async def main(host='127.0.0.1', port=8080):
    server = await asyncio.start_server(handle_client, host, port)
    print(f'Server listening on {host}:{port}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
