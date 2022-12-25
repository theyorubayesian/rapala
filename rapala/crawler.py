import asyncio
import csv
import random
from asyncio import Queue
from string import Template
from typing import Dict
from typing import Set

import aiohttp
import yaml

from rapala.helpers import *

CONFIG = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
ALL_CATEGORIES = CONFIG["CATEGORY_URLS"]

factor = lambda: random.uniform(0.89, 1.19)


async def get_all_urls(
    category_url: str, 
    collected_urls: Set[str],
    start_date: str,
    article_url_template: Template, 
    month_map: Dict[str, str], 
    url_queue: Queue,
    time_delay: float = 3
) -> None:
    global collected_all_urls

    async with aiohttp.ClientSession() as session:
        if start_date:
            dated_url = category_url + start_date
            page_soup = await get_page_soup(session, dated_url)
        else:
            page_soup = await get_page_soup(session, category_url)
        
        article_urls = get_valid_urls(page_soup, article_url_template)
        
        for url in article_urls:
            if url not in collected_urls:
                collected_urls.add(url)
                await url_queue.put(url)

        last_date = None
        date_template = Template(category_url + "$date")

        while True:
            next_date = get_next_date(page_soup, month_map, last_date, CONFIG["ARTICLE_DATE_SPAN_CLASS"])
            if next_date is None:
                collected_all_urls = True
                return
            
            url = date_template.substitute(date=next_date)
            page_soup = await get_page_soup(session, url)
            article_urls = get_valid_urls(page_soup, article_url_template)
            await asyncio.sleep(time_delay * factor())

            for url in article_urls:
                if url not in collected_urls:
                    collected_urls.add(url)
                    await url_queue.put(url)
            
            last_date = next_date


async def get_all_articles(
    category: str, 
    url_queue: Queue, 
    data_queue: Queue,
    time_delay: float = 3.4
) -> None:
    global collected_all_urls, collected_all_articles

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                article_url = await url_queue.get()
            except asyncio.QueueEmpty:
                if collected_all_urls:
                    collected_all_articles = True
                    return
                else:
                    await asyncio.sleep(time_delay * factor())
            else:
                await get_article_data(
                    session, 
                    article_url, 
                    category, 
                    data_queue, 
                    CONFIG["HEADLINE_TAG_CLASS"],
                    CONFIG["ARTICLE_DIV_CLASS"]
                )
                url_queue.task_done()
                await asyncio.sleep(time_delay * factor())


async def write_articles_to_file(
    output_file_name: str, 
    data_queue: Queue,
    total_num_articles: int
) -> None:
    global collected_all_articles

    with open(output_file_name, "w", encoding="utf-8") as csv_file:
        headers = ["headline", "content", "category", "url"]
        writer = csv.DictWriter(csv_file, delimiter="\t", fieldnames = headers, lineterminator='\n')
        writer.writeheader()

        story_num = 0
        while True:
            try:
                article_data = await data_queue.get()
            except asyncio.QueueEmpty:
                if collected_all_articles:
                    return
                else:
                    await asyncio.sleep(1.3 * factor())
            else:
                writer.writerow(article_data)
                story_num += 1

                data_queue.task_done()

                if story_num % 500 == 0:
                    print(f"Written {story_num} articles to file")

                if total_num_articles > 0 and story_num >= total_num_articles:
                    running_tasks = asyncio.all_tasks()
                    running_tasks.remove(asyncio.current_task())
                    [task.cancel() for task in running_tasks]
                    print(
                        f"Collected requested number of articles: {story_num} "
                        "for category: {article_data['category']}"
                    )
                    return


async def run_all(
    category_url: str, 
    category: str, 
    output_file: str,
    start_date: str,
    total_num_articles: int,
    template: Template, 
    month_map: Dict[str, str]
) -> None:
    tasks = []
    global collected_all_articles, collected_all_urls
    collected_all_urls = False
    collected_all_articles = False
    
    article_url_queue = Queue()
    article_data_queue = Queue()
    collected_urls = set()

    get_article_url_task = asyncio.create_task(
        get_all_urls(category_url, collected_urls, start_date, template, month_map, article_url_queue)
    )
    get_article_data_task = asyncio.create_task(
        get_all_articles(category, article_url_queue, article_data_queue))
    write_article_data_task = asyncio.create_task(
        write_articles_to_file(output_file, article_data_queue, total_num_articles))

    tasks = [get_article_data_task, get_article_url_task, write_article_data_task]

    await asyncio.gather(*tasks, return_exceptions=True)

    return


def main(
    category_url: str, 
    category: str,
    total_num_articles: int,
    start_date: str,
    output_file: str, 
    template: Template, 
    month_map: Dict[str, str],
) -> None:
    asyncio.run(
        run_all(category_url, category, output_file, start_date, total_num_articles, template, month_map)
    )
    return
