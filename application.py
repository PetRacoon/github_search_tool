import asyncio

from front_server import init_front

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    init_front(loop=loop)