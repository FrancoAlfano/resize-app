import asyncio
import time

async def make_request(host, port, message, semaphore):
    async with semaphore:
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message)
        await writer.drain()
        data = await reader.read(100)
        writer.close()
        await writer.wait_closed()
        return data.decode()

async def load_test(host, port, total_clients, requests_per_client, concurrent_limit):
    semaphore = asyncio.Semaphore(concurrent_limit)
    start_time = time.time()
    tasks = []
    client = 0
    request = 0
    for _ in range(total_clients):
        for _ in range(requests_per_client):
            task = asyncio.create_task(make_request(host, port, b'LOAD_TEST', semaphore))
            tasks.append(task)
    responses = await asyncio.gather(*tasks)
    end_time = time.time()
    print(f"All requests completed in {end_time - start_time} seconds.")
    print(f"Received {len(responses)} responses")

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8080
    TOTAL_CLIENTS = 100
    REQUESTS_PER_CLIENT = 100
    CONCURRENT_LIMIT = 100

    asyncio.run(load_test(HOST, PORT, TOTAL_CLIENTS, REQUESTS_PER_CLIENT, CONCURRENT_LIMIT))
