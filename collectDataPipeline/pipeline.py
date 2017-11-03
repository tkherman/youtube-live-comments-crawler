import sys
import threading
from collectData import *
from selenium import webdriver

def usage(status):
    print "Usage: ./collectData [keyword] [n] [t]"
    print ""
    print "     - keyword needs to be in quotations"
    print "     - n is the top n links in search result (< 5)"
    print "     - t is the time out in minutes"

    sys.exit(status)


def get_links(keyword, number):

    # Set url
    keyword = keyword.replace(' ', '+')
    url = "https://www.youtube.com/"
    url = url + "results?search_query=" + keyword # search query
    url = url + "&sp=EgJAAVAU" # live stream filter
    
    
    driver = webdriver.Chrome()
    driver.get(url)

    videos = driver.find_elements_by_tag_name('ytd-video-renderer')
    
    # Store links in list
    links = []
    n = 0
    for video in videos:
        thumb = video.find_element_by_id('thumbnail')
        link = thumb.get_attribute('href').encode('utf-8')
        links.append(link)

        n = n + 1
        if n == number:
            break

    driver.close()
    
    return links


if __name__ == "__main__":
    
    # Parse command line argument
    if len(sys.argv) != 4:
        usage(1)

    keyword = sys.argv[1]
    number = int(sys.argv[2])
    timeout = int(sys.argv[3])
    
    if number < 1 or number > 4:
        usage(1)

    links = list()
    links = get_links(keyword, number)

    # Start threads to crawl data
    for link in links:
        print "starting thread"
        t = threading.Thread(target = crawl_link, args=(link,))
        t.setDaemon(True)
        t.start()

    time.sleep(timeout*60)
    sys.exit(0)
