#!/usr/bin/python
import sys
from webcrawler import WebCrawler


if __name__ == "__main__":
    website = 'https://pier31.co'
    if len(sys.argv) <= 1:
        print "\nYou didn't enter an address. Defaulting to %s" % website
    else:
        website = sys.argv[1]
        print "\nChoosen address: %s" % website

    web_crawler = WebCrawler(website)
    web_crawler.crawl_it()
