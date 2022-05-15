from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Added
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

service = ChromeService(executable_path=ChromeDriverManager().install())
import time

class Rapala:
    
    def __init__(self, chrome_path=None, prefs=None, filename=None, unallowed_tokens=None, source_to_start_from=None, page_to_start_from=None,  article_to_start_from=None):
        self.page_to_start_from = page_to_start_from or 0
        self.article_to_start_from = article_to_start_from or 0
        self.source_to_start_from = source_to_start_from or 0
        
        self.chrome_path = chrome_path or 'C:\\Users\\NiniolaAdegboyega\\Downloads\\chromedriver_win32\\chromedriver.exe'
        # disable images in browser. For faster loading. 
        self.prefs = prefs or {"profile.managed_default_content_settings.images" : 2}
        self.driver = None
        
        # fixed error with defined Xpath
        #self.load_more_button_path = "/html/body/div[2]/div/div[4]/div/div/div/div/div/div[2]/p/a"
        self.first_article_path = "/html/body/div[2]/div/div[3]/div[1]/div/div/div/div[1]/div[2]/div/ul[1]/li/div/div/a"
        self.article_path = "/html/body/div[2]/div/div[3]/div[1]/div/div/div/div[1]/div[2]/div/ul[2]/li[{}]/div/div/a"


        self.sources = ["https://www.voahausa.com/z/2866/?p={}",
                        "https://www.voahausa.com/z/2863/?p={}",
                        "https://www.voahausa.com/z/5225/?p={}",
                        "https://www.voahausa.com/z/2870/?p={}",
                        "https://www.voahausa.com/z/2864/?p={}"
                       ]
        self.sources_page_limit = {0:101, 1:101,
                                   2:101,3:100,4:54
                                  }
        
        self.unallowed_tokens = unallowed_tokens or ["Print", "No media source currently available"]
        self.filename = filename or "voa_hausa_{}_{}_{}_{}.txt".format(time.strftime("%Y%m%d-%H%M%S"),
                                                                       self.source_to_start_from,
                                                                       self.page_to_start_from,
                                                                       self.article_to_start_from)
        self.file = open(self.filename, "w+", encoding="utf-8")
        
        
    def init_driver(self):
        """
        This func initializes the webdriver and disables images
        A wait is initialized with a 5 second timeout
        """
        options = Options()
        options.add_argument("--headless")
        options.add_experimental_option("prefs", self.prefs)

        driver = webdriver.Chrome(service=service, options=options)
        # define a generic wait to be used throughout
        driver.wait = WebDriverWait(driver, 5)

        return driver
    
    def __write_article_to_text(self, sentences):
        """
        This func write individual sentences to the file
        """
        # split into individual sentences
        sentence_split = filter(None, sentences.split("."))
        # write each individual sentences on a new line
        for s in sentence_split:
            self.file.write(s.strip() + "\n")
            
    def __on_article_action(self):
        """
        This func contains all actions that happen when an article is opened
        """
        #driver.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'p')))
        # grab & parse page html
        content = self.driver.page_source
        soup = bs(content, features="html.parser")
        
        # loop over individual p-elements 
        # & write their text to file
        for line in soup.findAll("p"):
            # remove unallowed tokens from text written to file
            if line.text.strip() not in self.unallowed_tokens:
                self.__write_article_to_text(line.text)
            
    def open_article_and_collect(self, article_path):
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
        
        # open the article in same window
        # edited from 'find_element_by_Xpath' as function is now deprecated
        self.driver.find_element(by= By.XPATH, value=article_path).click()
        # collect the article into file & increment articles_collected
        self.__on_article_action()

        # return to main page
        self.driver.back()
        time.sleep(1)
        #self.driver.switch_to.window(windows[0])
        
    def start(self):
        """
        This func uses all previous functions to 
        loop over all the sources and collect all articles 
        into a file. 
        """
        # initialize the driver
        self.driver = self.init_driver()
        
        # loop over the individual sections of the site
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
                            # ensure that the rest of the code does not run 
                            continue
                        elif k >= 2:
                            # scroll the article into view
                            # edited deprecated 'find_function_by_expert'
                            self.driver.execute_script("arguments[0].scrollIntoView();",
                                                       self.driver.find_element(by=By.XPATH, value=self.article_path.format(k-1)))
                            time.sleep(1)
                        # collect the other articles on the page
                        self.open_article_and_collect(self.article_path.format(k))
            self.file.close()
            self.driver.close()
            print("O ti pari! The end l'opin cinema. I love you lo n gbeyin mills and boon.")
        except Exception as e:
            self.file.close()
            self.driver.close()
            print("Failed after: Source {} Page {} Article {}".format(i, j, k))
            raise e

rpl = Rapala(source_to_start_from=2)

rpl.start()