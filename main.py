def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn



import profilegetter as pg
import newsextractor as extractor
import chatengine

db = extractor.NewsExtractor()
# db.build_all(force=True, save=True)
db.build_all()
getter = pg.ProfileGetter(db.news, use_Nao=False)
user = getter.start()
c = chatengine.ChatEngine(user=user, news=db)
c.start()