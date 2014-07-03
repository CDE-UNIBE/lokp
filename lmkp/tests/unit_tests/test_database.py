from lmkp.models.database_objects import Group, Permission, Language

def test_db_lookup(db_session):

    model_instance = Group(10, 'blabla')
    db_session.add(model_instance)
    db_session.flush()

    assert 5 == db_session.query(Group).count()


def test_db_is_rolled_back(db_session):
    assert 4 == db_session.query(Group).count()
    
def test_blabla(db_session):
    assert 3 == db_session.query(Language).count()