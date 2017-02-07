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


class NewsExtractor():
    """
    Extraction class for newspapers.

    Currently only extracts front page entries, also prints all skipped
    entries in news stories. This behaviour might not be preferable in
    later inplementations.
    """

    def __init__(self, newspapers=['cnn', 'bbc']):
        """Initialize all values."""
        self.newspapers = newspapers
        self.supported_news_papers = ['cnn', 'bbc']
        self.articles_parsed = 0

    def extract_news(self):
        """Get news from specified sources.

        Return news in standarized article format from sources specified in
        self.newspapers.
        """
        entry_list = []
        for newspaper in self.newspapers:
            if newspaper in self.supported_news_papers:
                if newspaper == 'cnn':
                    cnn_entries = self.extract_cnn()
                    entry_list = entry_list + cnn_entries
                if newspaper == 'bbc':
                    bbc_entries = self.extract_bbc()
                    entry_list = entry_list + bbc_entries

        self.articles_parsed += len(entry_list)

        # INSERT HERE METODS TO ADD FULL TEXT TO ARTICLE FORMAT,
        # all cnn body text is wrapped in class="zn-body__paragraph"
        # all bbc body text is wrapped in class="story-body__inner"
        return entry_list

    def extract_cnn(self):
        """Extract and return the news entries of the cnn frontpage."""
        d = feedparser.parse('http://rss.cnn.com/rss/edition.rss')
        parsed_entry_list = []
        for entry in d.entries:
            title = entry.title
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
                                           category=category)
            parsed_entry_list.append(parsed_entry)
        return parsed_entry_list

    def extract_bbc(self):
        """Extract and return the news entries of the bbc frontpage."""
        d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml')
        parsed_entry_list = []
        for entry in d.entries:
            title = entry.title
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
                                           category=category)
            parsed_entry_list.append(parsed_entry)

        return parsed_entry_list

    def __repr__(self):
        """Print supported newspapers  and total parsed articles."""
        return "<Supported newspapers: " + str(self.supported_news_papers) \
               + ", parsed articles: " + str(self.articles_parsed) + ">"
