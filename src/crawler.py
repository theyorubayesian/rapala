import argparse
import asyncio
import csv
import glob
import multiprocessing
import os
from asyncio import Queue
from functools import partial
from string import Template
from typing import Dict
from typing import Set

import aiohttp
import pandas as pd
import yaml

from src.constants import *
from src.helpers import *

CONFIG = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
ALL_CATEGORIES = CONFIG["CATEGORY_URLS"]


async def get_all_urls(
    category_url: str, 
    collected_urls: Set[str], 
    article_url_template: Template, 
    month_map: Dict[str, str], q: Queue
) -> None:
    global collected_all_urls

    async with aiohttp.ClientSession() as session:
        page_soup = await get_page_soup(session, category_url)
        article_urls = get_valid_urls(page_soup, article_url_template)
        
        for url in article_urls:
            if url not in collected_urls:
                collected_urls.add(url)
                await q.put(url)

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

            for url in article_urls:
                if url not in collected_urls:
                    collected_urls.add(url)
                    await q.put(url)
            
            last_date = next_date


async def get_all_articles(category: str, url_queue: Queue, data_queue: Queue) -> None:
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
                    pass
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


async def write_articles_to_file(output_file_name: str, data_queue: Queue) -> None:
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
                    pass
            else:
                writer.writerow(article_data)
                story_num += 1

                data_queue.task_done()

                if story_num % 500 == 0:
                    print(f"Written {story_num} articles to file")


async def run_all(
    category_url: str, 
    category: str, 
    output_file: str, 
    template: Template, 
    month_map: Dict[str, str]
) -> None:
    tasks = []
    
    article_url_queue = Queue()
    article_data_queue = Queue()
    collected_urls = set()

    get_article_url_task = asyncio.create_task(
        get_all_urls(category_url, collected_urls, template, month_map, article_url_queue))
    get_article_data_task = asyncio.create_task(
        get_all_articles(category, article_url_queue, article_data_queue))
    write_article_data_task = asyncio.create_task(write_articles_to_file(output_file, article_data_queue))

    tasks = [get_article_data_task, get_article_url_task, write_article_data_task]

    await asyncio.gather(*tasks, return_exceptions=True)

    return


def main(
    category_url: str, 
    category: str, 
    output_file: str, 
    template: Template, 
    month_map: Dict[str, str]
) -> None:
    asyncio.run(run_all(category_url, category, output_file, template, month_map))
    return


def get_parser() -> argparse.ArgumentParser:
    """
    parse command line arguments

    returns:
        parser - ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        prog="VOA-Scraper",
        description="VOA News Website Scraper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Written by: Akintunde 'theyorubayesian' Oladipo <akin.o.oladipo at gmail dot com>"
    )
    parser.add_argument(
        "--language",
        type=str,
        help="Language of BBC Website"
    )
    parser.add_argument(
        "--output_file_name", 
        type=str,
        help="Name of output file alone. Output file is written to `data` directory",
        )
    parser.add_argument(
        "--categories", 
        type=str, 
        default="all", 
        help="Specify what news categories to scrape from." 
              "Multiple news categories should be separated by a comma. eg. 'africa,world,sport'",
        )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove sub-topic TSV files created after combining them into final corpora"
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.categories != "all":
        categories = args.categories.upper().split(",")
        categories = {category: ALL_CATEGORIES[args.language][category] for category in categories}
    else:
        categories = ALL_CATEGORIES[args.language]
    
    article_template = Template(URLS[args.language] + "$href")
    month_map = MONTH_MAP[args.language]

    pool = multiprocessing.Pool()
    processes = [
        pool.apply_async(
            main,
            args=(
                url,
                category,
                f"data/{category}_{args.output_file_name}",
                article_template,
                month_map
            )
        ) for category, url in categories.items()
    ]

    result = [p.get() for p in processes]

    output_file_pattern = f"data/*_{args.output_file_name}"
    category_file_names = glob.glob(output_file_pattern)

    reader = partial(pd.read_csv, sep="\t", lineterminator="\n")
    all_dfs = map(reader, category_file_names)
    corpora = pd.concat(all_dfs).drop_duplicates(subset="url", keep="last")
    corpora.to_csv(args.output_file_name, sep="\t", index=False)

    if args.cleanup:
        for f in category_file_names:
            os.remove(f)
