from utils.db_api.postgres import UsersInfo

db = UsersInfo()
testing_persons = (
    (1, 'Kirill'),
    (2, 'Daniel'),
    (3, 'Antonina'),
    (4, 'Abraham')
)


def test():
    db.create_table_users()
    users = db.select_all_users()
    assert users == []

    for user_id, name in testing_persons:
        db.add_user(user_id, name)
    users = db.select_all_users()
    assert users == list(testing_persons)

    user = db.select_user(user_id=1)
    assert user == (1, 'Kirill')

    user = db.select_user(user_id=2, name='Daniel')
    assert user == (2, 'Daniel')


test()
