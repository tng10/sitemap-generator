# -*- coding: utf-8 -*-
import ssl
import urllib2
from parsers import AnchorHTMLParser, URLParser
from sitemap import SiteMapXML


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

    def is_argument_valid(self):
        """
        Verify valid URL
        """
        parsed_url = URLParser(self.url)
        test_request, error = self.test_http_get_request(self.url)
        if not parsed_url.get_domain() or not test_request:
            print error
            return False
        return True

    def crawl_it(self):
        """
        Set URL metadata
        Initialize crawling execution
        Generate XML
        """
        if not self.is_argument_valid():
            raise Exception('%s is not a valid URL' % self.url)
        self.get_url_info()
        self.perform_crawling([self.root_path], self.max_depth)

        sitemap_xml = SiteMapXML(self.website_content, self.prefix, self.domain)
        sitemap_xml.generate()

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
                response, lastmod = self.get(url)
                # set url info
                self.set(url, response, lastmod)
                # get all links inside the response
                links_from_response = self.get_links_from_response(response)
                # put new_urls_set and links_from_response together
                new_urls_set = new_urls_set.union(links_from_response)
            # recursion call (making sure max_depth gets decremented)
            self.perform_crawling(new_urls_set, max_depth-1)

    def get_links_from_response(self, response):
        """
        Extract links from the response using a parser
        https://docs.python.org/2/library/htmlparser.html#HTMLParser.HTMLParser.feed
        """
        anchor_parser = AnchorHTMLParser()
        anchor_parser.feed(response)
        links = set()
        for link in anchor_parser.get_links():
            is_valid = self.is_this_link_valid(link)
            if is_valid:
                links.add(link)
        return links

    def is_this_link_valid(self, link):
        if not isinstance(link, (str, unicode)):
            return False
        if link.startswith('/') or link.startswith(self.domain) or link.startswith('http' + self.domain):
            return True
        return False

    def set(self, current_url, response, lastmod):
        """
        SET URL information
        """
        # print 'Setting URL: ' + current_url
        self.website_content[current_url] = {'response': response, 'lastmod': lastmod}

    def get(self, current_url):
        """
        Get URL via HTTP
        """
        print 'Fetching URL: ' + current_url
        response_raw, lastmod = self.http_get_request(current_url)
        return (response_raw, lastmod)

    def http_get_request(self, url):
        """
        HTTP Request using urllib2
        """
        try:
            # Check url contains the domain already
            if not self.domain in url:
                complete_url = "%s://%s%s" % (self.prefix, self.domain, url)
            else:
                complete_url = url
            # This packages the request (it doesn't make it)
            request = urllib2.Request(complete_url)
            # Sends the request and catches the response
            response = urllib2.urlopen(request)
            response_raw = response.read().decode('utf-8', 'ignore')
            lastmod = response.headers.dict.get('last-modified') or response.headers.dict.get('date')
        except (urllib2.HTTPError, urllib2.URLError, ssl.CertificateError, ValueError), exc:
            print 'Something went wrong for this URL: [%s] - %s' % (url, exc)
            response_raw = str()
            lastmod = None

        return (response_raw, lastmod)

    def test_http_get_request(self, url):
        """
        Test HTTP Request using urllib2 (given url)
        """
        try:
            # This packages the request (it doesn't make it)
            request = urllib2.Request(url)
            # Sends the request and catches the response
            response = urllib2.urlopen(request)
        except Exception as e:
            return (False, e)
        return (True, None)
