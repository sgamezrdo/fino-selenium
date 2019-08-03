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
