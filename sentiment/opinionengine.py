#! usr/bin/python
#
# file:				opinion_engine
# author:			Joram Wessels
# date:				20-03-2017
# dependencies:		sentiment_analysis.py
#                   positive_replies.txt
#                   negative_replies.txt
#                   neutral_replies.txt
#                   question_replies.txt
# description:		Creates, stores, retrieves and provides opinions.

import os
import random
import sentimentanalysis


class OpinionEngine(object):
    """The OpinionEngine object keeps track of the computed opinions."""

    def __init__(self):
        """Init opinion engine class."""
        self.opinion_data_file = sentimentanalysis.output_filename
        self.opinions = None
        self.pos = [w.strip() for w in
                    open('sentiment/positive_replies.txt', 'r').readlines()]
        self.neg = [w.strip() for w in
                    open('sentiment/negative_replies.txt', 'r').readlines()]
        self.neu = [w.strip() for w in
                    open('sentiment/neutral_replies.txt',  'r').readlines()]
        self.que = [w.strip() for w in
                    open('sentiment/question_replies.txt', 'r').readlines()]

    def update_opinions(self, keywords,
                        tweet_limit=sentimentanalysis.max_tweets):
        """Update opinions.

        Remove the old opinions and replaces them by computing new opinions
        based on the lists of keywords given.

        Args:
            keywords:	A list of searches, where a search is a list of keywords

        """
        if os.path.isfile(self.opinion_data_file):
            os.remove(self.opinion_data_file)
        for search in keywords:
            sentimentanalysis.sentiment_analysis(search,
                                                  tweet_limit=tweet_limit)

    def read_opinions(self):
        """Read the current opinions into memory.

        In case of duplicates, only the last opinion is taken into account.

        """
        opinions = {}
        try:
            file = open(self.opinion_data_file, 'r')
        except FileNotFoundError as e:
            print(e)
            print("No opinion data file called '" + self.opinion_data_file +
                  "' was found. You may need to create one, or rename " +
                  "the existing file.")
            return
        for line in file:
            if line.split(',')[0].strip() in list(opinions.keys()):
                continue
            opinions[line.split(',')[0].strip().lower()] = \
                int(line.split(',')[1].strip())
        self.opinions = opinions

    def get_relevant_opinion(self, text, question=True):
        """Check the text for opinionated words and returns an opinion.

        Args:
            text:	A piece of text potentially sparking an opinion
            question (optional): Whether or not a question will be included

        Returns:
            A sentence with an opinion, or None if no opinion could be formed

        """
        if not self.opinions:
            return None
        keys = []
        for key in list(self.opinions.keys()):
            if key in text and self.opinions[key] != 0:
                keys.append(key)
        if keys == []:
            return None
        subject = random.choice(keys)
        q = (self.get_question(subject) + " " if question else '')
        return q + self.get_opinion(subject)

    def get_random_opinion(self):
        """Return a sentence about a random entity.

        Returns:
            A sentence with a random opinion, or None if it fails

        """
        if not self.opinions:
            return None
        subject = random.choice(list(self.opinions.keys()))
        return self.get_question(subject) + ' ' + self.get_opinion(subject)

    def get_question(self, subject):
        """Form a question to initiate a conversation about a subject.

        Args:
            subject:	The entity the conversation should be about

        Returns:
            A question-like sentence

        """
        return random.choice(self.que).replace('[SUBJ]', subject)

    def get_opinion(self, subject):
        """Return an appropriate sentence according to the opinion.

        Args:
            subject:	The entity the opinion is about

        Returns:
            A sentence with an opinion, or None if no opinion could be formed.

        """
        if not self.opinions:
            return None
        if subject not in list(self.opinions.keys()):
            return random.choice(self.neu).replace('[SUBJ]', subject)
        if self.opinions[subject] > 0:
            return random.choice(self.pos).replace('[SUBJ]', subject)
        elif self.opinions[subject] < 0:
            return random.choice(self.neg).replace('[SUBJ]', subject)
        else:
            return random.choice(self.neu).replace('[SUBJ]', subject)

    def present_opinion_article(self, article):
        """Plz doc this."""
        # Actually extract the article subject first
        keyword = random.choice(list(article.keywords))
        opinion = self.get_relevant_opinion(keyword)
        if opinion is not None:
            return "speak", [opinion]
        return None, [None]
