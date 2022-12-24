import argparse
import glob
import multiprocessing
import os
from functools import partial
from string import Template

import pandas as pd

from rapala.constants import *
from rapala.crawler import ALL_CATEGORIES
from rapala.crawler import main
from rapala.helpers import clean_string


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
        "--no_of_articles", 
        type=int,
        default=-1,
        help="Maximum number of articles to be scraped from each category"
             "If -1, we scrape all articles we find",
        )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove sub-topic TSV files created after combining them into final corpora"
    )
    parser.add_argument(
        "--spread",
        action="store_true",
        help="Spread `no_of_articles` evenly across categories instead"
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
    
    articles_per_category = args.no_of_articles
    if args.no_of_articles > 0 and args.spread:
        articles_per_category = args.no_of_articles // len(categories)
    
    article_template = Template(URLS[args.language] + "$href")
    month_map = MONTH_MAP[args.language]

    pool = multiprocessing.Pool()
    processes = [
        pool.apply_async(
            main,
            args=(
                url,
                category,
                articles_per_category,
                f"data/{clean_string(category)}_{args.output_file_name}",
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
