#!/usr/bin/python
from webcrawler import WebCrawler

if __name__ == "__main__":
    web_crawler = WebCrawler('https://pier31.co')
    web_crawler.crawl_it()
