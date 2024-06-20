import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    cr_contact,
    update_contact,
    delete_contact,
    search_contacts,
    get_upcoming_birthdays
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', password="qwerty", confirmed=True)
        self.contact_data = ContactCreate(first_name="John", last_name="Doe", email="johndoe@example.com",
                                          phone_number="1234567890")

    async def test_get_contacts(self):
        contacts = [Contact(id=i, user_id=self.user.id) for i in range(3)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(db=self.session, user=self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact(id=1, user_id=self.user.id)
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(db=self.session, user=self.user, contact_id=1)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await get_contact(db=self.session, user=self.user, contact_id=1)
        self.assertIsNone(result)

    async def test_create_contact(self):
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        result = await cr_contact(db=self.session, user=self.user, contact=self.contact_data)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, self.contact_data.first_name)
        self.assertEqual(result.last_name, self.contact_data.last_name)
        self.assertEqual(result.email, self.contact_data.email)

    async def test_update_contact_found(self):
        contact = Contact(id=1, user_id=self.user.id)
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        update_data = ContactUpdate(first_name="Jane", last_name="Doe", email="janedoe@example.com",
                                    phone_number="0987654321")
        result = await update_contact(db=self.session, contact_id=1, user=self.user, contact=update_data)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, update_data.first_name)
        self.assertEqual(result.last_name, update_data.last_name)
        self.assertEqual(result.email, update_data.email)

    async def test_update_contact_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = None
        self.session.execute.return_value = mocked_contact
        update_data = ContactUpdate(first_name="Jane", last_name="Doe", email="janedoe@example.com",
                                    phone_number="0987654321")
        result = await update_contact(db=self.session, contact_id=1, user=self.user, contact=update_data)
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = Contact(id=1, user_id=self.user.id)
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(db=self.session, contact_id=1, user=self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(db=self.session, contact_id=1, user=self.user)
        self.assertIsNone(result)

    async def test_search_contacts(self):
        contacts = [Contact(id=i, user_id=self.user.id) for i in range(3)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts(db=self.session, query="John", user=self.user)
        self.assertEqual(result, contacts)

    async def test_get_upcoming_birthdays(self):
        contacts = [Contact(id=i, user_id=self.user.id, birthday=date.today() + timedelta(days=i)) for i in range(3)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_upcoming_birthdays(db=self.session, user=self.user)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
