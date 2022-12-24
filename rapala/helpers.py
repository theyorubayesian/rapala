from asyncio import Queue
from datetime import datetime
from datetime import timedelta
from string import Template
from typing import  List

import aiohttp
from bs4 import BeautifulSoup


def clean_string(x: str) -> str:
    return (
        x.replace(" ", "_")
        .replace("\\", "")
        .replace("/", "")
        .replace("(", "")
        .replace(")", "")
    )


async def get_page_soup(session: aiohttp.ClientSession, url:str) -> BeautifulSoup:
    """
    Makes a request to a url and creates a beautiful soup oject from the response html

    input:
        :param url: input page url
    returns:
        - page_soup: beautiful soup oject from the response html
    """
    async with session.get(url) as response:
        res = await response.read()
        page_html = res.decode("utf-8")
        page_soup = BeautifulSoup(page_html, "html.parser")

        return page_soup


def get_valid_urls(page_soup: BeautifulSoup, url_template: Template) -> List[str]:
    urls = [
        url_template.substitute(href=link.get("href"))
        for link in page_soup.find_all("a") 
        if link.get("href") is not None and link.get("href").startswith("/a/")
    ]
    return urls


def get_next_date(page_soup: BeautifulSoup, month_map: dict, last_date: datetime, date_element_class_name: str) -> str:
    last_article_date_str = ""
    for cls_name in date_element_class_name:
        last_article_date_str = page_soup.find_all("span", attrs={"class": cls_name})

        if last_article_date_str:
            last_article_date_str = last_article_date_str[-1]
            break

    if not last_article_date_str:
        return None
    
    try:
        month, day, year = last_article_date_str.text.split("-")
        last_article_date = datetime(int(year), int(month), int(day))
    except ValueError:
        month, day, year = last_article_date_str.text.lower().replace(",", "").split(" ")
        last_article_date = datetime(int(year), month_map[month], int(day))
    finally:
        fmtd_last_article_date = last_article_date.strftime("%Y/%m/%d")

    if fmtd_last_article_date == last_date:
        return (last_article_date - timedelta(days=1)).strftime("%Y/%m/%d")

    return fmtd_last_article_date


def is_media_article(page_soup: BeautifulSoup) -> bool:
    media_element = page_soup.find("div", attrs={"class": "media-block-wrap"})
    return bool(media_element)


async def get_article_data(
    session: aiohttp.ClientSession, 
    article_url: str, category: str, 
    article_data_queue: Queue, 
    headline_element_class_name: str,
    article_content_container_class_name: str
) -> None:
    page_soup = await get_page_soup(session, article_url)

    headline = ""
    for cls_name in headline_element_class_name:
        if not headline:    # This is a hack. How to break commands work in async functions?
            headline = page_soup.find("h1", attrs={"class": cls_name})
        if headline:
            headline = headline.text.strip()
    
    for cls_name in article_content_container_class_name:
        story_container = page_soup.find("div", attrs={"class": cls_name})

        if story_container:
            content = " ".join([p.text.strip().replace("\r", "").replace("\n", "\\n") for p in story_container.find_all("p")])
            
            data = {
                "headline": headline,
                "content": content,
                "category": category,
                "url": article_url
            }
            await article_data_queue.put(data)
            return
    
    if not is_media_article(page_soup):
        print(f"Could not collect article content for URL: {article_url}")

    return
