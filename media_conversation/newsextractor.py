# -*-coding:utf-8-*-
"""Main article extraction class for the media understanding 2017 project.

File name: newsextractor.py
Author: Media Understanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.4
"""

import article
import feedparser
import requests
import sys
import pickle
import os.path
import datefinder
import itertools
import keywords as k

import re
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
from collections import Counter


# set global so file is read only once
keywords = k.KeyWords()
word = re.compile(r'\w+')


class NewsExtractor(object):
    """
    Extraction class for newspapers.

    Currently only extracts front page entries, also prints all skipped
    entries in news stories. This behaviour might not be preferable in
    later inplementations. The get_full_article method can be used
    seperately for finding the full text associated with the article,
    this would be computationally intensive to extract on first pass.
    Use the add_full_article_all method to add text to all entries
    in self.news. Use extract_rss to get all article summaries, dates etc.

    Run build_all() to build the entire database, this takes a while, Run
    it with True, to save the data to a .p file, beware though, if you
    initialize the object with a different newspaper subsection, you might
    run into weird bugs because the previous database is loaded, use force to
    circumvent this.
    """

    def __init__(self, newspapers=["cnn", "bbc", "reuters", "nytimes"]):
        """Initialize all values."""
        self.stemmer = SnowballStemmer("english")
        self.newspapers = newspapers
        self.supported_news_papers = ["cnn", "bbc", "reuters", "nytimes"]
        self.articles_parsed = 0
        self.news = []

    def extract_rss(self):
        """Get news from specified sources.

        Gathers news and parses it to standarized article format from sources
        specified in self.newspapers, stores results in self.news,
        resets parsed counter.
        """
        self.articles_parsed = 0
        # I assume you have 4 threads :)
        pool = ThreadPool(4)
        entry_lists = pool.map(self.extract_newspaper, self.newspapers)
        entry_list = list(itertools.chain(*entry_lists))

        self.articles_parsed += len(entry_list)
        self.news = entry_list
        print("parsed articles, available in OBJECT.news")

    def extract_newspaper(self, newspaper):
        """Do all extraction and parsing newspaper, need for threading."""
        entry_list = []
        if newspaper in self.supported_news_papers:
            if newspaper == "cnn":
                cnn_entries = self.extract_cnn_rss()
                entry_list = entry_list + cnn_entries
            if newspaper == "bbc":
                bbc_entries = self.extract_bbc_rss()
                entry_list = entry_list + bbc_entries
            if newspaper == "reuters":
                reuters_entries = self.extract_reuters_rss()
                entry_list = entry_list + reuters_entries
            if newspaper == "nytimes":
                nytimes_entries = self.extract_nytimes_rss()
                entry_list = entry_list + nytimes_entries
            else:
                print("the source: " + str(newspaper) + ", is not supported.")
        return entry_list

    def parse_rss(self, rss_category_list, source):
        """Parse urls."""
        parsed_entry_list = []
        duplicate_url_list = set()
        duplicate_title_list = set()
        for cat, url in rss_category_list:
            d = feedparser.parse(url)
            for entry in d.entries:
                # summaries and dates are missing sometimes, an empty strings
                # is returned when this happens.
                summary = ""
                published = ""

                url = entry.link
                if url in duplicate_url_list:
                    print("skipped duplicate url: " + url)
                    continue
                duplicate_url_list.add(url)

                title = entry.title
                if title in duplicate_title_list:
                    print("skipped duplicate title: " + title)
                    continue
                duplicate_title_list.add(title)

                try:
                    dirty_summary = entry.summary
                    summary = re.sub('<[^>]*>', '', dirty_summary)
                except BaseException:
                    print("skipped summary in: " + source + " title: " + title)
                try:
                    published = list(datefinder.find_dates(entry.published))[0]
                except BaseException:
                    print("skipped date in: " + source + " title: " + title)

                category = cat  # WATCH OUT! THIS SHOULD CHANGE WHEN USING
                # A NEW RSS FEED.
                parsed_entry = article.Article(title=title, summary=summary,
                                               url=url, published=published,
                                               category=category,
                                               source=source)
                parsed_entry_list.append(parsed_entry)
        return parsed_entry_list

    def extract_cnn_rss(self):
        """Extract and return the news entries of the cnn rss feeds."""
        rss_category_list = [
            ("top_stories", "http://rss.cnn.com/rss/edition.rss"),
            ("world", "http://rss.cnn.com/rss/edition_world.rss"),
            ("africa", "http://rss.cnn.com/rss/edition_africa.rss"),
            ("americas", "http://rss.cnn.com/rss/edition_americas.rss"),
            ("asia", "http://rss.cnn.com/rss/edition_asia.rss"),
            ("europe", "http://rss.cnn.com/rss/edition_europe.rss"),
            ("middle_east", "http://rss.cnn.com/rss/edition_meast.rss"),
            ("north_america", "http://rss.cnn.com/rss/edition_us.rss"),
            ("money", "http://rss.cnn.com/rss/money_news_international.rss"),
            ("technology", "http://rss.cnn.com/rss/edition_technology.rss"),
            ("science", "http://rss.cnn.com/rss/edition_space.rss"),
            ("entertainment",
                "http://rss.cnn.com/rss/edition_entertainment.rss"),
            ("sport", "http://rss.cnn.com/rss/edition_sport.rss"),
            ("football", "http://rss.cnn.com/rss/edition_football.rss"),
            ("golf", "http://rss.cnn.com/rss/edition_golf.rss"),
            ("motorsport", "http://rss.cnn.com/rss/edition_motorsport.rss"),
            ("tennis", "http://rss.cnn.com/rss/edition_tennis.rss"),
            ("travel", "http://rss.cnn.com/rss/edition_travel.rss"),
            ("latest", "http://rss.cnn.com/rss/cnn_latest.rss"),
                            ]

        return self.parse_rss(rss_category_list, "cnn")

    def extract_bbc_rss(self):
        """Extract and return the news entries of the bbc rss feeds."""
        rss_category_list = [
            ("top_stories", "http://feeds.bbci.co.uk/news/rss.xml"),
            ("world", "http://feeds.bbci.co.uk/news/world/rss.xml"),
            ("africa", "http://feeds.bbci.co.uk/news/world/africa/rss.xml"),
            ("asia", "http://feeds.bbci.co.uk/news/world/asia/rss.xml"),
            ("europe", "http://feeds.bbci.co.uk/news/world/europe/rss.xml"),
            ("latin_america",
                "http://feeds.bbci.co.uk/news/world/latin_america/rss.xml"),
            ("middle_east",
                "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml"),
            ("north_america",
                "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
            ("uk", "http://feeds.bbci.co.uk/news/uk/rss.xml"),
            ("england", "http://feeds.bbci.co.uk/news/england/rss.xml"),
            ("northern_ireland",
                "http://feeds.bbci.co.uk/news/northern_ireland/rss.xml"),
            ("scotland", "http://feeds.bbci.co.uk/news/scotland/rss.xml"),
            ("wales", "http://feeds.bbci.co.uk/news/wales/rss.xml"),
            ("business", "http://feeds.bbci.co.uk/news/business/rss.xml"),
            ("politics", "http://feeds.bbci.co.uk/news/politics/rss.xml"),
            ("health", "http://feeds.bbci.co.uk/news/health/rss.xml"),
            ("education", "http://feeds.bbci.co.uk/news/education/rss.xml"),
            ("science",
                "http://feeds.bbci.co.uk/news/science_and_environment/" +
                "rss.xml"),
            ("technology", "http://feeds.bbci.co.uk/news/technology/rss.xml"),
            ("entertainment",
                "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"),
            ("latest",
                "http://feeds.bbci.co.uk/news/system/" +
                "latest_published_content/rss.xml")
                            ]

        return self.parse_rss(rss_category_list, "bbc")

    def extract_reuters_rss(self):
        """Extract and return the news entries of the reuters rss feeds."""
        rss_category_list = [
            ("top_stories", "http://feeds.reuters.com/reuters/topNews"),
            ("art", "http://feeds.reuters.com/news/artsculture"),
            ("business", "http://feeds.reuters.com/reuters/businessNews"),
            ("companies", "http://feeds.reuters.com/reuters/companyNews"),
            ("entertainment",
                "http://feeds.reuters.com/reuters/entertainment"),
            ("environment", "http://feeds.reuters.com/reuters/environment"),
            ("health", "http://feeds.reuters.com/reuters/healthNews"),
            ("lifestyle", "http://feeds.reuters.com/reuters/lifestyle"),
            ("media", "http://feeds.reuters.com/news/reutersmedia"),
            ("economy", "http://feeds.reuters.com/news/wealth"),
            ("politics", "http://feeds.reuters.com/Reuters/PoliticsNews"),
            ("science", "http://feeds.reuters.com/reuters/scienceNews"),
            ("sport", "http://feeds.reuters.com/reuters/sportsNews"),
            ("technology", "http://feeds.reuters.com/reuters/technologyNews"),
            ("north_america", "http://feeds.reuters.com/Reuters/domesticNews"),
            ("world", "http://feeds.reuters.com/Reuters/worldNews"),
            ("odd", "http://feeds.reuters.com/reuters/oddlyEnoughNews")
                            ]

        return self.parse_rss(rss_category_list, "reuters")

    def extract_nytimes_rss(self):
        """Extract and return the news entries of the cnn rss feeds."""
        rss_category_list = [
            ("top_stories",
             "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"),
            ("world",
             "http://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
            ("africa",
             "http://rss.nytimes.com/services/xml/rss/nyt/Africa.xml"),
            ("americas",
             "http://rss.nytimes.com/services/xml/rss/nyt/Americas.xml"),
            ("asia",
             "http://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml"),
            ("europe",
             "http://rss.nytimes.com/services/xml/rss/nyt/Europe.xml"),
            ("middle_east",
             "http://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml"),
            ("north_america",
             "http://rss.nytimes.com/services/xml/rss/nyt/US.xml"),
            ("education",
             "http://rss.nytimes.com/services/xml/rss/nyt/Education.xml"),
            ("politics",
             "http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"),
            ("business",
             "http://rss.nytimes.com/services/xml/rss/nyt/Business.xml"),
            ("environment",
             "http://rss.nytimes.com/services/xml/rss/nyt/Environment.xml"),
            ("economy",
             "http://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"),
            ("money",
             "http://rss.nytimes.com/services/xml/rss/nyt/YourMoney.xml"),
            ("technology",
             "http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"),
            ("sport",
             "http://rss.nytimes.com/services/xml/rss/nyt/Sports.xml"),
            ("baseball",
             "http://rss.nytimes.com/services/xml/rss/nyt/Baseball.xml"),
            ("golf",
             "http://rss.nytimes.com/services/xml/rss/nyt/Golf.xml"),
            ("american_football",
             "http://rss.nytimes.com/services/xml/rss/nyt/ProFootball.xml"),
            ("football",
             "http://rss.nytimes.com/services/xml/rss/nyt/Soccer.xml"),
            ("tennis",
             "http://rss.nytimes.com/services/xml/rss/nyt/Tennis.xml"),
            ("basketball",
             "http://rss.nytimes.com/services/xml/rss/nyt/ProBasketball.xml"),
            ("science",
                "http://rss.nytimes.com/services/xml/rss/nyt/Science.xml"),
            ("health",
                "http://rss.nytimes.com/services/xml/rss/nyt/Health.xml"),
            ("art", "http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml"),
            ("travel",
             "http://rss.nytimes.com/services/xml/rss/nyt/Travel.xml")
                            ]

        return self.parse_rss(rss_category_list, "nytimes")

    def extract_slashdot_rss(self):
        """Not implemented yet."""
        return []

    def get_full_article_url(self, url, newspaper):
        """Get the full article text and tags from url.

        Computationally intensive, source of the tags is dependend on the
        newspaper.
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        if newspaper == "cnn":
            text_divs = soup.find_all("div", {"class": "zn-body__paragraph"})
        if newspaper == "bbc":
            # for div in soup.findall("div", {"class:": "bbccom_advert"}):
            #     div.decompose()
            # for div in soup.findall("figure", {"class:": "media-landscape no-caption full-width lead"}):
            #     div.decompose()
            # for div in soup.findall("figure", {"class:": "media-landscape has-caption full-width lead"}):
            #     div.decompose()
            # for div in soup.findall("figure", {"class:": "media-landscape no-caption full-width"}):
            #     div.decompose()
            # for div in soup.findall("figure", {"class:": "  media-landscape has-caption full-width"}):
            #     div.decompose()
            text_divs = soup.find_all("div", {"class": "story-body__inner"})
        if newspaper == "reuters":
            text_divs = soup.find_all("span", {"id": "article-text"})
            # nothing that resembles tags present in reuters pages :(
        if newspaper == "nytimes":
            text_divs = soup.find_all(
                        "p", {"class": "story-body-text story-content"})

        result_text = ""
        for div in text_divs:
            result_text = result_text + " " + div.get_text()
        # FIX SOMETHING HERE THAT CAUSES THIS: "his", "favorTrump"
        # these next lines are pretty computationally intensive
        result_text = " ".join(result_text.split())
        result_text = result_text.replace("\\", "")
        # load stopwordlist
        global keywords
        algorithm_tags = set(keywords.extract(result_text))
        return result_text, algorithm_tags

    def get_full_article_text(self, article):
        """Wrapper around get_full_article_url for easier debugging."""
        text, tags = self.get_full_article_url(article.url, article.source)
        return text

    def text_to_list(self, text):
        """Someone please explain what this does."""
        global word
        return word.findall(text)

    def convert_to_terms(self, article_title, article_keywords):
        """Explain this as well."""
        stemmed_terms = Counter()
        title_vector = self.text_to_list(article_title.lower())
        for term in title_vector:
            stem = self.stemmer.stem(term)
            if len(stem) > 1:
                stemmed_terms[stem] += 1
            else:
                stemmed_terms[term] += 1
        for keyword in article_keywords:
            for term in self.text_to_list(keyword):
                stem = self.stemmer.stem(term)
                if len(stem) > 1:
                    stemmed_terms[stem] += 1
                else:
                    stemmed_terms[term] += 1
        return stemmed_terms

    def add_full_article_all(self):
        """Add full text to all articles in self.news."""
        pool = ThreadPool(4)
        indices = range(len(self.news))
        pool.map(self.thread_build, indices)
        pool.close()
        pool.join()
        print("\nDone parsing.")

    def thread_build(self, i):
        """Build single entry, needed for threading."""
        try:
            self.news[i].text, self.news[i].keywords = \
                self.get_full_article_url(self.news[i].url,
                                          self.news[i].source)
            self.news[i].term_count = self.convert_to_terms(
                self.news[i].title, self.news[i].keywords)
        except BaseException:
            print(" skipped entry: " + str(i) + ", " + self.news[i].title)
        sys.stdout.write("\r{0}".format("parsed index: " + str(i + 1) + "/" +
                                        str(len(self.news)) + " articles"))
        sys.stdout.flush()

    def build_all(self, save=True, force=False):
        """Build the entire database with full article text.

        Use the force flag to force the database to be renewed, the default
        behaviour is building and saving the news to a file, if no data file
        is present. If a file is present nothing is build and that file is
        loaded instaad.
        """
        if not os.path.isfile("news.pickle") or force:
            self.extract_rss()
            self.add_full_article_all()
        else:
            with open('news.pickle', 'rb') as handle:
                self.news = pickle.load(handle)
        if save:
            with open('news.pickle', 'wb') as handle:
                pickle.dump(self.news, handle)

    def __repr__(self):
        """Print supported newspapers  and total parsed articles."""
        return "<Supported newspapers: " + str(self.supported_news_papers) \
               + ", parsed articles: " + str(self.articles_parsed) + ">"
