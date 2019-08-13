from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pickle
import time
import elem_getters as eg
import utils
import argparse
import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
import sys

def scrape_comments(driver, url):
    """ Scrapes the comments of a given post url
    :param driver: selenium webdriver
    :param url: url post
    :param logger: logging session
    :return: a list that contains the scrappend comment data
    """
    driver.get(url)
    elements_button = [el for el in driver.find_elements_by_class_name("qc-cmp-button") if el.text == "ACEPTO"]
    if len(elements_button) > 0:
        cookie_button = elements_button[0]
        cookie_button.click()
    thread = driver.find_element_by_id("disqus_thread")
    iframes = thread.find_elements_by_css_selector("*")
    # actual comments url
    url_comments = iframes[1].get_attribute("src")
    driver.get(url_comments)
    time.sleep(0.5)
    # check if there is any load more button, if there is, click it
    utils.click_all_load_more(driver)
    # get all comment-post elements
    #comments_list = driver.find_elements_by_class_name("post")
    comments_list = driver.find_elements_by_xpath("""//*[starts-with(@id, 'post-') and \
                                                     not(../../../*[contains(@class, 'children')])]""")
    comments_list = comments_list[1:]
    logger.debug(" -- has {} parent comments".format(len(comments_list)))
    #print("{} has {} comments".format(url, len(comments_list)))
    scraped_comments = []
    for idx, comment_element in enumerate(comments_list):
        if (idx % 10) == 0:
            logger.debug(' --- Scrapping comment # {}'.format(idx))
        try:
            scraped_comments.append(eg.extract_comment_data(comment_element))
        except:
            logger.error(" - Scraping comment # {} with content {} resulted in error".format(idx, comment_element.text))
            scraped_comments.append({})
    return scraped_comments

if __name__ == "__main__":
    # set up logging
    logger = logging.getLogger('fino-selenium')
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%d-%b-%y %H:%M:%S')
    # add stdout handling
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    logger.addHandler(ch)
    # add file handling
    fh = RotatingFileHandler('./logs/log.txt', maxBytes=(1048576 * 5), backupCount=7)
    fh.setFormatter(format)
    logger.addHandler(fh)

    logger.debug('Logging session set up')
    # command line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--npages", type=int,
                        help="number of pages to scrape")
    parser.add_argument("-a", "--aws",
                        action="store_true",
                        help="sets up drivers to run in aws")
    args = parser.parse_args()
    # web driver initialization
    fino_url = "https://finofilipino.org/"
    if args.aws:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        #options.add_argument('--no-sandbox')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('window-size=1200x600')
        driver = webdriver.Chrome(chrome_options=options)
        driver_secondary = webdriver.Chrome(chrome_options=options)
    else:
        driver = webdriver.Chrome()
        driver_secondary = webdriver.Chrome()
    driver.get(fino_url)
    # click on cookies button
    try:
        elements_button = [el for el in driver.find_elements_by_class_name("qc-cmp-button") if el.text == "ACEPTO"]
        cookie_button = elements_button[0]
        cookie_button.click()
    except:
        print("Unable to click on accept cookies button")
    # Wait 5 seconds for page to load
    timeout = 5
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "page-numbers")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        driver.quit()
    # either use command line input, or get user input
    if args.npages is not None:
        N_pages_extract = args.npages
    else:
        xpath_npages = """/html/body[@id='fino_theme_clean']/div[@id='page']/main[@class='main']/div[@class='container']\
        /div[@class='row']/div[@class='col-lg-8 col-xs-12']/div[@class='paging group']/a[@class='page-numbers'][3]"""
        n_pages = int(driver.find_element_by_xpath(xpath_npages).text.replace(".", ""))
        print("There are {} pages in finofilipino".format(n_pages))
        N_pages_extract = input("How many pages do you want to extract? (default = {}) ".format(n_pages))
    # check user input
    if N_pages_extract:
        try:
            N_pages_extract = int(N_pages_extract)
        except ValueError:
            print("The input number of pages was not possible to transform to integer")
    else:
        N_pages_extract = n_pages

    time.sleep(5.)
    dict_entries = {}
    for page in range(N_pages_extract):
        logger.debug("Working at page {}".format(page + 1))
        driver.get("{}page/{}/".format(fino_url, page+1))
        entries = driver.find_element_by_id("entries")
        entries_list = entries.find_elements_by_class_name("entry")
        # dictionary that will store all data
        # the url will be the key
        elements_button = [el for el in driver.find_elements_by_class_name("qc-cmp-button") if el.text == "ACEPTO"]
        if len(elements_button) > 0:
            cookie_button = elements_button[0]
            cookie_button.click()

        for entry in entries_list:
            #url extraction
            url = entry.find_element_by_css_selector("a").get_attribute("href")
            logger.debug(" - Scrapping url:  {}".format(url))
            dict_entries[url] = {}
            # title extraction
            title = entry.find_element_by_class_name("entry-title").text
            dict_entries[url]["title"] = title
            # content - TODO review content extraction, quite basic right now
            content = entry.find_element_by_class_name("entry-content").text
            dict_entries[url]["content"] = content
            # tags and number of views
            text_finotags = entry.find_element_by_class_name("entry-virality.fino-tags").text
            nviews, tags, is_trending, is_popular = eg.get_nbviews_tags(text_finotags)
            dict_entries[url]["nviews"] = nviews
            dict_entries[url]["tags"] = tags
            dict_entries[url]["is_trending"] = is_trending
            dict_entries[url]["is_popular"] = is_popular
            # number of comments
            text_comments = entry.find_element_by_class_name("entry-meta.fino-comments").text
            nbcomments = eg.get_nbcomments(text_comments)
            dict_entries[url]["nbcomments"] = nbcomments
            # categories and publish date
            text_cat_publishdate = entry.find_element_by_class_name("entry-meta.fino-category").text
            categories, publish_date = eg.get_cats_pubdate(text_cat_publishdate)
            dict_entries[url]["categories"] = categories
            dict_entries[url]["publish_date"] = publish_date
            # post comments scraping
            scraped_comments = scrape_comments(driver_secondary, url)
            dict_entries[url]["comments"] = scraped_comments

    #capture end execution time and dump data
    end_time = dt.datetime.now().strftime("%Y_%m_%d_%H_%M")
    logger.debug(" - Successful scrapping session")
    pickle.dump(dict_entries, open("./output/dict_entries_n_{}_{}.pkl".format(N_pages_extract, end_time), "wb"))
