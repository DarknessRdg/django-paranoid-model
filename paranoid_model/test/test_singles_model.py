from django.test import TestCase
from paranoid_model.models import Person
from faker import Faker
from paranoid_model.test.utils import isdeleted, any_list, all_list

fake = Faker('en_US')


class SingleModelTest(TestCase):
    """Test paranoid model behavion on a sigle model"""

    def setUp(self):
        pass

    @staticmethod
    def get_person_instance():
        """
        Method to return an instance of a Person
        not saved on database
        Returns:
            Person()
        """
        return Person(name=fake.prefix() + fake.name())

    def create_list_of_person(self, quantity_saved, quantity_deleted):
        """
        Method to create a list of person on database
        Args:
            quantity_saved: int with amount of instances to save
            quantity_deleted: int with amount of instances to save and then delete
        """
        for count in range(quantity_saved):
            person = self.get_person_instance()
            person.save()

        for count in range(quantity_deleted):
            person = self.get_person_instance()
            person.save()
            person.delete()

    def test_create(self):
        """Test create of a paranoid model"""
        person = self.get_person_instance()
        person.save()

        self.assertIsNotNone(person.created_at)
        self.assertIsNotNone(person.updated_at)
        self.assertIsNone(person.deleted_at)

    def test_soft_delete(self):
        """Test delete of a paranoid model"""
        self.get_person_instance().save()

        person = Person.objects.all().first()
        person.delete()

        self.assertIsNotNone(person.deleted_at)

    def test_all(self):
        """Test query all()"""
        save = 100
        delete = 50
        self.create_list_of_person(save, delete)

        all_without_param = Person.objects.all()
        self.assertTrue(all_list(all_without_param, lambda x: not isdeleted(x)))

    def test_all_with_deleted_param(self):
        """Test query all(with_deleted)"""

        save = 100
        delete = 50
        self.create_list_of_person(save, delete)

        all_without_deleted = Person.objects.all(with_deleted=False)
        self.assertTrue(all_list(all_without_deleted, lambda x: not isdeleted(x)))

        all_with_deleted = Person.objects.all(with_deleted=True)
        self.assertTrue(any_list(all_with_deleted, lambda x: isdeleted(x)))
        self.assertTrue(any_list(all_with_deleted, lambda x: not isdeleted(x)))

    def test_filter(self):
        """Test query filter()"""
        save = 100
        delete = 100
        self.create_list_of_person(save, delete)

        filter_without_param = Person.objects.filter(name__icontains='.')
        self.assertTrue(all_list(filter_without_param, lambda x: not isdeleted(x)))

    def test_filter_with_deleted_param(self):
        """Test query filter(with_deleted)"""
        save = 100
        delete = 100
        self.create_list_of_person(save, delete)

        filter_without_deleted = Person.objects.filter(with_deleted=False, name__icontains='.')
        self.assertTrue(all_list(filter_without_deleted, lambda x: not isdeleted(x)))

        filter_with_deleted = Person.objects.filter(with_deleted=True, name__icontains='.')
        self.assertTrue(any_list(filter_with_deleted, lambda x: isdeleted(x)))
        self.assertTrue(any_list(filter_with_deleted, lambda x: not isdeleted(x)))
