from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn

# return drink in sentence
def get_drink(sentence):
    labels = label_sentence(sentence)
    for label in labels:
        if check_if_drink(label):
            return label[0]

# POS tag a given sentence
def label_sentence(sentence):
    tokens = word_tokenize(sentence)
    return pos_tag(tokens)

# checks the first definition of the word if it contains some kind of drink in its tree
# also checks the second definition of the tree
def check_if_drink(word):
    synsets = wn.synsets(word[0])
    if len(synsets) == 0:
        return False
    elif len(synsets) == 1:
        synset = synsets[0]
        if is_drink(synset.lemma_names()[0]):
            return True
        while True:
            hypernyms = synset.hypernyms()
            if len(hypernyms) < 1:
                break
            for hypernym in hypernyms:
                synset = hypernym
                synset_name = synset.lemma_names()
                if is_drink(synset_name[0]):
                    return True
            synset = hypernyms[0]
        return False
    else:
        for i in range(2):
            synset = synsets[i]
            if is_drink(synset.lemma_names()[0]):
                return True
            while True:
                hypernyms = synset.hypernyms()
                if len(hypernyms) < 1:
                    break
                for hypernym in hypernyms:
                    synset = hypernym
                    synset_name = synset.lemma_names()
                    if is_drink(synset_name[0]):
                        return True
                synset = hypernyms[0]
        return False

# Database for drink aliases
def is_drink(synset_name):
    if (synset_name == "alcohol" or synset_name == "beverage" or synset_name == "drink" or 
        synset_name == "liquid" or synset_name == "cocktail" or synset_name == "juice"):
        return True
    else:
        return False

def get_name(sentence):
    labels = label_sentence(sentence)
    label_length = len(labels)
    if label_length == 1 and labels[0][1] == "NN":
        return(labels[0][0])
    elif label_length == 2 and labels[0][1] == "NN" and labels[1][1] == "NN":
        return(sentence)
    elif labels[label_length-1][1] == "NN" and labels[label_length-2][1] == "NN":
        return str(labels[label_length-2][0] + " " + labels[label_length-1][0])
    else:
        return "noname"

def is_word_pepper(word):
    if (word == "peppa" or word == "pepa" or word == "pepper" or 
        word == "pappa" or word == "papa"):
        return True
    else:
        return False

# Same as get_drink() but returns all drinks in a list, is probably quite slow
def get_all_drinks(sentence):
    labels = label_sentence(sentence)
    drinks = []
    for label in labels:
        if check_if_drink(label):
            drinks.append(label[0])
    return drinks


if __name__ == "__main__":
    print("STARTING")
    import time
    sentence = "martini cola parrot cocktail vodka beer water nothing monkey chair john lemon juice"
    # sentence = "hit me with your best beverage"
    a = time.time()
    print(get_all_drinks(sentence))
    print(time.time()-a)
    a = time.time()
    print(get_all_drinks(sentence))
    print(time.time()-a)