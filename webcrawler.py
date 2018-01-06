# -*- coding: utf-8 -*-

import urllib2
from urlparse import urlparse


class URLParser(object):

    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(self.url)

    def get_domain(self):
        """
        Extracted domain from the URL (e.g berlin.de)
        """
        return self.parsed_url.netloc

    def get_prefix(self):
        """
        Basically it will return either HTTP or HTTPS
        """
        return self.parsed_url.scheme

    def get_path(self):
        """
        Return path from the URL (e.g /blog/post/die-welt/)
        """
        return self.parsed_url.path


class WebCrawler(object):
    """
    URL of the website
    Maximum recursion depth allowed (defaulted to 3)
    """

    def __init__(self, url, max_depth=3):
        self.url = url
        self.max_depth = max_depth
        self.website_content = {}

    def get_url_info(self):
        """
        Extract information from the parsed URL
        """
        self.parsed_url = URLParser(self.url)
        self.domain = self.parsed_url.get_domain()
        self.prefix = self.parsed_url.get_prefix()
        self.root_path = self.parsed_url.get_path()

    def crawl_it(self):
        """
        Set URL metadata
        Initialize crawling execution
        """
        self.get_url_info()
        self.perform_crawling([self.root_path], self.max_depth)

    def perform_crawling(self, urls_set, max_depth):
        pass
