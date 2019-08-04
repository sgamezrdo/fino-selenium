from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pickle
import time
import elem_getters as eg
import argparse

def scrape_comments(driver, url):
    driver.get(url)
    #slowscrollDown(driver, 80, 50)
    #driver.get(url)
    timeout = 10
    #try:
    #    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "post-list")))
    #except TimeoutException:
    #    print("Timed out waiting for page to load Comments")
    #    driver.quit()
    thread = driver.find_element_by_id("disqus_thread")
    iframes = thread.find_elements_by_css_selector("*")
    # actual comments url
    url_comments = iframes[1].get_attribute("src")
    # get the comments content
    driver.get(url_comments)
    time.sleep(1.)
    comments_list = driver.find_elements_by_class_name("post")
    #print("{} has {} comments".format(url, len(comments_list)))
    scraped_comments = []
    for comment_element in comments_list:
        scraped_comments.append(eg.extract_comment_data(comment_element))
    return scraped_comments

if __name__ == "__main__":
    # command line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--npages", type=int,
                        help="number of pages to scrape")
    args = parser.parse_args()
    # web driver initialization
    fino_url = "https://finofilipino.org/"
    driver = webdriver.Chrome()
    driver_secondary = webdriver.Chrome()
    driver.get(fino_url)
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

    for page in range(N_pages_extract):
        print("Working at page {}".format(page + 1))
        driver.get("{}page/{}/".format(fino_url, page+1))
        entries = driver.find_element_by_id("entries")
        entries_list = entries.find_elements_by_class_name("entry")
        # dictionary that will store all data
        # the url will be the key
        dict_entries = {}

        for entry in entries_list:
            #url extraction
            url = entry.find_element_by_css_selector("a").get_attribute("href")
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
            scraped_comments = scrape_comments(driver_secondary, url)
            dict_entries[url]["comments"] = scraped_comments

    pickle.dump(dict_entries, open("./output/dict_entries.pkl", "wb"))