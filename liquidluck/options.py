from __future__ import absolute_import, division, with_statement

import os
import logging
import logging.handlers
import sys
import time


# For pretty log messages, if available
try:
    import curses
except ImportError:
    curses = None


class _Options(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError


def enable_pretty_logging(level='info'):
    """Turns on formatted logging output as configured.

    This is called automatically by `parse_command_line`.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    if not root_logger.handlers:
        # Set up color if we are in a tty and curses is installed
        color = False
        if curses and sys.stderr.isatty():
            try:
                curses.setupterm()
                if curses.tigetnum("colors") > 0:
                    color = True
            except Exception:
                pass
        channel = logging.StreamHandler()
        channel.setFormatter(_LogFormatter(color=color))
        root_logger.addHandler(channel)


class _LogFormatter(logging.Formatter):
    def __init__(self, color, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self._color = color
        if color:
            # The curses module has some str/bytes confusion in
            # python3.  Until version 3.2.3, most methods return
            # bytes, but only accept strings.  In addition, we want to
            # output these strings with the logging module, which
            # works with unicode strings.  The explicit calls to
            # unicode() below are harmless in python2 but will do the
            # right conversion in python 3.
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = unicode(fg_color, "ascii")
            self._colors = {
                logging.DEBUG: unicode(curses.tparm(fg_color, 4),  # Blue
                                       "ascii"),
                logging.INFO: unicode(curses.tparm(fg_color, 2),  # Green
                                      "ascii"),
                logging.WARNING: unicode(curses.tparm(fg_color, 3),  # Yellow
                                         "ascii"),
                logging.ERROR: unicode(curses.tparm(fg_color, 1),  # Red
                                       "ascii"),
            }
            self._normal = unicode(curses.tigetstr("sgr0"), "ascii")

    def format(self, record):
        try:
            record.message = record.getMessage()
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)
        record.asctime = time.strftime(
            "%y%m%d %H:%M:%S", self.converter(record.created))
        prefix = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]' % \
            record.__dict__
        if self._color:
            prefix = (self._colors.get(record.levelno, self._normal) +
                      prefix + self._normal)
        formatted = prefix + " " + record.message
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            formatted = formatted.rstrip() + "\n" + record.exc_text
        return formatted.replace("\n", "\n    ")


#: settings for blog user
settings = _Options()
settings.source = 'content'
settings.output = 'deploy'
settings.static_output = '%s/static' % settings.output
settings.static_prefix = '/static/'
settings.theme = 'default'

settings.permalink = '{{date.year}}/{{filename}}'
settings.perpage = 30
settings.feedcount = 20
settings.timezone = '+00:00'

settings.site = {
    'name': 'Felix Felicis',
    'url': 'http://github.com',
    'prefix': '',
}

settings.author = 'admin'
settings.authors = {}

settings.readers = {
    'markdown': 'liquidluck.readers.markdown.MarkdownReader',
}
settings.readers_variables = {}

settings.writers = {
    'post': 'liquidluck.writers.core.PostWriter',
    'page': 'liquidluck.writers.core.PageWriter',
    'archive': 'liquidluck.writers.core.ArchiveWriter',
    'archive_feed': 'liquidluck.writers.core.ArchiveFeedWriter',
    'file': 'liquidluck.writers.core.FileWriter',
    'static': 'liquidluck.writers.core.StaticWriter',
    'year': 'liquidluck.writers.core.YearWriter',
    'tag': 'liquidluck.writers.core.TagWriter',
    'category': 'liquidluck.writers.core.CategoryWriter',
    'category_feed': 'liquidluck.writers.core.CategoryFeedWriter',
}
settings.writers_variables = {}
settings.template_variables = {}
settings.template_filters = {}
settings.theme_variables = {}


#: settings for liquidluck
g = _Options()
g.detail_logging = False
g.liquid_directory = os.path.abspath(os.path.dirname(__file__))
g.source_directory = settings.source
g.output_directory = settings.output
g.static_directory = settings.static_output
g.theme_directory = os.path.join(g.liquid_directory, '_themes', settings.theme)
g.resource = {}
g.public_posts = []
g.secure_posts = []
g.pure_files = []
g.pure_pages = []
