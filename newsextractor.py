# -*-coding:utf-8-*-
"""Main article extraction class for the media understanding 2017 project.

File name: newsextractor.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.4
"""

import article
import feedparser
import requests
import sys
from bs4 import BeautifulSoup


class NewsExtractor():
    """
    Extraction class for newspapers.

    Currently only extracts front page entries, also prints all skipped
    entries in news stories. This behaviour might not be preferable in
    later inplementations. The get_full_article_text method can be used
    seperately for finding the full text associated with the article,
    this would be computationally intensive to extract on first pass.
    Use the add_full_article_text_all method to add text to all entries
    in self.news.
    """

    def __init__(self, newspapers=['cnn', 'bbc']):
        """Initialize all values."""
        self.newspapers = newspapers
        self.supported_news_papers = ['cnn', 'bbc']
        self.articles_parsed = 0
        self.news = []

    def extract_news(self):
        """Get news from specified sources.

        Gathers news and parses it to standarized article format from sources
        specified in self.newspapers, stores results in self.news,
        resets parsed counter.
        """
        self.articles_parsed = 0
        entry_list = []
        for newspaper in self.newspapers:
            if newspaper in self.supported_news_papers:
                if newspaper == 'cnn':
                    cnn_entries = self.extract_cnn_rss()
                    entry_list = entry_list + cnn_entries
                if newspaper == 'bbc':
                    bbc_entries = self.extract_bbc_rss()
                    entry_list = entry_list + bbc_entries
            else:
                print("the source: " + str(newspaper) + ", is not supported.")

        self.articles_parsed += len(entry_list)

        # INSERT HERE METODS TO ADD FULL TEXT TO ARTICLE FORMAT,
        # all cnn body text is wrapped in class="zn-body__paragraph"
        # all bbc body text is wrapped in class="story-body__inner"
        self.news = entry_list
        print("parsed articles, available in OBJECT.news")

    def extract_cnn_rss(self):
        """Extract and return the news entries of the cnn frontpage."""
        d = feedparser.parse('http://rss.cnn.com/rss/edition.rss')
        parsed_entry_list = []
        for entry in d.entries:
            title = entry.title
            source = "cnn"
            # summaries and dates are missing sometimes, an empty strings
            # is returned when this happens.
            summary = ""
            published = ""
            try:
                summary = entry.summary
            except:
                print("skipped summary in: " + title)
            try:
                published = entry.published
            except:
                print("skipped published in: " + title)

            link = entry.link
            category = "frontpage"  # WATCH OUT! THIS SHOULD CHANGE WHEN USING
            # A NEW RSS FEED.
            parsed_entry = article.Article(title=title, summary=summary,
                                           link=link, published=published,
                                           category=category, source=source)
            parsed_entry_list.append(parsed_entry)
        return parsed_entry_list

    def extract_bbc_rss(self):
        """Extract and return the news entries of the bbc frontpage."""
        d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml')
        parsed_entry_list = []
        for entry in d.entries:
            title = entry.title
            source = "bbc"
            # summaries and dates are missing sometimes, an empty strings
            # is returned when this happens.
            summary = ""
            published = ""
            try:
                summary = entry.summary
            except:
                print("skipped summary in: " + title)
            try:
                published = entry.published
            except:
                print("skipped published in: " + title)

            link = entry.link
            category = "frontpage"  # WATCH OUT! THIS SHOULD CHANGE WHEN USING
            # A NEW RSS FEED.
            parsed_entry = article.Article(title=title, summary=summary,
                                           link=link, published=published,
                                           category=category, source=source)
            parsed_entry_list.append(parsed_entry)
        return parsed_entry_list

    def get_full_article_text(self, url, newspaper):
        """Get the full article text and tags from url.

        Computationally intensive, source of the tags is dependend on the
        newspaper.
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        if newspaper == 'cnn':
            text_divs = soup.find_all("div", {"class": "zn-body__paragraph"})
            tag_divs = soup.find_all("ul",
                                     {"class": "el__storyhighlights__list"})
            # print("found: " + str(len(text_divs)) + " results")
        if newspaper == 'bbc':
            text_divs = soup.find_all("div", {"class": "story-body__inner"})
            tag_divs = soup.find_all("ul", {"class": "tags-list"})
            # print("found: " + str(len(text_divs)) + " results")

        result_text = ""
        result_tags = []
        for div in text_divs:
            result_text = result_text + " " + div.get_text()
        for li in tag_divs:
            result_tags = result_tags + li.get_text().split()
        # this next line is actually quite computationally intensive
        return ' '.join(result_text.split()), result_tags

    def add_full_article_text_all(self):
        """Add full text to all articles in self.news."""
        for i in range(len(self.news)):
            try:
                self.news[i].text, self.news[i].keywords = \
                    self.get_full_article_text(self.news[i].link,
                                               self.news[i].source)
            except:
                print(" skipped entry: " + str(i) + ", " + self.news[i].title)
            sys.stdout.write("\r{0}".format("parsed: " + str(i + 1) + "/" +
                                            str(len(self.news)) + " articles"))
            sys.stdout.flush()
        print("\nDone parsing.")

    def __repr__(self):
        """Print supported newspapers  and total parsed articles."""
        return "<Supported newspapers: " + str(self.supported_news_papers) \
               + ", parsed articles: " + str(self.articles_parsed) + ">"
