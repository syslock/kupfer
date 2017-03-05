__kupfer_name__ = _("Search the Web")
__kupfer_sources__ = ("OpenSearchSource", )
__kupfer_text_sources__ = ()
__kupfer_actions__ = (
        "SearchFor",
        "SearchWithEngine",
    )
__description__ = _("Search the web with OpenSearch search engines")
__version__ = ""
__author__ = "Thomas Frenzel <syslock@gmx.de>"

import locale
import os
import urllib.request, urllib.parse, urllib.error
import json
import lz4 # FIXME: dependency to non-standard module

from kupfer.objects import Action, Source, Leaf
from kupfer.objects import TextLeaf
from kupfer import utils, config

from kupfer.plugin import firefox # FIXME: import of another plugin


def _noescape_urlencode(items):
    """Assemble an url param string from @items, without
    using any url encoding.
    """
    return "?" + "&".join("%s=%s" % (n,v) for n,v in items)

def _urlencode(word):
    """Urlencode a single string of bytes @word"""
    return urllib.parse.urlencode({"q": word})[2:]

def _do_search_engine(terms, urls, encoding="UTF-8"):
    """Show an url searching for @search_url with @terms"""
    for url in urls:
        if url.type=="application/x-suggestions+json":
            continue
        param_dict = {}
        for param in url.params:
            param_dict[ param["name"] ] = param["value"].replace("{searchTerms}", terms)
        query_url = url.template
        query_string = urllib.parse.urlencode( param_dict )
        if "?" in query_url:
            query_url += "&" + query_string
        else:
            query_url += "?" + query_string
        query_url = query_url.replace("{searchTerms}", _urlencode(terms))
        utils.show_url(query_url)
        break

class SearchWithEngine (Action):
    """TextLeaf -> SearchWithEngine -> SearchEngine"""
    def __init__(self):
        Action.__init__(self, _("Search With..."))

    def activate(self, leaf, iobj):
        urls = iobj.urls
        terms = leaf.object
        _do_search_engine(terms, urls)

    def item_types(self):
        yield TextLeaf

    def requires_object(self):
        return True
    def object_types(self):
        yield SearchEngine

    def object_source(self, for_item=None):
        return OpenSearchSource()

    def get_description(self):
        return _("Search the web with OpenSearch search engines")
    def get_icon_name(self):
        return "edit-find"

class SearchFor (Action):
    """SearchEngine -> SearchFor -> TextLeaf

    This is the opposite action to SearchWithEngine
    """
    def __init__(self):
        Action.__init__(self, _("Search For..."))

    def activate(self, leaf, iobj):
        urls = leaf.urls
        terms = iobj.object
        _do_search_engine(terms, urls)

    def item_types(self):
        yield SearchEngine

    def requires_object(self):
        return True
    def object_types(self):
        yield TextLeaf

    def get_description(self):
        return _("Search the web with OpenSearch search engines")
    def get_icon_name(self):
        return "edit-find"

class SearchURL:
    def __init__( self, url_description ):
        self.template = url_description["template"]
        self.params = url_description["params"]
        self.type = url_description["type"] if "type" in url_description else None

class SearchEngine (Leaf):
    def __init__( self, search_description ):
        name = search_description["_name"]
        self.description = search_description["description"]
        self.urls = [SearchURL(u) for u in search_description["_urls"]]
        super().__init__( self.urls, name )
    def get_description(self):
        return self.description
    def get_icon_name(self):
        return "text-html"

def coroutine(func):
    """Coroutine decorator: Start the coroutine"""
    def startcr(*ar, **kw):
        cr = func(*ar, **kw)
        next(cr)
        return cr
    return startcr

class OpenSearchError (Exception):
    pass

class OpenSearchSource (Source):
    def __init__(self):
        Source.__init__(self, _("Search Engines"))

    def get_items(self):
        # Parse compressed search engine description from Firefox profile directory
        search_json_mozlz4 = firefox.get_firefox_home_file("search.json.mozlz4")
        if not search_json_mozlz4 or not os.path.isfile(search_json_mozlz4):
            raise OpenSearchError("Cannot find: %s" % search_json_mozlz4)
        f_search_json_mozlz4 = open(search_json_mozlz4, "rb")
        if( f_search_json_mozlz4.read(8) != b"mozLz40\0" ):
            raise OpenSearchError("Invalid header found in: %s" % search_json_mozlz4)
        search_json = lz4.decompress( f_search_json_mozlz4.read() )
        f_search_json_mozlz4.close()
        search_description = json.loads( search_json )
        for search_engine_description in search_description["engines"]:
            yield SearchEngine( search_engine_description )

    def should_sort_lexically(self):
        return True

    def provides(self):
        yield SearchEngine

    def get_icon_name(self):
        return "applications-internet"
