import sys

from selenium import webdriver

def get_links(keyword, number):
    
    # Set url
    keyword = keyword.replace(' ', '+')
    url = "https://www.youtube.com/"
    url = url + "results?search_query=" + keyword # search query
    url = url + "&sp=EgJAAVAU" # live stream filter
    
    
    driver = webdriver.Chrome()
    driver.get(url)

    videos = driver.find_elements_by_tag_name('ytd-video-renderer')
    
    # Get all links
    n = 0
    linkfile = open('links.txt', 'w')
    for video in videos:
        thumb = video.find_element_by_id('thumbnail')
        link = thumb.get_attribute('href').encode('utf-8')
        linkfile.write(link + "\n")
        
        n = n + 1
        if n == number:
            break

    driver.close()

    


if __name__ == "__main__":
    
    # Get command line argument
    keyword = sys.argv[1]
    number = int(sys.argv[2])

    # Check if number is valid
    if number < 1 or number > 10:
        print "Please enter a number between 1-10"
        sys.exit(1)

    get_links(keyword, number)
