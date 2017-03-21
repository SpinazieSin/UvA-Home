import opinion_engine as oe
en = oe.OpinionEngine()
en.update_opinions([['Trump', 'Budget'], ['Merkel', 'Germany'],
                    ['Erdogan', 'Turkey'], ['Trump', 'Russia', 'FBI']],
                   tweet_limit=25)
en.read_opinions()
en.get_random_opinion()
