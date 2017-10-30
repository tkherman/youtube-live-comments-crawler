from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys


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


url = sys.argv[1]

driver = webdriver.Chrome()
driver.get(url)
time.sleep(4)

driver.switch_to_frame('chatframe')
currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
currentSize = len(driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer'))


while True:
    element = WebDriverWait(driver, 40).until(
        height_has_changed((By.ID, 'item-offset'), currentStyle)
    )
    
    comments = driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer')
    
    lastFew = len(comments) - currentSize
    commentsToPrint = comments[-1*lastFew:]
    
    for comment in commentsToPrint:
        localtime = time.asctime(time.localtime(time.time()))
        print "[",localtime, "]", \
                comment.find_element_by_id('author-name').text, \
                ":", comment.find_element_by_id('message').text

    currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
    currentSize = len(comments)
