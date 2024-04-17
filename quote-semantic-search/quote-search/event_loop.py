import asyncio

# Set up the event loop so we can use it across threads.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def run_async(coroutine, blocking=True):
    f = asyncio.run_coroutine_threadsafe(coroutine, loop=loop)

    if blocking:
        return f.result()
