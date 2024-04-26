AUTHOR = 'Nicolas Galler'
SITENAME = 'Byte My Python'
SITESUBTITLE = "tfwwftwft"
SITEURL = ""

PATH = "content"
STATIC_PATHS = ["images"]

TIMEZONE = 'Europe/Brussels'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
THEME = "./theme"
ICONS_PATH = "images/icons"

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
)

# Social widget
SOCIAL = (
    ("github", "https://github.com/ngaller"),
    ("rss", "/feeds/all.atom.xml"),
)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
