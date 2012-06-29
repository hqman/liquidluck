import os
from liquidluck.utils import to_unicode


def __load_themes():
    import time
    import tempfile
    f = os.path.join(tempfile.gettempdir(), 'liquidluck.json')

    def fetch():
        import urllib
        content = urllib.urlopen(
            'http://project.lepture.com/liquidluck/themes.json'
        ).read()
        open(f, 'w').write(to_unicode(content))

    if not os.path.exists(f) or os.stat(f).st_mtime + 600 < time.time():
        fetch()

    content = to_unicode(open(f).read())

    try:
        import json
        json_decode = json.loads
    except ImportError:
        import simplejson
        json_decode = simplejson.loads

    themes = json_decode(content)
    return themes


SEARCH_TEMPLATE = '''
Theme: %(name)s
Author: %(author)s
Homepage: %(homepage)s

'''


def search(keyword=None):
    themes = __load_themes()

    if keyword and keyword not in themes:
        print("Can't find theme: %s" % keyword)
        return None

    if keyword:
        themes = {keyword: themes[keyword]}

    for name in themes:
        theme = themes[name]
        theme.update({'name': name})
        print(SEARCH_TEMPLATE % theme)
    return


def install(keyword):
    themes = __load_themes()
    if keyword not in themes:
        print("can't find theme %s" % keyword)
        return
    theme = themes[keyword]
    repo = theme['repo']
    output = '_themes/%s' % keyword
    import subprocess
    subprocess.call(['git', 'clone', repo, output])


if __name__ == '__main__':
    search('moment')