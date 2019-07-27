from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pickle

def get_nbviews_tags(text_tags):
    """ Extract nb of views and tags from the fino-tags class
    :param text_finotags: text representation of fino-tags
    :return: number of views, list with tags
    """
    txt_split = text_tags.split("\n")
    tags = txt_split[1:]
    nb_views = int(txt_split[0].replace(" VIEWS", ""))
    return nb_views, tags

def get_nbcomments(text_comments):
    """ Extract nb comments
    :param text_comments: text representation of fino-comments
    :return: number of comments
    """
    txt_nb = text_comments.replace(" COMENTARIOS", "")
    if txt_nb == "NO HAY":
        return 0
    else:
        return int(txt_nb)

def get_cats_pubdate(text_cat_publishdate):
    """ Handles the category and publish date text blob
    :param text_cat_publishdate:
    :return:
    """
    if "SIN CATEGORÍA" in text_cat_publishdate:
        cats = []
    else:
        txt_split = text_cat_publishdate.split(", ")
        cats = txt_split[:-1]
        txt_split_lastelem = txt_split[-1].split(" ")
        cats.append(txt_split_lastelem[0])
        #txt_split_lastelem = txt_split_lastelem[1:]
    return cats

fino_url = "https://finofilipino.org/"
driver = webdriver.Chrome()
driver.get(fino_url)

# Wait 5 seconds for page to load
timeout = 5
try:
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "page-numbers")))
except TimeoutException:
    print("Timed out waiting for page to load")
    driver.quit()

xpath_npages = """/html/body[@id='fino_theme_clean']/div[@id='page']/main[@class='main']/div[@class='container']\
/div[@class='row']/div[@class='col-lg-8 col-xs-12']/div[@class='paging group']/a[@class='page-numbers'][3]"""

n_pages = int(driver.find_element_by_xpath(xpath_npages).text.replace(".", ""))
print("There are {} pages in finofilipino".format(n_pages))


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
    # content - TODO review, quite basic right now
    content = entry.find_element_by_class_name("entry-content").text
    dict_entries[url]["content"] = content
    # tags and number of views
    text_finotags = entry.find_element_by_class_name("entry-virality.fino-tags").text
    nviews, tags = get_nbviews_tags(text_finotags)
    dict_entries[url]["nviews"] = nviews
    dict_entries[url]["tags"] = tags
    # number of comments
    text_comments = entry.find_element_by_class_name("entry-meta.fino-comments").text
    nbcomments = get_nbcomments(text_comments)
    dict_entries[url]["nbcomments"] = nbcomments
    # categories and publish date
    text_cat_publishdate = entry.find_element_by_class_name("entry-meta.fino-category").text
    categories = get_cats_pubdate(text_cat_publishdate)
    # TODO parse publish date
    dict_entries[url]["categories"] = categories

pickle.dump(dict_entries, open("./output/dict_entries.pkl", "wb"))