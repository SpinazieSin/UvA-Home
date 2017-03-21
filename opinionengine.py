#! usr/bin/python
#
# file:				opinion_engine
# author:			Joram Wessels
# date:				20-03-2017
# dependencies:		sentiment_analysis
# description:		Creates, stores, retrieves and provides opinions.

import sys, os, random
import sentiment_analysis

class OpinionEngine(object):
	"""The OpinionEngine object keeps track of the computed opinions."""
	
	def __init__(self):
		self.opinion_data_file = sentiment_analysis.output_filename
		self.opinions = None
	
	def update_opinions(self, keywords):
		"""Removes the old opinions and replaces them by computing new opinions
		based on the lists of keywords given.
		
		Args:
			keywords:	A list of searches, where a search is a list of keywords
		
		"""
		os.remove(self.opinion_data_file)
		for search in keywords:
			sentiment_analysis.sentiment_analysis(search)
	
	def read_opinions(self):
		"""Reads the current opinions into memory. In case of duplicates,
		only the last opinion is taken into account.
		
		"""
		opinions = {}
		try:
			file = open(self.opinion_data_file, 'r')
		except FileNotFoundError as e:
			print("No opinion data file called '" + self.opinion_data_file +
				"' was found. You may need to create one, or rename " + 
				"the existing file.")
			return
		for line in file:
			if line.split(',')[0].strip() in list(opinions.keys()): continue
			opinions[line.split(',')[0].strip()] = int(line.split(',')[1].strip())
		self.opinions = opinions
	
	def get_relevant_opinion(self, text, question=True):
		"""Checks the text for opinionated words and returns an opinion.
		
		Args:
			text:	A piece of text potentially sparking an opinion
			question (optional): Whether or not a question will be included
		
		Returns:
			A sentence with an opinion, or None if no opinion could be formed
		
		"""
		if not self.opinions: return None
		keys = []
		for key in list(self.opinions.keys()):
			if key in text and self.opinions[key] != 0: keys.append(key)
		if keys == []: return None
		subject = random.choice(keys)
		q = (self.get_question(subject) + " " if question else '')
		return q + self.get_opinion(subject)
	
	def get_random_opinion(self):
		"""Returns a sentence about a random entity.
		
		Returns:
			A sentence with a random opinion, or None if it fails
		
		"""
		if not self.opinions: return None
		subject = random.choice(list(self.opinions.keys()))
		return self.get_question(subject) + ' ' + self.get_opinion(subject)
	
	def get_question(self, subject):
		"""Forms a question to initiate a conversation about a subject.
		
		Args:
			subject:	The entity the conversation should be about
		
		Returns:
			A question-like sentence
		
		"""
		return random.choice(questions).replace('[SUBJ]', subject)
	
	def get_opinion(self, subject):
		"""Returns an appropriate sentence according to the opinion.
		
		Args:
			subject:	The entity the opinion is about
		
		Returns:
			A sentence with an opinion, or None if no opinion could be formed.
		
		"""
		if not self.opinions: return None
		if subject not in list(self.opinions.keys()):
			return random.choice(neutral_replies).replace('[SUBJ]', subject)
		if self.opinions[subject] > 0:
			return random.choice(positive_replies).replace('[SUBJ]', subject)
		elif self.opinions[subject] < 0:
			return random.choice(negative_replies).replace('[SUBJ]', subject)
		else:
			return random.choice(neutral_replies).replace('[SUBJ]', subject)

# The sentence database
positive_replies = ["Isn't [SUBJ] just the best?",
					"I think [SUBJ] is what we need more of in this world.",
					"[SUBJ]? I love [SUBJ]!",
					"I support [SUBJ] all the way!",
					"I'm glad to have [SUBJ] around.",
					"I mean, who doesn't like [SUBJ]!",
					"[SUBJ] is the best thing ever!",
					"[SUBJ] is amazing!",
					"You also like [SUBJ] right? Right?"]
negative_replies = ["I'm not too fond of [SUBJ].",
					"Actually, I'd rather not talk about [SUBJ].",
					"Every time I hear [SUBJ] I get sad.",
					"Can't we just remove [SUBJ] from this planet.",
					"I just want [SUBJ] to stop. Just, stop.",
					"Shall we start a petition against [SUBJ]?",
					"Why can't [SUBJ] just be nice?",
					"It makes me sad.",
					"I'd rather talk about something more positive."]
neutral_replies = [	"I don't know what to think about [SUBJ].",
					"I'm more or less indifferent about [SUBJ].",
					"I really don't know what to say about [SUBJ].",
					"[SUBJ]. I don't know.",
					"On the one hand [SUBJ] is all right, but then again.",
					"I think there are both positive as negatives sides to [SUBJ].",
					"I haven't really made up my mind about [SUBJ].",
					"What do you think?"]
questions = [		"What about [SUBJ]?",
					"What do you think about [SUBJ]?",
					"Any thoughts on [SUBJ]?",
					"What is your opinion on [SUBJ]?",
					"Do you wanna talk about [SUBJ]?",
					"Let's talk about [SUBJ].",
					"So. [SUBJ]. Am I right?",
					"Did you hear about [SUBJ]?",
					"I want to talk about [SUBJ].",
					"So what is the deal with [SUBJ].",
					"What is going on with [SUBJ]?",
					"We need to talk about [SUBJ].",
					"There was a lot of fuzz about [SUBJ] the other day.",
					"Have you heard? About [SUBJ]?",
					"A lot of people are talking about [SUBJ].",
					"[SUBJ] is a really hot topic right now.",
					"[SUBJ] is in the news again.",
					"I heard something about [SUBJ]?"]