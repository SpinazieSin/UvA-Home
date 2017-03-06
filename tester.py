import profilegetter as pg
import newsextractor as extractor


db = extractor.NewsExtractor()
# db.build_all(force=True, save=True)
db.build_all()
getter = pg.ProfileGetter(db.news, voiced=True)
# getter.train_model()
# print(db.news)
# print(finder.newsDB)
getter.start()
# print(prof.keywords)
# print(prof.interests)
