def _initTestingDB():
    from sqlalchemy import create_engine
    from ..models.meta import Base, DBSession as TestSession
    
    test_engine = create_engine('postgresql://LMKP_user:lmkp@localhost:5432/LMKP_test')
    Base.metadata.create_all(test_engine)
    TestSession.configure(bind=test_engine)
    
    return TestSession