from django.test import TestCase
from paranoid_model.tests.models import Person
from faker import Faker
from paranoid_model.tests.utils import any_list, all_list, get_person_instance, create_list_of_person


class SingleModelTest(TestCase):
    """Test paranoid model behavion on a sigle model"""

    def setUp(self):
        pass

    def assertNotRaises(self, function):
        """
        Method to check if a function does not raises an exception
        Args:
            function: callback function name
        """
        try:
            function()
        except Exception as exc:
            self.fail('Raised in a query that was not suposed to! Message: {}'.format(exc))

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
    
    def test_restore(self):
        """Test restore in a single object"""
        person = get_person_instance()
        person.save()
        
        self.assertFalse(person.is_soft_deleted)

        person.delete()
        self.assertTrue(person.is_soft_deleted)

        person.restore()
        self.assertFalse(person.is_soft_deleted)

    def test_restore_in_a_queryset(self):
        """Test restore in a queryset"""
        save, delete = 100, 0
        create_list_of_person(save, delete)

        Person.objects.all().delete()
        self.assertEquals(Person.objects.all().count(), 0)

        Person.objects.all(with_deleted=True).restore()
        self.assertEquals(Person.objects.all().count(), save)


    def test_soft_delete_in_a_queryset(self):
        """Test delete all instances in a querryset"""
        save, delete = 100, 0
        create_list_of_person(save, delete)

        self.assertTrue(all_list(
            Person.objects.all(with_deleted=True),
            lambda person: not person.is_soft_deleted
        ))

        Person.objects.all().delete()
        self.assertEqual(Person.objects.all().count(), 0)
        self.assertTrue(all_list(
            Person.objects.all(with_deleted=True),
            lambda person: person.is_soft_deleted
        ))

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
        self.assertTrue(any_list(
            all_with_deleted, 
            lambda x: x.is_soft_deleted))
        
        self.assertTrue(any_list(
            all_with_deleted, 
            lambda x: not x.is_soft_deleted))

    def test_filter(self):
        """Test query filter()"""
        save = 100
        delete = 100
        create_list_of_person(save, delete)

        filter_without_param = Person.objects.filter(name__icontains='.')
        self.assertTrue(all_list(
            filter_without_param, 
            lambda x: not x.is_soft_deleted))
        
        filter_from_filter = filter_without_param.filter(name__icontains='.')
        self.assertTrue(all_list(
            filter_from_filter, 
            lambda x: not x.is_soft_deleted))

    def test_filter_with_deleted_param(self):
        """Test query filter(with_deleted)"""
        save = 100
        delete = 100
        create_list_of_person(save, delete)

        filter_without_deleted = Person.objects.filter(with_deleted=False, name__icontains='.')
        self.assertTrue(all_list(
            filter_without_deleted, 
            lambda x: not x.is_soft_deleted))

        filter_with_deleted = Person.objects.filter(with_deleted=True, name__icontains='.')
        self.assertTrue(any_list(
            filter_with_deleted, 
            lambda x: x.is_soft_deleted))
        
        self.assertTrue(any_list(
            filter_with_deleted, 
            lambda x: not x.is_soft_deleted))

    def test_get(self):
        """Test get an object with Raises and without Raises"""

        person = get_person_instance()
        name = person.name

        person.save()

        self.assertNotRaises(lambda: Person.objects.get(name=name))

        self.assertRaises(
            Person.DoesNotExist, 
            lambda: Person.objects.get(name=name+'^'))
        
        person.delete()
        self.assertRaises(
            Person.DoesNotExist, 
            lambda: Person.objects.get(name=name+'^'))
        
        self.assertRaises(
            Person.SoftDeleted, 
            lambda: Person.objects.get(name=name))
    
    def test_filter_and_get(self):
        """Test .get() after a .filter() query"""

        person = get_person_instance()
        name = person.name
        person.save()

        query = Person.objects.filter(name=name)
        self.assertEquals(query.count(), 1)

        self.assertNotRaises(lambda: query.get(name=name))

        self.assertRaises(
            Person.DoesNotExist, 
            lambda: query.get(name=name+'^'))

        person.delete()
        self.assertRaises(
            Person.DoesNotExist, 
            lambda: query.get(name=name))

        query = Person.objects.filter(name=name, with_deleted=True)
        self.assertRaises(
            Person.SoftDeleted, 
            lambda: query.get(name=name))

    def test_get_deleted(self):
        """Test get on deleted item"""
        
        person = get_person_instance()
        person.save()
        name = person.name 
        
        self.assertRaises(
            Person.IsNotSoftDeleted, 
            lambda: Person.objects.get_deleted(name=name))
        
        person.delete()
        self.assertNotRaises(lambda: Person.objects.get_deleted(name=name))

    def test_get_or_restore(self):
        """Test get_or_restore on an single model"""

        person = get_person_instance()
        person.save()
        person.delete()

        self.assertTrue(person.is_soft_deleted)
        self.assertFalse(Person.objects.get_or_restore(name=person.name).is_soft_deleted)
        
        self.assertRaises(
            Person.DoesNotExist,
            lambda: Person.objects.get_or_restore(name=person.name+'^'))
            
        get_person_instance().save()
        self.assertRaises(
            Person.MultipleObjectsReturned,
            lambda: Person.objects.get())
    
    def test_filter_deleted_only(self):
        """Test filter deleted_only"""
        
        save, delete = 100, 200
        create_list_of_person(save, delete)

        deleted = Person.objects.deleted_only()
        self.assertEquals(deleted.count(), delete)
        
        deleted = Person.objects.all(with_deleted=True).deleted_only()
        self.assertEquals(deleted.count(), delete)

        deleted_zero = Person.objects.all().deleted_only()
        self.assertEquals(deleted_zero.count(), 0)