#! usr/bin/python
#
# file:				named_entity_recognition
# author:			Christopher Groskopf, Joram Wessels
# date:				21-02-2017
# source:			https://gist.github.com/onyxfish/322906
# dependencies:		NLTK
# description:		Extracts all named entities from a piece of text.
# public functions:	annotate
#						Returns a list of all named entities as tuples.

from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk_sents

def annotate(sample):
	"""Returns a list of all named entities in chronological order.
	
	Args:
		sample:	The piece of text to extract named entities from.
	
	Returns:
		A list of tuples with all named entities, including duplicates.
	
	"""
	sentences = sent_tokenize(sample)
	tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
	tagged_sentences = [pos_tag(sentence) for sentence in tokenized_sentences]
	chunked_sentences = ne_chunk_sents(tagged_sentences, binary=True)
	entity_names = []
	for tree in chunked_sentences:
		entity_names.extend(extract_entity_names(tree))
	return [(e, e) for e in entity_names]

def extract_entity_names(t):
	"""Extracts the named entities from the NLTK POS trees.
	
	Args:
		t:	NLTK POS tree of a sentence to tag.
	
	Returns:
		A list of strings that are the named entities, including duplicates.
	
	"""
	entity_names = []
	if hasattr(t, 'label') and t.label:
		if t.label() == 'NE':
			entity_names.append(' '.join([child[0] for child in t]))
		else:
			for child in t:
				entity_names.extend(extract_entity_names(child))
	return entity_names