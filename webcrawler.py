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


class AnchorHTMLParser(HTMLParser):
    """
    Responsible for parsing anchor tags (<a>) and grab its attributes
    On this particular case we are interested on href attribute
    https://docs.python.org/2/library/htmlparser.html#HTMLParser.HTMLParser.handle_starttag
    """

    tag = {'name': 'a', 'attribute': 'href'}
    links = set()

    def handle_starttag(self, tag, attrs):
        if tag == self.tag['name']:
            link = dict(attrs).get(self.tag.get('attribute'))
            if link:
                self.links.add(link)

    def get_links(self):
        return self.links


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
        """
        Navigate through urls (GET info, SET info, search for links, add new links)
        Respect some constraints (visited page, max depth recursion)
        """
        # create a set instead of list
        # because we want unique values
        new_urls_set = set()
        # infinte loop protection
        if max_depth:
            # make sure we just hit the url once
            gen = (url for url in urls_set if url not in self.website_content)
            for url in gen:
                # get response from url
                response = self.get(url)
                # set url info
                self.set(url, response)
                # get all links inside the response
                links_from_response = self.get_links_from_response(response)
                # put new_urls_set and links_from_response together
                new_urls_set = new_urls_set.union(links_from_response)
            # recursion call (making sure max_depth gets decremented)
            self.perform_crawling(new_urls_set, max_depth-1)

    def get_links_from_response(response):
        """
        Extract links from the response using a parser
        https://docs.python.org/2/library/htmlparser.html#HTMLParser.HTMLParser.feed
        """
        anchor_parser = AnchorHTMLParser()
        anchor_parser.feed(response)
        links = set()
        for link in anchor_parser.get_links():
            links.add(link)
        return links

    def set(self, current_url, response):
        """
        SET URL information
        """
        self.website_content[current_url] = response

    def get(self, current_url):
        """
        Get URL via HTTP
        """
        response = self.http_get_request(current_url)
        return response

    def http_get_request(self, url):
        """
        HTTP Request using urllib2
        """
        try:
            # This packages the request (it doesn't make it)
            request = urllib2.Request(url)
            # Sends the request and catches the response
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8', 'ignore')
        except (urllib2.HTTPError, urllib2.URLError), exc:
            print 'Something went wrong for this URL: [%s] - %s' % (url, exc)
            return str()
