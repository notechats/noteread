import datetime
import xml.dom.minidom
import xml.sax.saxutils
from io import BytesIO
from typing import List

from noteread.rss.element import *


class RSSItem(Element):
    """Publish an RSS Item"""
    element_attrs = {}

    def __init__(self,
                 title=None,
                 link=None,
                 description=None,
                 author=None,
                 categories=None,  # list of string or Category
                 comments=None,
                 enclosure: Enclosure = None,
                 guid=None,  # a unique string
                 pub_date=None,  # a datetime
                 source: Source = None,
                 ):
        super(RSSItem, self).__init__()
        if title is None and description is None:
            raise TypeError("must define at least one of 'title' or 'description'")
        self.title = title
        self.link = link
        self.description = description
        self.author = author
        if categories is None:
            categories = []
        self.categories = categories
        self.comments = comments
        self.enclosure = enclosure
        self.guid = guid
        self.pubDate = pub_date
        self.source = source

    def publish(self, handler=None):
        super(RSSItem, self).publish(handler)
        handler.startElement("item", self.element_attrs)
        self.write_opt_element("title", self.title)
        self.write_opt_element("link", self.link)
        self.publish_extensions(handler)
        self.write_opt_element("description", self.description)
        self.write_opt_element("author", self.author)

        for category in self.categories:
            if isinstance(category, str):
                category = Category(category)
            category.publish(handler)

        self.write_opt_element("comments", self.comments)
        if self.enclosure is not None:
            self.enclosure.publish(handler)
        self.write_opt_element("guid", self.guid)

        pub_date = self.pubDate
        if isinstance(pub_date, datetime.datetime):
            pub_date = DateElement("pubDate", pub_date)
        self.write_opt_element("pubDate", pub_date)

        if self.source is not None:
            self.source.publish(handler)

        handler.endElement("item")

    def publish_extensions(self, handler):
        pass


class BaseRss(Element):
    def __init__(self, *args, **kwargs):
        super(BaseRss, self).__init__()

    def write_xml_to_io(self, outfile, encoding="UTF-8"):
        handler = xml.sax.saxutils.XMLGenerator(outfile, encoding)
        self.handler = handler
        handler.startDocument()
        self.publish(handler)
        handler.endDocument()

    def write_xml_to_str(self, encoding="UTF-8"):
        f = BytesIO()
        self.write_xml_to_io(f, encoding)
        return xml.dom.minidom.parse(BytesIO(f.getvalue())).toprettyxml()

    def write_xml_to_file(self, path, encoding="UTF-8"):
        # self.write_xml_to_io(open(path, 'w'), encoding)
        with open(path, 'w') as f:
            f.write(self.write_xml_to_str(encoding))


class RssV2(BaseRss):
    rss_attrs = {"version": "2.0"}
    element_attrs = {}

    def __init__(self,
                 title,
                 link,
                 description,
                 language="zh-cn",
                 copy_right=None,
                 managing_editor=None,
                 web_master=None,
                 pub_date=None,  # a datetime, *in* *GMT*
                 last_build_date=None,  # a datetime

                 categories=None,  # list of strings or Category
                 generator="",
                 docs="",
                 cloud: Cloud = None,
                 ttl=None,  # integer number of minutes

                 image: Image = None,
                 rating=None,  # a string; I don't know how it's used
                 text_input: TextInput = None,
                 skip_hours=None,  # a SkipHours with a list of integers
                 skip_days=None,  # a SkipDays with a list of strings
                 item_list: List[RSSItem] = None, ):
        super(RssV2, self).__init__()
        self.title = title
        self.link = link
        self.description = description
        self.language = language
        self.copyright = copy_right
        self.managingEditor = managing_editor

        self.webMaster = web_master
        self.pubDate = pub_date
        self.lastBuildDate = last_build_date

        if categories is None:
            categories = []
        self.categories = categories
        self.generator = generator
        self.docs = docs
        self.cloud = cloud
        self.ttl = ttl
        self.image = image
        self.rating = rating
        self.textInput = text_input
        self.skipHours = skip_hours
        self.skipDays = skip_days

        if item_list is None:
            item_list = []
        self.item_list = item_list

    def publish(self, handler=None):
        super(RssV2, self).publish(handler)
        handler.startElement("rss", self.rss_attrs)
        handler.startElement("channel", self.element_attrs)
        self.write_element("title", self.title)
        self.write_element("link", self.link)
        self.write_element("description", self.description)

        self.publish_extensions(handler)

        self.write_opt_element("language", self.language)
        self.write_opt_element("copyright", self.copyright)
        self.write_opt_element("managingEditor", self.managingEditor)
        self.write_opt_element("webMaster", self.webMaster)

        pub_date = self.pubDate
        if isinstance(pub_date, datetime.datetime):
            pub_date = DateElement("pubDate", pub_date)
        self.write_opt_element("pubDate", pub_date)

        last_build_date = self.lastBuildDate
        if isinstance(last_build_date, datetime.datetime):
            last_build_date = DateElement("lastBuildDate", last_build_date)
        self.write_opt_element("lastBuildDate", last_build_date)

        for category in self.categories:
            if isinstance(category, str):
                category = Category(category)
            category.publish(handler)

        self.write_opt_element("generator", self.generator)
        self.write_opt_element("docs", self.docs)

        if self.cloud is not None:
            self.cloud.publish(handler)

        ttl = self.ttl
        if isinstance(self.ttl, int):
            ttl = IntElement("ttl", ttl)
        self.write_opt_element("ttl", ttl)

        if self.image is not None:
            self.image.publish(handler)

        self.write_opt_element("rating", self.rating)
        if self.textInput is not None:
            self.textInput.publish(handler)
        if self.skipHours is not None:
            self.skipHours.publish(handler)
        if self.skipDays is not None:
            self.skipDays.publish(handler)

        for item in self.item_list:
            item.publish(handler)

        handler.endElement("channel")
        handler.endElement("rss")

    def publish_extensions(self, handler):
        # Derived classes can hook into this to insert
        # output after the three required fields.
        pass
