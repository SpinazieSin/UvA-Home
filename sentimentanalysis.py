#! usr/bin/python
#
# file:		sentiment_analysis
# author:	Joram Wessels
# date:		14-02-2017
# Description:
#	Determines the sentiment consensus about the most frequently found named
#	entities based on tweets that include the given search term. The process
#	of calculating the sentiment about a named entity is based on the 2015 paper
#	"Contextual semantics for sentiment analysis of Twitter" by H. Saif et al.
#
# Dependencies:
#	- Sentistrength 2 (including the Thelwall-lexicon)
#	- Either:
#		- DBPedia (including large corpora)
#		- xmltodict (pip installable)
#		- dbpedia.py
#	- Or:
#		- NLTK
#		- named_entity_recognition.py
#	- Tweepy
#	- sentistrength.py
#
# Public functions:
#
# sentiment_analysis
#	Returns a dict with entities as keys and opinions as values.

""" TODO
 - speed: contextual feature generation during rate limit (limited increase)
 - DBPedia instead of NLTK
 - filtering "RT"
 - geometric median
 - negation (-> ordered dict of context words so a prior sentiment can be inverted)
"""

import sys, string, time
from math import log, cos, sin, pi
import tweepy
import sentistrength, named_entity_recognition#, dbpedia
import geometric_median

# File locations and paths, please note:
#	- All paths to folders should end in '/'
#	- File names without extention should remain without extention
model_path = "dbpedia-model/"
model_jar_file = "dbpedia-spotlight-latest.jar"
model_resource_folder = "en"	# folder that contains '/model' folder
lucene_path = "dbpedia-spotlight-quickstart-0.6.5/"
lucene_jar_file = "dbpedia-spotlight-0.6.5-jar-with-dependencies.jar"
sentistrength_jar = "SentiStrengthCom.jar"
sentistrength_data_location = "SentStrengthData/"
sentistrength_tmp_filename = ".context-words-temp"
output_filename = ".sentiment_scores"

# Algorithm parameters
max_tweets = 2500				# rate limit: 2500/15min
amount_of_named_entites = 10	# 0 means no limit (not advisable)
subj_threshold = 0.05

# Twitter API keys
CK  = "62f3T5JZjXXSZmKWQ5OyEIRxe"
CS  = "69shNq2kupktsUFoxbnFFrdexBuHmEuWbnhrNz0fNSxPSPkCua"
ATK = "102106748-TjKX9KSW3miMVxzVyglAQq42nvEAr62LnPwtAkd6"
ATS = "wU1MinoeQ7b0R1NBr1ZtHV415gww9P3IprNxHtrCJD5EX"

# Global logger closure
log_time = None

def sentiment_analysis(search_terms):
	"""Determines the sentiment consensus about named entities
	related to the search terms passed as the input.
	
	Args:
		search_terms: The list of search terms that select the tweets
				No search terms can contain any of these strings:
					OR, AND, "
	
	Returns:
		The sentiment consensus on Twitter
	
	"""
	global log_time
	log_time = time_logger()
	search_terms = check_input(search_terms)
	tweets, named_entities = collect_tweets(search_terms)
	index = term_indexing(tweets, named_entities)
	contextual_features = compute_contextual_features(index)
	senti_circle = senti_circle_generation(index, contextual_features)
	sentiment = entity_sentiment(senti_circle)
	log_time(0, "Finished analysing sentiment of " + str(search_terms))
	sentiment_array = [(dict(named_entities)[s[0]][0], s[1]) for s in sentiment]
	write_to_file(output_filename, sentiment_array)
	return

def check_input(search_terms):
	"""Checks the input search terms for API operators.
	
	Args:
		search_terms:	The input list of search terms
	
	Returns:
		The cleaned search term list
	
	"""
	definitions = ["OR", '"']
	cleaned = []
	for term in search_terms:
		for d in definitions:
			if d in term:
				log_time(0, "One of the search terms contains the invalid\
							string '" + d + "'. The term has been aborted.")
				cleaned.append(term)
	return cleaned

def collect_tweets(search_terms):
	"""Collects the raw tweets (without links) that use the 'search_term' The amount
	of tweets is limited by the global 'max_tweets' parameter. It simultaneously
	finds and links named entities and returns the n most frequently encountered
	named entities, where n is defined by the 'amount_of_named_entites' variable.
	
	Args:
		search_terms: A list of terms of which one needs to occur
						in each of the returned tweets
	
	Returns:
		A list of raw tweets as strings
		A list of (entity label, [aliases]) tuples
	
	"""
	log_time(0, "Starting tweet collection...")
	auth = tweepy.OAuthHandler(CK, CS)
	auth.set_access_token(ATK, ATS)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	query = ' OR '.join(['"' + term + '"' for term in search_terms]) + " -filter:links"
	NE = {}
	tweets = []
	try:
		tweet_count = 0
		for tweet in tweepy.Cursor(api.search, q=query, lang='en').items(max_tweets):
			
			if tweet.text.startswith("RT"): continue
			
			tweet_text = [w for w in tweet.text.encode("ascii", "ignore") if not w.startswith('@')]
			tweets.append(tweet_text)
			#named_entities = dbpedia.annotate(tweet.text)
			named_entities = named_entity_recognition.annotate(tweet_text)
			for entity in named_entities:
				if entity[1] in NE:
					NE[entity[1]][0].append(entity[0])
					NE[entity[1]][1] += 1
				else:
					NE[entity[1]] = [[entity[0]], 1]
			tweet_count += 1
			if (tweet_count % 500 == 0): log_time(1, str(tweet_count) + " tweets collected...")
	except tweepy.TweepError as e:
		print(e)
		log_time(0, "continuing...")
		pass
	log_time(1, "total tweets collected: " + str(len(tweets)))
	most_frequent = sorted(NE.items(), key=lambda x: x[1][1])[-amount_of_named_entites:]
	return tweets, [(e[0], list(set(e[1][0]))) for e in most_frequent]

def term_indexing(tweets, entities):
	"""Creats a quantified mapping between named entities and their context words.
	
	Args:
		tweets:		A list of raw tweets as strings
		entities:	A list of (entity label, [aliases]) tuples
	
	Returns:
		A dictionary mapping named entities to dicts with counts of contex words
				index[entity][context word] = count
	
	"""
	log_time(0, "Starting term_indexing...")
	clean_tweets = remove_non_english_words(tweets)
	index = {e[0]: {} for e in entities}
	for t in tweets:
		for e in entities:
			for a in e[1]:
				if a in t:
					context = t.replace(a, '').split()
					for w in context:
						ws = w.strip(string.punctuation)
						if ws == "" or ws.strip(string.digits) == "": continue
						if ws in index[e[0]]:
							index[e[0]][ws] += 1
						else:
							index[e[0]][ws] = 1
	return index

def remove_non_english_words(tweets):
	# cleaning data:
	# remove retweets/retweet tags
	# punctuation
	return tweets

def compute_contextual_features(index):
	"""Constructs a reversed dictionary, mapping context words to entity
	frequency and prior sentiment scores.
	
	Args:
		index: A dict mapping named entities to their context word frequencies
					index[entity][context word] = count
	
	Returns:
		A dict mapping context words to a (count, prior sentiment) tuple
	
	"""
	log_time(0, "Starting contextual features...")
	contextual_features = {}
	file_out = open(sentistrength_tmp_filename, 'w')
	for e in index:
		log_time(1, e)
		for c in index[e]:
			if c in contextual_features:
				contextual_features[c][0] += 1
			else:
				try:
					file_out.write(c + "\n")
					contextual_features[c] = [1, 0]
				except UnicodeEncodeError:
					pass
	file_out.close()
	contextual_features = sentistrength.prior_sentiment(contextual_features,
						sentistrength_tmp_filename, sentistrength_jar,
						sentistrength_data_location)
	return contextual_features

def senti_circle_generation(index, contextual_features):
	"""Generates a dict of SentiCircles based on the named entities and their context.
	
	Args:
		index: A dict mapping named entities to their context word frequencies
					index[entity][context word] = count
	
	Returns:
		A dict representing a the SentiCircles in (x, y) coordinates
				senti_circle[entity][context word] = (x, y)
	
	"""
	# computing the SentiCircles
	log_time(0, "Starting SentiCircle construction...")
	senti_circle = {e:{} for e in index}
	for e in index:
		log_time(1, e)
		for c in index[e]:
			try:
				r = index[e][c] * log(len(index)/contextual_features[c][0])
				theta = contextual_features[c][1] * pi
				senti_circle[e][c] = [r * cos(theta), r * sin(theta)]
			except KeyError:
				pass
	return senti_circle

def entity_sentiment(senti_circle):
	"""Computes the final sentiment score for each SentiCircles.
	
	Args:
		senti_circle: The SentiCircle represented as a nested dict with tuples
							senti_circle[entity][context word] = (x, y)
	
	Returns:
		A list of (entity label, sentiment) tuples
	
	"""
	log_time(0, "Starting entity sentiment...")
	sentiments = []
	for e in senti_circle:
		coordinates = senti_circle[e].values()
		g = senti_median(coordinates)
		print(e, g)
		if g[1] < -subj_threshold: sentiments.append([e, -1])
		elif g[1] > +subj_threshold: sentiments.append([e,  1])
		elif abs(g[1]) <= subj_threshold and g[0] >= 0: sentiments.append([e, 0])
	return sentiments

def senti_median(coordinates):
    """Computes the geometric median of all SentiCircle vectors.
    
    Args:
        coordinates: A list of coordinate tuples
    
    Returns:
        The coordinate tuple of the geometric median
    
    """
    return geometric_median.geometric_median(coordinates)

def time_logger():
	"""Returns a logger closure.
	
	Returns:
		A closure that logs and organizes metadata about the system to stdout
		
			Args:
				indent: The amount of preceding tabs
				label: The message to log
	
	"""
	start = time.time()
	def log_time(indent, label):
		tabs = (int((15-len(label))/8)+1 if len(label) < 16 else 1)
		print(indent*'\t' + label + tabs*'\t' + '+' + str(time.time()-start) + 's')
	return log_time

def write_to_file(filename, sentiment_array):
	"""Writes the results of the sentiment analysis to a txt file.
	
	Args:
		filename:			The name of the output file (without extention)
		sentiment_array:	An array of (entity, sentiment) tuples
	
	"""
	file = open(filename, 'a')
	for pair in sentiment_array:
		file.write(pair[0] + ", " + str(pair[1]) + '\n')
	file.close()

if __name__ == "__main__":
	s = sentiment_analysis(sys.argv[1:])
	print(s)