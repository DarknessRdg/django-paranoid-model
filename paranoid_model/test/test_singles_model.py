from django.test import TestCase
from paranoid_model.test.models import Person
from faker import Faker
from paranoid_model.test.utils import any_list, all_list, get_person_instance, create_list_of_person

fake = Faker('en_US')


class SingleModelTest(TestCase):
    """Test paranoid model behavion on a sigle model"""

    def setUp(self):
        pass

    def test_create(self):
        """Test create of a paranoid model"""
        person = get_person_instance()
        person.save()

        self.assertIsNotNone(person.created_at)
        self.assertIsNotNone(person.updated_at)
        self.assertIsNone(person.deleted_at)

    def test_soft_delete(self):
        """Test delete of a paranoid model"""
        get_person_instance().save()

        person = Person.objects.all().first()
        person.delete()

        self.assertIsNotNone(person.deleted_at)

    def test_all(self):
        """Test query all()"""
        save = 100
        delete = 50
        create_list_of_person(save, delete)

        all_without_param = Person.objects.all()
        self.assertTrue(all_list(all_without_param, lambda x: not x.is_soft_deleted))

    def test_all_with_deleted_param(self):
        """Test query all(with_deleted)"""

        save = 100
        delete = 50
        create_list_of_person(save, delete)

        all_without_deleted = Person.objects.all(with_deleted=False)
        self.assertTrue(all_list(all_without_deleted, lambda x: not x.is_soft_deleted))

        all_with_deleted = Person.objects.all(with_deleted=True)
        self.assertTrue(any_list(all_with_deleted, lambda x: x.is_soft_deleted))
        self.assertTrue(any_list(all_with_deleted, lambda x: not x.is_soft_deleted))

    def test_filter(self):
        """Test query filter()"""
        save = 100
        delete = 100
        create_list_of_person(save, delete)

        filter_without_param = Person.objects.filter(name__icontains='.')
        self.assertTrue(all_list(filter_without_param, lambda x: not x.is_soft_deleted))

    def test_filter_with_deleted_param(self):
        """Test query filter(with_deleted)"""
        save = 100
        delete = 100
        create_list_of_person(save, delete)

        filter_without_deleted = Person.objects.filter(with_deleted=False, name__icontains='.')
        self.assertTrue(all_list(filter_without_deleted, lambda x: not x.is_soft_deleted))

        filter_with_deleted = Person.objects.filter(with_deleted=True, name__icontains='.')
        self.assertTrue(any_list(filter_with_deleted, lambda x: x.is_soft_deleted))
        self.assertTrue(any_list(filter_with_deleted, lambda x: not x.is_soft_deleted))
