from concurrent.futures.process import ProcessPoolExecutor

import threading
import time
import matplotlib.pyplot as plt
import asyncio
import math

lock = threading.Lock()

def heavy(number):
    result = 0
    for i in range(1, 10000000):
        result += math.sqrt(number / i) * math.pow(number + math.log(i), 2.1) / math.log(number * i + 1)
    return result

def worker(results: list[float], number: int):
    result = heavy(number)

    lock.acquire()
    results.append(result)
    lock.release()

async def async_worker(results: list[float], number: int):
    result = heavy(number)

    lock.acquire()
    results.append(result)
    lock.release()

async def main():
    timings = []
    size = 10

    # synchronous
    start = time.time()

    titles = []
    for i in range(1, size + 1):
        worker(titles, i)

    end = time.time()
    timings.append(end - start)

    # multithreading
    start = time.time()

    titles = []
    threads = []
    for i in range(1, size + 1):
        threads.append(threading.Thread(target=worker, args=(titles, i)))
        threads[-1].start()
    for thread in threads:
        thread.join()

    end = time.time()
    timings.append(end - start)

    # multiprocessing
    start = time.time()

    titles = []
    processes = []
    with ProcessPoolExecutor(max_workers=6) as pool:
        for i in range(1, size + 1):
            pool.submit(worker, titles, i)
        pool.shutdown(wait=True)

    end = time.time()
    timings.append(end - start)

    # async
    start = time.time()

    titles = []
    for i in range(1, size + 1):
        asyncio.create_task(async_worker(titles, i))
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})

    end = time.time()
    timings.append(end - start)

    print(timings)
    plt.figure(figsize=(15,10))
    l = plt.bar(["Synchronous", "Multithreading", "Multiprocessing", "Async"], timings, 0.5)
    plt.bar_label(l, label_type="center")
    plt.title("Time of calculation depending on method, Python 3.12, CPython")
    plt.ylabel("Time, s")
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())