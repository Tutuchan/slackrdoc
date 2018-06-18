"""
Python class to parse RDocumentation website and retrieve function description
"""

import urllib.request
from xml.etree import ElementTree
from bs4 import BeautifulSoup

class Parser(object):
    """
    Instantiate a Parser object.
    """
    def __init__(self, package, fun):
        self.url = ""
        self.text = ""
        self.package = package
        self.function = fun

    """
    Build the RDocumentation URL
    """
    def build_url(self):
        self.url = "https://www.rdocumentation.org/packages/" + self.package + "/topics/" + self.function

    """
    Retrieve the function description.
    """
    def retrieve_desc(self):
        self.build_url()
        request = urllib.request.Request(self.url)
        result = urllib.request.urlopen(request).read().decode("UTF-8")
        soup = BeautifulSoup(result, 'html.parser').find(class_="topic packageData")
        raw_text = str(soup.select("div > section")[0].select("p")[0]). \
            replace("\n", " "). \
            replace("<code>", "`"). \
            replace("</code>", "`"). \
            strip()

        self.text = ''.join(ElementTree.fromstring(raw_text).itertext())
