import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from datetime import date
from fast_api_app.database.models import User, UserAuth
from fast_api_app.schemas import UserSchema, UserModel
from fast_api_app.repository.users import (
    get_user_by_email,
    create_user,
    update_avatar,
    update_token,
    get_users,
    get_user,
    get_birthday,
    search_users,
    create_users,
    update_user,
    remove_user,
    confirmed_email,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        user_auth = UserAuth(email="test@example.com")
        self.session.query().filter().first.return_value = user_auth
        result = await get_user_by_email(email="test@example.com", db=self.session)
        self.assertEqual(result, user_auth)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="nonexistent@example.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        user_data = UserModel(email="new@example.com")
        new_user = UserAuth(**user_data.dict(), avatar=None)
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        result = await create_user(body=user_data, db=self.session)
        self.assertEqual(result, new_user)

    async def test_update_avatar(self):
        user_auth = UserAuth(email="test@example.com", avatar="old_url")
        self.session.query().filter().first.return_value = user_auth
        new_url = "new_url"
        result = await update_avatar(email="test@example.com", url=new_url, db=self.session)
        self.assertEqual(result, user_auth)
        self.assertEqual(result.avatar, new_url)

    async def test_update_token(self):
        user_auth = UserAuth(email="test@example.com")
        new_token = "new_token"
        result = await update_token(user=user_auth, token=new_token, db=self.session)
        self.assertIsNone(result.refresh_token)
        self.assertEqual(user_auth.refresh_token, new_token)

    async def test_get_users(self):
        users = [User(), User(), User()]
        self.session.query().filter().offset().limit().all.return_value = users
        result = await get_users(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, users)

    async def test_get_user_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user(user_id=1, user=self.user, db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user(user_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserSchema(first_name="test", last_name="test", birthday_date="2000-01-01", phone_numbers="0000000000",
                          email="test@mail.com", other_description="test")
        result = await create_users(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.birthday_date, body.birthday_date)
        self.assertEqual(result.phone_numbers, body.phone_numbers)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.other_description, body.other_description)

    async def test_get_birthday(self):
        users = [User(birthday_date="2023-10-26")]
        today = date(2023, 10, 26)
        end_date = date(2023, 10, 27)
        self.session.query().all.return_value = users
        result = await get_birthday(today, end_date, user=self.user, db=self.session)
        self.assertEqual(result, users)

    async def test_search_users(self):
        users = [User(first_name="John"), User(last_name="Doe"), User(email="johndoe@example.com")]
        self.session.query().all.return_value = users
        result = await search_users(first_name="John", last_name=None, email=None, user=self.user, db=self.session)
        self.assertEqual(result, users)

    async def test_remove_user_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await remove_user(user_id=1, user=self.user, db=self.session)
        self.assertEqual(result, user)

    async def test_remove_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_user(user_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_user_found(self):
        body = UserSchema(first_name="test", last_name="test", birthday_date="2000-01-01", phone_numbers="0000000000",
                          email="test@mail.com", other_description="test")
        result = await update_user(user_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.birthday_date, body.birthday_date)
        self.assertEqual(result.phone_numbers, body.phone_numbers)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.other_description, body.other_description)

    async def test_update_user_not_found(self):
        body = UserSchema(first_name="test", last_name="test", birthday_date="2000-01-01", phone_numbers="0000000000",
                          email="test@mail.com", other_description="test")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_user(user_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        user_auth = UserAuth(email="test@example.com", confirmed=False)
        self.session.query().filter().first.return_value = user_auth
        self.session.commit.return_value = None
        result = await confirmed_email(email="test@example.com", db=self.session)
        self.assertTrue(user_auth.confirmed)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
