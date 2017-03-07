# -*-coding:utf-8-*-
"""Article class file for the media understanding 2017 project.

File name: article.py
Author: Media Understanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.4
"""
from collections import Counter

class Article(object):
    """
    Standarized format for a news entry from any source.

    All news entries should be in this format, unspecified arguments are
    initialized as empty strings, except for keywords, which is a list.
    Btw this initialized like this: article.Article(args)
    """

    def __init__(self, title="", author="", source="", url="", category="",
                 keywords=[], published="", summary="", text="", ID="", term_count=Counter()):
        """Initialize all values."""
        self.title = title
        self.author = author
        self.source = source
        self.url = url
        self.keywords = keywords
        self.category = category
        self.published = published
        self.summary = summary
        self.text = text
        self.ID = ID
        self.term_count = term_count

    def __repr__(self):
        """Print article name when object is printed."""
        return "<Article Title: " + str(self.title.encode('utf-8')) + ">"
