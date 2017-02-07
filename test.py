# -*-coding:utf-8-*-
"""Test file for the media understanding 2017 project.

File name: test.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.4
"""

import feedparser

newspapers = {
    'nu': 'http://www.nu.nl/rss/Algemeen',
    'volkskrant': 'http://www.volkskrant.nl/nieuws-voorpagina/rss.xml',
    'telegraaf': 'http://www.telegraaf.nl/rss/'
}


def main():
    """Main."""
    d = getFeed('volkskrant')
    print(d)
    # for entry in d.entries:
    #     print(entry.title)


def getFeed(newspaper):
    """Get RSS feed from given newspaper."""
    d = feedparser.parse(newspapers[newspaper])
    return d


if __name__ == '__main__':
    main()
