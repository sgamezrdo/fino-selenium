from datetime import datetime as dt
from datetime import timedelta

# Dictionary mapping raw text to the time dimension that
# represents
dict_time_dims = {"SEGUNDOS": timedelta(seconds=1),
                  "MIN": timedelta(minutes=1),
                  "MINUTOS": timedelta(minutes=1),
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
    """ transforms the list of string to the publish date
    :param date_elemns: list of strings (containing time since publish date, e.g. 5 minutos)
    :param now: datetime containing the execution time as reference
    :return: datetime with the publish date
    """
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

def get_comment_pubdate(text_compubdate):
    """ Handles the comment publish date
    :param text_compubdate
    :return: comment publish date
    """
    #firt two chars are not useful
    text_compubdate = text_compubdate[2:].upper()
    date_elems = text_compubdate.split(" ")
    now = dt.now()
    pub_date = get_publish_date(date_elems[1:], now)
    return pub_date


def extract_comment_data(comment_element):
    """ Each comment has the following elements:
        - post-byline: contains the name of the user that made the comment
        - post-meta: contains the time that the comment was made
        - post-body-inner: contains the actual comment
        - children: answers (which are also comments) given to the main comment under study
    :param comment_element:
    :param dict_entries:
    :return: scrapped comment data of a given comment element
    """
    dict_comment = {}
    # extract data out of the comment element
    body_element = comment_element.find_element_by_class_name("post-body")
    comment_author = body_element.find_element_by_class_name("post-byline").text
    comment_post_time = body_element.find_element_by_class_name("post-meta").text
    # TODO if content are gifs / links / videos the field is empty
    comment_body = body_element.find_element_by_class_name("post-body-inner").text
    dict_comment["author"] = comment_author
    # TODO parse comment post date
    dict_comment["post_time"] = comment_post_time
    dict_comment["body"] = comment_body
    children = comment_element.find_elements_by_xpath("""*[contains(@class, 'children') and contains(@class, 'post-body')]""")
    dict_comment["children"] = []
    # if there are any children, call extract_comment_data recursively
    if len(children) > 0:
        print("Scrapping {} children".format(len(children)))
        for idx, child in enumerate(children):
            dict_comment["children"].append((idx, extract_comment_data(child)))
    return dict_comment
