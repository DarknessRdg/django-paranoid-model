from django.db.models import Q
from django.test import TestCase

from paranoid_model.tests.models import Person

from model_bakery import baker
import time


class SingleModelTest(TestCase):
    """Test paranoid model behavion on a single model"""
    databases = '__all__'

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
        person = baker.make(Person)

        self.assertIsNotNone(person.created_at)
        self.assertIsNotNone(person.updated_at)
        self.assertIsNone(person.deleted_at)

    def test_created_at_and_updated_at(self):
        """Test fields created_at and updated_ad"""
        person = baker.make(Person)
        person.save()

        self.assertEqual(
            person.created_at.replace(microsecond=0),
            person.updated_at.replace(microsecond=0)
        )
        # Replace microseconds possibles machine delays don't interfere

        seconds = .1
        time.sleep(seconds)  # wait seconds before save again so time should be different
        person.save()

        self.assertNotEqual(person.created_at, person.updated_at)

    def test_soft_delete(self):
        """Test delete of a paranoid model"""
        person = baker.make(Person)
        person.delete()
        self.assertIsNotNone(person.deleted_at)

    def test_restore(self):
        """Test restore in a single object"""
        person = baker.make(Person)

        self.assertFalse(person.is_soft_deleted)

        person.delete()
        self.assertTrue(person.is_soft_deleted)

        person.restore()
        self.assertFalse(person.is_soft_deleted)

    def test_restore_in_a_queryset(self):
        """Test restore in a queryset"""
        baker.make(Person, _quantity=10)

        Person.objects.all().delete()
        self.assertEqual(Person.objects.all().count(), 0)

        Person.objects.all(with_deleted=True).restore()
        self.assertEqual(Person.objects.all().count(), 10)

    def test_soft_delete_in_a_queryset(self):
        """Test soft delete all instances in a querryset"""
        baker.make(Person, _quantity=10)

        for person in Person.objects.all(with_deleted=True):
            self.assertFalse(person.is_soft_deleted)

        Person.objects.all().delete()
        self.assertEqual(Person.objects.all().count(), 0)

        for person in Person.objects.all(with_deleted=True):
            self.assertTrue(person.is_soft_deleted)

    def test_all(self):
        """Test query all()"""
        baker.make(Person, _quantity=10)
        baker.make(Person, _quantity=5, _fill_optional=['deleted_at'])

        all_without_param = Person.objects.all()
        for person in all_without_param:
            self.assertFalse(person.is_soft_deleted)

    def test_all_with_deleted_param(self):
        """Test query all(with_deleted)"""
        baker.make(Person, _quantity=10)
        baker.make(Person, _quantity=5, _fill_optional=['deleted_at'])

        all_without_deleted = Person.objects.all(with_deleted=False)
        for person in all_without_deleted:
            self.assertFalse(person.is_soft_deleted)

        all_with_deleted = Person.objects.all(with_deleted=True)

        self.assertTrue(
            filter(lambda instance: instance.is_soft_deleted, all_with_deleted)
        )

        self.assertTrue(
            filter(lambda instance: not instance.is_soft_deleted, all_with_deleted)
        )

    def test_filter(self):
        """Test query filter()"""
        baker.make(Person, _quantity=10)
        baker.make(Person, _quantity=10, _fill_optional=['deleted_at'])

        filter_without_param = Person.objects.filter()
        self.assertTrue(
            filter(lambda instance: instance.is_soft_deleted, filter_without_param)
        )

        filter_from_filter = filter_without_param.filter()
        self.assertTrue(
            filter(lambda instance: not instance.is_soft_deleted, filter_from_filter))

    def test_filter_with_q_object_should_not_return_deleted_objects(self):
        """Test query filter()"""
        baker.make(Person, _quantity=1, name='foo')
        baker.make(Person, _quantity=10, _fill_optional=['deleted_at'])

        filter_without_param = Person.objects.filter(Q(name='foo'))
        self.assertEqual(filter_without_param.count(), 1)
        self.assertTrue(
            filter(lambda instance: instance.is_soft_deleted, filter_without_param)
        )

        filter_from_filter = filter_without_param.filter()
        self.assertTrue(
            filter(lambda instance: not instance.is_soft_deleted, filter_from_filter))

    def test_filter_with_deleted_param(self):
        """Test query filter(with_deleted)"""
        baker.make(Person, _quantity=10)
        baker.make(Person, _quantity=10, _fill_optional=['deleted_at'])

        filter_without_deleted = Person.objects.filter(with_deleted=False)
        self.assertTrue(
            filter(lambda instance: not instance.is_soft_deleted, filter_without_deleted)
        )

        filter_with_deleted = Person.objects.filter(with_deleted=True)
        self.assertTrue(
            filter(lambda instance: instance.is_soft_deleted, filter_with_deleted)
        )

        self.assertTrue(
            filter(lambda instance: not instance.is_soft_deleted, filter_with_deleted)
        )

    def test_get(self):
        """Test get an object with Raises and without Raises"""
        person = baker.make(Person)
        name = person.name

        self.assertNotRaises(Person.objects.get)

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(name=name+'^')

        person.delete()
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(name=name+'^')

        with self.assertRaises(Person.SoftDeleted):
            Person.objects.get(name=name)

    def test_filter_and_get(self):
        """Test .get() after a .filter() query"""
        person = baker.make(Person)
        name = person.name

        query = Person.objects.filter()
        self.assertEqual(query.count(), 1)

        self.assertNotRaises(query.get)

        with self.assertRaises(Person.DoesNotExist):
            query.get(name=name+'^')

        person.delete()
        with self.assertRaises(Person.DoesNotExist):
            query.get()

        query = Person.objects.filter(with_deleted=True)
        with self.assertRaises(Person.SoftDeleted):
            query.get()

    def test_get_deleted(self):
        """Test get on deleted item"""
        person = baker.make(Person)

        with self.assertRaises(Person.IsNotSoftDeleted):
            Person.objects.get_deleted()

        person.delete()
        self.assertNotRaises(Person.objects.get_deleted)

    def test_get_or_restore(self):
        """Test get_or_restore on an single model"""
        person = baker.make(Person)
        person.delete()

        self.assertTrue(person.is_soft_deleted)

        person = Person.objects.get_or_restore(name=person.name)
        self.assertFalse(person.is_soft_deleted)

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get_or_restore(name=person.name+'^')

        baker.make(Person)
        with self.assertRaises(Person.MultipleObjectsReturned):
            Person.objects.get()

    def test_filter_deleted_only(self):
        """Test filter deleted_only"""
        baker.make(Person, _quantity=5)
        baker.make(Person, _quantity=10, _fill_optional=['deleted_at'])

        deleted = Person.objects.deleted_only()
        self.assertEqual(deleted.count(), 10)

        deleted = Person.objects.all(with_deleted=True).deleted_only()
        self.assertEqual(deleted.count(), 10)

        deleted_zero = Person.objects.all().deleted_only()
        self.assertEqual(deleted_zero.count(), 0)

    def test_delete_using(self):
        using = 'db2'
        person = baker.make(Person, _save_kwargs={'using': using})

        person.delete()
        self.assertTrue(person.is_soft_deleted)

    def test_save_using(self):
        using = 'db2'
        person = baker.make(Person, _save_kwargs={'using': using})

        self.assertIsNotNone(person.id)
        self.assertNotRaises(Person.objects.using(using).get)
