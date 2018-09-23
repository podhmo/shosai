import asyncio


def map(fn, xs, *, loop=None, concurrency=4, return_exceptions=True):
    loop = loop or asyncio.get_event_loop()
    sem = asyncio.Semaphore(concurrency)

    async def do_task(x):
        async with sem:
            return await loop.run_in_executor(None, fn, x)

    async def run():
        tasks = [do_task(x) for x in xs]
        return await asyncio.gather(*tasks, loop=loop, return_exceptions=return_exceptions)

    return loop.run_until_complete(run())
