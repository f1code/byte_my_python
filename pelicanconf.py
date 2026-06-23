AUTHOR = 'Nicolas Galler'
SITENAME = 'Byte My Python'
SITESUBTITLE = "Python, data, and more"
SITEURL = ""

PATH = "content"
STATIC_PATHS = ["images", "pages", "extra/CNAME"]

# Place the CNAME file at the site root for GitHub Pages custom domain
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
}

TIMEZONE = 'Europe/Brussels'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
THEME = "./theme"
# store customizable theme pictures
ICONS_PATH = "images/icons"
PROFILE_ICON = "python.jpg"

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
)

SIDEBAR_LINKS = (
    ("/", "Home", "home"),
    ("/pages/about.html", "About", "question"),
    ("https://github.com/nicoglr", "Github", "github"),
    ("/feeds/all.atom.xml", "Feed", "rss"),
)

# Social widget
SOCIAL = (
)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
