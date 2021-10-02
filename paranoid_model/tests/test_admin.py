from unittest.mock import MagicMock

from django.test import TestCase
from model_bakery import baker

from paranoid_model.admin import ParanoidAdmin
from paranoid_model.tests.models import Person


class TestParanoidAdmin(TestCase):
    def setUp(self) -> None:
        self.admin = ParanoidAdmin(
            model=Person,
            admin_site=MagicMock()
        )
        self.person = baker.make(Person)

    def test_get_object_even_when_even_when_obj_is_soft_deleted(self):
        person_found = self.admin.get_object(
            request=MagicMock(),
            object_id=self.person.id
        )
        self.assertEqual(self.person, person_found)

    def test_get_object_return_None_when_obj_does_not_exist(self):
        person_id = self.person.id
        self.person.delete(hard_delete=True)

        person_found = self.admin.get_object(
            request=MagicMock(),
            object_id=person_id
        )
        self.assertIsNone(person_found)
