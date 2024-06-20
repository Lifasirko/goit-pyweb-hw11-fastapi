import unittest
from unittest.mock import AsyncMock, MagicMock
from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, email='test_user@example.com', password="qwerty", confirmed=False)
        self.user_data = UserModel(username='test_user', email='test_user@example.com', password='qwerty')

    async def test_get_user_by_email_found(self):
        mocked_user = MagicMock()
        mocked_user.scalars.return_value.first.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email='test_user@example.com', db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_user_by_email_not_found(self):
        mocked_user = MagicMock()
        mocked_user.scalars.return_value.first.return_value = None
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email='non_existent_user@example.com', db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        mocked_gravatar = MagicMock(spec=Gravatar)
        mocked_gravatar.get_image.return_value = 'http://example.com/avatar'
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        with unittest.mock.patch('src.repository.users.Gravatar', return_value=mocked_gravatar):
            result = await create_user(body=self.user_data, db=self.session)

        self.assertIsInstance(result, User)
        self.assertEqual(result.email, self.user_data.email)
        self.assertEqual(result.avatar, 'http://example.com/avatar')

    async def test_update_token(self):
        new_token = 'new_refresh_token'
        self.session.commit.return_value = None
        await update_token(user=self.user, token=new_token, db=self.session)
        self.assertEqual(self.user.refresh_token, new_token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        mocked_user = MagicMock()
        mocked_user.scalars.return_value.first.return_value = self.user
        self.session.execute.return_value = mocked_user
        self.session.commit.return_value = None
        await confirmed_email(email='test_user@example.com', db=self.session)
        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        new_avatar_url = 'http://example.com/new_avatar'
        mocked_user = MagicMock()
        mocked_user.scalars.return_value.first.return_value = self.user
        self.session.execute.return_value = mocked_user
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        result = await update_avatar(email='test_user@example.com', url=new_avatar_url, db=self.session)
        self.assertEqual(result.avatar, new_avatar_url)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(self.user)


if __name__ == '__main__':
    unittest.main()
