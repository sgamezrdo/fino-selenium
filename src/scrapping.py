from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pickle
from datetime import datetime as dt
from datetime import timedelta

dict_time_dims = {"SEGUNDOS": timedelta(seconds=1),
                  "MIN": timedelta(minutes=1),
                  "HORA": timedelta(hours=1),
                  "HORAS": timedelta(hours=1),
                  "DÍA": timedelta(days=1),
                  "DÍAS": timedelta(days=1),
                  "SEMANAS": timedelta(weeks=1)}

def get_nbviews_tags(text_tags):
    """ Extract nb of views, tags from the fino-tags class and is trending flag
    :param text_finotags: text representation of fino-tags
    :return: number of views, list with tags, is trending flat
    """
    is_trending = False
    is_popular = False
    if "THIS POST IS TRENDING" in text_tags:
        is_trending = True
        text_tags = text_tags.replace("THIS POST IS TRENDING.\n", "")
    if "THIS POST IS POPULAR" in text_tags:
        is_popular = True
        text_tags = text_tags.replace("THIS POST IS POPULAR.\n", "")
    txt_split = text_tags.split("\n")
    tags = txt_split[1:]
    txt_clean = txt_split[0].replace(" VIEWS", "").replace(".", "")
    nb_views = int(txt_clean)
    return nb_views, tags, is_trending, is_popular

def get_nbcomments(text_comments):
    """ Extract nb comments
    :param text_comments: text representation of fino-comments
    :return: number of comments
    """
    txt_nb = text_comments.replace(" COMENTARIOS", "").replace("COMENTARIOS", "")
    txt_nb = txt_nb.replace("COMENTARIO", "")
    if (txt_nb == "NO HAY") or (txt_nb == ""):
        return 0
    else:
        return int(txt_nb)

def get_publish_date(date_elemns, now):
    if date_elemns[1] in dict_time_dims.keys():
        time_dim = dict_time_dims[date_elemns[1]]
        return now - int(date_elemns[0]) * time_dim
    else:
    # TODO custom parsing if needed
        print ("Need to develop custom parsing for: {}".format(date_elemns))
        return now

def get_cats_pubdate(text_cat_publishdate):
    """ Handles the category and publish date text blob
    :param text_cat_publishdate:
    :return: cats, publish date
    """
    if text_cat_publishdate.startswith("SIN CATEGORÍA"):
        cats = []
        date_elems = text_cat_publishdate.replace("SIN CATEGORÍA ", "").split(" ")
    else:
        text_cat_publishdate = text_cat_publishdate.replace(" SIN CATEGORÍA", " SIN_CATEGORÍA")
        txt_split = text_cat_publishdate.split(", ")
        cats = txt_split[:-1]
        txt_split_lastelem = txt_split[-1].split(" ")
        cats.append(txt_split_lastelem[0])
        date_elems = txt_split_lastelem[1:][:-1]
        #txt_split_lastelem = txt_split_lastelem[1:]
    now = dt.now()
    pub_date = get_publish_date(date_elems, now)
    return cats, pub_date

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

N_pages_extract = input("How many pages do you want to extract? (default = {}) ".format(n_pages))

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
        # content - TODO review, quite basic right now
        content = entry.find_element_by_class_name("entry-content").text
        dict_entries[url]["content"] = content
        # tags and number of views
        text_finotags = entry.find_element_by_class_name("entry-virality.fino-tags").text
        nviews, tags, is_trending, is_popular = get_nbviews_tags(text_finotags)
        dict_entries[url]["nviews"] = nviews
        dict_entries[url]["tags"] = tags
        dict_entries[url]["is_trending"] = is_trending
        dict_entries[url]["is_popular"] = is_popular
        # number of comments
        text_comments = entry.find_element_by_class_name("entry-meta.fino-comments").text
        nbcomments = get_nbcomments(text_comments)
        dict_entries[url]["nbcomments"] = nbcomments
        # categories and publish date
        text_cat_publishdate = entry.find_element_by_class_name("entry-meta.fino-category").text
        categories, publish_date = get_cats_pubdate(text_cat_publishdate)
        dict_entries[url]["categories"] = categories
        dict_entries[url]["publish_date"] = publish_date

pickle.dump(dict_entries, open("./output/dict_entries.pkl", "wb"))