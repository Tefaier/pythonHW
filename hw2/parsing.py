from concurrent.futures.process import ProcessPoolExecutor

from bs4 import BeautifulSoup
import grequests
import threading
import time
import matplotlib.pyplot as plt
import multiprocessing
import concurrent
import asyncio

lock = threading.Lock()

def create_url(number: int) -> str:
    return f"https://author.today/work/genre/detective?eg=-&fnd=false&page={number}"

def get_soup(url: str) -> BeautifulSoup:
    response = grequests.map([grequests.get(url)])
    return BeautifulSoup(response[0].content.decode("utf-8"), 'html.parser')

def get_titles_names(soup: BeautifulSoup) -> list[str]:
    divs = soup.find_all("div", {"class": "book-title"})
    return [div.text.strip() for div in divs]

def worker(titles: list[str], number: int):
    results = get_titles_names(get_soup(create_url(number)))
    lock.acquire()
    for title in results:
        titles.append(title)
    lock.release()

async def async_worker(titles: list[str], number: int):
    response = None
    for result in grequests.imap([grequests.get(create_url(number))]):
        response = result
        break
    content = response.content
    soup = BeautifulSoup(content.decode("utf-8"), 'html.parser')
    divs = soup.find_all("div", {"class": "book-title"})
    results = [div.text.strip() for div in divs]
    lock.acquire()
    for title in results:
        titles.append(title)
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
    for i in range(size + 1, size * 2 + 1):
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
        for i in range(size * 2 + 1, size * 3 + 1):
            pool.submit(worker, titles, i)
        pool.shutdown(wait=True)

    end = time.time()
    timings.append(end - start)

    # async
    start = time.time()

    titles = []
    for i in range(size * 3 + 1, size * 4 + 1):
        asyncio.create_task(async_worker(titles, i))
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})

    end = time.time()
    timings.append(end - start)

    print(timings)
    plt.figure(figsize=(15,10))
    l = plt.bar(["Synchronous", "Multithreading", "Multiprocessing", "Async"], timings, 0.5)
    plt.bar_label(l, label_type="center")
    plt.title(f"Time of parsing {size} pages depending on method, Python 3.12, CPython")
    plt.ylabel("Time, s")
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())