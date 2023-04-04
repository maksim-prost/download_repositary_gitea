"""Модуль движка асинхроного скачивания."""
import asyncio


async def run_queue(list_file, func, count_worker):
    """Асинхронный запуск функции func с аргументами из list_file.

    Args:
        list_file: list
            список аргументов.
        func: function
            выполняемая функция.
        count_worker: string
            количество асинхроно выполняемых задач.
    """
    queue = asyncio.Queue()
    for title_file in list_file:
        await queue.put(title_file)
    tasks = [
        asyncio.ensure_future(worker(queue, func))
        for _ in range(count_worker)
    ]
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def worker(queue: asyncio.Queue, func):
    """Получет аргумент из очереди и запускает функцию с этим аргументом.

    Args:
        queue: asyncio.Queue
            Очередь.
        func: function
            Выполняемая функция.
    """
    while not queue.empty():
        # Получить "рабочий элемент" из очереди.
        title_file = await queue.get()
        await func(title_file)
        queue.task_done()
