from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import time
from typing import Any, Dict, List


class Rapala:
    def __init__(
        self,
        chrome_path: str = None,
        prefs: Dict[str:Any] = None,
        filename: str = None,
        unallowed_tokens: List = None,
        source_to_start_from: int = None,
        page_to_start_from: int = None,
        article_to_start_from: int = None,
    ) -> None:
        """ """
        self.page_to_start_from = page_to_start_from or 0
        self.article_to_start_from = article_to_start_from or 0
        self.source_to_start_from = source_to_start_from or 0

        self.chrome_path = chrome_path

        # disable images in browser for faster loading.
        self.prefs = prefs or {"profile.managed_default_content_settings.images": 2}
        self.driver = None

        self.first_article_path = (
            './/*[@id="content"]/div[1]/div/div/div/div[1]/div[2]/div/ul[1]/li/div/div/a/h4'
            or "/html/body/div[2]/div/div[4]/div/div/div/div/div/div[2]/div/ul[1]/li/div/div/a/h4"
        )
        self.article_path = (
            './/*[@id="ordinaryItems"]/li[{}]/div/div/a/h4'
            or "/html/body/div[2]/div/div[4]/div/div/div/div/div/div[2]/div/ul[2]/li[{}]/div/div/a/h4"
        )

        self.sources = [
            "https://www.voaswahili.com/z/4658/?p={}",
            "https://www.voaswahili.com/z/4657/?p={}",
            "https://www.voaswahili.com/z/4660/?p={}",
            "https://www.voaswahili.com/z/4768/?p={}",
            "https://www.voaswahili.com/z/4659/?p={}",
            "https://www.voaswahili.com/z/2774/?p={}",
            "https://www.voaswahili.com/z/2775/?p={}",
            "https://www.voaswahili.com/z/2783/?p={}",
        ]

        # sources_page_limit now properly addressed
        self.sources_page_limit = {
            0: 101,
            1: 101,
            2: 59,
            3: 38,
            4: 72,
            5: 101,
            6: 101,
            7: 101,
        }

        self.unallowed_tokens = unallowed_tokens or [
            "Print",
            "No media source currently available",
        ]
        self.filename = filename or "voa_swahili_{}_{}_{}_{}.txt".format(
            time.strftime("%Y%m%d-%H%M%S"),
            self.source_to_start_from,
            self.page_to_start_from,
            self.article_to_start_from,
        )
        self.file = open(self.filename, "w+", encoding="utf-8")

    def init_driver(self) -> webdriver:
        """
        This func initializes the webdriver and disables images
        A wait is initialized with a 5 second timeout
        """
        options = Options()
        options.add_argument("--headless")
        options.add_experimental_option("prefs", self.prefs)
        service = Service(self.chrome_path)
        driver = webdriver.Chrome(service=service, options=options)
        # define a generic wait to be used throughout
        driver.wait = WebDriverWait(driver, 5)

        return driver

    def __write_article_to_text(self, sentences: str) -> None:
        """
        This func write individual sentences to the file
        """
        sentence_split = filter(None, sentences.split("."))
        for s in sentence_split:
            self.file.write(s.strip() + "\n")

    def __on_article_action(self) -> None:
        """
        This func contains all actions that happen when an article is opened
        """
        # driver.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'p')))
        # grab & parse page html
        content = self.driver.page_source
        soup = bs(content)
        # included to write article title and category into file
        title = None

        if title:
            title = soup.find(
                "div", attrs={"class": "col-title col-xs-12 col-lg-10 pull-right"}
            ).text.strip()
            self.__write_article_to_text(title)
        elif title == None:
            title = soup.find("h1", attrs={"class": "title pg-title"}).text.strip()
            self.__write_article_to_text(title)

        category = soup.find(
            "div", attrs={"class": "category js-category js-category--used"}
        ).text.strip()
        self.__write_article_to_text(category)
        # loop over individual p-elements
        # & write their text to file
        for line in soup.findAll("p"):
            # remove unallowed tokens from text written to file
            if line.text.strip() not in self.unallowed_tokens:
                self.__write_article_to_text(line.text)

    def open_article_and_collect(self, article_path: str) -> None:
        """
        This func open an article on the same browser window,
        calls on_article_action and then returns to the index
        page.
        """

        # get link of article to be collected
        """link = self.driver.find_element_by_xpath(article_path).get_attribute("href")
        
        # open article in new window and switch to it 
        self.driver.execute_script("window.open('{}')".format(link))
        time.sleep(1)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])
        time.sleep(1)"""
        WebElement
        button = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, article_path))
        )
        button.click()
        # open the article in same window
        # self.driver.find_element_by_xpath(article_path).click()
        # collect the article into file & increment articles_collected
        self.__on_article_action()

        self.driver.back()
        time.sleep(1)

    def start(self):
        """
        This func uses all previous functions to
        loop over all the sources and collect all articles
        into a file.
        """

        # initialize the driver
        self.driver = self.init_driver()

        try:
            for i in range(self.source_to_start_from, len(self.sources)):
                print("Collecting source: {}".format(self.sources[i]))

                # loop over the number of pages that section has, starting from pages_collected
                for j in range(self.page_to_start_from, self.sources_page_limit[i]):

                    self.driver.get(self.sources[i].format(j))
                    # loop over the number of articles on the page
                    for k in range(self.article_to_start_from, 12):
                        if k == 0:
                            # collect the first article on the page
                            self.open_article_and_collect(self.first_article_path)
                            continue
                        elif k > 2:
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView();",
                                self.driver.find_element(
                                    By.XPATH, self.article_path.format(k - 2)
                                ),
                            )
                            time.sleep(1)
                        self.open_article_and_collect(self.article_path.format(k))
            self.file.close()
            self.driver.close()
            print(
                "O ti pari! The end l'opin cinema. I love you lo n gbeyin mills and boon."
            )
        except Exception as e:
            self.file.close()
            self.driver.close()
            print("Failed after: Source {} Page {} Article {}".format(i, j, k))
            raise e


if __name__ == "__main__":
    rpl = Rapala(chrome_path="C:\Program Files\chromedriver.exe")
    rpl.start()
