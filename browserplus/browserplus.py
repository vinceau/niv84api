"""BrowserPlus is a module which utilises lxml to provide simple methods to
scrape information from the mechanize browser.

Vincent Au (c) 2015
vinceau/browserplus
"""
import logging
from lxml import etree, html
from .gaemechanize import Browser, LinkNotFoundError
from sys import stdout

__version__ = '0.0.1'

_log = logging.getLogger(__name__)
logging.basicConfig(stream=stdout, level=logging.DEBUG)

class BrowserPlus(Browser):
    """BrowserPlus extends the mechanize Browser providing extra functions and
    robot handling by default. It obviously has all the methods of the
    mechanize Browser but it also has the web scraping capabilities of lxml.
    """
    def __init__(self):
        Browser.__init__(self)
        self.set_handle_robots(False)
        self.addheaders = [(
            'Accept',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        )]

    def _tree(self):
        """Return the current page in a form that's actually useful (a HTML
        element).
        """
        return html.fromstring(self.response().read())

    def xpath(self, xpathstring):
        """Call lxml's xpath function on the current page.
        """
        return self._tree().xpath(xpathstring)

    def has(self, msg):
        """This returns true if msg is contained in the browsers current page.
        """
        if self.response() is None:
            return False
        return msg in self.xpath('string()')

    def select_form_by(self, attr, search):
        """Usage: BrowserPlus.select_form_by('id', 'login')
        """
        try:
            formcount = 0
            for frm in self.forms():
                if frm.attrs[attr] == search:
                    break
                formcount += 1
            return self.select_form(nr=formcount)
        except KeyError:
            _log.error('Failed to find form with the %s "%s"', attr, search)
            return False

    def find(self, css):
        """Returns the first occurence of an element matching the css selector
        if it exists and None otherwise
        """
        e = self.find_all(css)
        return e[0] if e else None

    def find_all(self, css):
        """Returns a list of all elements that match the css selector
        """
        return self._tree().cssselect(css)

    def get(self, element, attr, value):
        """Returns the first 'element' tag with 'value' as their attribute
        'attr'. e.g. get('a', 'href', 'http://google.com') will return
        the first <a> tag with a link to Google.
        """
        e = self.get_all(element, attr, value)
        return e[0] if e else None

    def get_all(self, element, attr, value):
        """Returns a list of all 'element' tags with 'value' as their attribute
        'attr'. e.g. get_all('a', 'href', 'http://google.com') will return
        a list of all the <a> tags with links to Google.
        """
        return self.xpath("//%s[@%s='%s']" % (element, attr, value))

    def go(self, text):
        """Follow the link (a href) containing certain text.
        e.g. <a href="http://google.com">Google</a> BrowserPlus.go('Google')
        will open a link to Google.
        """
        try:
            return self.follow_link(text_regex=text)
        except LinkNotFoundError:
            _log.error("Can't find link with text '%s'", text)
            return None

    def show(self, prettify=True):
        """Prints the source of the current page. If prettify is True then it
        will print it prettily and append a newline to the output. Otherwise it
        will just print the raw source of the page.
        """
        if self.response() is not None:
            if prettify:
                print(etree.tostring(self._tree(), pretty_print=True))
            else:
                print(self.response().read())

    def url(self):
        if self.response() is None:
            return None
        return self.response().geturl()

