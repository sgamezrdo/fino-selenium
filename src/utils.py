import time

def scrollDown(driver, value):
    driver.execute_script("window.scrollBy(0,"+str(value)+")")

def slowscrollDown(driver, steps, value_step):
    for i in range(steps):
        time.sleep(0.1)
        scrollDown(driver, value_step)

def show_tags(elem, suff='-'):
    print(" {} {}".format(suff, elem.tag_name))
    #for sub_elem in elem.find_elements_by_css_selector("*"):
    for sub_elem in elem.find_elements_by_xpath(".//*"):
        show_tags(sub_elem, suff + "-")

def click_all_load_more(driver):
    """ If there is any "load more comments" button in the page, click it
    :param driver: selenium.webdriver
    :return Nothing:
    """
    load_more_elems = driver.find_elements_by_class_name("btn.load-more__button")
    while len(load_more_elems) > 0:
        elem_load_more = load_more_elems[0]
        try:
            elem_load_more.click()
        except:
            return
        time.sleep(2.5)
        load_more_elems = driver.find_elements_by_class_name("btn.load-more__button")
    return
