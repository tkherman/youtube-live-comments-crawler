import os
import re
import sys
import time
import threading
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



"""
    Create a directory for the link with another directory within it called driver
"""
def setup_directory(name):
    try:
        os.mkdir(name)
        os.mkdir(name + "/screenshots")
    except OSError:
        pass

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
def stream_comments(dir_name, driver, shutdown):
    # Set initial timer
    last_scnshot = time.time()

    # Create a file called comments.txt
    textfile = open(dir_name + "/comments.txt", "w")

    # Switch frame and intialize variables for detecting new comments
    driver.switch_to_frame('chatframe')
    try:
        currentStyle = driver.find_element_by_id('item-offset').get_attribute('style')
    except NoSuchElementException:
        print(driver.current_url, "has no live comments")
        return
    currentSize = len(driver.find_elements_by_tag_name('yt-live-chat-text-message-renderer'))

    # Loop that continuous detect new comments, then write to comments.txt
    while True:
        element = WebDriverWait(driver, 40).until(
            height_has_changed((By.ID, 'item-offset'), currentStyle)
        )

        try:
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
        except NoSuchElementException:
            print(driver.current_url, "shuts down...")
            return

        # Check flags to see if it's time to shut down
        if shutdown():
            break

        if time.time() - last_scnshot > 60:
            last_scnshot = time.time()
            driver.save_screenshot(dir_name + "/screenshots/" + str(time.time()) + ".png")



"""
    Worker function that gets meta_data and stream comments
"""
def crawl_link(url, shutdown):

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')

    # Start an instance of browser
    #driver1 = webdriver.Chrome(chrome_options=options)
    driver1 = webdriver.Chrome()
    driver1.get(url)

    # Make sure everything is loaded before beginning
    time.sleep(2)

    # Access title of the stream and set up directory
    try:
        title = driver1.find_element_by_class_name('title').text
    except NoSuchElementException:
        print(driver1.current_url, "shuts down...")
        return

    title = re.sub("/", "-", title)

    setup_directory(title)

    # Collect meta_data and write them to meta_data.txt
    try:
        collect_meta_data(title, driver1)
    except NoSuchElementException:
        print(driver1.current_url, "shuts down...")
        return

    # Collect comments and write them to comments.txt
    print("Starting comments streaming")
    stream_comments(title, driver1, shutdown)

    driver1.close()



"""
    Open file containing links, create a thread for each link
"""
if __name__ == "__main__":
    filename = sys.argv[1]

    for link in open(filename, "r"):
        t = threading.Thread(target = crawl_link, args=(link,))
        t.start()
