"""
NIV84 API
"""
import os
import jinja2
import webapp2
from urllib import quote_plus
from browserplus import BrowserPlus, URLError
from collections import OrderedDict
import json

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

bp = BrowserPlus()

def render(name, values={}):
    return JINJA_ENV.get_template('templates/' + name).render(values)


def load(passage):
    passage = quote_plus(passage)
    try:
        data = {
            'passages': [],
        }
        url = 'http://www.biblestudytools.com/search/?q=' + passage
        bp.open(url)
        search = bp.find_all('div.scripture')
        if len(search) == 0:
            return {}
        csssearch = '.verse .verse-number'
        title = bp.find('div.section-title h1').text
        for scripture in search:
            passage = OrderedDict()
            if len(search) > 1:
                title = scripture.getparent().cssselect('h2 a')[0].text
                csssearch = '.verse strong'
            for b in scripture.cssselect('sup a, div.panel'):
                b.getparent().remove(b)
            verses = OrderedDict()
            for v in scripture.cssselect(csssearch):
                #get the verse number
                num = ''.join(v.itertext()).strip()
                #get the actual verse content
                if v.getnext() is not None:
                    verses[num] = ''.join(v.getnext().itertext()).strip()
            passage['title'] = title
            passage['verses'] = verses
            data['passages'].append(passage)
        return data
    except URLError:
        return {}

class ApiPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json; charset=utf-8',
        }
        passage = self.request.get('passage')
        data = load(passage)
        if not data:
            self.response.set_status(404, 'Couldn\'t find %s' % passage)
        print(data)
        self.response.write(json.dumps(data))

    def options(self):
        self.response.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
            'Access-Control-Allow-Methods': 'GET',
        }

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(render('main.html'))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'/api/?', ApiPage),
], debug=True)
