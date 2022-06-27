# Wed, 12 Jan 2022 17:00:00 +0800
def _format_date(dt):
    """convert a datetime into an RFC 822 formatted date

    Input date must be in GMT.
    """
    # Looks like:
    #   Sat, 07 Sep 2002 00:00:01 GMT
    # Can't use strftime because that's locale dependent
    #
    # Isn't there a standard way to do this for Python?  The
    # rfc822 and email.Utils modules assume a timestamp.  The
    # following is based on the rfc822 module.
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
        dt.day,
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month - 1],
        dt.year, dt.hour, dt.minute, dt.second)


class Element:
    def __init__(self, *args, **kwargs):
        self.handler = None

    def publish(self, handler=None):
        self.handler = handler

    def write_element(self, name: str, value, d=None):
        d = d or {}
        if isinstance(value, str) or value is None:
            self.handler.startElement(name, d)
            if value is not None:
                self.handler.characters(value)
            self.handler.endElement(name)
        else:
            value.publish(self.handler)

    def write_opt_element(self, name: str, obj):
        if obj is None:
            return
        self.write_element(name, obj)


class IntElement(Element):
    element_attrs = {}

    def __init__(self, name, val, *args, **kwargs):
        super(IntElement, self).__init__(*args, **kwargs)
        self.name = name
        self.val = val

    def publish(self, handler=None):
        super(IntElement, self).publish(handler)
        self.handler.startElement(self.name, self.element_attrs)
        self.handler.characters(str(self.val))
        self.handler.endElement(self.name)


class DateElement(Element):
    def __init__(self, name, dt, date_format="%a, %d %b %Y %H:%M:%S +0800", *args, **kwargs):
        super(DateElement, self).__init__(*args, **kwargs)

        self.name = name
        self.dt = dt
        self.date_format = date_format

    def publish(self, handler=None):
        super(DateElement, self).publish(handler)
        self.write_element(self.name, self.dt.strftime(self.date_format))


class Category(Element):
    def __init__(self, category, domain=None, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self.category = category
        self.domain = domain

    def publish(self, handler=None):
        super(Category, self).publish(handler)
        d = {}
        if self.domain is not None:
            d["domain"] = self.domain
        self.write_element("category", self.category, d)


class Cloud(Element):
    def __init__(self, domain, port, path, register_procedure, protocol, *args, **kwargs):
        super(Cloud, self).__init__(*args, **kwargs)
        self.domain = domain
        self.port = port
        self.path = path
        self.registerProcedure = register_procedure
        self.protocol = protocol

    def publish(self, handler=None):
        super(Cloud, self).publish(handler)
        self.write_element("cloud", None, {
            "domain": self.domain,
            "port": str(self.port),
            "path": self.path,
            "registerProcedure": self.registerProcedure,
            "protocol": self.protocol})


class Image(Element):
    """Publish a channel Image"""
    element_attrs = {}

    def __init__(self, url, title, link, width=None, height=None, description=None, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self.url = url
        self.title = title
        self.link = link
        self.width = width
        self.height = height
        self.description = description

    def publish(self, handler=None):
        super(Image, self).publish(handler)
        handler.startElement("image", self.element_attrs)

        self.write_element("url", self.url)
        self.write_element("title", self.title)
        self.write_element("link", self.link)

        width = self.width
        if isinstance(width, int):
            width = IntElement("width", width)
        self.write_opt_element("width", width)

        height = self.height
        if isinstance(height, int):
            height = IntElement("height", height)
        self.write_opt_element("height", height)

        self.write_opt_element("description", self.description)

        handler.endElement("image")


class Guid(Element):
    def __init__(self, guid, is_perma_link=1, *args, **kwargs):
        super(Guid, self).__init__(*args, **kwargs)
        self.guid = guid
        self.isPermaLink = is_perma_link

    def publish(self, handler=None):
        super(Guid, self).publish(handler)
        d = {}
        if self.isPermaLink:
            d["isPermaLink"] = "true"
        else:
            d["isPermaLink"] = "false"
        self.write_element("guid", self.guid, d)


class TextInput(Element):
    element_attrs = {}

    def __init__(self, title, description, name, link, *args, **kwargs):
        super(TextInput, self).__init__(*args, **kwargs)
        self.title = title
        self.description = description
        self.name = name
        self.link = link

    def publish(self, handler=None):
        super(TextInput, self).publish(handler)
        handler.startElement("textInput", self.element_attrs)
        self.write_element("title", self.title)
        self.write_element("description", self.description)
        self.write_element("name", self.name)
        self.write_element("link", self.link)
        handler.endElement("textInput")


class Enclosure(Element):
    def __init__(self, url, length, type, *args, **kwargs):
        super(Enclosure, self).__init__(*args, **kwargs)
        self.url = url
        self.length = length
        self.type = type

    def publish(self, handler=None):
        super(Enclosure, self).publish(handler)
        self.write_element("enclosure", None,
                           {"url": self.url,
                            "length": str(self.length),
                            "type": self.type,
                            })


class Source(Element):
    def __init__(self, name, url, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.name = name
        self.url = url

    def publish(self, handler=None):
        super(Source, self).publish(handler)
        self.write_element("source", self.name, {"url": self.url})


class SkipHours(Element):
    element_attrs = {}

    def __init__(self, hours, *args, **kwargs):
        super(SkipHours, self).__init__(*args, **kwargs)
        self.hours = hours

    def publish(self, handler=None):
        super(SkipHours, self).publish(handler)
        if self.hours:
            handler.startElement("skipHours", self.element_attrs)
            for hour in self.hours:
                self.write_element("hour", str(hour))
            handler.endElement("skipHours")


class SkipDays(Element):
    element_attrs = {}

    def __init__(self, days, *args, **kwargs):
        super(SkipDays, self).__init__(*args, **kwargs)
        self.days = days

    def publish(self, handler=None):
        super(SkipDays, self).publish(handler)
        if self.days:
            handler.startElement("skipDays", self.element_attrs)
            for day in self.days:
                self.write_element("day", day)
            handler.endElement("skipDays")
