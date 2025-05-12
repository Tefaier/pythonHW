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
    response, = grequests.map([grequests.get(url)])
    return BeautifulSoup(response.content.decode("utf-8"), 'html.parser')

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

    # synchronous
    start = time.time()

    titles = []
    for i in range(1, 10):
        worker(titles, i)

    end = time.time()
    timings.append(end - start)

    # multithreading
    start = time.time()

    titles = []
    threads = []
    for i in range(11, 20):
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
        for i in range(21, 30):
            pool.submit(worker, titles, i)
        pool.shutdown(wait=True)

    end = time.time()
    timings.append(end - start)

    # async
    start = time.time()

    titles = []
    for i in range(31, 40):
        asyncio.create_task(async_worker(titles, i))
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})

    end = time.time()
    timings.append(end - start)

    print(timings)

if __name__ == "__main__":
    asyncio.run(main())