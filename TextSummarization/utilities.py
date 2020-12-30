import urllib.request as u
import re
import regex
from newspaper import Article

def is_link(link):
    regex = r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
    if re.search(regex, link):
        try:
            u.urlopen(link)
            return True
        except IOError:
            return False
    else:
        return False


def get_text_from_link(link):
    article = Article(link, language = 'vi')
    try:
        article.download()
        article.parse()
        try:
            title = article.title
        except:
            title = ""
        return article.text, title
    except:
        return None
