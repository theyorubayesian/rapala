from asyncio import Queue
from datetime import datetime
from datetime import timedelta
from string import Template
from typing import  List

import aiohttp
from bs4 import BeautifulSoup


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
    try:
        last_article_date_str = page_soup.find_all("span", attrs={"class": date_element_class_name})[-1]
    except IndexError:
        return None
    
    month, day, year = last_article_date_str.text.lower().replace(",", "").split(" ")

    last_article_date = datetime(int(year), month_map[month], int(day))
    fmtd_last_article_date = last_article_date.strftime("%Y/%m/%d")

    if fmtd_last_article_date == last_date:
        return (last_article_date - timedelta(days=1)).strftime("%Y/%m/%d")

    return fmtd_last_article_date


async def get_article_data(
    session: aiohttp.ClientSession, 
    article_url: str, category: str, 
    article_data_queue: Queue, 
    headline_element_class_name: str,
    article_content_container_class_name: str
) -> None:
    page_soup = await get_page_soup(session, article_url)

    headline = page_soup.find("h1", attrs={"class": headline_element_class_name})
    if headline:
        headline = headline.text.strip()
    
    story_container = page_soup.find("div", attrs={"class": article_content_container_class_name})
    if story_container:
        content = " ".join([p.text.strip().replace("\r", "").replace("\n", "\\n") for p in story_container.find_all("p")])
        
        data = {
            "headline": headline,
            "content": content,
            "category": category,
            "url": article_url
        }
        await article_data_queue.put(data)
    else:
        print(f"Could not collect article content for URL: {article_url}")

    return
