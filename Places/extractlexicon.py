lexicon_name = "Place"
lexicon_file = "BigListOfPlaces.txt"
items_per_line = 6

with open(lexicon_file, "r") as f:
    with open(lexicon_name + "Lexicon.rsc", "w") as l:
        print("module", lexicon_name + "Lexicon\n", file=l)
        print("lexical", lexicon_name, "= " , end='', file=l)
        places = f.readlines()
        for idx, p in enumerate(places, start=1):
            print(p[:-1], "| ", end='', file=l) # remove newline
            if not idx % items_per_line:
                print("", file=l) # newline
