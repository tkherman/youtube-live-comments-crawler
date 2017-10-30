from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import threading

"""
    Customize class that works with WebDriverWait to detect new comments
"""
class height_has_changed(object):
    def __init__(self, locator, style_string):
        self.locator = locator
        self.style_string = style_string

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if element.get_attribute('style') != self.style_string:
            return element
        else:
            return False
"""
    Thread worker that collects and streams live comments
        all variables are declared to be local so new instances
"""
def streamingWorker(url):

    driver = threading.local() # convert all variables to local
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(4)
    
    title = threading.local()
    title = driver.find_element_by_class_name('title').text

    driver.switch_to_frame('chatframe')
    currentStyle = threading.local()
    currentSize = threading.local()
    currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
    currentSize = len(driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer'))


    while True:
        element = threading.local()
        element = WebDriverWait(driver, 40).until(
            height_has_changed((By.ID, 'item-offset'), currentStyle)
        )
        
        comments = threading.local()
        comments = driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer')
        
        lastFew = threading.local()
        lastFew = len(comments) - currentSize
        commentsToPrint = threading.local()
        commentsToPrint = comments[-1*lastFew:]
        
        for comment in commentsToPrint:
            localtime = threading.local()
            localtime = time.asctime(time.localtime(time.time()))
            print "[", localtime, "]", \
                    comment.find_element_by_id('author-name').text, \
                    ":", comment.find_element_by_id('message').text

        currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
        currentSize = len(comments)

"""
    Create two threads that streams the data
"""
if __name__ == "__main__":
    t1 = threading.Thread(target = streamingWorker, args=(sys.argv[1],))
    t2 = threading.Thread(target = streamingWorker, args=(sys.argv[2],))

    t1.start()
    t2.start()
