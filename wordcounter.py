import re

debug = False

class WordCounter():
    def __init__(self, stopwords):
        self.num_keywords = 10
        # Define stopwords
        self.stopword_filepath = "SmartStoplist.txt"
        self.stopwords = stopwords

    def get(self, text):
        return self.keywords(text, self.num_keywords)

    def split_words(self, text):
        """Split a string into array of words
        """
        try:
            text = re.sub(r'[^\w ]', '', text)  # strip special chars
            return [x.strip('.').lower() for x in text.split()]
        except TypeError:
            return None

    def keywords(self, text, num_keywords):
        """Get the top 10 keywords and their frequency scores ignores blacklisted
        words in stopwords, counts the number of occurrences of each word, and
        sorts them in reverse natural order (so descending) by number of
        occurrences.
        """
        text = self.split_words(text)
        # of words before removing blacklist words
        if text:
            num_words = len(text)
            text = [x for x in text if x not in self.stopwords]
            freq = {}
            for word in text:
                if word in freq:
                    freq[word] += 1
                else:
                    freq[word] = 1

            min_size = min(num_keywords, len(freq))
            keywords = sorted(freq.items(),
                              key=lambda x: (x[1], x[0]),
                              reverse=True)
            keywords = keywords[:min_size]
            keywords = dict((x, y) for x, y in keywords)

            for k in keywords:
                articleScore = keywords[k]*1.0 / max(num_words, 1)
                keywords[k] = articleScore * 1.5 + 1
            return dict(keywords)
        else:
            return dict()

if debug:
    text = "The long-string instrument is a musical instrument in which the string is of such a length that the ... One example of a long-string instrument was invented by the American composer Ellen Fullman. It is tuned in just intonation and played by"
    with open('test_article.txt', 'r') as myfile:
        text = myfile.read().replace('\n', '')
    keys = WordCounter(text)
    print(keys.wordcount)