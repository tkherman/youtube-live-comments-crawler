from selenium import webdriver
import sys
import time

url = sys.argv[1]

driver = webdriver.Chrome()
driver.get(url)
time.sleep(4)

owner = driver.find_element_by_xpath('//yt-formatted-string[@id="owner-name"]').text
title = driver.find_element_by_class_name('title').text
description = driver.find_element_by_xpath("//yt-formatted-string[@id='description']").text
viewers = driver.find_element_by_class_name('view-count').text.split()[0]

likesNdislikes = driver.find_elements_by_xpath('//yt-formatted-string[@id="text"][@class="style-scope ytd-toggle-button-renderer style-text"]')
likes = likesNdislikes[0].text
dislikes = likesNdislikes[1].text

print "Owner: ", owner
print "Title: ", title
print "Description: ", description
print "Viewers: ", viewers
print "Likes: ", likes
print "Dislikes: ", dislikes

driver.close()
