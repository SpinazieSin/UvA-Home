import profilegetter as pg
import newsextractor as extractor
import chatengine

db = extractor.NewsExtractor()
# db.build_all(force=True, save=True)
db.build_all()
getter = pg.ProfileGetter(db.news, use_Nao=True)
# getter.train_model()
user = getter.start()
c = chatengine.ChatEngine(user=user, news=db)
c.start()
