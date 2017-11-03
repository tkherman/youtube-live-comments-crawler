import os
import re
import sys
import time
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



"""
    Create a directory for the link with another directory within it called driver
"""
def setup_directory(name):
    os.mkdir(name)
    os.mkdir(name + "/screenshots")
    return


"""
    Get meta_data such as title, owner, description and store it in meta_data.txt
"""
def collect_meta_data(dir_name, driver):
    
    # Get meta_data
    owner = driver.find_element_by_xpath('//yt-formatted-string[@id="owner-name"]').text
    title = driver.find_element_by_class_name('title').text
    description = driver.find_element_by_xpath("//yt-formatted-string[@id='description']").text
    viewers = driver.find_element_by_class_name('view-count').text.split()[0]
    likesNdislikes = driver.find_elements_by_xpath('//yt-formatted-string[@id="text"][@class="style-scope ytd-toggle-button-renderer style-text"]')
    likes = likesNdislikes[0].text
    dislikes = likesNdislikes[1].text

    # Write meta_data to a text file
    textfile = open(dir_name + "/meta_data.txt", "w")
    textfile.write("Owner:          " + owner.encode('utf-8') + "\n")
    textfile.write("Title:          " + title.encode('utf-8') + "\n")
    textfile.write("Viewers:        " + viewers.encode('utf-8') + "\n")
    textfile.write("Likes:          " + likes.encode('utf-8') + "\n")
    textfile.write("Dislikes:       " + dislikes.encode('utf-8') + "\n")
    textfile.write("Description:    " + "\n")
    textfile.write(description.encode('utf-8') + "\n")


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
    Stream comments and write them to comments.txt
"""
def stream_comments(dir_name, driver):
    
    # Create a file called comments.txt
    textfile = open(dir_name + "/comments.txt", "w")

    # Switch frame and intialize variables for detecting new comments
    driver.switch_to_frame('chatframe')
    currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
    currentSize = len(driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer'))

    # Loop that continuous detect new comments, then write to comments.txt
    while True:
        element = WebDriverWait(driver, 40).until(
            height_has_changed((By.ID, 'item-offset'), currentStyle)
        )
        
        comments = driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer')
        
        lastFew = len(comments) - currentSize
        commentsToPrint = comments[-1*lastFew:]
        
        for comment in commentsToPrint:
            localtime = time.asctime(time.localtime(time.time()))
            print "[", localtime, "]", \
                    comment.find_element_by_id('author-name').text, \
                    ":", comment.find_element_by_id('message').text
            textfile.write("[" + localtime + "] " +\
                    comment.find_element_by_id('author-name').text.encode('utf-8') + \
                    ": " + comment.find_element_by_id('message').text.encode('utf-8') + "\n")

        currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
        currentSize = len(comments)



"""
    Worker function that take screenshots every minute
"""
def screenshot(dir_name, driver):
    
    # While loop that takes a screenshot every minute
    while True:
        driver.save_screenshot(dir_name + "/screenshots/" + str(time.time()) + ".png")
        
        time.sleep(60)

    
"""
    Worker function that gets meta_data and stream comments
"""
def crawl_link(url):
    
    # Start an instance of browser
    driver1 = webdriver.Chrome()
    driver1.get(url)

    # Make sure everything is loaded before beginning
    time.sleep(2)

    # Access title of the stream and set up directory
    title = driver1.find_element_by_class_name('title').text
    
    title = re.sub("/", "-", title)

    setup_directory(title)

    # Create a new thread that take screenshot every minute
    driver2 = webdriver.Chrome()
    driver2.get(url)
    t = threading.Thread(target = screenshot, args=(title, driver2,))
    t.start()
    

    # Collect meta_data and write them to meta_data.txt
    collect_meta_data(title, driver1)

    # Collect comments and write them to comments.txt
    stream_comments(title, driver1)



"""
    Open file containing links, create a thread for each link
"""
if __name__ == "__main__":
    filename = sys.argv[1]

    for link in open(filename, "r"):
        t = threading.Thread(target = crawl_link, args=(link,))
        t.start()
